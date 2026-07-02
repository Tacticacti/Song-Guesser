ARTIST_FILE = 'artists.txt'

def populate_artist_pool():
    with open(ARTIST_FILE, 'r') as file:
        artist_pool = [line.strip() for line in file if line.strip()]
    return artist_pool

def save_artist_pool(artist_pool):
    with open(ARTIST_FILE, 'w') as file:
        file.write("\n".join(artist_pool))
