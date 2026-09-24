"""
pages/speaking.py
--------------------
Speaking practice: 30+ topics, text-based response practice (primary and
always-working path), with an OPTIONAL microphone recorder for the user's
own reference. Automatic speech-to-text is not performed locally (no
reliable offline STT is bundled), so recordings are for the learner's own
playback/practice only — analysis always runs on the typed response. This
guarantees the app never breaks due to microphone permissions.
"""

import random
import streamlit as st

from config import SPEAKING_FILE
from utils.helpers import load_json_data, safe_ai_notice
from utils.progress_manager import award_xp, record_category_score
from nlp.scoring import compute_practice_score
from nlp.sentence_analyzer import basic_counts, detect_filler_words, vocabulary_diversity
from ai.groq_client import is_configured, conversational_feedback


def _render_analysis(result, text):
    st.markdown("#### 🔍 Speaking Analysis")
    counts = basic_counts(text)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Word Count", counts["word_count"])
    c2.metric("Sentences", counts["sentence_count"])
    c3.metric("Vocabulary Diversity", f"{vocabulary_diversity(text)}%")
    fillers = detect_filler_words(text)
    c4.metric("Filler Words", sum(fillers.values()))

    comp = result["components"]
    c5, c6, c7 = st.columns(3)
    c5.metric("Grammar", f"{comp['grammar']}%")
    c6.metric("Sentence Quality", f"{comp['sentence_quality']}%")
    rel = comp["topic_relevance"]
    c7.metric("Topic Relevance", f"{rel}%" if rel is not None else "N/A")

    st.markdown(f"### 🎤 SpeakMate Practice Score: {result['overall']}%")
    st.caption("This is an application-specific learning score, not an official English proficiency certification.")

    if fillers:
        st.markdown("**Filler words detected:** " + ", ".join(f"'{w}' ×{c}" for w, c in fillers.items()))

    issues = result["grammar_issues"]
    if issues:
        st.markdown("**Grammar observations:**")
        for i in issues[:5]:
            st.markdown(f"- *{i['issue']}*: {i['suggestion']}")


def render():
    st.markdown("## 🎤 Speaking Practice")
    topics = load_json_data(SPEAKING_FILE, [])
    if not topics:
        st.warning("Speaking topic data could not be loaded.")
        return

    categories = sorted(set(t["category"] for t in topics))
    selected_cat = st.selectbox("Filter by category (optional)", ["All"] + categories)
    filtered = topics if selected_cat == "All" else [t for t in topics if t["category"] == selected_cat]

    if "speaking_topic_id" not in st.session_state or st.session_state.speaking_topic_id not in [t["id"] for t in filtered]:
        st.session_state.speaking_topic_id = filtered[0]["id"]

    topic = next(t for t in filtered if t["id"] == st.session_state.speaking_topic_id)

    if st.button("🎲 Pick a Random Topic"):
        st.session_state.speaking_topic_id = random.choice(filtered)["id"]
        st.rerun()

    st.markdown(
        f"""
        <div class="sm-card">
            <span class="sm-badge">{topic['category']}</span>
            <h3 style="margin-top:0.6rem;">{topic['title']}</h3>
            <p>{topic['prompt']}</p>
            <p style="color:#8B85B8;">Suggested speaking time: ~{topic['suggested_duration_seconds']} seconds</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🎙️ Optional: Record yourself (for your own practice only)"):
        st.caption(
            "Recording is optional and used only for your own playback — this app does not transcribe audio "
            "automatically. If your microphone is unavailable or permission is denied, simply skip this and "
            "type your response below; everything still works perfectly."
        )
        try:
            audio = st.audio_input("Record your spoken response", key=f"audio_{topic['id']}")
            if audio is not None:
                st.audio(audio)
                st.success("Recording captured. Now type what you said (or a summary) below for analysis.")
        except Exception:
            st.info("Microphone recording isn't available in this environment. Please use text input below.")

    response = st.text_area("✍️ Type your spoken response (or a transcript of it):", height=150, key=f"speak_text_{topic['id']}")

    if st.button("Analyze My Speaking", disabled=(not response.strip())):
        result = compute_practice_score(response, reference_text=topic["title"] + " " + topic["prompt"])
        st.session_state["speak_last_result"] = result
        st.session_state["speak_last_text"] = response
        record_category_score("speaking", result["overall"])
        xp = award_xp("speaking", unique_key=f"speak_{topic['id']}_{random.random()}")
        if xp:
            st.toast(f"+{xp} XP earned!", icon="🎉")

    if st.session_state.get("speak_last_result"):
        _render_analysis(st.session_state["speak_last_result"], st.session_state["speak_last_text"])

        st.markdown("#### 🤖 AI Coaching Feedback (optional)")
        if not is_configured():
            safe_ai_notice()
        else:
            if st.button("Get AI Coaching Feedback"):
                with st.spinner("Analyzing your response..."):
                    feedback = conversational_feedback(topic["title"], st.session_state["speak_last_text"])
                st.markdown(feedback)
