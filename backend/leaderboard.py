import json
import os

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), 'leaderboard.json')


def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE) as file:
            entries = json.load(file)
    except (OSError, ValueError):
        return []
    if not isinstance(entries, list):
        return []
    valid_entries = [
        {'name': entry['name'], 'score': entry['score']}
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get('name'), str)
        and isinstance(entry.get('score'), int)
    ]
    return sorted(valid_entries, key=lambda entry: entry['score'], reverse=True)


def save_leaderboard(entries):
    with open(LEADERBOARD_FILE, 'w') as file:
        json.dump(entries, file, indent=2)


def submit_score(name, score):
    """Record a score, keeping only each player's best.

    Players are matched by name case-insensitively; a better score replaces
    their old entry (adopting the newly typed casing), a worse one is ignored.
    Returns (new_best, best_score, leaderboard).
    """
    entries = load_leaderboard()
    existing = next((entry for entry in entries if entry['name'].lower() == name.lower()), None)
    if existing is None:
        entries.append({'name': name, 'score': score})
        new_best, best_score = True, score
    elif score > existing['score']:
        existing['name'] = name
        existing['score'] = score
        new_best, best_score = True, score
    else:
        new_best, best_score = False, existing['score']
    entries.sort(key=lambda entry: entry['score'], reverse=True)
    save_leaderboard(entries)
    return new_best, best_score, entries
