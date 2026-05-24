# MoodMusic

**Emotion-based music recommendation app**
Project for the *Affective Computing* course.

Live app: [moodmusic-affective-computing.streamlit.app](https://moodmusic-affective-computing.streamlit.app)

---

## About

MoodMusic recommends music based on:
- **Current emotional state** (self-reporting)
- **Activity / context** (cooking, working out, studying...)
- **Listening goal** (cheer up, calm down, focus...)

After listening, the user rates (1–5) how well the music achieved the goal. These ratings enable a minimal analysis of music's effect on mood over time.

---

## Affective Computing — Theoretical Background

### Emotion Model

The app uses the **Russell Circumplex Model** — a two-dimensional space defined by:

| Dimension | Description | Range |
|-----------|-------------|-------|
| **Valence** | Pleasantness (negative to positive) | 0.0 – 1.0 |
| **Arousal** | Activation level (calm to excited) | 0.0 – 1.0 |

```
        High Arousal
               |
    Anxious    |    Excited
    Angry      |    Happy
               |
Negative ------+------ Positive
               |
    Sad        |    Calm
    Tired      |    Content
               |
        Low Arousal
```

### Affective State Acquisition

We use **self-reporting**, the user selects their emotion directly. This method is:
- **Reliable** for subjective emotional states
- **Simple** to implement without physiological sensors
- **Validated** in affective computing research

### Context as a Modifier

The same emotion in different contexts calls for different music:
- *Calm + Working* — quiet ambient music, low tempo
- *Calm + Cooking* — light pop, moderate tempo

Context modifies the Spotify audio parameter targets (energy, tempo, danceability, acousticness) without changing the base emotion.

### Emotion to Audio Feature Mapping

| Emotion | Valence | Arousal | Energy | Tempo (BPM) |
|---------|---------|---------|--------|-------------|
| Happy | 0.85 | 0.70 | 0.70 | ~130 |
| Excited | 0.90 | 0.90 | 0.90 | ~150 |
| Calm | 0.65 | 0.20 | 0.20 | ~80 |
| Sad | 0.20 | 0.25 | 0.25 | ~85 |
| Angry | 0.15 | 0.85 | 0.85 | ~145 |
| Focused | 0.55 | 0.55 | 0.55 | ~115 |

---

## Architecture

```
moodmusic/
|
+-- app/
|   +-- Home.py                  # Entry point
|   |
|   +-- core/
|   |   +-- emotion_model.py     # Emotions, contexts, valence-arousal mapping
|   |   +-- lastfm_client.py     # Last.fm API — track recommendations
|   |   +-- spotify_client.py    # Spotify API wrapper (retained for reference)
|   |   +-- data_store.py        # Session storage in CSV
|   |
|   +-- pages/
|       +-- 1_mood.py            # Emotion and context selection
|       +-- 2_playlist.py        # Track display
|       +-- 3_feedback.py        # Rating (1–5)
|       +-- 4_analysis.py        # Session data visualisation
|
+-- data/
|   +-- sessions.csv             # User session storage (gitignored)
|
+-- test_core.py                 # Smoke tests for core modules
+-- requirements.txt
+-- README.md
```

### Data Flow

```
User selects emotion + context
        |
        v
emotion_model.get_spotify_params()
  maps emotion to valence/arousal
  applies context modifiers
        |
        v
User selects listening goal
        |
        v
lastfm_client.get_recommendations() fetches tracks by mood/genre tags
  deduplicates and ranks by popularity
        |
        v
User listens on Spotify
        |
        v
User rates the effect (1–5)
        |
        v
data_store.save_session()
  appends session to sessions.csv
        |
        v
4_analysis.py
  visualises session data
```

---

## API Note

This project originally planned to use the **Spotify Recommendations API**
(`/recommendations` and `/audio-features`). Spotify removed access to these
endpoints for new applications in November 2024.

We use the **Last.fm Tag API** instead. Last.fm tags are crowd-sourced which means that
users label tracks with terms like "calm", "happy", or "energetic" — which
maps naturally onto the affective computing concept of user-perceived emotion
in music. Track links open a Spotify search so the user listens on Spotify
as originally intended.

---

## Running Locally

### Prerequisites

- Python 3.10+
- Spotify Developer account (for `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`)
- Last.fm API account (for `LASTFM_API_KEY`)

### Setup

```bash
git clone https://github.com/your-username/moodmusic.git
cd moodmusic

python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your API keys

streamlit run app/Home.py
```

App runs at `http://localhost:8501`.

### Environment Variables

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8501
LASTFM_API_KEY=your_lastfm_key
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web interface |
| Last.fm API | Track recommendations by mood tag |
| Spotipy | Spotify API wrapper (retained for reference) |
| pandas | Session data analysis |
| plotly | Interactive visualisations |
| python-dotenv | API key management |

---

## Feedback and Analysis

The app collects minimal session data for academic analysis:

- Which emotion + context combination has the highest average rating?
- Did users who wanted to "cheer up" achieve that goal?
- Which contexts show the most consistent effect?

Analysis is available on the **Analysis** page within the app.
