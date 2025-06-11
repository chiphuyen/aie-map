from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request
from models import Base, Book, City, Review, ReviewAsset, ReviewCreate, ReviewResponse, CityStats
from comprehensive_location_data import validate_location, get_coordinates, get_city_suggestions, get_country_suggestions, get_all_countries
from typing import List, Optional, Union
import os
import json
from datetime import datetime, date
from dateutil import parser
import requests
import pytesseract
from PIL import Image
import uuid

app = FastAPI(title="AIE Map", description="Track book reviews on a world map")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./aie_map.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_data(db: Session):
    """Initialize default books if they don't exist"""
    if db.query(Book).count() == 0:
        books = [
            Book(title="AI Engineering", short_name="AIE", pin_color="#FF0000"),
            Book(title="Designing Machine Learning Systems", short_name="DMLS", pin_color="#00FF00")
        ]
        db.add_all(books)
        db.commit()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    init_default_data(db)
    db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return templates.TemplateResponse("upload.html", {"request": request, "books": books})

@app.get("/api/cities/suggestions")
async def get_city_suggestions_api(q: str = "", db: Session = Depends(get_db)):
    """Get city suggestions for autocomplete - includes both predefined and user-added cities"""
    if len(q) < 2:
        return []
    
    # Get suggestions from predefined list
    predefined_suggestions = get_city_suggestions(q, limit=15)
    
    # Get suggestions from database (user-added cities)
    q_lower = q.lower()
    db_cities = db.query(City).filter(
        City.name.ilike(f"%{q}%")
    ).limit(10).all()
    
    db_suggestions = [
        {
            "city": city.name,
            "country": city.country,
            "full_name": f"{city.name}, {city.country}",
            "source": "database"
        }
        for city in db_cities
    ]
    
    # Combine and deduplicate
    all_suggestions = predefined_suggestions + db_suggestions
    seen = set()
    unique_suggestions = []
    
    for suggestion in all_suggestions:
        key = f"{suggestion['city']}, {suggestion['country']}"
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(suggestion)
    
    return unique_suggestions[:20]

@app.get("/api/countries/suggestions")
async def get_country_suggestions_api(q: str = ""):
    """Get country suggestions for autocomplete"""
    if len(q) < 2:
        return []
    return get_country_suggestions(q, limit=20)


@app.get("/api/countries")
async def get_all_countries_api():
    """Get all valid countries"""
    return get_all_countries()

@app.get("/api/map-data")
async def get_map_data(db: Session = Depends(get_db)):
    """Get separate review data for each book type per city"""
    
    # Debug: Check total reviews and cities
    total_reviews = db.query(Review).count()
    total_cities = db.query(City).count()
    print(f"DEBUG: Total reviews: {total_reviews}, Total cities: {total_cities}")
    
    # Query to get separate entries for each book type per city
    query = db.query(
        City.name,
        City.country, 
        City.latitude,
        City.longitude,
        Book.short_name,
        Book.title,
        Book.pin_color,
        func.count(Review.id).label('review_count')
    ).join(Review, City.id == Review.city_id)\
     .join(Book, Review.book_id == Book.id)\
     .group_by(City.id, Book.id)
    
    result = query.all()
    print(f"DEBUG: Map data query returned {len(result)} city-book combinations")
    
    map_data = [
        {
            "city_name": row.name,
            "country": row.country,
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "book_short_name": row.short_name,
            "book_title": row.title,
            "pin_color": row.pin_color,
            "review_count": row.review_count
        }
        for row in result
    ]
    
    print(f"DEBUG: Returning map data: {map_data}")
    return map_data

