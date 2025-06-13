from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Cookie, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request
from models import Base, Book, City, Review, ReviewAsset, ReviewCreate, ReviewResponse, CityStats, AdminSession
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
from dotenv import load_dotenv
from auth import (
    verify_password, check_rate_limit, record_login_attempt, 
    create_session, get_session, delete_session, clean_expired_sessions,
    get_client_ip, SESSION_COOKIE_NAME
)

# Load environment variables
load_dotenv()

app = FastAPI(title="AIE Map", description="Track book reviews on a world map")

# Create directories FIRST before database connection
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Determine data directory based on environment
# Render mounts disk at /app/data, locally we use ./data
DATA_DIR = os.getenv("RENDER", None) and "/app/data" or "./data"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{DATA_DIR}/uploads", exist_ok=True)

# Database setup
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/aie_map.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(
    request: Request,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db)
) -> Optional[AdminSession]:
    """Get current admin session if authenticated"""
    if not session_id:
        return None
    
    session = get_session(db, session_id)
    return session

def require_admin(
    session: Optional[AdminSession] = Depends(get_current_admin)
) -> AdminSession:
    """Require admin authentication"""
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return session

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
async def home(request: Request, admin_session: Optional[AdminSession] = Depends(get_current_admin)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "is_admin": admin_session is not None
    })

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
    
    db_suggestions = []
    for city in db_cities:
        # Build display name with state if available
        display_parts = [city.name]
        if city.state:
            display_parts.append(city.state)
        display_parts.append(city.country)
        
        db_suggestions.append({
            "city": city.name,
            "country": city.country,
            "state": city.state,
            "full_name": ", ".join(display_parts),
            "source": "database"
        })
    
    # Combine and deduplicate
    all_suggestions = predefined_suggestions + db_suggestions
    seen = set()
    unique_suggestions = []
    
    for suggestion in all_suggestions:
        # Include state in deduplication key to allow same city name in different states
        state_part = f", {suggestion.get('state')}" if suggestion.get('state') else ""
        key = f"{suggestion['city']}{state_part}, {suggestion['country']}"
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

@app.get("/api/books")
async def get_books(db: Session = Depends(get_db)):
    """Get all books"""
    books = db.query(Book).all()
    return books

