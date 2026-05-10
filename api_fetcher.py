import requests
import random

def fetch_metadata(url, params):
    response = requests.get(url, params)
    results = response.json()['results']
    if len(results) == 0:
        raise ValueError()
    data = results[get_random_index(results)]
    artist_name = data['artistName']
    track_name = data['trackName']
    release_date = data['releaseDate']
    preview_url = data['previewUrl']
    return artist_name, track_name, release_date, preview_url

def get_random_index(results):
    return random.randint(0, len(results) - 1)