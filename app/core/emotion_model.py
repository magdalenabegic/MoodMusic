"""
Maps emotions to the Russell Circumplex Model (valence–arousal space) and
translates them into Spotify audio feature targets.

Each emotion is defined by:
    valence — pleasantness (0.0 = negative, 1.0 = positive)
    arousal — activation level (0.0 = calm, 1.0 = excited)
    label — display name shown in the UI
    emoji — visual indicator in the UI
    color — card accent colour in the UI

Context (the user's current activity) modifies the audio feature targets sent
to Spotify without changing the emotion itself — the emotion is subjective,
the context is an objective filter on the recommendation.

Spotify Audio Features used:
    valence — musical positiveness (0.0–1.0)
    energy — intensity and activity (0.0–1.0)
    tempo — beats per minute
    danceability — suitability for dancing (0.0–1.0)
    acousticness — acoustic confidence (0.0–1.0)
"""

from dataclasses import dataclass


@dataclass
class Emotion:
    key: str
    label: str
    emoji: str
    valence: float  # 0.0 (negative) = 1.0 (positive)
    arousal: float  # 0.0 (calm) = 1.0 (excited)
    color: str      # hex accent colour for the UI


# Emotion catalogue mapped onto the Russell Circumplex quadrants:
#
#   high arousal + high valence = excited, happy (top-right)
#   high arousal + low valence = angry, anxious (top-left)
#   low arousal + high valence = calm, content (bottom-right)
#   low arousal + low valence = sad, tired (bottom-left)

EMOTIONS: dict[str, Emotion] = {
    "happy": Emotion(
        key="happy", label="Happy", emoji="😊",
        valence=0.85, arousal=0.70, color="#F6C90E"
    ),
    "excited": Emotion(
        key="excited", label="Excited", emoji="🤩",
        valence=0.90, arousal=0.90, color="#FF6B6B"
    ),
    "calm": Emotion(
        key="calm", label="Calm", emoji="😌",
        valence=0.65, arousal=0.20, color="#74C0FC"
    ),
    "sad": Emotion(
        key="sad", label="Sad", emoji="😢",
        valence=0.20, arousal=0.25, color="#9B8EC4"
    ),
    "anxious": Emotion(
        key="anxious", label="Anxious", emoji="😰",
        valence=0.25, arousal=0.75, color="#FFA94D"
    ),
    "angry": Emotion(
        key="angry", label="Angry", emoji="😤",
        valence=0.15, arousal=0.85, color="#FF4757"
    ),
    "romantic": Emotion(
        key="romantic", label="Romantic", emoji="🥰",
        valence=0.80, arousal=0.45, color="#F783AC"
    ),
    "focused": Emotion(
        key="focused", label="Focused", emoji="🎯",
        valence=0.55, arousal=0.55, color="#63E6BE"
    ),
    "tired": Emotion(
        key="tired", label="Tired", emoji="😴",
        valence=0.35, arousal=0.10, color="#A9A9A9"
    ),
    "nostalgic": Emotion(
        key="nostalgic", label="Nostalgic", emoji="🌅",
        valence=0.50, arousal=0.30, color="#FFB347"
    ),
}


@dataclass
class Context:
    key: str
    label: str
    emoji: str
    energy_mod: float
    tempo_mod: float
    acousticness_mod: float
    danceability_mod: float


CONTEXTS: dict[str, Context] = {
    "cooking": Context(
        key="cooking", label="Cooking", emoji="🍳",
        energy_mod=0.05, tempo_mod=5, acousticness_mod=0.10, danceability_mod=0.05
    ),
    "working": Context(
        key="working", label="Working / Studying", emoji="💻",
        energy_mod=-0.10, tempo_mod=-10, acousticness_mod=0.15, danceability_mod=-0.15
    ),
    "working_out": Context(
        key="working_out", label="Working Out", emoji="🏋️",
        energy_mod=0.20, tempo_mod=20, acousticness_mod=-0.20, danceability_mod=0.10
    ),
    "driving": Context(
        key="driving", label="Driving", emoji="🚗",
        energy_mod=0.10, tempo_mod=10, acousticness_mod=-0.05, danceability_mod=0.05
    ),
    "relaxing": Context(
        key="relaxing", label="Relaxing", emoji="🛋️",
        energy_mod=-0.15, tempo_mod=-15, acousticness_mod=0.20, danceability_mod=-0.10
    ),
    "dancing": Context(
        key="dancing", label="Dancing", emoji="💃",
        energy_mod=0.15, tempo_mod=15, acousticness_mod=-0.15, danceability_mod=0.25
    ),
    "sleeping": Context(
        key="sleeping", label="Falling Asleep", emoji="🌙",
        energy_mod=-0.30, tempo_mod=-30, acousticness_mod=0.35, danceability_mod=-0.30
    ),
    "socializing": Context(
        key="socializing", label="Socializing", emoji="🎉",
        energy_mod=0.10, tempo_mod=10, acousticness_mod=-0.10, danceability_mod=0.15
    ),
}


def get_spotify_params(emotion_key: str, context_key: str) -> dict:
    """
    Combine an emotion and a context into Spotify recommendation parameters.

    Arousal maps directly to energy; tempo is derived as 60 + arousal * 100 BPM.
    Context offsets are added on top and the result is clamped to valid ranges.

    Args:
        emotion_key: key from the EMOTIONS dict.
        context_key: key from the CONTEXTS dict.

    Returns:
        Dict of Spotify audio feature target parameters.
    """
    emotion = EMOTIONS[emotion_key]
    context = CONTEXTS[context_key]

    def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, val))

    base_energy = emotion.arousal
    base_tempo = 60 + emotion.arousal * 100  # range: 60–160 BPM

    return {
        "target_valence": clamp(emotion.valence),
        "target_energy": clamp(base_energy + context.energy_mod),
        "target_tempo": max(40, base_tempo + context.tempo_mod),
        "target_danceability": clamp(0.5 + context.danceability_mod),
        "target_acousticness": clamp(0.5 + context.acousticness_mod),
    }