"""
pages/grammar.py
-------------------
Grammar learning/practice module: topic selection, MCQ practice with
instant feedback, explanations, XP, and score tracking.
"""

import random
import streamlit as st

from config import GRAMMAR_QUESTIONS_FILE, XP_RULES
from utils.helpers import load_json_data, difficulty_for_level
from utils.progress_manager import get_profile, award_xp, record_category_score

CATEGORY_ORDER = ["Foundation", "Tenses", "Other Grammar"]


def _get_questions():
    return load_json_data(GRAMMAR_QUESTIONS_FILE, [])


def _init_quiz(topic, questions):
    qs = list(questions)
    random.shuffle(qs)
    qs = qs[:10]
    st.session_state.quiz_state["grammar"] = {
        "topic": topic,
        "questions": qs,
        "index": 0,
        "score": 0,
        "answered": False,
        "selected": None,
        "finished": False,
    }


def _render_topic_picker(all_questions):
    profile = get_profile()
    preferred = set(difficulty_for_level(profile.get("english_level")))

    topics = {}
    for q in all_questions:
        topics.setdefault(q["category"], {}).setdefault(q["topic"], []).append(q)

    st.markdown("### 📝 Choose a Grammar Topic")
    st.caption("All topics are always open. Suggested topics are highlighted based on your level, but you can practice anything.")

    for cat in CATEGORY_ORDER:
        if cat not in topics:
            continue
        with st.expander(f"**{cat}**", expanded=(cat == "Foundation")):
            topic_names = sorted(topics[cat].keys())
            cols = st.columns(3)
            for i, tname in enumerate(topic_names):
                qs = topics[cat][tname]
                suggested = any(q["difficulty"] in preferred for q in qs)
                with cols[i % 3]:
                    label = f"⭐ {tname}" if suggested else tname
                    if st.button(f"{label} ({len(qs)} Qs)", key=f"topic_{cat}_{tname}", use_container_width=True):
                        _init_quiz(tname, qs)
                        st.rerun()


def _render_quiz():
    state = st.session_state.quiz_state["grammar"]
    questions = state["questions"]

    if state["finished"]:
        st.markdown(f"## 🎉 Practice Complete: {state['topic']}")
        pct = round((state["score"] / len(questions)) * 100) if questions else 0
        st.markdown(
            f"""
            <div class="sm-gradient-card">
                <h2>Your Score: {state['score']} / {len(questions)} ({pct}%)</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        record_category_score("grammar", pct)
        xp = award_xp("grammar", unique_key=f"grammar_{state['topic']}_{len(questions)}_{state['score']}_{random.random()}")
        if xp:
            st.success(f"You earned +{xp} XP! 🎉")
        c1, c2 = st.columns(2)
        if c1.button("Practice Another Topic"):
            del st.session_state.quiz_state["grammar"]
            st.rerun()
        if c2.button("Retry This Topic"):
            _init_quiz(state["topic"], questions)
            st.rerun()
        return

    idx = state["index"]
    q = questions[idx]

    st.markdown(f"#### {state['topic']} &nbsp;·&nbsp; Question {idx + 1} of {len(questions)}")
    st.progress((idx) / len(questions))
    st.markdown(f"<div class='sm-card'><h4>{q['question']}</h4></div>", unsafe_allow_html=True)

    if not state["answered"]:
        choice = st.radio("Choose your answer:", q["options"], key=f"grammar_choice_{idx}", index=None)
        if st.button("Submit Answer", disabled=(choice is None)):
            state["selected"] = choice
            state["answered"] = True
            if choice == q["correct_answer"]:
                state["score"] += 1
            st.rerun()
    else:
        is_correct = state["selected"] == q["correct_answer"]
        if is_correct:
            st.markdown("<span class='sm-pill sm-pill-correct'>✓ Correct</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='sm-pill sm-pill-wrong'>✗ Incorrect</span>", unsafe_allow_html=True)
            st.markdown(f"Your answer: *{state['selected']}*")
            st.markdown(f"Correct answer: **{q['correct_answer']}**")
        st.info(f"💡 {q['explanation']}")

        if st.button("Next Question ▶"):
            state["index"] += 1
            state["answered"] = False
            state["selected"] = None
            if state["index"] >= len(questions):
                state["finished"] = True
            st.rerun()


def render():
    st.markdown("## 📝 Grammar Practice")
    all_questions = _get_questions()

    if not all_questions:
        st.warning("Grammar question data could not be loaded. Please check the data files.")
        return

    if "grammar" in st.session_state.quiz_state:
        _render_quiz()
        st.markdown("---")
        if st.button("← Back to Topics"):
            del st.session_state.quiz_state["grammar"]
            st.rerun()
    else:
        _render_topic_picker(all_questions)
