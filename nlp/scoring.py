"""
nlp/scoring.py
----------------
Computes the transparent "SpeakMate Practice Score" — an APPLICATION-SPECIFIC
learning score. This is NOT an IELTS, TOEFL, CEFR, or any official English
proficiency score.

Weighting (visible and documented):
    Grammar            30%
    Vocabulary          20%
    Sentence Quality    20%
    Topic Relevance     20%
    Fluency Indicators  10%
"""

from config import SCORE_WEIGHTS
from nlp.preprocessing import sentence_tokenize
from nlp.grammar_checker import analyze_text, grammar_score_from_issues
from nlp.sentence_analyzer import (
    basic_counts,
    vocabulary_diversity,
    detect_filler_words,
    sentence_quality_indicators,
)
from nlp.vocabulary_analyzer import vocabulary_richness_label
from nlp.similarity import topic_relevance_score


def _vocabulary_component(text: str) -> float:
    """Score 0-100 based on vocabulary diversity and content richness."""
    diversity = vocabulary_diversity(text)
    counts = basic_counts(text)
    word_count = counts["word_count"]
    if word_count < 5:
        return max(diversity * 0.5, 10)
    # Diversity naturally drops with longer texts; apply a gentle length bonus.
    length_bonus = min(word_count / 60, 1.0) * 10
    score = min(diversity + length_bonus, 100)
    return round(score, 1)


def _sentence_quality_component(text: str) -> float:
    """Score 0-100 based on sentence balance and structure."""
    quality = sentence_quality_indicators(text)
    sentences = sentence_tokenize(text)
    if not sentences:
        return 0.0
    penalty = (quality["very_short_sentences"] + quality["very_long_sentences"]) * 8
    score = max(0.0, 100.0 - penalty)
    # Reward having more than one sentence (shows sentence-building ability)
    if len(sentences) >= 3:
        score = min(score + 5, 100)
    return round(score, 1)


def _fluency_component(text: str) -> float:
    """Score 0-100 based on filler-word density and text length."""
    counts = basic_counts(text)
    word_count = counts["word_count"]
    if word_count == 0:
        return 0.0
    fillers = detect_filler_words(text)
    filler_count = sum(fillers.values())
    filler_ratio = filler_count / max(word_count, 1)
    score = max(0.0, 100.0 - (filler_ratio * 300))
    if word_count < 15:
        score = min(score, 60)  # very short responses can't score high on fluency
    return round(score, 1)


def compute_practice_score(text: str, reference_text: str = None):
    """
    Compute the full SpeakMate Practice Score breakdown.

    Returns a dict with each component score, the weighted overall score,
    and whether topic relevance was actually computable (no fake numbers).
    """
    text = (text or "").strip()
    if not text:
        return {
            "overall": 0.0,
            "components": {
                "grammar": 0.0,
                "vocabulary": 0.0,
                "sentence_quality": 0.0,
                "topic_relevance": None,
                "fluency": 0.0,
            },
            "weights": SCORE_WEIGHTS,
            "grammar_issues": [],
        }

    sentences = sentence_tokenize(text)
    issues = analyze_text(text)
    grammar_score = grammar_score_from_issues(len(sentences), len(issues))
    vocab_score = _vocabulary_component(text)
    sentence_score = _sentence_quality_component(text)
    fluency_score = _fluency_component(text)

    relevance_score = None
    if reference_text:
        relevance_score = topic_relevance_score(text, reference_text)

    # Build the weighted overall score. If relevance is not computable,
    # redistribute its weight proportionally across the other components.
    weights = dict(SCORE_WEIGHTS)
    components = {
        "grammar": grammar_score,
        "vocabulary": vocab_score,
        "sentence_quality": sentence_score,
        "topic_relevance": relevance_score,
        "fluency": fluency_score,
    }

    if relevance_score is None:
        redistributable = weights.pop("topic_relevance")
        total_remaining = sum(weights.values())
        for k in weights:
            weights[k] += redistributable * (weights[k] / total_remaining)
        overall = sum(components[k] * weights[k] for k in weights)
    else:
        overall = sum(components[k] * weights[k] for k in weights)

    return {
        "overall": round(overall, 1),
        "components": components,
        "weights": weights,
        "grammar_issues": issues,
    }
