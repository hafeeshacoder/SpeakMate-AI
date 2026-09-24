"""
app.py
--------
SpeakMate AI — main application entry point.

This file sets up the page configuration, injects the custom light-theme
CSS, initializes session state, renders a polished custom sidebar
navigation, and routes to the selected page module. No database is used;
all state lives in st.session_state and optional local JSON files.
"""

import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_ICON, NAV_SECTIONS
from utils.helpers import inject_custom_css, level_label
from utils.progress_manager import init_session_state, get_profile, get_level_info

from pages import (
    home,
    grammar,
    sentence_formation,
    vocabulary,
    communication,
    speaking,
    interview,
    nlp_analyzer,
    progress,
    achievements,
    settings,
)

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Initialize
# ----------------------------------------------------------------------
init_session_state()
inject_custom_css()

PAGE_MODULES = {
    "home": home,
    "grammar": grammar,
    "sentence_formation": sentence_formation,
    "vocabulary": vocabulary,
    "communication": communication,
    "speaking": speaking,
    "interview": interview,
    "nlp_analyzer": nlp_analyzer,
    "progress": progress,
    "achievements": achievements,
    "settings": settings,
}


def _render_sidebar():
    profile = get_profile()

    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                <div style="font-size:2.2rem;">🗣️</div>
                <div style="font-weight:700; font-size:1.2rem; color:#241E4E;">{APP_NAME}</div>
                <div style="font-size:0.78rem; color:#8B85B8;">{APP_TAGLINE}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if profile.get("onboarded"):
            level_info = get_level_info(profile.get("xp", 0))
            st.markdown(
                f"""
                <div class="sm-card" style="padding:0.9rem;">
                    <div style="font-weight:600;">{profile.get('name') or 'Learner'}</div>
                    <div style="font-size:0.8rem; color:#8B85B8;">{level_label(profile.get('english_level'))}</div>
                    <div style="font-size:0.8rem; color:#6C63FF; font-weight:600; margin-top:0.3rem;">
                        ⭐ {profile.get('xp', 0)} XP · Lvl {level_info['level_number']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        for key, label in NAV_SECTIONS:
            is_active = st.session_state.current_page == key
            btn_label = f"➤ {label}" if is_active else label
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("---")
        st.caption("No account needed. No database used. Your progress is stored locally in this browser session.")


def main():
    _render_sidebar()

    profile = get_profile()
    page_key = st.session_state.current_page

    # Force onboarding flow until the user has completed initial setup.
    if not profile.get("onboarded") and page_key != "home":
        st.session_state.current_page = "home"
        page_key = "home"

    module = PAGE_MODULES.get(page_key, home)
    try:
        module.render()
    except Exception as e:  # pragma: no cover — final safety net, never show a raw traceback
        st.error("Something went wrong while loading this page. Please try again or return to Home.")
        with st.expander("Technical details (for developers)"):
            st.code(str(e))
        if st.button("← Return to Home"):
            st.session_state.current_page = "home"
            st.rerun()


if __name__ == "__main__":
    main()
