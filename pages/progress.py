"""
pages/progress.py
--------------------
A polished, data-driven progress dashboard: English level, SpeakMate level,
XP, streaks, category scores, achievements summary, and simple charts.
"""

import streamlit as st

from utils.helpers import level_label
from utils.progress_manager import (
    get_profile,
    get_level_info,
    get_category_progress,
    get_overall_progress,
    get_achievements_status,
    CATEGORIES,
)

CATEGORY_LABELS = {
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "sentence_formation": "Sentence Formation",
    "communication": "Communication",
    "speaking": "Speaking",
    "interview": "Interview",
}


def render():
    st.markdown("## 📊 My Progress")
    profile = get_profile()
    level_info = get_level_info(profile.get("xp", 0))

    st.markdown(
        f"""
        <div class="sm-gradient-card">
            <h3 style="margin-bottom:0.2rem;">{level_label(profile.get('english_level'))} learner &nbsp;·&nbsp;
            SpeakMate Level {level_info['level_number']}: {level_info['level_name']}</h3>
            <p style="opacity:0.9; margin-bottom:0;">Keep practicing daily to grow your streak and XP!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⭐ Total XP", profile.get("xp", 0))
    c2.metric("🔥 Current Streak", f"{profile['streak'].get('current', 0)} days")
    c3.metric("🏅 Longest Streak", f"{profile['streak'].get('longest', 0)} days")
    total_activities = sum(profile["activity_counts"].values())
    c4.metric("✅ Total Activities", total_activities)

    st.markdown("### 📚 Category Scores")
    scores = {cat: get_category_progress(cat) for cat in CATEGORIES}
    chart_data = {CATEGORY_LABELS[c]: v for c, v in scores.items()}

    if any(v > 0 for v in chart_data.values()):
        st.bar_chart(chart_data)
    else:
        st.caption("Complete a few practice sessions to see your category chart here.")

    cols = st.columns(3)
    for i, cat in enumerate(CATEGORIES):
        with cols[i % 3]:
            st.markdown(f"**{CATEGORY_LABELS[cat]}**")
            st.progress(scores[cat] / 100, text=f"{scores[cat]}% · {profile['activity_counts'][cat]} activities")

    avg_practice = round(sum(scores.values()) / len(scores), 1) if scores else 0
    st.markdown("### 🎯 Average Practice Score")
    st.progress(avg_practice / 100, text=f"{avg_practice}% average across all categories")

    st.markdown("### 🔤 Vocabulary Progress")
    st.markdown(f"You have learned **{len(profile['learned_words'])} words** so far.")

    st.markdown("### 🏆 Achievements Summary")
    achievements = get_achievements_status()
    unlocked_count = sum(1 for a in achievements if a["unlocked"])
    st.progress(unlocked_count / len(achievements), text=f"{unlocked_count} / {len(achievements)} achievements unlocked")

    ac1, ac2 = st.columns(2)
    half = (len(achievements) + 1) // 2
    for i, a in enumerate(achievements):
        target = ac1 if i < half else ac2
        icon = "✅" if a["unlocked"] else "🔒"
        with target:
            st.markdown(f"{icon} **{a['name']}** — {a['desc']}")

    st.markdown("### 📈 Overall Progress")
    overall = get_overall_progress()
    st.progress(overall / 100, text=f"{overall}% overall progress across SpeakMate AI")