@app.get("/api/map-data")
async def get_map_data(db: Session = Depends(get_db)):
    """Get separate review data for each book type per city"""
    
    # Debug: Check total reviews and cities
    total_reviews = db.query(Review).count()
    total_cities = db.query(City).count()
    
    # Query to get separate entries for each book type per city
    query = db.query(
        City.name,
        City.country,
        City.state,
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
    
    map_data = [
        {
            "city_name": row.name,
            "country": row.country,
            "state": row.state,
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "book_short_name": row.short_name,
            "book_title": row.title,
            "pin_color": row.pin_color,
            "review_count": row.review_count
        }
        for row in result
    ]
    
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
    # Sanitize string inputs
    city = city.strip() if city else None
    country = country.strip() if country else None
    company = company.strip() if company else None
    
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
        query = query.filter(func.lower(City.name) == city.lower(), func.lower(City.country) == country.lower())
        active_filters.append(f"Location: {city}, {country}")
    elif city:
        query = query.filter(func.lower(City.name) == city.lower())
        active_filters.append(f"City: {city}")
    elif country:
        query = query.filter(func.lower(City.country) == country.lower())
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
            "state": city_obj.state,
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
    # Sanitize input
    query = query.strip() if query else None
    
    # Get distinct cities from reviews
    cities_query = db.query(City.name, City.country).join(Review).distinct()
    
    if query:
        cities_query = cities_query.filter(City.name.ilike(f"%{query}%"))
    
    cities = cities_query.order_by(City.name).all()
    
    return [{"name": city.name, "country": city.country, "label": f"{city.name}, {city.country}"} for city in cities]

@app.get("/api/autocomplete/countries")
async def get_autocomplete_countries(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Get countries for autocomplete based on reviews in database"""
    # Sanitize input
    query = query.strip() if query else None
    
    # Get distinct countries from reviews
    countries_query = db.query(City.country).join(Review).distinct()
    
    if query:
        countries_query = countries_query.filter(City.country.ilike(f"%{query}%"))
    
    countries = countries_query.order_by(City.country).all()
    
    return [{"name": country[0], "label": country[0]} for country in countries]

@app.get("/api/autocomplete/companies")
async def get_autocomplete_companies(query: Optional[str] = None, db: Session = Depends(get_db)):
    """Get companies for autocomplete based on reviews in database"""
    # Sanitize input
    query = query.strip() if query else None
    
    # Get distinct companies from reviews
    companies_query = db.query(Review.company).filter(Review.company.isnot(None)).distinct()
    
    if query:
        companies_query = companies_query.filter(Review.company.ilike(f"%{query}%"))
    
    companies = companies_query.order_by(Review.company).all()
    
    return [{"name": company[0], "label": company[0]} for company in companies if company[0]]

@app.get("/api/reviews/{city_name}")
async def get_city_reviews(city_name: str, country: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all reviews for a specific city"""
    # Sanitize inputs
    city_name = city_name.strip()
    country = country.strip()
    state = state.strip() if state else None
    
    # Case-insensitive search with optional state
    query = db.query(City).filter(
        func.lower(City.name) == func.lower(city_name),
        func.lower(City.country) == func.lower(country)
    )
    
    if state:
        query = query.filter(func.lower(City.state) == func.lower(state))
    else:
        # Handle both NULL and empty string for state when not specified
        query = query.filter((City.state.is_(None)) | (City.state == ""))
    
    city = query.first()
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
            "state": city.state,
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


def get_or_create_city(db: Session, city_name: str, country: str, state: Optional[str] = None) -> City:
    """Get existing city or create new one with comprehensive geocoding"""
    # Input is already sanitized by Pydantic validator
    # Build query with optional state
    # We need to be precise about state matching to handle cities with same name
    
    # Normalize empty string to None for consistent handling
    if state == "":
        state = None
    
    if state:
        # If state is provided, look for exact match including state
        city = db.query(City).filter(
            func.lower(City.name) == city_name.lower(), 
            func.lower(City.country) == country.lower(),
            func.lower(City.state) == state.lower()
        ).first()
    else:
        # If no state provided, look for entry without state (NULL or empty string)
        city = db.query(City).filter(
            func.lower(City.name) == city_name.lower(), 
            func.lower(City.country) == country.lower(),
            (City.state.is_(None)) | (City.state == "")
        ).first()
    
    if not city:
        # Try multiple sources for coordinates:
        # 1. Comprehensive geonames database
        coords = get_coordinates(city_name, country, state)
        
        # 2. Fallback to Nominatim API for any location
        if not coords:
            coords = geocode_city_api(city_name, country, state)
        
        if not coords:
            location_str = f"{city_name}, {state}, {country}" if state else f"{city_name}, {country}"
            raise HTTPException(
                status_code=400, 
                detail=f"Could not find coordinates for '{location_str}'. Please check the spelling and try again, or verify this location exists."
            )
        
        city = City(
            name=city_name,
            country=country,
            state=state if state else None,  # Ensure empty strings become None
            latitude=coords[0],
            longitude=coords[1]
        )
        db.add(city)
        db.commit()
        db.refresh(city)
    
    return city

def geocode_city_api(city_name: str, country: str, state: Optional[str] = None) -> Optional[tuple]:
    """Get coordinates using Nominatim API for any city"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        # Build query with optional state
        query_parts = [city_name]
        if state:
            query_parts.append(state)
        query_parts.append(country)
        
        params = {
            "q": ", ".join(query_parts),
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
    book = db.query(Book).filter(Book.id == review_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    city = get_or_create_city(db, review_data.city_name, review_data.country, review_data.state)
    
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
    file_path = f"{DATA_DIR}/uploads/{file_id}.{file_extension}"
    
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
    # Sanitize inputs
    city = city.strip() if city else None
    country = country.strip() if country else None
    
    if not city and not country:
        raise HTTPException(status_code=400, detail="Either city or country must be provided")
    
    # If both city and country are provided, filter by specific city
    if city and country:
        city_obj = db.query(City).filter(
            func.lower(City.name) == func.lower(city),
            func.lower(City.country) == func.lower(country)
        ).first()
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
                    .filter(func.lower(City.country) == func.lower(country)).all()
        
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
                    .filter(func.lower(City.name) == func.lower(city)).all()
        
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
            "state": city_obj.state,
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
    # Sanitize input
    company_name = company_name.strip()
    
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
                      country: Optional[str] = None, company: Optional[str] = None, 
                      admin_session: Optional[AdminSession] = Depends(get_current_admin),
                      db: Session = Depends(get_db)):
    """Reviews listing page with optional filters"""
    books = db.query(Book).all()
    return templates.TemplateResponse("reviews.html", {
        "request": request, 
        "books": books,
        "book_id": book_id,
        "city": city,
        "country": country,
        "company": company,
        "is_admin": admin_session is not None
    })

# Authentication endpoints
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Display admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/admin/edit", response_class=HTMLResponse)
async def edit_review_page(
    request: Request,
    admin: AdminSession = Depends(require_admin)
):
    """Display review edit page (admin only)"""
    return templates.TemplateResponse("edit_review.html", {"request": request})

@app.post("/api/admin/login")
async def admin_login(
    request: Request,
    response: Response,
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    ip_address = get_client_ip(request)
    
    # Check rate limiting
    if not check_rate_limit(ip_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Verify password
    if not verify_password(password):
        record_login_attempt(ip_address, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Create session
    record_login_attempt(ip_address, True)
    session_id = create_session(db, ip_address)
    
    # Set secure cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24  # 24 hours
    )
    
    return {"message": "Login successful"}

@app.post("/api/admin/logout")
async def admin_logout(
    response: Response,
    session: Optional[AdminSession] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin logout endpoint"""
    if session:
        delete_session(db, session.id)
    
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logout successful"}

@app.get("/api/admin/check")
async def check_admin_status(
    session: Optional[AdminSession] = Depends(get_current_admin)
):
    """Check if user is authenticated as admin"""
    return {"authenticated": session is not None}

# Review editing endpoints (protected)
@app.put("/api/reviews/{review_id}")
async def update_review(
    review_id: int,
    review_data: ReviewCreate,
    admin: AdminSession = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an existing review (admin only)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Update city if location changed
    city = get_or_create_city(db, review_data.city_name, review_data.country, review_data.state)
    
    # Update review fields
    review.book_id = review_data.book_id
    review.city_id = city.id
    review.review_text = review_data.review_text
    review.reviewer_name = review_data.reviewer_name
    review.company = review_data.company
    review.role = review_data.role
    review.original_post_url = review_data.original_post_url
    review.social_media_url = review_data.social_media_url
    review.source = review_data.source
    
    # Parse and update date if provided
    if review_data.review_date:
        try:
            review.review_date = parser.parse(review_data.review_date).date()
        except:
            pass
    
    db.commit()
    db.refresh(review)
    
    return {"message": "Review updated successfully", "id": review.id}

@app.delete("/api/reviews/{review_id}")
async def delete_review(
    review_id: int,
    admin: AdminSession = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a review (admin only)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}

@app.get("/api/review/{review_id}")
async def get_single_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a single review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    book = db.query(Book).filter(Book.id == review.book_id).first()
    city = db.query(City).filter(City.id == review.city_id).first()
    assets = db.query(ReviewAsset).filter(ReviewAsset.review_id == review.id).all()
    
    return {
        "id": review.id,
        "book_id": review.book_id,
        "book_title": book.title,
        "book_short_name": book.short_name,
        "city_name": city.name,
        "country": city.country,
        "state": city.state,
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
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)