@app.get("/api/reviews/filtered")
async def get_filtered_reviews(
    request: Request,
    book_id: Union[int, None] = None,
    city: Union[str, None] = None, 
    country: Union[str, None] = None,
    company: Union[str, None] = None,
    db: Session = Depends(get_db)
):
    """Get reviews with combined filters"""
    print(f"DEBUG: Received params - book_id: {book_id}, city: {city}, country: {country}, company: {company}")
    
    # Start with base query
    query = db.query(Review, Book, City).join(Book, Review.book_id == Book.id)\
              .join(City, Review.city_id == City.id)
    
    # Apply filters cumulatively
    active_filters = []
    
    if book_id:
        query = query.filter(Review.book_id == book_id)
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            active_filters.append(f"Book: {book.title}")
    
    if city and country:
        query = query.filter(City.name == city, City.country == country)
        active_filters.append(f"Location: {city}, {country}")
    elif city:
        query = query.filter(City.name == city)
        active_filters.append(f"City: {city}")
    elif country:
        query = query.filter(City.country == country)
        active_filters.append(f"Country: {country}")
    
    if company:
        query = query.filter(Review.company.ilike(f"%{company}%"))
        active_filters.append(f"Company: {company}")
    
    # Execute query
    reviews = query.all()
    
    # Format results
    result = []
    for review, book, city_obj in reviews:
        # Get assets for this review
        assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.id).all()
        
        result.append({
            "id": review.id,
            "book_title": book.title,
            "book_short_name": book.short_name,
            "city_name": city_obj.name,
            "country": city_obj.country,
            "review_text": review.review_text,
            "reviewer_name": review.reviewer_name,
            "company": review.company,
            "role": review.role,
            "review_date": review.review_date.isoformat() if review.review_date else None,
            "created_at": review.created_at,
            "original_post_url": review.original_post_url,
            "social_media_url": review.social_media_url,
            "source": review.source,
            "assets": [
                {
                    "id": asset.id,
                    "file_path": asset.file_path,
                    "file_name": asset.file_name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "created_at": asset.created_at
                }
                for asset in assets
            ]
        })
    
    return {
        "filters": {
            "book_id": book_id,
            "city": city,
            "country": country,
            "company": company,
            "active_filters": active_filters
        },
        "reviews": result,
        "total_count": len(result)
    }

