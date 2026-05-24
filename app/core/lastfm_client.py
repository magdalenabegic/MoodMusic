"""
Last.fm API client for mood-based track recommendations.

We use the Last.fm Tag API to fetch tracks associated with mood and genre tags.
Last.fm tags are crowd-sourced — users label tracks with terms like "calm",
"happy", "energetic" — which maps naturally onto the affective computing
concept of user-perceived emotion in music.

Authentication:
    Last.fm uses a simple API key (no OAuth required for read-only access).
    The key is loaded from the .env file as LASTFM_API_KEY.

Endpoints used:
    tag.getTopTracks — returns top tracks for a given tag.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"

# Emotion + context = Last.fm tags.
# Tags are tried in order; if the first returns no results we fall back to the next.
EMOTION_TAGS: dict[str, list[str]] = {
    "happy": ["happy", "feel good", "upbeat", "fun"],
    "excited": ["energetic", "euphoric", "hype", "upbeat"],
    "calm": ["calm", "peaceful", "relaxing", "chill"],
    "sad": ["sad", "melancholic", "heartbreak", "emotional"],
    "anxious": ["anxious", "tense", "dark", "indie"],
    "angry": ["angry", "aggressive", "intense", "metal"],
    "romantic": ["romantic", "love", "sensual", "soul"],
    "focused": ["focus", "study", "concentration", "instrumental"],
    "tired": ["sleep", "dreamy", "soft", "ambient"],
    "nostalgic": ["nostalgic", "retro", "memories", "classic"],
}

CONTEXT_TAGS: dict[str, str] = {
    "cooking": "cooking",
    "working": "study",
    "working_out": "workout",
    "driving": "driving",
    "relaxing": "chill",
    "dancing": "dance",
    "sleeping": "sleep",
    "socializing": "party",
}


def _get_api_key() -> str:
    # Try Streamlit Cloud secrets first, fall back to .env for local development.
    try:
        import streamlit as st
        key = st.secrets.get("LASTFM_API_KEY")
    except Exception:
        key = None
    if not key:
        key = os.getenv("LASTFM_API_KEY")
    if not key:
        raise ValueError(
            "Last.fm API key not found. "
            "Add LASTFM_API_KEY to your .env file or Streamlit secrets."
        )
    return key


def _fetch_tag_tracks(tag: str, limit: int = 20) -> list[dict]:
    """
    Fetch top tracks for a Last.fm tag.

    Returns a list of raw Last.fm track dicts, or an empty list on failure.
    """
    params = {
        "method": "tag.getTopTracks",
        "tag": tag,
        "api_key": _get_api_key(),
        "format": "json",
        "limit": limit,
    }
    response = requests.get(LASTFM_BASE, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("tracks", {}).get("track", [])


def _build_spotify_search_url(artist: str, title: str) -> str:
    """Build a Spotify search URL so the user can open the track directly."""
    query = f"{artist} {title}".replace(" ", "+")
    return f"https://open.spotify.com/search/{query}"


def get_recommendations(
    emotion_key: str,
    context_key: str,
    spotify_params: dict,
    limit: int = 10,
) -> list[dict]:
    """
    Return tracks matching the given emotion and context using Last.fm tags.

    Strategy:
        1. Try the primary emotion tag.
        2. If fewer than `limit` tracks are returned, try the context tag
           and merge, deduplicating by (artist, title).
        3. Fall back to secondary emotion tags if still short.

    Args:
        emotion_key: key from emotion_model.EMOTIONS.
        context_key: key from emotion_model.CONTEXTS.
        spotify_params: retained for interface compatibility and documentation.
        limit: number of tracks to return.

    Returns:
        List of track dicts with keys:
            name, artist, url, image, lastfm_url
    """
    primary_tag = EMOTION_TAGS.get(emotion_key, ["pop"])[0]
    fallback_tags = EMOTION_TAGS.get(emotion_key, ["pop"])[1:]
    context_tag = CONTEXT_TAGS.get(context_key, "")

    seen: set[tuple] = set()
    tracks: list[dict] = []

    def add_tracks(raw: list[dict]) -> None:
        for t in raw:
            artist = t.get("artist", {}).get("name", "") if isinstance(t.get("artist"), dict) else t.get("artist", "")
            name = t.get("name", "")
            key = (artist.lower(), name.lower())
            if key in seen or not artist or not name:
                continue
            seen.add(key)

            image_list = t.get("image", [])
            image = next((img["#text"] for img in reversed(image_list) if img.get("#text")), None)

            tracks.append({
                "name": name,
                "artist": artist,
                "url": _build_spotify_search_url(artist, name),
                "image": image,
                "lastfm_url": t.get("url", ""),
            })

    add_tracks(_fetch_tag_tracks(primary_tag, limit=limit * 2))

    if len(tracks) < limit and context_tag and context_tag != primary_tag:
        add_tracks(_fetch_tag_tracks(context_tag, limit=limit))

    for tag in fallback_tags:
        if len(tracks) >= limit:
            break
        add_tracks(_fetch_tag_tracks(tag, limit=limit))

    return tracks[:limit]