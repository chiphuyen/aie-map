from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, DECIMAL, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, List

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    short_name = Column(String(10), nullable=False, unique=True)
    pin_color = Column(String(7), nullable=False)
    
    reviews = relationship("Review", back_populates="book")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    state = Column(String(255), nullable=True)  # State/Province/Region
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    
    reviews = relationship("Review", back_populates="city")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    review_text = Column(Text)
    reviewer_name = Column(String(255))
    company = Column(String(255))
    role = Column(String(255))
    review_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    original_post_url = Column(Text)
    social_media_url = Column(Text)
    screenshot_path = Column(String(500))
    source = Column(String(255))  # GoodReads, Amazon, LinkedIn, etc.
    
    book = relationship("Book", back_populates="reviews")
    city = relationship("City", back_populates="reviews")
    assets = relationship("ReviewAsset", back_populates="review", cascade="all, delete-orphan")

class ReviewAsset(Base):
    __tablename__ = "review_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_type = Column(String(50))  # image, document, etc.
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    review = relationship("Review", back_populates="assets")

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    
    id = Column(String(255), primary_key=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))  # Support IPv6

# Pydantic models for API
class ReviewCreate(BaseModel):
    book_id: int
    city_name: str
    country: str
    state: Optional[str] = None
    review_text: Optional[str] = None
    reviewer_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    review_date: Optional[str] = None
    original_post_url: Optional[str] = None
    social_media_url: Optional[str] = None
    source: Optional[str] = None
    
    @field_validator('city_name', 'country')
    @classmethod
    def strip_required_strings(cls, v):
        return v.strip() if v else v
    
    @field_validator('state', 'review_text', 'reviewer_name', 'company', 'role', 'original_post_url', 'social_media_url', 'source')
    @classmethod
    def strip_optional_strings(cls, v):
        return v.strip() if v else v

class ReviewAssetResponse(BaseModel):
    id: int
    file_path: str
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    book_title: str
    book_short_name: str
    city_name: str
    country: str
    state: Optional[str]
    review_text: Optional[str]
    reviewer_name: Optional[str]
    company: Optional[str]
    role: Optional[str]
    review_date: Optional[str]
    created_at: datetime
    original_post_url: Optional[str]
    social_media_url: Optional[str]
    source: Optional[str]
    assets: List[ReviewAssetResponse] = []
    
    class Config:
        from_attributes = True

class CityStats(BaseModel):
    city_name: str
    country: str
    state: Optional[str]
    latitude: float
    longitude: float
    aie_count: int
    dmls_count: int
    total_count: int