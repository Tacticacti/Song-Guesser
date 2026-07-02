import os

# resolve relative to this file so the game works no matter
# which directory it is launched from
ARTIST_FILE = os.path.join(os.path.dirname(__file__), 'artists.txt')

def populate_artist_pool():
    with open(ARTIST_FILE, 'r') as file:
        artist_pool = [line.strip() for line in file if line.strip()]
    return artist_pool

def save_artist_pool(artist_pool):
    with open(ARTIST_FILE, 'w') as file:
        file.write("\n".join(artist_pool))
