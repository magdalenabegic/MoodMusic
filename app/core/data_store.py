"""
Persists and loads user sessions in CSV format.

Each session records one full usage cycle:
    1. User selects an emotion and context.
    2. App recommends tracks.
    3. User listens on Spotify.
    4. User rates the effect (1-5).

CSV columns:
    timestamp — ISO 8601 datetime of the session
    emotion_key — selected emotion key (e.g. "happy")
    emotion_label — display name (e.g. "Happy")
    context_key — selected context key (e.g. "working_out")
    context_label  — display name (e.g. "Working Out")
    mood_goal — what the user wanted to achieve
    rating  — 1-5 score of how well music achieved the goal
    tracks_played — number of tracks in the session

A flat CSV is sufficient for academic analysis. A production app would use
a proper database.
"""

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.csv"

CSV_HEADERS = [
    "timestamp",
    "emotion_key",
    "emotion_label",
    "context_key",
    "context_label",
    "mood_goal",
    "rating",
    "tracks_played",
]

MOOD_GOALS = [
    "Cheer me up 😄",
    "Calm me down 😌",
    "Boost my energy ⚡",
    "Help me focus 🎯",
    "Match my current mood 🎵",
]


def ensure_data_file() -> None:
    """Create the CSV file with headers if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def save_session(
    emotion_key: str,
    emotion_label: str,
    context_key: str,
    context_label: str,
    mood_goal: str,
    rating: int,
    tracks_played: int,
) -> None:
    """
    Append one session to the CSV file.

    Args:
        emotion_key: emotion key for analysis.
        emotion_label: display name for the emotion.
        context_key: context key for analysis.
        context_label: display name for the context.
        mood_goal: what the user wanted to achieve.
        rating: 1-5 rating.
        tracks_played: number of tracks recommended.
    """
    ensure_data_file()
    with open(SESSIONS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "emotion_key": emotion_key,
            "emotion_label": emotion_label,
            "context_key": context_key,
            "context_label": context_label,
            "mood_goal": mood_goal,
            "rating": rating,
            "tracks_played": tracks_played,
        })


def load_sessions():
    """
    Load all sessions from the CSV as a pandas DataFrame.

    Returns:
        pandas.DataFrame with all sessions, or an empty DataFrame if none exist.
    """
    import pandas as pd

    ensure_data_file()
    df = pd.read_csv(SESSIONS_FILE)

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    return df