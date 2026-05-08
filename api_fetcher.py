import requests

def fetch_metadata(url):
    response = requests.get(url)
    # print(response.json()['results'][0])
    data = response.json()
    artist_name = data['results'][0]['artistName']
    track_name = data['results'][0]['trackName']
    release_date = data['results'][0]['releaseDate']
    preview_url = data['results'][0]['previewUrl']
    return artist_name, track_name, release_date, preview_url