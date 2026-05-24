"""
Spotify API wrapper using the Spotipy library.

Authentication:
    We use the Client Credentials Flow — a simple OAuth 2.0 flow that does not
    require user login. This is appropriate since we only read public track data
    and do not access user playlists.

    CLIENT_ID and CLIENT_SECRET are loaded from the .env file via python-dotenv.
    They are never hardcoded in source.

Search-based recommendations:
    The /recommendations endpoint was removed by Spotify in November 2024 for
    new applications. We use the /search endpoint instead, constructing queries
    from emotion-mapped genres and mood keywords. Results are then sorted by
    how closely their available metadata matches the target valence/energy
    profile derived from emotion_model.get_spotify_params().
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()


# Emotion → (genres, mood keywords) used to build the search query.
EMOTION_SEARCH: dict[str, dict] = {
    "happy": {"genres": ["pop", "funk"], "moods": ["happy", "upbeat", "feel good"]},
    "excited": {"genres": ["edm", "dance"], "moods": ["energetic", "hype", "euphoric"]},
    "calm": {"genres": ["ambient", "acoustic"], "moods": ["calm", "peaceful", "relaxing"]},
    "sad": {"genres": ["indie", "folk"], "moods": ["sad", "melancholic", "heartbreak"]},
    "anxious": {"genres": ["indie", "ambient"], "moods": ["anxious", "tense", "unsettled"]},
    "angry": {"genres": ["rock", "metal"], "moods": ["angry", "intense", "aggressive"]},
    "romantic": {"genres": ["soul", "r&b"], "moods": ["romantic", "love", "sensual"]},
    "focused": {"genres": ["ambient", "classical"], "moods": ["focus", "study", "concentration"]},
    "tired": {"genres": ["ambient", "classical"], "moods": ["sleep", "dreamy", "soft"]},
    "nostalgic": {"genres": ["soul", "indie"], "moods": ["nostalgic", "retro", "memories"]},
}

# Context → additional search keyword appended to narrow results.
CONTEXT_KEYWORDS: dict[str, str] = {
    "cooking": "cooking",
    "working": "study",
    "working_out": "workout",
    "driving": "driving",
    "relaxing": "chill",
    "dancing": "dance",
    "sleeping": "sleep",
    "socializing": "party",
}


def get_spotify_client() -> spotipy.Spotify:
    """
    Initialise and return a Spotify client using Client Credentials auth.

    Raises:
        ValueError: if SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET are missing.
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Spotify credentials not found. "
            "Check your .env file (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)."
        )

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def _build_query(emotion_key: str, context_key: str) -> str:
    """
    Build a Spotify search query string from emotion and context.

    Example: "genre:ambient calm sleeping"
    """
    search_cfg = EMOTION_SEARCH.get(emotion_key, {"genres": ["pop"], "moods": ["music"]})
    genre = search_cfg["genres"][0]
    mood = search_cfg["moods"][0]
    context_word = CONTEXT_KEYWORDS.get(context_key, "")

    parts = [genre, mood]
    if context_word and context_word != mood:
        parts.append(context_word)

    return " ".join(parts)


def _popularity_score(track: dict) -> float:
    """
    Heuristic score for ranking search results when audio features are unavailable.

    Uses track popularity (0–100) as a proxy for quality, with a small penalty
    for tracks that are either too obscure or over-mainstream. Since the
    /audio-features endpoint is also restricted for new apps, we cannot
    re-rank by valence/energy directly.
    """
    popularity = track.get("popularity") or 50
    if popularity < 20:
        return popularity * 0.5
    if popularity > 85:
        return popularity * 0.8
    return float(popularity)


def get_recommendations(
    emotion_key: str,
    context_key: str,
    spotify_params: dict,
    limit: int = 10,
) -> list[dict]:
    """
    Search for tracks matching the given emotion and context.

    Because /recommendations and /audio-features are unavailable for new apps
    (removed November 2024), we use /search with a mood+genre query and rank
    results by track popularity as a quality proxy.

    Args:
        emotion_key:    emotion key for building the search query.
        context_key:    context key for narrowing the query.
        spotify_params: audio feature targets (retained for documentation purposes).
        limit:          number of tracks to return.

    Returns:
        List of track dicts with keys: id, name, artist, album, image, preview, url, popularity.
    """
    sp = get_spotify_client()
    query = _build_query(emotion_key, context_key)

    raw = sp.search(q=query, type="track", limit=20, market="US")
    items = raw.get("tracks", {}).get("items", [])
    items = [t for t in items if t.get("id")]
    items.sort(key=_popularity_score, reverse=True)

    tracks = []
    for track in items[:limit]:
        tracks.append({
            "id": track["id"],
            "name": track["name"],
            "artist": ", ".join(a["name"] for a in track["artists"]),
            "album": track["album"]["name"],
            "image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "preview": track.get("preview_url"),
            "url": track["external_urls"].get("spotify"),
            "popularity": track.get("popularity"),
        })

    return tracks