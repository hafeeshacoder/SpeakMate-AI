"""
pages/home.py
---------------
Welcome/onboarding screen (first-time users) and the main Home Dashboard
(returning users). Levels never lock features — they only personalize
recommendations.
"""

from datetime import datetime

import streamlit as st

from config import ENGLISH_LEVELS, LEARNING_GOALS, DAILY_GOAL_OPTIONS, APP_NAME, APP_TAGLINE
from utils.progress_manager import (
    get_profile,
    persist,
    get_level_info,
    get_category_progress,
    get_overall_progress,
    get_weakest_category,
    CATEGORIES,
    load_history,
)
from utils.helpers import level_label

CATEGORY_LABELS = {
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "sentence_formation": "Sentence Formation",
    "communication": "Communication",
    "speaking": "Speaking",
    "interview": "Interview",
}

RECOMMENDATIONS = {
    "grammar": ("Practice Subject-Verb Agreement", "grammar"),
    "vocabulary": ("Learn 5 new Workplace words", "vocabulary"),
    "sentence_formation": ("Try 3 sentence-building exercises", "sentence_formation"),
    "communication": ("Practice a Self Introduction scenario", "communication"),
    "speaking": ("Record a response to 'Tell me about yourself'", "speaking"),
    "interview": ("Answer a common HR interview question", "interview"),
}


def _render_welcome_screen():
    st.markdown(
        f"""
        <div style="text-align:center; padding: 2.5rem 1rem 1rem 1rem;">
            <div style="font-size: 3.2rem;">🗣️</div>
            <h1 style="font-size:2.4rem; margin-bottom:0.2rem;">{APP_NAME}</h1>
            <p style="font-size:1.15rem; color:#6C63FF; font-weight:600;">{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3 style='text-align:center;'>What is your current English level?</h3>", unsafe_allow_html=True)
    st.caption(
        "This only personalizes your experience — every feature stays fully open at any level."
    )

    profile = get_profile()
    selected = profile.get("english_level")

    cols = st.columns(5)
    for i, lvl in enumerate(ENGLISH_LEVELS):
        with cols[i]:
            is_selected = selected == lvl["key"]
            border = "3px solid #6C63FF" if is_selected else "1px solid rgba(108,99,255,0.15)"
            st.markdown(
                f"""
                <div class="sm-card" style="text-align:center; border:{border}; min-height:150px;">
                    <div style="font-size:2rem;">{lvl['icon']}</div>
                    <div style="font-weight:700; margin-top:0.3rem;">{lvl['label']}</div>
                    <div style="font-size:0.8rem; color:#8B85B8; margin-top:0.3rem;">{lvl['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select" if not is_selected else "✓ Selected", key=f"lvl_{lvl['key']}", use_container_width=True):
                profile["english_level"] = lvl["key"]
                persist()
                st.rerun()

    st.markdown("---")

    if profile.get("english_level"):
        with st.form("onboarding_form"):
            st.markdown("#### Tell us a little more (all optional)")
            name = st.text_input("Your name (optional)", value=profile.get("name", ""))
            goal = st.selectbox(
                "What is your main learning goal?",
                LEARNING_GOALS,
                index=LEARNING_GOALS.index(profile["learning_goal"]) if profile.get("learning_goal") in LEARNING_GOALS else 0,
            )
            daily_goal = st.select_slider(
                "Daily learning goal (minutes)",
                options=DAILY_GOAL_OPTIONS,
                value=profile.get("daily_goal_minutes", 15),
            )
            submitted = st.form_submit_button("Start Learning 🚀", use_container_width=True)
            if submitted:
                profile["name"] = name.strip()
                profile["learning_goal"] = goal
                profile["daily_goal_minutes"] = daily_goal
                profile["onboarded"] = True
                persist()
                st.session_state.current_page = "home"
                st.rerun()


def _greeting():
    profile = get_profile()
    name = profile.get("name", "").strip()
    hour = datetime.now().hour
    if 5 <= hour < 12:
        time_greet = "Good Morning"
    elif 12 <= hour < 17:
        time_greet = "Good Afternoon"
    else:
        time_greet = "Good Evening"
    if name:
        return f"{time_greet}, {name} 👋"
    return "Welcome to SpeakMate AI 👋"


def _render_dashboard():
    profile = get_profile()
    level_info = get_level_info(profile.get("xp", 0))

    st.markdown(
        f"""
        <div class="sm-gradient-card">
            <h2 style="margin-bottom:0.1rem;">{_greeting()}</h2>
            <p style="opacity:0.95;">Level: {level_label(profile.get('english_level'))} &nbsp;•&nbsp;
            Goal: {profile.get('learning_goal') or 'Overall English'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⭐ XP", profile.get("xp", 0))
    c2.metric("🏆 SpeakMate Level", f"{level_info['level_number']}. {level_info['level_name']}")
    c3.metric("🔥 Streak", f"{profile['streak'].get('current', 0)} days")
    dg = profile.get("daily_goal", {})
    c4.metric("🎯 Daily Goal", f"{min(dg.get('minutes_completed', 0), profile.get('daily_goal_minutes', 15))}/{profile.get('daily_goal_minutes', 15)} min")

    if level_info["next_level_name"]:
        st.progress(level_info["progress_fraction"], text=f"{level_info['xp_needed_for_next']} XP to reach '{level_info['next_level_name']}'")
    else:
        st.progress(1.0, text="🏆 Maximum SpeakMate level reached!")

    st.markdown("### 📊 Overall Progress")
    overall = get_overall_progress()
    st.progress(overall / 100, text=f"{overall}% overall progress")

    st.markdown("### 📚 Category Progress")
    cols = st.columns(3)
    for i, cat in enumerate(CATEGORIES):
        val = get_category_progress(cat)
        with cols[i % 3]:
            st.markdown(f"**{CATEGORY_LABELS[cat]}**")
            st.progress(val / 100, text=f"{val}%")

    st.markdown("### 💡 Today's Recommendation")
    weakest = get_weakest_category()
    rec_text, rec_page = RECOMMENDATIONS.get(weakest, RECOMMENDATIONS["grammar"])
    st.markdown(
        f"""
        <div class="sm-card">
            <span class="sm-badge">Based on your progress in {CATEGORY_LABELS.get(weakest, 'Grammar')}</span>
            <h4 style="margin-top:0.6rem;">{rec_text}</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Start Practice ▶", key="start_recommendation"):
        st.session_state.current_page = rec_page
        st.rerun()

    st.markdown("### 🕘 Recent Activity")
    history = load_history()
    if not history:
        st.caption("No activity yet — complete a practice session to see your history here.")
    else:
        for event in reversed(history[-6:]):
            cat = event.get("category", "activity")
            amt = event.get("amount", 0)
            ts = event.get("timestamp", "")
            st.markdown(f"- Earned **+{amt} XP** in *{CATEGORY_LABELS.get(cat, cat)}* — `{ts}`")


def render():
    profile = get_profile()
    if not profile.get("onboarded"):
        _render_welcome_screen()
    else:
        _render_dashboard()
