"""
Feedback page.

After listening, the user rates how well the music achieved their goal (1-5).
The session is then saved to disk via data_store.
"""

import streamlit as st
from core.data_store import save_session
from core.emotion_model import EMOTIONS, CONTEXTS

st.set_page_config(
    page_title="MoodMusic - Rate it",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

required = ["emotion_key", "context_key", "mood_goal", "tracks_played"]
if not all(k in st.session_state for k in required):
    st.warning("Session data missing. Please start from the beginning.")
    if st.button("Go to start"):
        st.switch_page("pages/1_mood.py")
    st.stop()

emotion = EMOTIONS[st.session_state.emotion_key]
context = CONTEXTS[st.session_state.context_key]

st.markdown("## How did it go?")
st.caption(
    f"You were feeling {emotion.emoji} **{emotion.label}** "
    f"while {context.label.lower()}, "
    f"and wanted music to: **{st.session_state.mood_goal}**"
)

st.divider()

st.markdown("#### How well did the music achieve your goal?")
st.caption("1 = not at all, 5 = perfectly")

rating = st.radio(
    "Rating:",
    options=[1, 2, 3, 4, 5],
    horizontal=True,
    label_visibility="collapsed",
    index=None,
)

RATING_LABELS = {
    1: "Not at all",
    2: "Slightly",
    3: "Somewhat",
    4: "Well",
    5: "Perfectly",
}

if rating:
    st.info(f"**{rating}/5** — {RATING_LABELS[rating]}")

st.divider()

if rating:
    if st.button("Save and see your history", use_container_width=True, type="primary"):
        save_session(
            emotion_key=st.session_state.emotion_key,
            emotion_label=emotion.label,
            context_key=st.session_state.context_key,
            context_label=context.label,
            mood_goal=st.session_state.mood_goal,
            rating=rating,
            tracks_played=st.session_state.tracks_played,
        )
        # Clear cache so a new session fetches fresh tracks.
        cache_key = f"tracks_{st.session_state.emotion_key}_{st.session_state.context_key}"
        for key in [cache_key, "mood_goal", "emotion_key", "context_key", "spotify_params"]:
            st.session_state.pop(key, None)
        st.switch_page("pages/4_analysis.py")
else:
    st.info("Pick a rating above to continue.")