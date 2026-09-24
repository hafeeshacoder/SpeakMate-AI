"""
pages/communication.py
-------------------------
Real-life communication practice across everyday and professional
scenarios. Users type a free-text response, which is analyzed locally
with NLP (grammar, vocabulary, sentence quality) and optionally enriched
with Groq-generated conversational feedback.
"""

import random
import streamlit as st

from config import COMMUNICATION_FILE
from utils.helpers import load_json_data, safe_ai_notice
from utils.progress_manager import get_profile, award_xp, record_category_score
from nlp.scoring import compute_practice_score
from ai.groq_client import is_configured, conversational_feedback


def _render_analysis(result):
    st.markdown("#### 🔍 NLP-Based Analysis")
    comp = result["components"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Grammar", f"{comp['grammar']}%")
    c2.metric("Vocabulary", f"{comp['vocabulary']}%")
    c3.metric("Sentence Quality", f"{comp['sentence_quality']}%")

    c4, c5 = st.columns(2)
    rel = comp["topic_relevance"]
    c4.metric("Topic Relevance", f"{rel}%" if rel is not None else "N/A")
    c5.metric("Fluency", f"{comp['fluency']}%")

    st.markdown(f"### 🏆 SpeakMate Practice Score: {result['overall']}%")
    st.caption("This is an application-specific learning score, not an official English proficiency score (e.g. IELTS/TOEFL/CEFR).")

    issues = result["grammar_issues"]
    if issues:
        st.markdown("**Grammar observations:**")
        for i in issues[:5]:
            st.markdown(f"- *{i['issue']}*: {i['suggestion']}")
    else:
        st.markdown("**Grammar observations:** No obvious issues detected. 👍")


def render():
    st.markdown("## 💬 Communication Practice")
    scenarios = load_json_data(COMMUNICATION_FILE, [])
    if not scenarios:
        st.warning("Communication scenario data could not be loaded.")
        return

    categories = sorted(set(s["category"] for s in scenarios))
    selected_cat = st.selectbox("Choose a scenario category", categories)
    cat_scenarios = [s for s in scenarios if s["category"] == selected_cat]

    if "comm_scenario_id" not in st.session_state or st.session_state.get("comm_last_cat") != selected_cat:
        st.session_state.comm_scenario_id = cat_scenarios[0]["id"]
        st.session_state.comm_last_cat = selected_cat

    scenario = next((s for s in cat_scenarios if s["id"] == st.session_state.comm_scenario_id), cat_scenarios[0])

    if st.button("🔀 New Scenario in this Category"):
        st.session_state.comm_scenario_id = random.choice(cat_scenarios)["id"]
        st.rerun()

    st.markdown(
        f"""
        <div class="sm-card">
            <span class="sm-badge">{scenario['category']}</span>
            <h4 style="margin-top:0.6rem;">{scenario['scenario']}</h4>
            <p><b>Suggested opening:</b> {scenario['suggested_opening']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("💡 Useful phrases for this situation"):
        for p in scenario["useful_phrases"]:
            st.markdown(f"- {p}")

    st.markdown(f"**Practice prompt:** {scenario['practice_prompt']}")
    user_response = st.text_area("Type your response:", height=120, key=f"comm_input_{scenario['id']}")

    if st.button("Analyze My Response", disabled=(not user_response.strip())):
        result = compute_practice_score(user_response, reference_text=scenario["scenario"] + " " + scenario["practice_prompt"])
        st.session_state["comm_last_result"] = result
        st.session_state["comm_last_response"] = user_response
        record_category_score("communication", result["overall"])
        xp = award_xp("communication", unique_key=f"comm_{scenario['id']}_{random.random()}")
        if xp:
            st.toast(f"+{xp} XP earned!", icon="🎉")

    if st.session_state.get("comm_last_result"):
        _render_analysis(st.session_state["comm_last_result"])

        with st.expander("📖 See an example response"):
            st.write(scenario["example_response"])

        st.markdown("#### 🤖 AI Feedback (optional)")
        if not is_configured():
            safe_ai_notice()
        else:
            if st.button("Get AI Feedback"):
                with st.spinner("Getting personalized feedback..."):
                    feedback = conversational_feedback(scenario["scenario"], st.session_state["comm_last_response"])
                st.markdown(feedback)
