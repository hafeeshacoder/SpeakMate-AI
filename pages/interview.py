"""
pages/interview.py
---------------------
Interview preparation: HR questions and Technical Communication topics.
Free-text answers are analyzed with local NLP for grammar, vocabulary,
sentence quality, and relevance, with an optional Groq-generated
follow-up question for realistic practice.
"""

import random
import streamlit as st

from config import INTERVIEW_FILE
from utils.helpers import load_json_data, safe_ai_notice
from utils.progress_manager import award_xp, record_category_score
from nlp.scoring import compute_practice_score
from ai.groq_client import is_configured, interview_followup


def _render_analysis(result):
    comp = result["components"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Grammar", f"{comp['grammar']}%")
    c2.metric("Vocabulary", f"{comp['vocabulary']}%")
    c3.metric("Sentence Quality", f"{comp['sentence_quality']}%")

    c4, c5 = st.columns(2)
    rel = comp["topic_relevance"]
    c4.metric("Relevance", f"{rel}%" if rel is not None else "N/A")
    c5.metric("Fluency", f"{comp['fluency']}%")

    st.markdown(f"### 💼 Overall Practice Score: {result['overall']}%")
    st.caption("This is an application-specific practice score, not an official assessment.")

    issues = result["grammar_issues"]
    if issues:
        st.markdown("**Suggested improvements:**")
        for i in issues[:5]:
            st.markdown(f"- *{i['issue']}*: {i['suggestion']}")

    st.markdown("**Suggested answer structure:** Situation/Context → Action you took → Result/Outcome → What you learned (the STAR method works well for most behavioral questions).")


def render():
    st.markdown("## 💼 Interview Preparation")
    data = load_json_data(INTERVIEW_FILE, {"hr_questions": [], "technical_topics": []})
    hr_questions = data.get("hr_questions", [])
    tech_topics = data.get("technical_topics", [])

    tab1, tab2 = st.tabs(["🧑‍💼 HR Interview", "💻 Technical Communication"])

    with tab1:
        if not hr_questions:
            st.warning("HR question data could not be loaded.")
        else:
            if "hr_q_id" not in st.session_state:
                st.session_state.hr_q_id = hr_questions[0]["id"]
            question = next(q for q in hr_questions if q["id"] == st.session_state.hr_q_id)

            if st.button("🔀 New HR Question"):
                st.session_state.hr_q_id = random.choice(hr_questions)["id"]
                st.rerun()

            st.markdown(f"<div class='sm-card'><span class='sm-badge'>HR</span><h4 style='margin-top:0.6rem;'>{question['question']}</h4></div>", unsafe_allow_html=True)
            answer = st.text_area("Your answer:", height=140, key=f"hr_answer_{question['id']}")

            if st.button("Analyze My Answer", key="hr_analyze", disabled=(not answer.strip())):
                result = compute_practice_score(answer, reference_text=question["question"])
                st.session_state["hr_last_result"] = result
                st.session_state["hr_last_answer"] = answer
                record_category_score("interview", result["overall"])
                xp = award_xp("interview", unique_key=f"hr_{question['id']}_{random.random()}")
                if xp:
                    st.toast(f"+{xp} XP earned!", icon="🎉")

            if st.session_state.get("hr_last_result"):
                _render_analysis(st.session_state["hr_last_result"])
                st.markdown("#### 🤖 AI Interview Coach (optional)")
                if not is_configured():
                    safe_ai_notice()
                else:
                    if st.button("Get AI Feedback + Follow-up Question", key="hr_ai"):
                        with st.spinner("Reviewing your answer..."):
                            fb = interview_followup(question["question"], st.session_state["hr_last_answer"])
                        st.markdown(fb)

    with tab2:
        if not tech_topics:
            st.warning("Technical topic data could not be loaded.")
        else:
            if "tech_t_id" not in st.session_state:
                st.session_state.tech_t_id = tech_topics[0]["id"]
            topic = next(t for t in tech_topics if t["id"] == st.session_state.tech_t_id)

            if st.button("🔀 New Technical Topic"):
                st.session_state.tech_t_id = random.choice(tech_topics)["id"]
                st.rerun()

            st.markdown(f"<div class='sm-card'><span class='sm-badge'>{topic['topic']}</span><h4 style='margin-top:0.6rem;'>{topic['prompt']}</h4></div>", unsafe_allow_html=True)
            answer = st.text_area("Your answer:", height=140, key=f"tech_answer_{topic['id']}")

            if st.button("Analyze My Answer", key="tech_analyze", disabled=(not answer.strip())):
                result = compute_practice_score(answer, reference_text=topic["topic"] + " " + topic["prompt"])
                st.session_state["tech_last_result"] = result
                st.session_state["tech_last_answer"] = answer
                record_category_score("interview", result["overall"])
                xp = award_xp("interview", unique_key=f"tech_{topic['id']}_{random.random()}")
                if xp:
                    st.toast(f"+{xp} XP earned!", icon="🎉")

            if st.session_state.get("tech_last_result"):
                _render_analysis(st.session_state["tech_last_result"])
                st.markdown("#### 🤖 AI Interview Coach (optional)")
                if not is_configured():
                    safe_ai_notice()
                else:
                    if st.button("Get AI Feedback + Follow-up Question", key="tech_ai"):
                        with st.spinner("Reviewing your answer..."):
                            fb = interview_followup(topic["prompt"], st.session_state["tech_last_answer"])
                        st.markdown(fb)
