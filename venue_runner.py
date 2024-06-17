import json
import os
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.venue.api import ESPNVenueAPI
from espn_api_orm.consts import ESPNSportLeagueTypes

from geopy.geocoders import Nominatim, ArcGIS
import h3
import requests
import datetime

from src.utils import name_filter, get_json_file, put_json_file


def make_geocoding_address_string(name, address):
    items = [name, address.city, address.state, address.zipCode]
    items = list(filter(None, items))
    geocoding_address = ', '.join(items)
    return geocoding_address

def get_elevations(lats, lons, n=50):
    if n > 50:
        raise ValueError("Batch size cannot be greater than 50.")
    try:
        datasets = ','.join([
            # 'aster30m',
            'etopo1',
            # 'eudem25m',
            # 'mapzen',
            'ned10m',
            'srtm30m',
            # 'gebco2020',
            'emod2018',
        ])

        elevations = []
        for i in range(0, len(lats), n):
            batch_lats = lats[i:i + n]
            batch_lons = lons[i:i + n]
            locations = '|'.join([f'{lat},{lon}' for lat, lon in zip(batch_lats, batch_lons)])
            #time.sleep(1.0) # free api
            res = requests.get(f'https://api.opentopodata.org/v1/{datasets}?locations={locations}')
            if res.status_code != 200:
                raise Exception(res.json())
            data = json.loads(res.text)

            batch_elevations = [dataset_response['elevation'] * 3.28084 if dataset_response['elevation'] is not None else None for dataset_response in data['results']]
            elevations.extend(batch_elevations)

        return elevations
    except Exception as e:
        print(e)
        return None

def get_geocoding(name, address):
    if address is None:
        city = None
        state = None
        zip_code = None
    else:
        city = address.city
        state = address.state
        zip_code = address.zipCode
    items = [name, city, state, zip_code]
    items = list(filter(None, items))
    geocoding_address = ', '.join(items)

    geocoding_id = None

    geocoding = {
        'requestedAddress': geocoding_address,
        'codedAddress': None,
        'latitude': None,
        'longitude': None,
        'provider': None,
        'h3Index': None,
        'name': name,
        'city': city,
        'state': state,
        'zipCode': zip_code,
        'elevation': None,
        'lastUpdated': None
    }

    geolocators = {
        "ArcGIS": ArcGIS(), 
        "OSM":Nominatim(user_agent="venue_locator")
    }
    for provider, geolocator in geolocators.items():
        try:
            location = geolocator.geocode(geocoding_address)
            if location:
                geocoding_id = name_filter(location.address)
                geocoding['provider'] = provider
                geocoding['latitude'] = location.latitude
                geocoding['longitude'] = location.longitude
                geocoding['codedAddress'] = location.address
                geocoding['h3Index'] = h3.geo_to_h3(location.latitude, location.longitude, 15)
                geocoding['lastUpdated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return {geocoding_id: geocoding}
        except:
            continue
    return {geocoding_id: geocoding}



def get_new_venue_coding(sport_str, league_str, venue_id):
    venue = None
    try:
        venue_api = ESPNVenueAPI(sport_str, league_str, venue_id)
        venue = venue_api.get_venue()
        geocoding = get_geocoding(venue.fullName, venue.address)

        if geocoding.keys() == {None}:
            print(f"Geocoding not found for: {sport_str} {league_str} {venue_id}")
        obj = json.loads(venue.json())
        obj.pop('id')
        obj.pop('address')
        new_venue_obj = {
            venue_id : obj
        }

        new_venue_obj[venue_id]['geocodingId'] = list(geocoding.keys())[0]
        new_venue_obj[venue_id]['lastUpdated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return new_venue_obj, geocoding
    except Exception as e:
        print(venue)
        raise e

def main():
    root_path = ''
    geocoding_path = root_path + '/' + 'geocoding.json'
    geocoding_addresses = get_json_file(geocoding_path)

    sport_league_pairs = list(ESPNSportLeagueTypes)
    sport_league_pairs = [ESPNSportLeagueTypes.FOOTBALL_NFL, ESPNSportLeagueTypes.FOOTBALL_COLLEGE_FOOTBALL]
    for sport_league in sport_league_pairs:
        sport_str, league_str = sport_league.value.split('/')
        path = f'{root_path}/{sport_str}/{league_str}/'
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        venue_path = path + 'venues.json'

        # For each LeagueAPI get the venue IDs
        league_api = ESPNLeagueAPI(sport_str, league_str)
        venue_ids = list(map(str, league_api.get_venues()))

        # Try to get the saved sport league venue file if it exists.
        sport_league_venues = get_json_file(venue_path)

        # Handle upsert logic for new or stale venue IDs
        existing_venue_ids = list(sport_league_venues.keys())
        new_venue_ids = list(set(venue_ids) - set(existing_venue_ids))
        new_venue_ids = sorted(new_venue_ids)

        # Skip if no new venues
        if len(new_venue_ids) == 0:
            print(f"No new venues for: {league_str} {sport_str} ")
            continue

        print(f"Getting {len(new_venue_ids)} new venues for: {league_str} {sport_str}")
        new_venues = {}
        new_geocodings = {}
        for venue_id in new_venue_ids:
            new_venue_obj, geocoding = get_new_venue_coding(sport_str, league_str, venue_id)
            new_venues.update(new_venue_obj)
            new_geocodings.update(geocoding)

        print(f"Saving new venues for: {league_str} {sport_str} ...")
        put_json_file(venue_path, {**sport_league_venues, **new_venues})

        geocoding_addresses = {**geocoding_addresses, **new_geocodings}
        print(f"Saving new geocodings for: {league_str} {sport_str} ...")
        put_json_file(geocoding_path, geocoding_addresses)
        print("\n")

if __name__ == '__main__':
    main()