import random
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api_fetcher import fetch_metadata
from artist_pool import populate_artist_pool, save_artist_pool
from leaderboard import load_leaderboard, submit_score

EXTERNAL_URL = 'https://itunes.apple.com/search'
MAX_FETCH_ATTEMPTS = 5
MAX_ACTIVE_ROUNDS = 1000
MAX_NAME_LENGTH = 20
TOP_SCORES = 10

app = FastAPI(title="Song Guesser API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active rounds keyed by round_id; the answers stay server-side so the
# browser never sees them before the player has guessed.
rounds = {}

class ArtistRequest(BaseModel):
    name: str

class GuessRequest(BaseModel):
    year: int

class BonusRequest(BaseModel):
    artist_guess: str
    track_guess: str

class ScoreRequest(BaseModel):
    name: str
    score: int

@app.get("/api/artists")
def get_artists():
    return {"artists": populate_artist_pool()}

@app.post("/api/artists")
def add_artist(request: ArtistRequest):
    name = request.name.strip()
    if not name:
        raise HTTPException(400, "The artist name cannot be empty!")
    if '\n' in name or '\r' in name:
        raise HTTPException(400, "The artist name cannot contain line breaks!")
    artist_pool = populate_artist_pool()
    if name.lower() in (artist.lower() for artist in artist_pool):
        raise HTTPException(400, f"{name} is already in the list!")
    artist_pool.append(name)
    save_artist_pool(artist_pool)
    return {"artists": artist_pool}

@app.delete("/api/artists/{name:path}")
def remove_artist(name: str):
    artist_pool = populate_artist_pool()
    for artist in artist_pool:
        if artist.lower() == name.strip().lower():
            if len(artist_pool) == 1:
                raise HTTPException(400, "You cannot remove the last artist in the list!")
            artist_pool.remove(artist)
            save_artist_pool(artist_pool)
            return {"artists": artist_pool}
    raise HTTPException(404, f"{name} is not in the list!")

@app.get("/api/leaderboard")
def get_leaderboard():
    return {"leaderboard": load_leaderboard()[:TOP_SCORES]}

@app.post("/api/leaderboard")
def post_score(request: ScoreRequest):
    name = request.name.strip()
    if not name:
        raise HTTPException(400, "Please enter a name!")
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(400, f"Names can be at most {MAX_NAME_LENGTH} characters long!")
    if request.score < 0:
        raise HTTPException(400, "Scores cannot be negative!")
    new_best, best_score, entries = submit_score(name, request.score)
    return {
        "new_best": new_best,
        "best_score": best_score,
        "leaderboard": entries[:TOP_SCORES],
    }

@app.post("/api/rounds")
def start_round():
    artist_pool = populate_artist_pool()
    if not artist_pool:
        raise HTTPException(400, "The artist list is empty! Add an artist in the settings first.")
    for _ in range(MAX_FETCH_ATTEMPTS):
        artist = random.choice(artist_pool)
        params = {"term": artist, "media": "music", "entity": "song", "attribute": "artistTerm"}
        try:
            fetched_artist_name, fetched_track_name, fetched_release_date, fetched_preview_url = fetch_metadata(EXTERNAL_URL, params)
        except ValueError:
            continue
        except requests.RequestException:
            raise HTTPException(502, "Could not reach the iTunes API. Check your internet connection!")
        if len(rounds) >= MAX_ACTIVE_ROUNDS:
            # drop the oldest abandoned round so the store cannot grow forever
            rounds.pop(next(iter(rounds)))
        round_id = str(uuid.uuid4())
        rounds[round_id] = {
            "artist": fetched_artist_name,
            "track": fetched_track_name,
            "year": int(fetched_release_date.split("-")[0]),
            "awaiting_bonus": False,
        }
        return {"round_id": round_id, "preview_url": fetched_preview_url}
    raise HTTPException(502, "Could not find a song for any artist in the list. Try again!")

def closeness_hint(year_difference):
    if year_difference < 5:
        return "So Close!"
    elif year_difference < 10:
        return "Close! But not close enough!"
    return "Way off!"

@app.post("/api/rounds/{round_id}/guess")
def guess_year(round_id: str, request: GuessRequest):
    game_round = rounds.get(round_id)
    if game_round is None:
        raise HTTPException(404, "Round not found!")
    if game_round["awaiting_bonus"]:
        raise HTTPException(400, "This round is waiting for its bonus guesses!")
    if request.year == game_round["year"]:
        game_round["awaiting_bonus"] = True
        return {"correct": True, "points": 1, "year": game_round["year"]}
    del rounds[round_id]
    return {
        "correct": False,
        "points": 0,
        "hint": closeness_hint(abs(game_round["year"] - request.year)),
        "year": game_round["year"],
        "artist": game_round["artist"],
        "track": game_round["track"],
    }

@app.post("/api/rounds/{round_id}/bonus")
def guess_bonus(round_id: str, request: BonusRequest):
    game_round = rounds.get(round_id)
    if game_round is None or not game_round["awaiting_bonus"]:
        raise HTTPException(404, "Round not found!")
    artist_correct = request.artist_guess.strip().lower() == game_round["artist"].lower()
    track_correct = request.track_guess.strip().lower() == game_round["track"].lower()
    del rounds[round_id]
    return {
        "artist_correct": artist_correct,
        "track_correct": track_correct,
        "points": int(artist_correct) + int(track_correct),
        "artist": game_round["artist"],
        "track": game_round["track"],
    }
