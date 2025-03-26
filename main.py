import googlemaps
import os
import pandas as pd
from dotenv import load_dotenv
import time
import math

load_dotenv()

GMAPS_KEY = os.getenv("GMAPS_KEY")
gmaps = googlemaps.Client(key=GMAPS_KEY)

# query = input("Enter a query: ")
query = "metal recyclers near New York"
places_data = []

# Parse location from query
location_parts = query.split("near ")
search_term = location_parts[0].strip()
location = location_parts[1].strip() if len(location_parts) > 1 else "Topeka, Kansas"

# Get geocode for the location to use as center point
geocode_result = gmaps.geocode(location)
if not geocode_result:
    print(f"Could not geocode location: {location}")
    exit(1)

center_lat = geocode_result[0]['geometry']['location']['lat']
center_lng = geocode_result[0]['geometry']['location']['lng']
print(f"Searching for '{search_term}' near {location} ({center_lat}, {center_lng})")

# Track place IDs to avoid duplicates
processed_place_ids = set()

# Search with increasing radius to get more results
search_radii = [5000, 10000, 20000, 50000]  # in meters
max_results = 200  # Set a reasonable limit to avoid excessive API calls

# Function to process results
def process_results(results):
    for place in results['results']:
        place_id = place.get('place_id')
        
        # Skip if we've already processed this place
        if place_id in processed_place_ids:
            continue
            
        processed_place_ids.add(place_id)
        
        # Get detailed place information to get phone number and website
        place_details = gmaps.place(place_id=place_id)['result']
        
        place_info = {
            'name': place.get('name', ''),
            'address': place.get('formatted_address', ''),
            'rating': place.get('rating', ''),
            'types': ', '.join(place.get('types', [])),
            'place_id': place_id,
            'latitude': place['geometry']['location'].get('lat', ''),
            'longitude': place['geometry']['location'].get('lng', ''),
            'phone_number': place_details.get('formatted_phone_number', ''),
            'url': place_details.get('website', '')
        }
        places_data.append(place_info)

for radius in search_radii:
    print(f"Searching with radius: {radius} meters")
    
    # Initial search with radius
    results = gmaps.places(
        query=search_term,
        location=(center_lat, center_lng),
        radius=radius
    )
    
    # Process first page
    process_results(results)
    
    # Continue getting pages until there are no more or we hit our limit
    page_count = 1
    while 'next_page_token' in results and len(places_data) < max_results:
        # Wait before making the next request (required by the API)
        time.sleep(2)
        
        # Get the next page of results
        results = gmaps.places(
            query=search_term,
            location=(center_lat, center_lng),
            radius=radius,
            page_token=results['next_page_token']
        )
        
        # Process the results
        process_results(results)
        page_count += 1
        
        print(f"Processed page {page_count} for radius {radius}m, total places: {len(places_data)}")
    
    # If we've got enough results, stop expanding the radius
    if len(places_data) >= max_results:
        print(f"Reached maximum result limit ({max_results})")
        break


print(f"Found {len(places_data)} places")

# Create DataFrame and save to CSV
df = pd.DataFrame(places_data)
csv_filename = "output.csv"
df.to_csv(csv_filename, index=False)
print(f"Results saved to {csv_filename}")