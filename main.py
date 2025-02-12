import googlemaps
import os
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

GMAPS_KEY = os.getenv("GMAPS_KEY")
gmaps = googlemaps.Client(key=GMAPS_KEY)

query = input("Enter a query: ")
places_data = []

# Get initial results
results = gmaps.places(query)
places_data = []

while True:
    # Process current page of results
    for place in results['results']:
        # Get detailed place information to get phone number
        place_details = gmaps.place(place_id=place['place_id'])['result']
        
        place_info = {
            'name': place.get('name', ''),
            'address': place.get('formatted_address', ''),
            'rating': place.get('rating', ''),
            'types': ', '.join(place.get('types', [])),
            'place_id': place.get('place_id', ''),
            'latitude': place['geometry']['location'].get('lat', ''),
            'longitude': place['geometry']['location'].get('lng', ''),
            'phone_number': place_details.get('formatted_phone_number', '')
        }
        places_data.append(place_info)
    
    # Check if there are more results
    if 'next_page_token' not in results:
        break
        
    # Wait before making the next request (required by the API)
    time.sleep(2)
    
    # Get the next page of results
    results = gmaps.places(query, page_token=results['next_page_token'])

print(f"Found {len(places_data)} places")

# Create DataFrame and save to CSV
df = pd.DataFrame(places_data)
csv_filename = "output.csv"
df.to_csv(csv_filename, index=False)
print(f"Results saved to {csv_filename}")