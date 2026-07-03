# Song Guesser

Hear a song preview and guess the year it came out! Guess the artist and song name for bonus points. Three wrong year guesses and it's game over.

Songs come from the [iTunes Search API](https://performance-partners.apple.com/search-api) based on a customisable artist list.

## Project layout

- `backend/` — Python package: FastAPI server (`server.py`), CLI game (`main.py`), and their tests in `backend/tests/`
- `frontend/` — Svelte + TypeScript app, with its tests in `frontend/tests/`

## Web version (Svelte + FastAPI)

Run both servers with one command (from the repo root):

```sh
npm install   # first time only
npm run dev
```

Then open http://localhost:5173. Press `Ctrl+C` to stop both servers.

### Running the servers separately

Run the backend:

```sh
cd backend
venv/Scripts/python -m uvicorn server:app --port 8000
```

Run the frontend in a second terminal:

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

## CLI version

```sh
cd backend
venv/Scripts/python main.py
```

Requires [VLC](https://www.videolan.org/) to be installed for audio playback. While a song is playing, type `/vol <0-100>` to adjust the volume.

## Setup from scratch

```sh
cd backend
python -m venv venv
venv/Scripts/python -m pip install -r requirements.txt
```

## Tests

Run everything (Python + frontend) with one command from the repo root:

```sh
npm test
```

Or each suite on its own:

```sh
cd backend && venv/Scripts/python -m unittest discover tests   # backend + CLI (unittest)
npm test --prefix frontend                                     # frontend (vitest)
```
