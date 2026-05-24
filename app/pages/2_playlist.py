"""
Playlist page.

Fetches track recommendations based on the emotion and context selected on
the previous page, then displays them with album art and Spotify search links.
The user must select a mood goal before tracks are fetched and displayed.
"""

import streamlit as st
from core.lastfm_client import get_recommendations
from core.data_store import MOOD_GOALS
from core.emotion_model import EMOTIONS, CONTEXTS

st.set_page_config(
    page_title="MoodMusic - Your Playlist",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "emotion_key" not in st.session_state or not st.session_state.emotion_key:
    st.warning("No emotion selected. Please start from the beginning.")
    if st.button("Go to start"):
        st.switch_page("pages/1_mood.py")
    st.stop()

emotion_key = st.session_state.emotion_key
context_key = st.session_state.context_key
spotify_params = st.session_state.get("spotify_params", {})

emotion = EMOTIONS[emotion_key]
context = CONTEXTS[context_key]

st.markdown(f"## Your playlist for {emotion.emoji} {emotion.label}")
st.caption(f"Context: {context.emoji} {context.label}")

st.divider()

st.markdown("#### What do you want music to do for you?")
existing_goal = st.session_state.get("mood_goal")
goal_index = MOOD_GOALS.index(existing_goal) if existing_goal in MOOD_GOALS else None
goal = st.radio("Pick a goal:", MOOD_GOALS, index=goal_index, label_visibility="collapsed", disabled=bool(existing_goal))
if goal and not existing_goal:
    st.session_state.mood_goal = goal

st.divider()

if not st.session_state.get("mood_goal"):
    st.info("Pick a goal above to see your tracks.")
    st.stop()

cache_key = f"tracks_{emotion_key}_{context_key}"
if cache_key not in st.session_state:
    with st.spinner("Finding your music..."):
        try:
            st.session_state[cache_key] = get_recommendations(
                emotion_key, context_key, spotify_params, limit=10
            )
        except Exception as e:
            st.error(f"Could not fetch tracks: {e}")
            st.stop()

tracks = st.session_state[cache_key]
st.session_state.tracks_played = len(tracks)

if not tracks:
    st.warning("No tracks found for this combination. Try a different emotion or context.")
    st.stop()

st.markdown(f"#### {len(tracks)} tracks picked for you")

for track in tracks:
    col_img, col_info = st.columns([1, 4])
    with col_img:
        if track["image"]:
            st.image(track["image"], width=80)
    with col_info:
        st.markdown(f"**{track['name']}**")
        st.caption(track["artist"])
        if track["url"]:
            st.markdown(f"[Search on Spotify]({track['url']})")
    st.divider()

if st.button("I'm done listening — rate it", use_container_width=True, type="primary"):
    st.switch_page("pages/3_feedback.py")