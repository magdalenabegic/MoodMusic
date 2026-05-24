"""
Mood selection page.

The user picks an emotion and a context. Both selections are stored in
st.session_state and carried through to the playlist page.
"""

import streamlit as st
from core.emotion_model import EMOTIONS, CONTEXTS, get_spotify_params

st.set_page_config(
    page_title="MoodMusic - How do you feel?",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "emotion_key" not in st.session_state:
    st.session_state.emotion_key = None
if "context_key" not in st.session_state:
    st.session_state.context_key = None

st.markdown("## How do you feel right now?")
st.caption("Pick the emotion that best describes your current state.")

cols = st.columns(5)
for i, (key, emotion) in enumerate(EMOTIONS.items()):
    with cols[i % 5]:
        if st.button(f"{emotion.emoji}\n{emotion.label}", key=f"emotion_{key}", use_container_width=True):
            st.session_state.emotion_key = key

if st.session_state.emotion_key:
    e = EMOTIONS[st.session_state.emotion_key]
    st.success(f"Selected: {e.emoji} {e.label}")

st.divider()

st.markdown("## What are you doing?")
st.caption("Context helps us pick the right music for the moment.")

cols2 = st.columns(4)
for i, (key, context) in enumerate(CONTEXTS.items()):
    with cols2[i % 4]:
        if st.button(f"{context.emoji}\n{context.label}", key=f"context_{key}", use_container_width=True):
            st.session_state.context_key = key

if st.session_state.context_key:
    c = CONTEXTS[st.session_state.context_key]
    st.success(f"Selected: {c.emoji} {c.label}")

st.divider()

if st.session_state.emotion_key and st.session_state.context_key:
    st.session_state.spotify_params = get_spotify_params(
        st.session_state.emotion_key,
        st.session_state.context_key,
    )
    if st.button("Find my music", use_container_width=True, type="primary"):
        st.switch_page("pages/2_playlist.py")
else:
    st.info("Pick both an emotion and a context to continue.")