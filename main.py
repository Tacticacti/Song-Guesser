from audio_player import play_audio
from api_fetcher import fetch_metadata
import random

MAX_STRIKES = 3
EXTERNAL_URL = 'https://itunes.apple.com/search'

def start_game(artist_pool, strikes, score):
    while strikes < MAX_STRIKES:
        print(f"\n--- score: {score} | strikes: {strikes}/{MAX_STRIKES} ---")
        artist = random.choice(artist_pool)
        params = {"term": artist, "media": "music", "entity": "song"}
        fetched_artist_name, fetched_track_name, fetched_release_date, fetched_preview_url = fetch_metadata(EXTERNAL_URL, params)
        correct_year = int(fetched_release_date.split("-")[0])

        player_instance = play_audio(fetched_preview_url)
        user_guess = ""
        guess_val = user_guess
        while True:
            user_guess = input("What year did this song come out? ")
            try:
                guess_val = int(user_guess)
                player_instance.stop()
                break
            except ValueError:
                print("Please enter a number between 0 and 2026!")

        if guess_val == correct_year:
            score += 1
            print(f"You got it right!")
        else:
            strikes += 1
            print(f"Unlucky! You were off by {abs(correct_year - guess_val)} years!")
        print(f"This song was {fetched_track_name} by {fetched_artist_name}!")

def populate_artist_pool():
    with open('artists.txt', 'r') as file:
        artist_pool = file.read().splitlines()
    return artist_pool

def main():
    strikes = 0
    score = 0
    artist_pool = populate_artist_pool()
    start_game(artist_pool, strikes, score)

if __name__ == "__main__":
    main()