@app.get("/api/autocomplete/cities")
async def get_autocomplete_cities(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Get cities for autocomplete based on reviews in database"""
    # Get distinct cities from reviews
    cities_query = db.query(City.name, City.country).join(Review).distinct()
    
    if query:
        cities_query = cities_query.filter(City.name.ilike(f"%{query}%"))
    
    cities = cities_query.order_by(City.name).all()
    
    return [{"name": city.name, "country": city.country, "label": f"{city.name}, {city.country}"} for city in cities]

@app.get("/api/autocomplete/countries")
async def get_autocomplete_countries(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Get countries for autocomplete based on reviews in database"""
    # Get distinct countries from reviews
    countries_query = db.query(City.country).join(Review).distinct()
    
    if query:
        countries_query = countries_query.filter(City.country.ilike(f"%{query}%"))
    
    countries = countries_query.order_by(City.country).all()
    
    return [{"name": country[0], "label": country[0]} for country in countries]

@app.get("/api/autocomplete/companies")
async def get_autocomplete_companies(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Get companies for autocomplete based on reviews in database"""
    # Get distinct companies from reviews
    companies_query = db.query(Review.company).filter(Review.company.isnot(None)).distinct()
    
    if query:
        companies_query = companies_query.filter(Review.company.ilike(f"%{query}%"))
    
    companies = companies_query.order_by(Review.company).all()
    
    return [{"name": company[0], "label": company[0]} for company in companies if company[0]]

@app.get("/api/reviews/{city_name}")
async def get_city_reviews(city_name: str, country: str, db: Session = Depends(get_db)):
    """Get all reviews for a specific city"""
    city = db.query(City).filter(City.name == city_name, City.country == country).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    reviews = db.query(Review, Book).join(Book, Review.book_id == Book.id)\
                .filter(Review.city_id == city.id).all()
    
    result = []
    for review in reviews:
        # Get assets for this review
        assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.Review.id).all()
        
        result.append({
            "id": review.Review.id,
            "book_title": review.Book.title,
            "book_short_name": review.Book.short_name,
            "city_name": city.name,
            "country": city.country,
            "review_text": review.Review.review_text,
            "reviewer_name": review.Review.reviewer_name,
            "company": review.Review.company,
            "role": review.Review.role,
            "review_date": review.Review.review_date.isoformat() if review.Review.review_date else None,
            "created_at": review.Review.created_at,
            "original_post_url": review.Review.original_post_url,
            "social_media_url": review.Review.social_media_url,
            "source": review.Review.source,
            "assets": [
                {
                    "id": asset.id,
                    "file_path": asset.file_path,
                    "file_name": asset.file_name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "created_at": asset.created_at
                }
                for asset in assets
            ]
        })
    
    return result


def get_or_create_city(db: Session, city_name: str, country: str) -> City:
    """Get existing city or create new one with comprehensive geocoding"""
    city = db.query(City).filter(City.name == city_name, City.country == country).first()
    
    if not city:
        # Try multiple sources for coordinates:
        # 1. Comprehensive geonames database
        coords = get_coordinates(city_name, country)
        
        # 2. Fallback to Nominatim API for any location
        if not coords:
            coords = geocode_city_api(city_name, country)
        
        if not coords:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not find coordinates for '{city_name}, {country}'. Please check the spelling and try again, or verify this location exists."
            )
        
        print(f"DEBUG: Creating new city: {city_name}, {country} at {coords}")
        
        city = City(
            name=city_name,
            country=country,
            latitude=coords[0],
            longitude=coords[1]
        )
        db.add(city)
        db.commit()
        db.refresh(city)
    
    return city

def geocode_city_api(city_name: str, country: str) -> Optional[tuple]:
    """Get coordinates using Nominatim API for any city"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{city_name}, {country}",
            "format": "json",
            "limit": 1
        }
        response = requests.get(url, params=params, headers={"User-Agent": "AIE-Map/1.0"})
        data = response.json()
        
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

@app.post("/api/reviews")
async def create_review(review_data: ReviewCreate, file_path: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a new review"""
    print(f"DEBUG: Creating review for book {review_data.book_id}, city {review_data.city_name}, {review_data.country}")
    
    book = db.query(Book).filter(Book.id == review_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    print(f"DEBUG: Found book: {book.title}")
    
    city = get_or_create_city(db, review_data.city_name, review_data.country)
    print(f"DEBUG: City: {city.name}, {city.country} (ID: {city.id})")
    
    # Parse date if provided
    review_date = None
    if review_data.review_date:
        try:
            review_date = parser.parse(review_data.review_date).date()
        except:
            pass
    
    review = Review(
        book_id=review_data.book_id,
        city_id=city.id,
        review_text=review_data.review_text,
        reviewer_name=review_data.reviewer_name,
        company=review_data.company,
        role=review_data.role,
        review_date=review_date,
        original_post_url=review_data.original_post_url,
        social_media_url=review_data.social_media_url,
        source=review_data.source,
        screenshot_path=file_path
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    print(f"DEBUG: Created review with ID: {review.id}")
    
    # Add asset if file_path provided
    if file_path:
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            asset = ReviewAsset(
                review_id=review.id,
                file_path=file_path,
                file_name=file_name,
                file_type="image",
                file_size=file_size
            )
            db.add(asset)
            db.commit()
            print(f"DEBUG: Added asset for review {review.id}")
        except Exception as e:
            print(f"Error adding asset: {e}")
    
    return {"id": review.id, "message": "Review created successfully"}

def extract_text_from_image(image_path: str) -> str:
    """Extract text from uploaded screenshot using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

@app.post("/api/upload-screenshot")
async def upload_screenshot(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload screenshot and extract review information"""
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    file_path = f"uploads/{file_id}.{file_extension}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Extract text using OCR
    extracted_text = extract_text_from_image(file_path)
    
    # Basic text analysis to extract information
    extracted_info = {
        "raw_text": extracted_text,
        "book_detected": None,
        "books_detected": [],
        "reviewer_name": None,
        "company": None,
        "role": None,
        "review_text": extracted_text[:500] if extracted_text else None,
        "source": None,
        "file_info": {
            "file_path": file_path,
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": "image"
        }
    }
    
    # Simple book detection - can detect both books
    text_lower = extracted_text.lower()
    if "ai engineering" in text_lower or "aie" in text_lower:
        extracted_info["books_detected"].append("AIE")
    if "designing machine learning" in text_lower or "dmls" in text_lower:
        extracted_info["books_detected"].append("DMLS")
    
    # Set primary book if only one detected
    if len(extracted_info["books_detected"]) == 1:
        extracted_info["book_detected"] = extracted_info["books_detected"][0]
    
    # Detect common review sources
    if "goodreads" in text_lower:
        extracted_info["source"] = "GoodReads"
    elif "amazon" in text_lower:
        extracted_info["source"] = "Amazon"
    elif "linkedin" in text_lower:
        extracted_info["source"] = "LinkedIn"
    elif "twitter" in text_lower or "x.com" in text_lower:
        extracted_info["source"] = "X"
    
    return {
        "file_path": file_path,
        "extracted_info": extracted_info
    }

@app.get("/api/reviews/by-book/{book_id}")
async def get_reviews_by_book(book_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific book"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    reviews = db.query(Review, City).join(City, Review.city_id == City.id)\
                .filter(Review.book_id == book_id).all()
    
    result = []
    for review, city in reviews:
        # Get assets for this review
        assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.id).all()
        
        result.append({
            "id": review.id,
            "book_title": book.title,
            "book_short_name": book.short_name,
            "city_name": city.name,
            "country": city.country,
            "review_text": review.review_text,
            "reviewer_name": review.reviewer_name,
            "company": review.company,
            "role": review.role,
            "review_date": review.review_date.isoformat() if review.review_date else None,
            "created_at": review.created_at,
            "original_post_url": review.original_post_url,
            "social_media_url": review.social_media_url,
            "source": review.source,
            "assets": [
                {
                    "id": asset.id,
                    "file_path": asset.file_path,
                    "file_name": asset.file_name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "created_at": asset.created_at
                }
                for asset in assets
            ]
        })
    
    return {
        "book": {
            "id": book.id,
            "title": book.title,
            "short_name": book.short_name,
            "pin_color": book.pin_color
        },
        "reviews": result,
        "total_count": len(result)
    }

@app.get("/api/reviews/by-location")
async def get_reviews_by_location(city: Optional[str] = None, country: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all reviews for a specific city/country or country only"""
    if not city and not country:
        raise HTTPException(status_code=400, detail="Either city or country must be provided")
    
    # If both city and country are provided, filter by specific city
    if city and country:
        city_obj = db.query(City).filter(City.name == city, City.country == country).first()
        if not city_obj:
            raise HTTPException(status_code=404, detail="City not found")
        
        reviews = db.query(Review, Book, City).join(Book, Review.book_id == Book.id)\
                    .join(City, Review.city_id == City.id)\
                    .filter(Review.city_id == city_obj.id).all()
        
        location_info = {
            "type": "city",
            "city": city_obj.name,
            "country": city_obj.country,
            "latitude": float(city_obj.latitude),
            "longitude": float(city_obj.longitude)
        }
    
    # If only country is provided, filter by country
    elif country:
        reviews = db.query(Review, Book, City).join(Book, Review.book_id == Book.id)\
                    .join(City, Review.city_id == City.id)\
                    .filter(City.country == country).all()
        
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this country")
        
        location_info = {
            "type": "country",
            "country": country
        }
    
    # If only city is provided (any country), filter by city name
    else:  # city but no country
        reviews = db.query(Review, Book, City).join(Book, Review.book_id == Book.id)\
                    .join(City, Review.city_id == City.id)\
                    .filter(City.name == city).all()
        
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this city")
        
        location_info = {
            "type": "city_global",
            "city": city
        }
    
    result = []
    for review, book, city_obj in reviews:
        # Get assets for this review
        assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.id).all()
        
        result.append({
            "id": review.id,
            "book_title": book.title,
            "book_short_name": book.short_name,
            "city_name": city_obj.name,
            "country": city_obj.country,
            "review_text": review.review_text,
            "reviewer_name": review.reviewer_name,
            "company": review.company,
            "role": review.role,
            "review_date": review.review_date.isoformat() if review.review_date else None,
            "created_at": review.created_at,
            "original_post_url": review.original_post_url,
            "social_media_url": review.social_media_url,
            "source": review.source,
            "assets": [
                {
                    "id": asset.id,
                    "file_path": asset.file_path,
                    "file_name": asset.file_name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "created_at": asset.created_at
                }
                for asset in assets
            ]
        })
    
    return {
        "location": location_info,
        "reviews": result,
        "total_count": len(result)
    }

@app.get("/api/reviews/by-company/{company_name}")
async def get_reviews_by_company(company_name: str, db: Session = Depends(get_db)):
    """Get all reviews for a specific company"""
    reviews = db.query(Review, Book, City).join(Book, Review.book_id == Book.id)\
                .join(City, Review.city_id == City.id)\
                .filter(Review.company.ilike(f"%{company_name}%")).all()
    
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this company")
    
    result = []
    for review, book, city in reviews:
        # Get assets for this review
        assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.id).all()
        
        result.append({
            "id": review.id,
            "book_title": book.title,
            "book_short_name": book.short_name,
            "city_name": city.name,
            "country": city.country,
            "review_text": review.review_text,
            "reviewer_name": review.reviewer_name,
            "company": review.company,
            "role": review.role,
            "review_date": review.review_date.isoformat() if review.review_date else None,
            "created_at": review.created_at,
            "original_post_url": review.original_post_url,
            "social_media_url": review.social_media_url,
            "source": review.source,
            "assets": [
                {
                    "id": asset.id,
                    "file_path": asset.file_path,
                    "file_name": asset.file_name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "created_at": asset.created_at
                }
                for asset in assets
            ]
        })
    
    return {
        "company": company_name,
        "reviews": result,
        "total_count": len(result)
    }


@app.get("/reviews", response_class=HTMLResponse)
async def reviews_page(request: Request, book_id: Optional[int] = None, city: Optional[str] = None, 
                      country: Optional[str] = None, company: Optional[str] = None, db: Session = Depends(get_db)):
    """Reviews listing page with optional filters"""
    books = db.query(Book).all()
    return templates.TemplateResponse("reviews.html", {
        "request": request, 
        "books": books,
        "book_id": book_id,
        "city": city,
        "country": country,
        "company": company
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)