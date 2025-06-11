#!/usr/bin/env python3
"""
Test the API endpoint directly to see if it returns data
"""

import requests
import json

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/api/reviews/filtered?book_id=1",
        "/api/reviews/filtered?book_id=2", 
        "/api/reviews/filtered?country=United%20States",
        "/api/reviews/filtered?city=London",
        "/api/reviews/by-book/1",
        "/api/reviews/by-location?city=London&country=The%20UK"
    ]
    
    print("Testing API endpoints (requires server to be running):")
    print("="*60)
    
    for endpoint in endpoints_to_test:
        try:
            url = base_url + endpoint
            print(f"\nTesting: {endpoint}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'reviews' in data:
                    review_count = len(data['reviews'])
                    print(f"✅ SUCCESS: {review_count} reviews returned")
                    if review_count > 0:
                        print(f"   First review: {data['reviews'][0]['book_title']} in {data['reviews'][0]['city_name']}")
                else:
                    print(f"✅ SUCCESS: Response received but no 'reviews' field")
                    print(f"   Keys: {list(data.keys())}")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: Server not running on {base_url}")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_api_endpoints()