# venue-data-pump

[![Venue Data trigger](https://github.com/theedgepredictor/venue-data-pump/actions/workflows/venue_data_trigger.yaml/badge.svg)](https://github.com/theedgepredictor/venue-data-pump/actions/workflows/venue_data_trigger.yaml)

The `venue-data-pump` is a GitHub Action designed to extract venue-related endpoints from the `espn-api-orm`. It automates several steps in the data pipeline, ensuring accurate and up-to-date information for sports venues.


## Pipeline Overview

1. **Collect Venue IDs:**
   - For each sport-league pair, retrieve all associated venue IDs.
2. **Determine Venues to Upsert:**
   - Analyze the sport league file to identify venues that need updating (if not already saved).
3. **Retrieve Venue Details:**
   - Fetch detailed information for each venue (if necessary).
4. **Geocode Venue Addresses:**
   - Obtain geolocation coordinates (latitude and longitude) for venue addresses.
5. **Generate H3 Index:**
   - Calculate H3 indexes based on the geocoded addresses.
6. **Venue Elevation:**
   - Retrieve elevation data for each venue.
7. **Update Sport League File:**
   - Incorporate new venue IDs into the sport league file.
8. **Update Master Geocoding File:**
   - Append new geocoding IDs to the master geocoding file.
   

## Data Objects

Venue: ```data/SPORT/LEAGUE/venues.json```
```python
{
        "ref": str,
        "fullName": str,
        "capacity": int,
        "grass": bool,
        "indoor": bool,
        "images": List[Images],
        "geocodingId": str,
        "lastUpdated": str
}
```

Geocoding: ```data/geocoding.json```
```python
{  
    'requestedAddress': str,
    'codedAddress': str,
    'latitude': float,
    'longitude': float,
    'provider': str,
    'h3Index': str,
    'name': str,
    'city': str,
    'state': str,
    'zipCode': str,
    'elevation': float,
    'lastUpdated': str
}

```

## Resources
- [espn-api-orm](https://pypi.org/project/espn-api-orm/)
- [geopy](https://pypi.org/project/geopy/)
- [h3](https://pypi.org/project/h3/)
- [Github Actions Setup Python](https://github.com/actions/setup-python/tree/main)
- [Github Actions Pricing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
