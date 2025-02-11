import googlemaps
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GMAPS_KEY = os.getenv("GMAPS_KEY")
gmaps = googlemaps.Client(key=GMAPS_KEY)

query = input("Enter a query: ")
results = gmaps.places(query)

# Extract relevant information from results
places_data = []
for place in results['results']:
    place_info = {
        'name': place.get('name', ''),
        'address': place.get('formatted_address', ''),
        'rating': place.get('rating', ''),
        'types': ', '.join(place.get('types', [])),
        'place_id': place.get('place_id', ''),
        'latitude': place['geometry']['location'].get('lat', ''),
        'longitude': place['geometry']['location'].get('lng', '')
    }
    places_data.append(place_info)

# Create DataFrame and save to CSV
df = pd.DataFrame(places_data)
csv_filename = "output.csv"
df.to_csv(csv_filename, index=False)
print(f"Results saved to {csv_filename}")