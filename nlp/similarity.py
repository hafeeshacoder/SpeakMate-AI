"""
nlp/similarity.py
-------------------
TF-IDF vectorization and cosine similarity using scikit-learn.
Used to compare a user's answer against a reference answer/topic for
relevance scoring in Communication, Speaking, and Interview modules.

If there is no reference text, similarity is NOT computed or displayed
(a fake number is never shown).
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(text_a: str, text_b: str):
    """
    Compute TF-IDF cosine similarity between two texts.
    Returns a float 0-100 (percentage), or None if either text is empty/too short.
    """
    if not text_a or not text_b:
        return None
    a = text_a.strip()
    b = text_b.strip()
    if len(a.split()) < 2 or len(b.split()) < 2:
        return None

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([a, b])
        if tfidf_matrix.shape[1] == 0:
            return None
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        return None


def top_tfidf_terms(text: str, top_n: int = 8):
    """Return the top TF-IDF weighted terms in a single document (for keyword insight)."""
    text = (text or "").strip()
    if len(text.split()) < 2:
        return []
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
        matrix = vectorizer.fit_transform([text])
        scores = matrix.toarray()[0]
        terms = vectorizer.get_feature_names_out()
        pairs = sorted(zip(terms, scores), key=lambda x: -x[1])
        return [t for t, s in pairs[:top_n] if s > 0]
    except Exception:
        return []


def topic_relevance_score(user_text: str, topic_or_reference: str):
    """
    Wrapper used by scoring.py: returns a relevance percentage (0-100),
    or None if not computable — callers must handle the 'no reference' case
    and avoid displaying a fake score.
    """
    return compute_similarity(user_text, topic_or_reference)
