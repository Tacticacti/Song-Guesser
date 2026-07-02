from audio_player import play_audio, set_volume
from api_fetcher import fetch_metadata
import random
import sys

MAX_STRIKES = 3
EXTERNAL_URL = 'https://itunes.apple.com/search'

game_settings = {"volume": 100}

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

def change_volume():
    user_input = input("Please enter a new volume between 0 and 100\n")
    try:
        new_volume = max(0, min(100, int(user_input)))
    except ValueError:
        print("Please enter a number!")
        return
    game_settings["volume"] = new_volume
    print(f"🔊 Volume set to {new_volume}%")

def save_artist_pool(artist_pool):
    with open('artists.txt', 'w') as file:
        file.write("\n".join(artist_pool))

def add_artist(artist_pool):
    new_artist = input("Enter the name of the artist to add\n").strip()
    if not new_artist:
        print("The artist name cannot be empty!")
        return
    if new_artist.lower() in (artist.lower() for artist in artist_pool):
        print(f"{new_artist} is already in the list!")
        return
    artist_pool.append(new_artist)
    save_artist_pool(artist_pool)
    print(f"Added {new_artist}!")

def remove_artist(artist_pool):
    target = input("Enter the name of the artist to remove\n").strip()
    for artist in artist_pool:
        if artist.lower() == target.lower():
            if len(artist_pool) == 1:
                print("You cannot remove the last artist in the list!")
                return
            artist_pool.remove(artist)
            save_artist_pool(artist_pool)
            print(f"Removed {artist}!")
            return
    print(f"{target} is not in the list!")

def customise_artist_list():
    while True:
        artist_pool = populate_artist_pool()
        print("---------------------------Artist List---------------------------")
        for artist in artist_pool:
            print(f"- {artist}")
        print("1. Add an artist")
        print("2. Remove an artist")
        print("3. Go Back")
        user_choice = input("Please choose an option\n")
        match user_choice:
            case "1":
                add_artist(artist_pool)
            case "2":
                remove_artist(artist_pool)
            case "3":
                return
            case _:
                print("Please enter a valid number from 1 to 3!")

def evaluate_setting_choice(user_choice):
    match user_choice:
        case "1":
            change_volume()
        case "2":
            customise_artist_list()
        case "3":
            return
        case _:
            print("Please enter a valid number from 1 to 3!")

def show_settings():
    user_choice = 0
    while user_choice != "3":
        print("------------------------------Settings------------------------------")
        print(f"1. Volume ({game_settings['volume']}%)")
        print("2. Customise Current Artist List")
        print("3. Go Back")
        user_choice = input("Please choose a setting\n")
        evaluate_setting_choice(user_choice)

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
            show_settings()
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
        set_volume(player_instance, game_settings["volume"])
        guess_val = 0
        while True:
            user_input = input("What year did this song come out? ")
            if user_input.startswith("/vol "):
                try:
                    new_volume = max(0, min(100, int(user_input.split(" ")[1])))
                    set_volume(player_instance, new_volume)
                    game_settings["volume"] = new_volume
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
        artist_pool = [line.strip() for line in file if line.strip()]
    return artist_pool

def main():
    show_main_menu()

if __name__ == "__main__":
    main()