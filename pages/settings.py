"""
pages/settings.py
--------------------
Settings page: change name, English level, learning goal, daily goal,
and reset options. No authentication, no database — everything is
stored in st.session_state and data/progress.json.
"""

import streamlit as st

from config import ENGLISH_LEVELS, LEARNING_GOALS, DAILY_GOAL_OPTIONS, GROQ_API_KEY
from utils.progress_manager import get_profile, persist, reset_progress, reset_profile_full
from ai.groq_client import is_configured


def render():
    st.markdown("## ⚙️ Settings")
    profile = get_profile()

    st.markdown("### 👤 Profile")
    with st.form("settings_profile_form"):
        name = st.text_input("Your name", value=profile.get("name", ""))
        level_keys = [l["key"] for l in ENGLISH_LEVELS]
        level_labels = [f"{l['icon']} {l['label']}" for l in ENGLISH_LEVELS]
        current_level_idx = level_keys.index(profile["english_level"]) if profile.get("english_level") in level_keys else 0
        level_choice = st.selectbox("English level", level_labels, index=current_level_idx)

        goal_idx = LEARNING_GOALS.index(profile["learning_goal"]) if profile.get("learning_goal") in LEARNING_GOALS else 0
        goal = st.selectbox("Learning goal", LEARNING_GOALS, index=goal_idx)

        daily_goal = st.select_slider(
            "Daily learning goal (minutes)",
            options=DAILY_GOAL_OPTIONS,
            value=profile.get("daily_goal_minutes", 15),
        )

        submitted = st.form_submit_button("Save Changes 💾")
        if submitted:
            profile["name"] = name.strip()
            profile["english_level"] = level_keys[level_labels.index(level_choice)]
            profile["learning_goal"] = goal
            profile["daily_goal_minutes"] = daily_goal
            persist()
            st.success("Settings saved!")

    st.caption(
        "Note: your English level personalizes recommendations and suggested difficulty only — "
        "it never locks any feature. Every module remains open at every level."
    )

    st.markdown("---")
    st.markdown("### 🤖 AI Features")
    if is_configured():
        st.success("Groq API key detected — AI-powered feedback features are enabled.")
    else:
        st.info(
            "No Groq API key found. AI-powered feedback features are unavailable, but all local NLP "
            "features (grammar checking, scoring, vocabulary, analysis) work fully without it. "
            "Add a key to your `.env` file (see `.env.example`) to enable AI features."
        )

    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")

    with st.expander("Reset Progress (keep name/level/goal)"):
        st.warning("This will clear your XP, streaks, achievements, and scores — but keep your profile info.")
        confirm1 = st.checkbox("I understand this cannot be undone.", key="confirm_reset_progress")
        if st.button("Reset Progress", disabled=not confirm1):
            reset_progress(keep_profile_info=True)
            st.success("Progress has been reset.")
            st.rerun()

    with st.expander("Reset Entire Profile (start over completely)"):
        st.warning("This will erase everything, including your name, level, and all progress, and return you to the welcome screen.")
        confirm2 = st.checkbox("I understand this cannot be undone.", key="confirm_reset_profile")
        if st.button("Reset Entire Profile", disabled=not confirm2):
            reset_profile_full()
            st.success("Profile has been fully reset.")
            st.rerun()
