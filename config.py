"""
config.py
---------
Central configuration and constants for SpeakMate AI.
No database, no secrets stored here. Only static configuration values.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------
# App Meta
# ----------------------------------------------------------------------
APP_NAME = "SpeakMate AI"
APP_TAGLINE = "Your Personal AI English Learning & Communication Coach"
APP_ICON = "🗣️"

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

GRAMMAR_QUESTIONS_FILE = os.path.join(DATA_DIR, "grammar_questions.json")
SENTENCE_QUESTIONS_FILE = os.path.join(DATA_DIR, "sentence_questions.json")
VOCABULARY_FILE = os.path.join(DATA_DIR, "vocabulary.json")
COMMUNICATION_FILE = os.path.join(DATA_DIR, "communication_topics.json")
SPEAKING_FILE = os.path.join(DATA_DIR, "speaking_topics.json")
INTERVIEW_FILE = os.path.join(DATA_DIR, "interview_questions.json")

# ----------------------------------------------------------------------
# Groq API
# ----------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# ----------------------------------------------------------------------
# English Levels (never lock features — used only for personalization)
# ----------------------------------------------------------------------
ENGLISH_LEVELS = [
    {
        "key": "beginner",
        "label": "Beginner",
        "icon": "🌱",
        "description": "I know basic words and simple sentences.",
    },
    {
        "key": "elementary",
        "label": "Elementary",
        "icon": "🌿",
        "description": "I can form simple sentences and hold basic chats.",
    },
    {
        "key": "intermediate",
        "label": "Intermediate",
        "icon": "🌳",
        "description": "I can talk about daily life and studies fairly well.",
    },
    {
        "key": "upper_intermediate",
        "label": "Upper Intermediate",
        "icon": "⭐",
        "description": "I can discuss most topics with good fluency.",
    },
    {
        "key": "advanced",
        "label": "Advanced",
        "icon": "🏆",
        "description": "I speak confidently and communicate professionally.",
    },
]

# ----------------------------------------------------------------------
# Learning goals
# ----------------------------------------------------------------------
LEARNING_GOALS = [
    "Improve Grammar",
    "Speak Confidently",
    "Improve Vocabulary",
    "Daily Communication",
    "Interview Preparation",
    "Overall English",
]

DAILY_GOAL_OPTIONS = [10, 15, 20, 30]

# ----------------------------------------------------------------------
# XP rules
# ----------------------------------------------------------------------
XP_RULES = {
    "grammar": 15,
    "vocabulary": 10,
    "sentence_formation": 15,
    "communication": 20,
    "speaking": 25,
    "interview": 30,
    "daily_goal": 25,
}

# ----------------------------------------------------------------------
# Levels (gamification, unrelated to English level)
# ----------------------------------------------------------------------
SPEAKMATE_LEVELS = [
    (1, "First Steps", 0),
    (2, "Beginner Speaker", 100),
    (3, "Growing Speaker", 250),
    (4, "Clear Speaker", 450),
    (5, "Confident Speaker", 700),
    (6, "Conversation Builder", 1000),
    (7, "Speaking Pro", 1400),
    (8, "Advanced Speaker", 1900),
    (9, "Communication Expert", 2500),
    (10, "English Master", 3200),
]

# ----------------------------------------------------------------------
# Achievements
# ----------------------------------------------------------------------
ACHIEVEMENTS = [
    {"key": "first_practice", "name": "First Practice", "icon": "🏅",
     "desc": "Complete your very first practice activity."},
    {"key": "grammar_starter", "name": "Grammar Starter", "icon": "🏅",
     "desc": "Complete 5 grammar practice sessions."},
    {"key": "word_collector", "name": "Word Collector", "icon": "🏅",
     "desc": "Learn 20 vocabulary words."},
    {"key": "sentence_builder", "name": "Sentence Builder", "icon": "🏅",
     "desc": "Complete 10 sentence formation exercises."},
    {"key": "conversation_starter", "name": "Conversation Starter", "icon": "🏅",
     "desc": "Complete 5 communication scenarios."},
    {"key": "speaking_champion", "name": "Speaking Champion", "icon": "🏅",
     "desc": "Complete 10 speaking practice sessions."},
    {"key": "interview_ready", "name": "Interview Ready", "icon": "🏅",
     "desc": "Complete 10 interview practice answers."},
    {"key": "seven_day_speaker", "name": "7-Day Speaker", "icon": "🏅",
     "desc": "Reach a 7-day streak."},
    {"key": "daily_champion", "name": "Daily Champion", "icon": "🏅",
     "desc": "Meet your daily goal 5 times."},
    {"key": "consistency_star", "name": "Consistency Star", "icon": "🏅",
     "desc": "Complete 50 total activities."},
]

# ----------------------------------------------------------------------
# Scoring weights (SpeakMate Practice Score — NOT an official test score)
# ----------------------------------------------------------------------
SCORE_WEIGHTS = {
    "grammar": 0.30,
    "vocabulary": 0.20,
    "sentence_quality": 0.20,
    "topic_relevance": 0.20,
    "fluency": 0.10,
}

FILLER_WORDS = {
    "um", "uh", "like", "actually", "basically", "literally", "you know",
    "sort of", "kind of", "i mean", "well", "so", "right", "okay", "erm",
    "hmm", "just", "stuff", "things", "totally", "honestly",
}

NAV_SECTIONS = [
    ("home", "🏠 Home"),
    ("grammar", "📝 Grammar"),
    ("sentence_formation", "🧩 Sentence Formation"),
    ("vocabulary", "🔤 Vocabulary"),
    ("communication", "💬 Communication"),
    ("speaking", "🎤 Speaking Practice"),
    ("interview", "💼 Interview Preparation"),
    ("nlp_analyzer", "🧠 NLP Analyzer"),
    ("progress", "📊 My Progress"),
    ("achievements", "🏆 Achievements"),
    ("settings", "⚙️ Settings"),
]
