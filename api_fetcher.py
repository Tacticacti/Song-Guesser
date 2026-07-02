import requests
import random

def fetch_metadata(url, params):
    response = requests.get(url, params)
    results = response.json()['results']
    matching_results = filter_by_artist(results, params['term'])
    if len(matching_results) == 0:
        raise ValueError()
    data = matching_results[get_random_index(matching_results)]
    artist_name = data['artistName']
    track_name = data['trackName']
    release_date = data['releaseDate']
    preview_url = data['previewUrl']
    return artist_name, track_name, release_date, preview_url

def get_random_index(results):
    return random.randint(0, len(results) - 1)

def filter_by_artist(results, artist):
    return [result for result in results if result['artistName'].lower() == artist.lower()]