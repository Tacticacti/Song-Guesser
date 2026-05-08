import requests

def fetch(url):
    response = requests.get(url)
    # print(response.json()['results'][0])
    data = response.json()
    artist_name = data['results'][0]['artistName']
    track_name = data['results'][0]['trackName']
    release_date = data['results'][0]['releaseDate']
    preview_url = data['results'][0]['previewUrl']
    return artist_name, track_name, release_date, preview_url

if __name__ == "__main__":
    artist_name, track_name, release_date, preview_url = fetch("https://itunes.apple.com/search?term=michael+jackson&media=music&entity=song&sort=recent")
    print(f"Artist Name: {artist_name}")
    print(f"Track Name: {track_name}")
    print(f"Release Date: {release_date}")
    print(f"Preview URL: {preview_url}")
    print(f"Release Year: {release_date.split("-")[0]}")