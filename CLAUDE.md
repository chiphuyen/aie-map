# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIE Map is a web application that tracks book reviews for "AI Engineering" (AIE) and "Designing Machine Learning Systems" (DMLS) on an interactive world map. Users can view review locations, upload screenshots of reviews for automatic text extraction, and browse reviews by city.

## Architecture

**Backend**: FastAPI with SQLAlchemy ORM and SQLite database
**Frontend**: HTML/CSS/JavaScript with Leaflet.js for mapping
**Key Features**:
- Interactive world map with clustered review pins (red for AIE, green for DMLS)
- OCR-powered screenshot upload for automatic review extraction
- Geocoding service for city location mapping
- Review management and display system

**Database Schema**:
- `books`: Track the two target books with colors
- `cities`: Store city locations with coordinates  
- `reviews`: Store review details, linking books and cities

## Commands

**Setup and Run**:
```bash
pip install -r requirements.txt
python app.py
```

**Database**: SQLite database (`data/aie_map.db`) is created automatically on first run

**Development Server**: Runs on http://localhost:8000

## Key Files

- `app.py`: Main FastAPI application with all endpoints
- `models.py`: SQLAlchemy models and Pydantic schemas
- `database_schema.sql`: Database schema reference
- `templates/`: HTML templates for web interface
- `static/`: Static assets (created automatically)
- `data/`: Data folder containing database and uploads (excluded from git)
  - `data/aie_map.db`: SQLite database
  - `data/uploads/`: Screenshot uploads

## External Dependencies

- **Tesseract OCR**: Required for screenshot text extraction
- **Geonames Cache**: Comprehensive database of 40,000+ cities worldwide with coordinates
- **PyCountry**: Complete list of countries and territories
- **OpenStreetMap Nominatim**: Fallback geocoding for cities not in geonames database
- **Leaflet.js**: Client-side mapping library loaded via CDN

## Location Support

**Cities**: Supports all cities worldwide (40,000+ from geonames database with population > 1000)
- Autocomplete suggestions show existing cities first, sorted by population
- Users can enter any city name - new cities are geocoded and added automatically
- Smart autocomplete combines pre-loaded cities with previously added cities

**Countries**: All countries and territories supported with common name variations
- Includes standard country names plus common alternatives (USA, UK, etc.)