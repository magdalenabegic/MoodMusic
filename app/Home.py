"""
Entry point for the MoodMusic Streamlit application.

Streamlit automatically treats files in the /pages/ directory as subpages.
This file is the first screen the user sees.
"""

import streamlit as st

st.set_page_config(
    page_title="MoodMusic",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        background: linear-gradient(135deg, #1DB954, #158a3e);
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎵 MoodMusic</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Music tailored to your mood and activity</div>',
    unsafe_allow_html=True
)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### Feel")
    st.write("Tell us how you are feeling right now")
with col2:
    st.markdown("### Listen")
    st.write("Get music personalised to you")
with col3:
    st.markdown("### Track")
    st.write("See how music affects your mood over time")

st.divider()

st.markdown("#### How it works")
st.markdown("""
1. **Pick an emotion** — tell us how you feel
2. **Pick a context** — what are you doing right now?
3. **Set a goal** — what do you want music to do for you?
4. **Listen** — get a personalised playlist on Spotify
5. **Rate it** — tell us whether it helped
""")

st.divider()

if st.button("Get started →", use_container_width=True):
    st.switch_page("pages/1_Mood.py")

st.caption("Affective Computing project built with Python, Streamlit and the Spotify API")