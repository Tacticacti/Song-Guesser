import requests
import random

# some tracks come back without a preview or release date; those cannot be played
REQUIRED_FIELDS = ('artistName', 'trackName', 'releaseDate', 'previewUrl')

def fetch_metadata(url, params):
    response = requests.get(url, params)
    results = response.json().get('results', [])
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

def is_playable(result):
    return all(result.get(field) for field in REQUIRED_FIELDS)

def filter_by_artist(results, artist):
    return [result for result in results
            if is_playable(result) and result['artistName'].lower() == artist.lower()]