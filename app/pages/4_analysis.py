"""
Analysis page.

Loads all saved sessions and visualises the relationship between emotions,
contexts, goals, and user ratings. Provides a minimal but meaningful picture
of how music affected the user's mood over time.
"""

import streamlit as st
import plotly.express as px
from core.data_store import load_sessions

st.set_page_config(
    page_title="MoodMusic - Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("## Your mood music history")

df = load_sessions()

if df.empty:
    st.info("No sessions recorded yet. Complete a listening session and come back here.")
    if st.button("Start a session"):
        st.switch_page("pages/1_mood.py")
    st.stop()

# Summary metrics
total = len(df)
avg_rating = df["rating"].mean()
best_emotion = df.groupby("emotion_label")["rating"].mean().idxmax()
best_context = df.groupby("context_label")["rating"].mean().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sessions", total)
col2.metric("Average rating", f"{avg_rating:.1f} / 5")
col3.metric("Best emotion", best_emotion)
col4.metric("Best context", best_context)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Average rating by emotion")
    emotion_avg = df.groupby("emotion_label")["rating"].mean().reset_index()
    emotion_avg.columns = ["Emotion", "Average rating"]
    fig1 = px.bar(
        emotion_avg,
        x="Emotion",
        y="Average rating",
        color="Average rating",
        color_continuous_scale="Greens",
        range_y=[0, 5],
    )
    fig1.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.markdown("#### Average rating by context")
    context_avg = df.groupby("context_label")["rating"].mean().reset_index()
    context_avg.columns = ["Context", "Average rating"]
    fig2 = px.bar(
        context_avg,
        x="Context",
        y="Average rating",
        color="Average rating",
        color_continuous_scale="Blues",
        range_y=[0, 5],
    )
    fig2.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.markdown("#### Rating by mood goal")
goal_avg = df.groupby("mood_goal")["rating"].mean().reset_index()
goal_avg.columns = ["Goal", "Average rating"]
fig3 = px.bar(
    goal_avg,
    x="Goal",
    y="Average rating",
    color="Average rating",
    color_continuous_scale="Purples",
    range_y=[0, 5],
)
fig3.update_layout(coloraxis_showscale=False, margin=dict(t=20, b=20))
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.markdown("#### Rating over time")
fig4 = px.scatter(
    df,
    x="timestamp",
    y="rating",
    color="emotion_label",
    hover_data=["context_label", "mood_goal"],
    range_y=[0, 5],
)
fig4.update_layout(margin=dict(t=20, b=20))
st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.markdown("#### All sessions")
display_cols = ["timestamp", "emotion_label", "context_label", "mood_goal", "rating", "tracks_played"]
st.dataframe(df[display_cols].sort_values("timestamp", ascending=False), use_container_width=True)

if st.button("Start a new session", use_container_width=True, type="primary"):
    st.switch_page("pages/1_mood.py")