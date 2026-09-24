"""
utils/helpers.py
-------------------
Shared helper functions: safe JSON data loading, custom CSS injection,
and small reusable UI components used across pages.
"""

import json
import os
import streamlit as st

from config import ENGLISH_LEVELS


# ----------------------------------------------------------------------
# Safe data loading
# ----------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_json_data(path, default=None):
    """Load a JSON data file safely. Returns `default` ([] or {}) if missing/invalid."""
    if default is None:
        default = []
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except Exception:
        return default


def level_label(level_key: str) -> str:
    for lvl in ENGLISH_LEVELS:
        if lvl["key"] == level_key:
            return f"{lvl['icon']} {lvl['label']}"
    return "Not set"


def difficulty_for_level(level_key: str):
    """Map an English level to a preferred question difficulty (personalization only)."""
    mapping = {
        "beginner": ["beginner", "elementary"],
        "elementary": ["beginner", "elementary", "intermediate"],
        "intermediate": ["elementary", "intermediate", "upper_intermediate"],
        "upper_intermediate": ["intermediate", "upper_intermediate", "advanced"],
        "advanced": ["upper_intermediate", "advanced"],
    }
    return mapping.get(level_key, ["beginner", "elementary", "intermediate", "upper_intermediate", "advanced"])


# ----------------------------------------------------------------------
# Custom CSS (light theme, modern learning dashboard look)
# ----------------------------------------------------------------------
def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', 'Poppins', sans-serif;
        }

        .stApp {
            background: linear-gradient(180deg, #F7F6FD 0%, #F2F1FB 40%, #EFF3FC 100%);
        }

        h1, h2, h3, h4 {
            font-family: 'Poppins', sans-serif;
            color: #241E4E;
        }

        p, li, span, label, div {
            color: #2E2A4A;
        }

        /* Card container */
        .sm-card {
            background: #FFFFFF;
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 4px 20px rgba(99, 91, 255, 0.08);
            border: 1px solid rgba(99, 91, 255, 0.08);
            margin-bottom: 1rem;
        }

        .sm-gradient-card {
            background: linear-gradient(135deg, #6C63FF 0%, #7B7FFF 50%, #4FC3F7 100%);
            border-radius: 18px;
            padding: 1.6rem 1.8rem;
            color: white;
            box-shadow: 0 8px 24px rgba(108, 99, 255, 0.25);
            margin-bottom: 1rem;
        }
        .sm-gradient-card h1, .sm-gradient-card h2, .sm-gradient-card h3, .sm-gradient-card p {
            color: white !important;
        }

        .sm-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            background: #EDEBFF;
            color: #5A4FCF;
            font-weight: 600;
            font-size: 0.8rem;
            margin-right: 0.4rem;
        }

        .sm-metric-label {
            font-size: 0.85rem;
            color: #8B85B8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .sm-metric-value {
            font-size: 1.7rem;
            font-weight: 700;
            color: #241E4E;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #6C63FF, #4FC3F7);
            color: white;
            font-weight: 600;
            padding: 0.55rem 1.4rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 4px 14px rgba(108, 99, 255, 0.25);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(108, 99, 255, 0.35);
            color: white;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid rgba(108, 99, 255, 0.08);
        }
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            text-align: left;
            background: transparent;
            color: #3B3566;
            box-shadow: none;
            font-weight: 500;
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #F0EEFF;
            color: #5A4FCF;
            transform: none;
            box-shadow: none;
        }

        /* Progress bars */
        .stProgress > div > div {
            background: linear-gradient(90deg, #6C63FF, #4FC3F7);
            border-radius: 8px;
        }

        /* Metric widget */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 2px 10px rgba(99, 91, 255, 0.06);
        }

        hr {
            border-color: rgba(108, 99, 255, 0.12);
        }

        .sm-pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .sm-pill-correct { background: #E3F8EC; color: #1E8E5A; }
        .sm-pill-wrong { background: #FDEAEA; color: #C0392B; }
        .sm-pill-info { background: #EAF3FE; color: #2E6FCC; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="sm-gradient-card">
            <h2 style="margin-bottom:0.2rem;">{title}</h2>
            <p style="margin-bottom:0;opacity:0.95;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_ai_notice():
    """Consistent friendly notice shown whenever AI features are unavailable."""
    st.info("🤖 AI features are unavailable right now. Local NLP features are still fully available.", icon="ℹ️")
