"""
Smoke test for core modules. Run from the project root:

    python test_core.py

Requires valid Spotify credentials in .env.
Does not write anything to disk.
"""

import sys
sys.path.insert(0, "app")
from app.core.emotion_model import EMOTIONS, CONTEXTS, get_spotify_params
from app.core.spotify_client import get_spotify_client, get_recommendations

print("── emotion_model ─────────────────────────────────────")

print(f"emotions: {list(EMOTIONS.keys())}")
print(f"contexts: {list(CONTEXTS.keys())}")

p1 = get_spotify_params("happy", "working_out")
p2 = get_spotify_params("calm", "sleeping")
print(f"\n happy + working_out = {p1}")
print(f"calm + sleeping = {p2}")

assert 0.0 <= p1["target_valence"] <= 1.0
assert 0.0 <= p1["target_energy"] <= 1.0
assert p2["target_energy"] < p1["target_energy"], "calm should have lower energy than happy"

print("OK")

print("\n── spotify_client ────────────────────────────────────")


try:
    sp = get_spotify_client()
    print("authenticated")

    tracks = get_recommendations("happy", "working_out", p1, limit=3)
    assert len(tracks) > 0, "expected at least one track"
    print(f"got {len(tracks)} tracks for happy + working_out:")
    for t in tracks:
        print(f"{t['artist']} — {t['name']} (popularity {t['popularity']})")
        print(f"{t['url']}")

    tracks2 = get_recommendations("calm", "sleeping", p2, limit=3)
    print(f"\ngot {len(tracks2)} tracks for calm + sleeping:")
    for t in tracks2:
        print(f"{t['artist']} — {t['name']} (popularity {t['popularity']})")

except ValueError as e:
    print(f"credentials error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"unexpected error: {e}")
    raise

print("\n ─── all tests passed ────────────────────────────────────")