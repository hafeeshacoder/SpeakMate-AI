"""
pages/nlp_analyzer.py
------------------------
Dedicated NLP Analyzer page. Lets the user enter any English paragraph and
runs real, local NLP processing: tokenization, POS tagging, lemmatization,
vocabulary diversity, filler/repeated word detection, TF-IDF keyword
extraction, optional cosine similarity to a reference text, readability,
and basic rule-based grammar observations. Nothing here is faked — every
number is actually calculated.
"""

import streamlit as st

from nlp.preprocessing import (
    sentence_tokenize,
    word_tokenize,
    pos_tag,
    lemmatize_tokens,
    remove_stopwords,
)
from nlp.sentence_analyzer import full_analysis
from nlp.similarity import compute_similarity, top_tfidf_terms
from nlp.grammar_checker import analyze_text

SAMPLE_TEXT = (
    "I am a final year computer science student. I am really interested in AI and "
    "machine learning technology. I have completed a college project about a chatbot, "
    "and I am currently doing an internship. I go to college every day and I enjoy "
    "learning new things about programming."
)


def render():
    st.markdown("## 🧠 NLP Analyzer")
    st.caption("Enter any English paragraph below. Every result is calculated live using real NLP techniques — nothing is pre-scripted.")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Load Sample Text"):
            st.session_state["nlp_input"] = SAMPLE_TEXT

    text = st.text_area(
        "Enter your paragraph:",
        value=st.session_state.get("nlp_input", ""),
        height=160,
        key="nlp_input",
    )

    with st.expander("⚙️ Optional: Compare with a reference text (for topic similarity)"):
        reference = st.text_area("Reference text (optional):", height=80, key="nlp_reference")

    if not text.strip():
        st.info("Enter a paragraph above (or load the sample text) to see the full NLP analysis.")
        return

    if st.button("🔍 Run NLP Analysis", type="primary"):
        st.session_state["nlp_run"] = True

    if not st.session_state.get("nlp_run"):
        return

    result = full_analysis(text)

    # -------------------- Overview metrics --------------------
    st.markdown("### 📊 NLP Analysis Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Word Count", result["word_count"])
    c2.metric("Sentences", result["sentence_count"])
    c3.metric("Unique Words", result["unique_word_count"])
    c4.metric("Vocabulary Diversity", f"{result['vocabulary_diversity']}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Filler Words", result["filler_word_count"])
    c6.metric("Repeated Words", len(result["repeated_words"]))
    c7.metric("Readability", result["readability_label"])
    c8.metric("Avg. Sentence Length", result["sentence_quality"]["avg_sentence_length"])

    # -------------------- POS distribution --------------------
    st.markdown("### 🔤 Part-of-Speech Distribution")
    pos = result["pos_distribution"]
    pc1, pc2, pc3, pc4, pc5 = st.columns(5)
    pc1.metric("Nouns", pos.get("Nouns", 0))
    pc2.metric("Verbs", pos.get("Verbs", 0))
    pc3.metric("Adjectives", pos.get("Adjectives", 0))
    pc4.metric("Adverbs", pos.get("Adverbs", 0))
    pc5.metric("Other", pos.get("Other", 0))

    # -------------------- Keywords / TF-IDF --------------------
    st.markdown("### 🔑 Important Keywords")
    if result["keywords"]:
        st.markdown(" ".join(f"<span class='sm-badge'>{k}</span>" for k in result["keywords"]), unsafe_allow_html=True)
    else:
        st.caption("Not enough content to extract keywords.")

    tfidf_terms = top_tfidf_terms(text)
    if tfidf_terms:
        st.markdown("**Top TF-IDF weighted terms:**")
        st.markdown(" ".join(f"<span class='sm-badge'>{t}</span>" for t in tfidf_terms), unsafe_allow_html=True)

    # -------------------- Similarity --------------------
    if reference and reference.strip():
        sim = compute_similarity(text, reference)
        st.markdown("### 🔗 Cosine Similarity to Reference Text")
        if sim is not None:
            st.progress(sim / 100, text=f"{sim}% similar (TF-IDF cosine similarity)")
        else:
            st.caption("Similarity could not be computed — try a longer reference text.")

    # -------------------- Repeated & filler words --------------------
    st.markdown("### 🔁 Repeated & Filler Words")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("**Repeated content words (3+ times):**")
        if result["repeated_words"]:
            for w, c in result["repeated_words"].items():
                st.markdown(f"- '{w}' — {c} times")
        else:
            st.caption("No significantly repeated words detected.")
    with rc2:
        st.markdown("**Filler words:**")
        if result["filler_words"]:
            for w, c in result["filler_words"].items():
                st.markdown(f"- '{w}' — {c} times")
        else:
            st.caption("No filler words detected.")

    # -------------------- Grammar observations --------------------
    st.markdown("### ✏️ Grammar Observations")
    issues = analyze_text(text)
    if issues:
        for i in issues[:8]:
            st.markdown(f"- *{i['issue']}* in \"{i['sentence']}\": {i['suggestion']}")
    else:
        st.success("No obvious rule-based grammar issues detected. 👍")
    st.caption("This is a practical, rule-based checker for common learner mistakes — not a professional-grade grammar engine.")

    # -------------------- Sentence quality --------------------
    st.markdown("### 🧩 Sentence Quality Indicators")
    q = result["sentence_quality"]
    st.markdown(
        f"- Average sentence length: **{q['avg_sentence_length']} words**\n"
        f"- Very short sentences: **{q['very_short_sentences']}**\n"
        f"- Very long/complex sentences: **{q['very_long_sentences']}**\n"
        f"- Overall balance: **{q['sentence_length_balance']}**"
    )

    # -------------------- Under the hood --------------------
    with st.expander("🔬 See tokenization, POS tags & lemmatization (under the hood)"):
        sentences = sentence_tokenize(text)
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        lemmas = lemmatize_tokens(tokens)
        no_stop = remove_stopwords([t.lower() for t in tokens])

        st.markdown(f"**Sentences ({len(sentences)}):**")
        for s in sentences:
            st.markdown(f"- {s}")

        st.markdown(f"**Word Tokens ({len(tokens)}):**")
        st.write(tokens)

        st.markdown("**POS Tags (word, tag):**")
        st.write(tagged)

        st.markdown("**Lemmatized Tokens:**")
        st.write(lemmas)

        st.markdown(f"**Tokens after stopword removal ({len(no_stop)}):**")
        st.write(no_stop)
