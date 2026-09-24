"""
nlp/vocabulary_analyzer.py
-----------------------------
Vocabulary-focused NLP analysis used across Communication, Speaking, and
Interview modules: word diversity, vocabulary level estimation, and
free-text comparison helpers.
"""

from nlp.preprocessing import word_tokenize, remove_stopwords
from nlp.sentence_analyzer import vocabulary_diversity

# A tiny reference list to approximate "advanced" vocabulary usage.
_ADVANCED_WORDS = {
    "consequently", "furthermore", "nevertheless", "significant", "substantial",
    "demonstrate", "facilitate", "comprehensive", "innovative", "meticulous",
    "articulate", "versatile", "leverage", "optimize", "synergy", "feasible",
    "proactive", "adaptable", "accountability", "transparent", "diplomatic",
    "empathy", "rapport", "collaborate", "strategic", "efficient", "resilient",
}


def unique_word_ratio(text: str) -> float:
    return vocabulary_diversity(text)


def advanced_word_usage(text: str):
    """Count how many advanced/professional-level words were used."""
    words = set(word_tokenize(text, lowercase=True))
    used = sorted(words.intersection(_ADVANCED_WORDS))
    return used


def vocabulary_richness_label(diversity_pct: float, word_count: int) -> str:
    """Give a friendly label describing vocabulary richness."""
    if word_count < 8:
        return "Too short to evaluate"
    if diversity_pct >= 75:
        return "Excellent variety"
    if diversity_pct >= 55:
        return "Good variety"
    if diversity_pct >= 35:
        return "Fair variety — try using more varied words"
    return "Limited variety — try to avoid repeating the same words"


def content_word_count(text: str) -> int:
    """Number of meaningful (non-stopword) words used."""
    words = word_tokenize(text, lowercase=True)
    return len(remove_stopwords(words))
