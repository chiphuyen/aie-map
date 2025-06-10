"""
Comprehensive location data using geonames and pycountry packages
"""

import geonamescache
import pycountry
from typing import Dict, List, Optional, Tuple

# Initialize geonames cache
gc = geonamescache.GeonamesCache()

class LocationService:
    def __init__(self):
        self.cities_cache = None
        self.countries_cache = None
        self._load_data()
    
    def _load_data(self):
        """Load all cities and countries data"""
        print("Loading comprehensive location data...")
        
        # Get all cities from geonames (this includes tens of thousands of cities)
        raw_cities = gc.get_cities()
        
        # Convert to our format and filter for better quality
        self.cities_cache = {}
        for city_id, city_data in raw_cities.items():
            # Only include cities with population > 1000 for better data quality
            if city_data.get('population', 0) >= 1000:
                city_name = city_data['name']
                country_code = city_data['countrycode']
                
                # Get country name from country code
                try:
                    country = pycountry.countries.get(alpha_2=country_code)
                    country_name = country.name if country else country_code
                except:
                    country_name = country_code
                
                # Create unique key for city-country combination
                key = f"{city_name}_{country_name}"
                
                self.cities_cache[key] = {
                    'city': city_name,
                    'country': country_name,
                    'country_code': country_code,
                    'latitude': float(city_data['latitude']),
                    'longitude': float(city_data['longitude']),
                    'population': city_data.get('population', 0),
                    'timezone': city_data.get('timezone', ''),
                }
        
        # Get all countries
        self.countries_cache = []
        for country in pycountry.countries:
            self.countries_cache.append(country.name)
        
        # Add some common alternative names
        additional_countries = [
            "United States", "UK", "England", "Scotland", "Wales", "Northern Ireland"
        ]
        self.countries_cache.extend(additional_countries)
        self.countries_cache = sorted(list(set(self.countries_cache)))
        
        print(f"Loaded {len(self.cities_cache)} cities and {len(self.countries_cache)} countries")
    
    def search_cities(self, query: str, limit: int = 20) -> List[Dict]:
        """Search cities by name"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = []
        
        for key, city_data in self.cities_cache.items():
            if query_lower in city_data['city'].lower():
                results.append({
                    'city': city_data['city'],
                    'country': city_data['country'],
                    'full_name': f"{city_data['city']}, {city_data['country']}",
                    'latitude': city_data['latitude'],
                    'longitude': city_data['longitude'],
                    'population': city_data['population']
                })
                
                if len(results) >= limit:
                    break
        
        # Sort by population (larger cities first)
        results.sort(key=lambda x: x['population'], reverse=True)
        return results[:limit]
    
    def search_countries(self, query: str, limit: int = 20) -> List[str]:
        """Search countries by name"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = [country for country in self.countries_cache 
                  if query_lower in country.lower()]
        return results[:limit]
    
    def get_city_coordinates(self, city_name: str, country_name: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a specific city and country"""
        # Normalize country name
        normalized_country = self._normalize_country_name(country_name)
        
        # Try exact match first
        key = f"{city_name}_{normalized_country}"
        if key in self.cities_cache:
            city_data = self.cities_cache[key]
            return (city_data['latitude'], city_data['longitude'])
        
        # Try case-insensitive search
        for key, city_data in self.cities_cache.items():
            if (city_data['city'].lower() == city_name.lower() and 
                city_data['country'].lower() == normalized_country.lower()):
                return (city_data['latitude'], city_data['longitude'])
        
        return None
    
    def _normalize_country_name(self, country_name: str) -> str:
        """Normalize country names to handle common variations"""
        country_mappings = {
            "usa": "United States",
            "us": "United States", 
            "america": "United States",
            "uk": "United Kingdom",
            "britain": "United Kingdom",
            "england": "United Kingdom",
            "scotland": "United Kingdom", 
            "wales": "United Kingdom",
            "northern ireland": "United Kingdom"
        }
        
        normalized = country_mappings.get(country_name.lower(), country_name)
        return normalized
    
    def validate_location(self, city_name: str, country_name: str) -> bool:
        """Check if a city/country combination exists in our data"""
        return self.get_city_coordinates(city_name, country_name) is not None
    
    def get_all_countries(self) -> List[str]:
        """Get all available countries"""
        return self.countries_cache.copy()

# Global instance
location_service = None

def get_location_service():
    """Get the global location service instance"""
    global location_service
    if location_service is None:
        location_service = LocationService()
    return location_service

# Convenience functions for backward compatibility
def get_city_suggestions(query: str, limit: int = 20) -> List[Dict]:
    """Get city suggestions based on partial input"""
    service = get_location_service()
    return service.search_cities(query, limit)

def get_country_suggestions(query: str, limit: int = 20) -> List[str]:
    """Get country suggestions based on partial input"""
    service = get_location_service()
    return service.search_countries(query, limit)

def validate_location(city_name: str, country_name: str) -> bool:
    """Validate if city and country combination exists in our data"""
    service = get_location_service()
    return service.validate_location(city_name, country_name)

def get_coordinates(city_name: str, country_name: str) -> Optional[Tuple[float, float]]:
    """Get coordinates for a valid city/country combination"""
    service = get_location_service()
    return service.get_city_coordinates(city_name, country_name)

def get_all_countries() -> List[str]:
    """Get all valid countries"""
    service = get_location_service()
    return service.get_all_countries()