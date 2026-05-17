from audio_player import play_audio, set_volume
from api_fetcher import fetch_metadata
import random
import sys

MAX_STRIKES = 3
EXTERNAL_URL = 'https://itunes.apple.com/search'

def bonus_point(fetched_artist_name, fetched_track_name):
    bonus_score = 0
    artist_guess = input("Guess the artist name for a bonus point!\n")
    if artist_guess == fetched_artist_name:
        bonus_score += 1
        print(f"You are right! This song is indeed by {fetched_artist_name}!")
    else:
        print(f"Nope! This song is by {fetched_artist_name}!")
    guess_track_name = input("Guess this song's name for a bonus point!\n")
    if guess_track_name == fetched_track_name:
        bonus_score += 1
        print("That's right!")
    else:
        print(f"Nope! That was incorrect!")
    return bonus_score

def evaluate_guess(fetched_artist_name, fetched_track_name, correct_year, guess_val, strikes, score):
    if guess_val == correct_year:
        score += 1
        print(f"You got it right!")
        score += bonus_point(fetched_artist_name, fetched_track_name)
    else:
        strikes += 1
        year_difference = abs(correct_year - guess_val)
        if year_difference < 5:
            print("So Close!")
        elif year_difference < 10:
            print("Close! But not close enough!")
        else:
            print("Way off!")
    print(f"This song was {fetched_track_name} by {fetched_artist_name}!")
    return score, strikes

def exit_game():
    print("See you next time!")
    print("<------------------------------------------------------------>")
    sys.exit()

def evaluate_choice(user_choice):
    match user_choice:
        case "1":
            strikes = 0
            score = 0
            artist_pool = populate_artist_pool()
            standard(artist_pool, strikes, score)
        case "2":
            print("WIP!")
        case "3":
            print("WIP")
        case "4":
            exit_game()
        case _:
            print("Please enter a valid number from 1 to 4!")

def show_main_menu():
    while True:
        print("<------------------Welcome to Song Guesser!------------------>")
        print("1. Start Normal Mode")
        print("2. More Modes")
        print("3. Settings")
        print("4. Quit game")
        user_choice = input("Please enter your choice between 1 to 4!\n")
        evaluate_choice(user_choice)

def standard(artist_pool, strikes, score):
    while strikes < MAX_STRIKES:
        print("Starting Standard Mode")
        print(f"\n--- score: {score} | strikes: {strikes}/{MAX_STRIKES} ---")
        artist = random.choice(artist_pool)
        params = {"term": artist, "media": "music", "entity": "song", "attribute": "artistTerm"}

        try:
            fetched_artist_name, fetched_track_name, fetched_release_date, fetched_preview_url = fetch_metadata(EXTERNAL_URL, params)
        except ValueError:
            print(f"The artist {params['term']} was not found!")
            print('Skipping artist...')
            continue
        correct_year = int(fetched_release_date.split("-")[0])

        player_instance = play_audio(fetched_preview_url)
        guess_val = 0
        while True:
            user_input = input("What year did this song come out? ")
            if user_input.startswith("/vol "):
                try:
                    new_volume = int(user_input.split(" ")[1])
                    set_volume(player_instance, new_volume)
                    print(f"🔊 Volume adjusted to {new_volume}%")
                    continue
                except (ValueError, IndexError):
                    print("❌ Invalid volume command. To adjust volume, please use the format: /vol <volume value>")
                    continue
            try:
                guess_val = int(user_input)
                player_instance.stop()
                break
            except ValueError:
                print("Please enter a number!")

        score, strikes = evaluate_guess(fetched_artist_name, fetched_track_name, correct_year, guess_val, strikes, score)
    print(f"Game Over!")
    print(f"Your final score was: {score}")

def populate_artist_pool():
    with open('artists.txt', 'r') as file:
        artist_pool = file.read().splitlines()
    return artist_pool

def main():
    show_main_menu()

if __name__ == "__main__":
    main()