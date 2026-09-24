"""
pages/achievements.py
------------------------
Displays all achievements with unlock status, based on real activity —
nothing is faked or pre-unlocked.
"""

import streamlit as st

from utils.progress_manager import get_achievements_status, get_profile


def render():
    st.markdown("## 🏆 Achievements")
    profile = get_profile()
    achievements = get_achievements_status()
    unlocked_count = sum(1 for a in achievements if a["unlocked"])

    st.markdown(
        f"""
        <div class="sm-gradient-card">
            <h3 style="margin-bottom:0.2rem;">{unlocked_count} / {len(achievements)} Achievements Unlocked</h3>
            <p style="opacity:0.9; margin-bottom:0;">Achievements unlock automatically as you practice across SpeakMate AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, a in enumerate(achievements):
        with cols[i % 3]:
            if a["unlocked"]:
                st.markdown(
                    f"""
                    <div class="sm-card" style="text-align:center; border: 2px solid #6C63FF;">
                        <div style="font-size:2.2rem;">{a['icon']}</div>
                        <div style="font-weight:700; margin-top:0.3rem;">{a['name']}</div>
                        <div style="font-size:0.85rem; color:#8B85B8; margin-top:0.3rem;">{a['desc']}</div>
                        <div class="sm-pill sm-pill-correct" style="margin-top:0.6rem;">Unlocked</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="sm-card" style="text-align:center; opacity:0.6;">
                        <div style="font-size:2.2rem;">🔒</div>
                        <div style="font-weight:700; margin-top:0.3rem;">{a['name']}</div>
                        <div style="font-size:0.85rem; color:#8B85B8; margin-top:0.3rem;">{a['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.write("")
