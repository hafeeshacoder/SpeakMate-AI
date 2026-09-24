"""
pages/sentence_formation.py
------------------------------
Practical sentence formation exercises: word arranging, sentence correction,
positive/negative conversion, statement/question conversion, tense change,
sentence completion, and situation-based sentence creation. Free-text
answers are compared using local NLP (similarity + basic normalization).
"""

import random
import re
import streamlit as st

from config import SENTENCE_QUESTIONS_FILE
from utils.helpers import load_json_data
from utils.progress_manager import get_profile, award_xp, record_category_score
from nlp.similarity import compute_similarity

TYPE_LABELS = {
    "arrange_words": "🧩 Arrange the Words",
    "correct_sentence": "✏️ Correct the Sentence",
    "positive_to_negative": "🔄 Positive → Negative",
    "statement_to_question": "❓ Statement → Question",
    "change_tense": "⏳ Change the Tense",
    "complete_sentence": "🧠 Complete the Sentence",
    "situation_based": "💬 Situation-Based Sentence",
}


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[.!?]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _evaluate_answer(exercise, user_answer: str):
    """Return (is_correct: bool or None, similarity: float or None, feedback: str)."""
    ans_type = exercise["type"]
    correct = exercise["answer"]

    if ans_type == "situation_based":
        sim = compute_similarity(user_answer, correct)
        return None, sim, "Situation-based answers can vary — compare your response with the example below."

    normalized_user = _normalize(user_answer)
    normalized_correct = _normalize(correct)
    exact = normalized_user == normalized_correct
    sim = compute_similarity(user_answer, correct)
    return exact, sim, ""


def _init_practice(exercises):
    ex = list(exercises)
    random.shuffle(ex)
    ex = ex[:10]
    st.session_state.quiz_state["sentence"] = {
        "exercises": ex,
        "index": 0,
        "score": 0,
        "answered": False,
        "user_answer": "",
        "finished": False,
    }


def _render_type_picker(all_exercises):
    st.markdown("### 🧩 Choose an Exercise Type")
    st.caption("All exercise types are always available to every level.")

    by_type = {}
    for ex in all_exercises:
        by_type.setdefault(ex["type"], []).append(ex)

    cols = st.columns(3)
    for i, (t, label) in enumerate(TYPE_LABELS.items()):
        exs = by_type.get(t, [])
        with cols[i % 3]:
            st.markdown(f"<div class='sm-card' style='text-align:center;'><h4>{label}</h4><p>{len(exs)} exercises</p></div>", unsafe_allow_html=True)
            if st.button("Practice", key=f"sf_{t}", use_container_width=True, disabled=(len(exs) == 0)):
                _init_practice(exs)
                st.rerun()

    st.markdown("---")
    if st.button("🎲 Mixed Practice (All Types)"):
        _init_practice(all_exercises)
        st.rerun()


def _render_exercise_prompt(ex):
    if ex["type"] == "arrange_words":
        words = ex["data"]["words"]
        st.markdown(f"<div class='sm-card'><b>Arrange these words into a correct sentence:</b><br><br>"
                     + " &nbsp;|&nbsp; ".join(f"<span class='sm-badge'>{w}</span>" for w in words)
                     + "</div>", unsafe_allow_html=True)
    elif ex["type"] == "correct_sentence":
        st.markdown(f"<div class='sm-card'><b>Find and correct the mistake:</b><br><br>❌ {ex['data']['incorrect']}</div>", unsafe_allow_html=True)
    elif ex["type"] == "positive_to_negative":
        st.markdown(f"<div class='sm-card'><b>Convert to negative form:</b><br><br>{ex['data']['positive']}</div>", unsafe_allow_html=True)
    elif ex["type"] == "statement_to_question":
        st.markdown(f"<div class='sm-card'><b>Convert this statement into a question:</b><br><br>{ex['data']['statement']}</div>", unsafe_allow_html=True)
    elif ex["type"] == "change_tense":
        target = ex["data"]["target_tense"].replace("_", " ")
        st.markdown(f"<div class='sm-card'><b>Rewrite in the {target} tense:</b><br><br>{ex['data']['original']}</div>", unsafe_allow_html=True)
    elif ex["type"] == "complete_sentence":
        st.markdown(f"<div class='sm-card'><b>Complete the sentence:</b><br><br>{ex['data']['sentence']}</div>", unsafe_allow_html=True)
    elif ex["type"] == "situation_based":
        st.markdown(f"<div class='sm-card'><b>Situation:</b><br><br>{ex['prompt']}</div>", unsafe_allow_html=True)


def _render_practice():
    state = st.session_state.quiz_state["sentence"]
    exercises = state["exercises"]

    if state["finished"]:
        st.markdown("## 🎉 Sentence Formation Complete")
        pct = round((state["score"] / len(exercises)) * 100) if exercises else 0
        st.markdown(f"<div class='sm-gradient-card'><h2>Score: {state['score']} / {len(exercises)} ({pct}%)</h2></div>", unsafe_allow_html=True)
        record_category_score("sentence_formation", pct)
        xp = award_xp("sentence_formation", unique_key=f"sf_{len(exercises)}_{state['score']}_{random.random()}")
        if xp:
            st.success(f"You earned +{xp} XP! 🎉")
        if st.button("Practice Again"):
            del st.session_state.quiz_state["sentence"]
            st.rerun()
        return

    idx = state["index"]
    ex = exercises[idx]

    st.markdown(f"#### {TYPE_LABELS[ex['type']]} &nbsp;·&nbsp; {idx + 1} of {len(exercises)}")
    st.progress(idx / len(exercises))
    _render_exercise_prompt(ex)

    if not state["answered"]:
        user_answer = st.text_area("Your answer:", key=f"sf_input_{idx}", height=80)
        if st.button("Submit", disabled=(not user_answer.strip())):
            exact, sim, note = _evaluate_answer(ex, user_answer)
            state["user_answer"] = user_answer
            state["answered"] = True
            state["last_exact"] = exact
            state["last_similarity"] = sim
            if exact is True or (exact is None and sim is not None and sim >= 55):
                state["score"] += 1
            st.rerun()
    else:
        exact = state.get("last_exact")
        sim = state.get("last_similarity")
        if exact is True:
            st.markdown("<span class='sm-pill sm-pill-correct'>✓ Correct</span>", unsafe_allow_html=True)
        elif exact is False:
            st.markdown("<span class='sm-pill sm-pill-wrong'>✗ Not an exact match</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='sm-pill sm-pill-info'>Open-ended — compare with the example</span>", unsafe_allow_html=True)

        if sim is not None:
            st.caption(f"NLP similarity to model answer: {sim}%")

        st.markdown(f"**Model answer:** {ex['answer']}")
        st.info(f"💡 {ex['explanation']}")

        if st.button("Next ▶"):
            state["index"] += 1
            state["answered"] = False
            if state["index"] >= len(exercises):
                state["finished"] = True
            st.rerun()


def render():
    st.markdown("## 🧩 Sentence Formation")
    all_exercises = load_json_data(SENTENCE_QUESTIONS_FILE, [])

    if not all_exercises:
        st.warning("Sentence formation data could not be loaded.")
        return

    if "sentence" in st.session_state.quiz_state:
        _render_practice()
        st.markdown("---")
        if st.button("← Back to Exercise Types"):
            del st.session_state.quiz_state["sentence"]
            st.rerun()
    else:
        _render_type_picker(all_exercises)
