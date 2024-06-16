# venue-data-pump

Data pump for venue related endpoints from the espn-api-orm. 

## Pipeline

1. For each sport league pair get all of the venue IDs
2. Get sport league file and determine venues to upsert
3. Get each venue (if not already saved)
4. Get venue address geocoding
5. Get h3 index from address geocoding
6. Update sport league file with new IDs

## Data Objects

Venue
- ID
- GeocodingID
- Address
- State
- City
- ZipCode

Geocoding
- ID
- Address (Address, City, State, ZipCode)
- Latitude
- Longitude
- H3IndexSmall
- H3IndexMedium
- H3IndexLarge
- LastUpdated
