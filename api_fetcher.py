import requests
import random

def fetch_metadata(url, params):
    response = requests.get(url, params)
    # print(response.json()['results'][0])
    results = response.json()['results']
    data = results[random.randint(0, len(results))]
    artist_name = data['artistName']
    track_name = data['trackName']
    release_date = data['releaseDate']
    preview_url = data['previewUrl']
    return artist_name, track_name, release_date, preview_url