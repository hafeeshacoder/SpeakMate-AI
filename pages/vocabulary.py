"""
pages/vocabulary.py
----------------------
Vocabulary learning: word of the day, flashcards, multiple-choice quiz,
learned-word tracking, and category browsing.
"""

import random
from datetime import date

import streamlit as st

from config import VOCABULARY_FILE
from utils.helpers import load_json_data
from utils.progress_manager import get_profile, award_xp, record_category_score, learn_word


def _get_words():
    return load_json_data(VOCABULARY_FILE, [])


def _word_of_the_day(words):
    if not words:
        return None
    seed = int(date.today().strftime("%Y%m%d"))
    return words[seed % len(words)]


def _render_word_of_day(words):
    word = _word_of_the_day(words)
    if not word:
        return
    st.markdown("### 🌟 Word of the Day")
    st.markdown(
        f"""
        <div class="sm-gradient-card">
            <h2 style="margin-bottom:0.2rem;">{word['word'].capitalize()}</h2>
            <p style="opacity:0.95; margin-bottom:0.3rem;"><b>Meaning:</b> {word['meaning']}</p>
            <p style="opacity:0.95; margin-bottom:0.3rem;"><b>Example:</b> {word['example']}</p>
            <p style="opacity:0.95; margin-bottom:0;"><b>Synonym:</b> {word['synonym']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    profile = get_profile()
    already_learned = word["word"] in profile["learned_words"]
    if st.button("✓ Mark as Learned" if not already_learned else "✓ Learned", disabled=already_learned, key="wotd_learn"):
        learn_word(word["word"])
        award_xp("vocabulary", unique_key=f"wotd_{word['word']}")
        st.rerun()


def _render_flashcards(words):
    st.markdown("### 🃏 Flashcards")
    categories = sorted(set(w["category"] for w in words))
    cat = st.selectbox("Category", ["All"] + categories, key="fc_category")
    filtered = words if cat == "All" else [w for w in words if w["category"] == cat]

    if "fc_index" not in st.session_state:
        st.session_state.fc_index = 0
    if "fc_flipped" not in st.session_state:
        st.session_state.fc_flipped = False

    if not filtered:
        st.info("No words in this category yet.")
        return

    idx = st.session_state.fc_index % len(filtered)
    word = filtered[idx]

    if not st.session_state.fc_flipped:
        st.markdown(
            f"""<div class="sm-card" style="text-align:center; min-height:180px; display:flex; flex-direction:column; justify-content:center;">
            <h1>{word['word'].capitalize()}</h1>
            <p style="color:#8B85B8;">{word['category']} · {word['difficulty'].replace('_',' ').title()}</p>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class="sm-card" style="min-height:180px;">
            <p><b>Meaning:</b> {word['meaning']}</p>
            <p><b>Example:</b> {word['example']}</p>
            <p><b>Synonym:</b> {word['synonym']}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns(3)
    if c1.button("🔄 Flip Card"):
        st.session_state.fc_flipped = not st.session_state.fc_flipped
        st.rerun()
    if c2.button("➡ Next Card"):
        st.session_state.fc_index = (idx + 1) % len(filtered)
        st.session_state.fc_flipped = False
        st.rerun()
    profile = get_profile()
    already = word["word"] in profile["learned_words"]
    if c3.button("✓ Mark Learned" if not already else "✓ Learned", disabled=already):
        learn_word(word["word"])
        award_xp("vocabulary", unique_key=f"flashcard_{word['word']}")
        st.rerun()


def _init_vocab_quiz(words):
    pool = list(words)
    random.shuffle(pool)
    pool = pool[:10]
    quiz_items = []
    for w in pool:
        distractors = [x["meaning"] for x in words if x["word"] != w["word"]]
        random.shuffle(distractors)
        options = [w["meaning"]] + distractors[:3]
        random.shuffle(options)
        quiz_items.append({"word": w, "options": options})
    st.session_state.quiz_state["vocab"] = {"items": quiz_items, "index": 0, "score": 0, "answered": False, "selected": None, "finished": False}


def _render_vocab_quiz():
    state = st.session_state.quiz_state["vocab"]
    items = state["items"]

    if state["finished"]:
        pct = round((state["score"] / len(items)) * 100) if items else 0
        st.markdown(f"<div class='sm-gradient-card'><h2>Quiz Complete! Score: {state['score']}/{len(items)} ({pct}%)</h2></div>", unsafe_allow_html=True)
        record_category_score("vocabulary", pct)
        xp = award_xp("vocabulary", unique_key=f"vocabquiz_{len(items)}_{state['score']}_{random.random()}")
        if xp:
            st.success(f"You earned +{xp} XP! 🎉")
        if st.button("Take Another Quiz"):
            del st.session_state.quiz_state["vocab"]
            st.rerun()
        return

    idx = state["index"]
    item = items[idx]
    word = item["word"]

    st.markdown(f"#### Question {idx + 1} of {len(items)}")
    st.progress(idx / len(items))
    st.markdown(f"<div class='sm-card'><h4>What does '<b>{word['word']}</b>' mean?</h4></div>", unsafe_allow_html=True)

    if not state["answered"]:
        choice = st.radio("Choose the correct meaning:", item["options"], key=f"vq_{idx}", index=None)
        if st.button("Submit", disabled=(choice is None)):
            state["selected"] = choice
            state["answered"] = True
            if choice == word["meaning"]:
                state["score"] += 1
            st.rerun()
    else:
        correct = state["selected"] == word["meaning"]
        if correct:
            st.markdown("<span class='sm-pill sm-pill-correct'>✓ Correct</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='sm-pill sm-pill-wrong'>✗ Incorrect</span>", unsafe_allow_html=True)
        st.info(f"**{word['word'].capitalize()}** means: {word['meaning']}\n\nExample: *{word['example']}*")
        if st.button("Next ▶"):
            state["index"] += 1
            state["answered"] = False
            if state["index"] >= len(items):
                state["finished"] = True
            st.rerun()


def _render_progress(words):
    profile = get_profile()
    learned = len(profile["learned_words"])
    total = len(words)
    st.markdown("### 📈 Vocabulary Progress")
    st.progress(min(learned / max(total, 1), 1.0), text=f"{learned} / {total} words learned")
    if profile["learned_words"]:
        with st.expander("View learned words"):
            st.write(", ".join(sorted(profile["learned_words"])))


def render():
    st.markdown("## 🔤 Vocabulary Builder")
    words = _get_words()
    if not words:
        st.warning("Vocabulary data could not be loaded.")
        return

    _render_progress(words)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🌟 Word of the Day", "🃏 Flashcards", "📝 Quiz"])
    with tab1:
        _render_word_of_day(words)
    with tab2:
        _render_flashcards(words)
    with tab3:
        if "vocab" in st.session_state.quiz_state:
            _render_vocab_quiz()
            if st.button("← Exit Quiz"):
                del st.session_state.quiz_state["vocab"]
                st.rerun()
        else:
            st.caption("Test yourself on 10 random words from across all categories.")
            if st.button("Start Vocabulary Quiz"):
                _init_vocab_quiz(words)
                st.rerun()
