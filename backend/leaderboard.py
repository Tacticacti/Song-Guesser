import os

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert, select, update

# points at the dockerized PostgreSQL from docker-compose.yml by default;
# tests override this with a local SQLite database so they need no Docker
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+psycopg://songguesser:songguesser@localhost:5432/songguesser',
)

metadata = MetaData()

scores = Table(
    'scores',
    metadata,
    # players are identified by their lowercased name, so "Ed" and "ED"
    # share one entry; the display name keeps whatever they typed last
    Column('name_key', String, primary_key=True),
    Column('name', String, nullable=False),
    Column('score', Integer, nullable=False),
)

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        # pre-ping discards stale pooled connections, so the leaderboard
        # recovers on its own after a database restart
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        metadata.create_all(_engine)
    return _engine


def reset_engine():
    """Drop the cached engine so the next call reconnects (used by tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def load_leaderboard():
    with get_engine().connect() as connection:
        rows = connection.execute(
            select(scores.c.name, scores.c.score).order_by(scores.c.score.desc(), scores.c.name)
        ).all()
    return [{'name': row.name, 'score': row.score} for row in rows]


def submit_score(name, score):
    """Record a score, keeping only each player's best.

    Players are matched by name case-insensitively; a better score replaces
    their old entry (adopting the newly typed casing), a worse one is ignored.
    Returns (new_best, best_score, leaderboard).
    """
    name_key = name.lower()
    with get_engine().begin() as connection:
        existing_score = connection.execute(
            select(scores.c.score).where(scores.c.name_key == name_key)
        ).scalar_one_or_none()
        if existing_score is None:
            connection.execute(insert(scores).values(name_key=name_key, name=name, score=score))
            new_best, best_score = True, score
        elif score > existing_score:
            connection.execute(
                update(scores).where(scores.c.name_key == name_key).values(name=name, score=score)
            )
            new_best, best_score = True, score
        else:
            new_best, best_score = False, existing_score
    return new_best, best_score, load_leaderboard()
