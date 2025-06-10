"""
Pre-defined lists of valid cities and countries with their coordinates
"""

# Major cities with coordinates for the AIE Map
VALID_CITIES = {
    # United States
    "New York": {"country": "United States", "lat": 40.7128, "lng": -74.0060},
    "Los Angeles": {"country": "United States", "lat": 34.0522, "lng": -118.2437},
    "San Francisco": {"country": "United States", "lat": 37.7749, "lng": -122.4194},
    "Chicago": {"country": "United States", "lat": 41.8781, "lng": -87.6298},
    "Seattle": {"country": "United States", "lat": 47.6062, "lng": -122.3321},
    "Boston": {"country": "United States", "lat": 42.3601, "lng": -71.0589},
    "Austin": {"country": "United States", "lat": 30.2672, "lng": -97.7431},
    "Denver": {"country": "United States", "lat": 39.7392, "lng": -104.9903},
    "Miami": {"country": "United States", "lat": 25.7617, "lng": -80.1918},
    "Atlanta": {"country": "United States", "lat": 33.7490, "lng": -84.3880},
    "Washington": {"country": "United States", "lat": 38.9072, "lng": -77.0369},
    "Philadelphia": {"country": "United States", "lat": 39.9526, "lng": -75.1652},
    
    # Canada
    "Toronto": {"country": "Canada", "lat": 43.6532, "lng": -79.3832},
    "Vancouver": {"country": "Canada", "lat": 49.2827, "lng": -123.1207},
    "Montreal": {"country": "Canada", "lat": 45.5017, "lng": -73.5673},
    "Calgary": {"country": "Canada", "lat": 51.0447, "lng": -114.0719},
    "Ottawa": {"country": "Canada", "lat": 45.4215, "lng": -75.6972},
    
    # United Kingdom
    "London": {"country": "United Kingdom", "lat": 51.5074, "lng": -0.1278},
    "Manchester": {"country": "United Kingdom", "lat": 53.4808, "lng": -2.2426},
    "Edinburgh": {"country": "United Kingdom", "lat": 55.9533, "lng": -3.1883},
    "Birmingham": {"country": "United Kingdom", "lat": 52.4862, "lng": -1.8904},
    "Cambridge": {"country": "United Kingdom", "lat": 52.2053, "lng": 0.1218},
    
    # Germany
    "Berlin": {"country": "Germany", "lat": 52.5200, "lng": 13.4050},
    "Munich": {"country": "Germany", "lat": 48.1351, "lng": 11.5820},
    "Hamburg": {"country": "Germany", "lat": 53.5511, "lng": 9.9937},
    "Frankfurt": {"country": "Germany", "lat": 50.1109, "lng": 8.6821},
    "Stuttgart": {"country": "Germany", "lat": 48.7758, "lng": 9.1829},
    
    # France
    "Paris": {"country": "France", "lat": 48.8566, "lng": 2.3522},
    "Lyon": {"country": "France", "lat": 45.7640, "lng": 4.8357},
    "Marseille": {"country": "France", "lat": 43.2965, "lng": 5.3698},
    "Toulouse": {"country": "France", "lat": 43.6047, "lng": 1.4442},
    
    # Netherlands
    "Amsterdam": {"country": "Netherlands", "lat": 52.3676, "lng": 4.9041},
    "Rotterdam": {"country": "Netherlands", "lat": 51.9244, "lng": 4.4777},
    "The Hague": {"country": "Netherlands", "lat": 52.0705, "lng": 4.3007},
    
    # Switzerland
    "Zurich": {"country": "Switzerland", "lat": 47.3769, "lng": 8.5417},
    "Geneva": {"country": "Switzerland", "lat": 46.2044, "lng": 6.1432},
    "Basel": {"country": "Switzerland", "lat": 47.5596, "lng": 7.5886},
    
    # Sweden
    "Stockholm": {"country": "Sweden", "lat": 59.3293, "lng": 18.0686},
    "Gothenburg": {"country": "Sweden", "lat": 57.7089, "lng": 11.9746},
    
    # Norway
    "Oslo": {"country": "Norway", "lat": 59.9139, "lng": 10.7522},
    
    # Denmark
    "Copenhagen": {"country": "Denmark", "lat": 55.6761, "lng": 12.5683},
    
    # Finland
    "Helsinki": {"country": "Finland", "lat": 60.1699, "lng": 24.9384},
    
    # Spain
    "Madrid": {"country": "Spain", "lat": 40.4168, "lng": -3.7038},
    "Barcelona": {"country": "Spain", "lat": 41.3851, "lng": 2.1734},
    "Valencia": {"country": "Spain", "lat": 39.4699, "lng": -0.3763},
    
    # Italy
    "Rome": {"country": "Italy", "lat": 41.9028, "lng": 12.4964},
    "Milan": {"country": "Italy", "lat": 45.4642, "lng": 9.1900},
    "Naples": {"country": "Italy", "lat": 40.8518, "lng": 14.2681},
    "Turin": {"country": "Italy", "lat": 45.0703, "lng": 7.6869},
    
    # Japan
    "Tokyo": {"country": "Japan", "lat": 35.6762, "lng": 139.6503},
    "Osaka": {"country": "Japan", "lat": 34.6937, "lng": 135.5023},
    "Kyoto": {"country": "Japan", "lat": 35.0116, "lng": 135.7681},
    "Yokohama": {"country": "Japan", "lat": 35.4437, "lng": 139.6380},
    
    # South Korea
    "Seoul": {"country": "South Korea", "lat": 37.5665, "lng": 126.9780},
    "Busan": {"country": "South Korea", "lat": 35.1796, "lng": 129.0756},
    
    # China
    "Beijing": {"country": "China", "lat": 39.9042, "lng": 116.4074},
    "Shanghai": {"country": "China", "lat": 31.2304, "lng": 121.4737},
    "Shenzhen": {"country": "China", "lat": 22.3193, "lng": 114.1694},
    "Guangzhou": {"country": "China", "lat": 23.1291, "lng": 113.2644},
    "Hangzhou": {"country": "China", "lat": 30.2741, "lng": 120.1551},
    
    # India
    "Mumbai": {"country": "India", "lat": 19.0760, "lng": 72.8777},
    "Delhi": {"country": "India", "lat": 28.7041, "lng": 77.1025},
    "Bangalore": {"country": "India", "lat": 12.9716, "lng": 77.5946},
    "Hyderabad": {"country": "India", "lat": 17.3850, "lng": 78.4867},
    "Chennai": {"country": "India", "lat": 13.0827, "lng": 80.2707},
    "Pune": {"country": "India", "lat": 18.5204, "lng": 73.8567},
    
    # Singapore
    "Singapore": {"country": "Singapore", "lat": 1.3521, "lng": 103.8198},
    
    # Australia
    "Sydney": {"country": "Australia", "lat": -33.8688, "lng": 151.2093},
    "Melbourne": {"country": "Australia", "lat": -37.8136, "lng": 144.9631},
    "Brisbane": {"country": "Australia", "lat": -27.4698, "lng": 153.0251},
    "Perth": {"country": "Australia", "lat": -31.9505, "lng": 115.8605},
    
    # New Zealand
    "Auckland": {"country": "New Zealand", "lat": -36.8485, "lng": 174.7633},
    "Wellington": {"country": "New Zealand", "lat": -41.2865, "lng": 174.7762},
    
    # Israel
    "Tel Aviv": {"country": "Israel", "lat": 32.0853, "lng": 34.7818},
    "Jerusalem": {"country": "Israel", "lat": 31.7683, "lng": 35.2137},
    
    # UAE
    "Dubai": {"country": "United Arab Emirates", "lat": 25.2048, "lng": 55.2708},
    "Abu Dhabi": {"country": "United Arab Emirates", "lat": 24.2539, "lng": 54.3773},
    
    # Brazil
    "São Paulo": {"country": "Brazil", "lat": -23.5558, "lng": -46.6396},
    "Rio de Janeiro": {"country": "Brazil", "lat": -22.9068, "lng": -43.1729},
    "Brasília": {"country": "Brazil", "lat": -15.8267, "lng": -47.9218},
    
    # Mexico
    "Mexico City": {"country": "Mexico", "lat": 19.4326, "lng": -99.1332},
    "Guadalajara": {"country": "Mexico", "lat": 20.6597, "lng": -103.3496},
    
    # Argentina
    "Buenos Aires": {"country": "Argentina", "lat": -34.6118, "lng": -58.3960},
    
    # South Africa
    "Cape Town": {"country": "South Africa", "lat": -33.9249, "lng": 18.4241},
    "Johannesburg": {"country": "South Africa", "lat": -26.2041, "lng": 28.0473},
    
    # Russia
    "Moscow": {"country": "Russia", "lat": 55.7558, "lng": 37.6176},
    "Saint Petersburg": {"country": "Russia", "lat": 59.9311, "lng": 30.3609},
}

# Extract unique countries from the cities data
VALID_COUNTRIES = sorted(list(set(city_data["country"] for city_data in VALID_CITIES.values())))

def get_city_suggestions(query: str, limit: int = 10):
    """Get city suggestions based on partial input"""
    query_lower = query.lower()
    suggestions = []
    
    for city, data in VALID_CITIES.items():
        if query_lower in city.lower():
            suggestions.append({
                "city": city,
                "country": data["country"],
                "full_name": f"{city}, {data['country']}"
            })
    
    return suggestions[:limit]

def get_country_suggestions(query: str, limit: int = 10):
    """Get country suggestions based on partial input"""
    query_lower = query.lower()
    suggestions = [country for country in VALID_COUNTRIES if query_lower in country.lower()]
    return suggestions[:limit]

def validate_location(city_name: str, country_name: str):
    """Validate if city and country combination exists in our data"""
    if city_name in VALID_CITIES:
        return VALID_CITIES[city_name]["country"] == country_name
    return False

def get_coordinates(city_name: str, country_name: str):
    """Get coordinates for a valid city/country combination"""
    if validate_location(city_name, country_name):
        city_data = VALID_CITIES[city_name]
        return city_data["lat"], city_data["lng"]
    return None