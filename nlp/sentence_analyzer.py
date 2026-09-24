"""
nlp/sentence_analyzer.py
--------------------------
Analyzes sentence and paragraph quality: word/sentence counts, vocabulary
diversity, repeated words, filler words, readability, and basic sentence
quality indicators.
"""

from collections import Counter
from config import FILLER_WORDS
from nlp.preprocessing import (
    sentence_tokenize,
    word_tokenize,
    pos_tag,
    pos_distribution,
    remove_stopwords,
)

try:
    import textstat
    _TEXTSTAT_AVAILABLE = True
except Exception:  # pragma: no cover
    _TEXTSTAT_AVAILABLE = False


def basic_counts(text: str):
    """Word count, sentence count, unique word count, average sentence length."""
    sentences = sentence_tokenize(text)
    words = word_tokenize(text, lowercase=True)
    unique_words = set(words)
    avg_sentence_len = round(len(words) / len(sentences), 1) if sentences else 0.0
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "unique_word_count": len(unique_words),
        "avg_sentence_length": avg_sentence_len,
    }


def vocabulary_diversity(text: str) -> float:
    """Type-token ratio expressed as a percentage: unique words / total words."""
    words = word_tokenize(text, lowercase=True)
    if not words:
        return 0.0
    unique = set(words)
    return round((len(unique) / len(words)) * 100, 1)


def repeated_words(text: str, min_count: int = 3, min_length: int = 3):
    """Find content words repeated an unusually high number of times."""
    words = word_tokenize(text, lowercase=True)
    words = [w for w in words if len(w) >= min_length]
    filtered = remove_stopwords(words)
    counts = Counter(filtered)
    repeated = {w: c for w, c in counts.items() if c >= min_count}
    return dict(sorted(repeated.items(), key=lambda x: -x[1]))


def detect_filler_words(text: str):
    """Detect filler words/phrases commonly used by English learners."""
    low = " " + text.lower() + " "
    found = {}
    for filler in FILLER_WORDS:
        count = low.count(" " + filler + " ")
        if count > 0:
            found[filler] = count
    return found


def readability_level(text: str):
    """Return a simple readability label using textstat's Flesch Reading Ease, with fallback."""
    words = word_tokenize(text)
    if not words:
        return "N/A", None
    if _TEXTSTAT_AVAILABLE:
        try:
            score = textstat.flesch_reading_ease(text)
            if score >= 80:
                label = "Very Easy"
            elif score >= 60:
                label = "Easy"
            elif score >= 40:
                label = "Moderate"
            elif score >= 20:
                label = "Difficult"
            else:
                label = "Very Difficult"
            return label, round(score, 1)
        except Exception:
            pass
    # Fallback: rough heuristic using average word/sentence length
    sentences = sentence_tokenize(text)
    avg_words_per_sentence = len(words) / max(len(sentences), 1)
    avg_word_len = sum(len(w) for w in words) / len(words)
    if avg_words_per_sentence < 12 and avg_word_len < 5:
        return "Easy", None
    elif avg_words_per_sentence < 20 and avg_word_len < 6:
        return "Moderate", None
    else:
        return "Difficult", None


def extract_keywords(text: str, top_n: int = 8):
    """Extract important keywords using POS tagging: prioritize nouns and proper adjectives."""
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    candidates = [w.lower() for w, t in tagged if t.startswith("NN") and len(w) > 2]
    candidates = [w for w in remove_stopwords(candidates)]
    counts = Counter(candidates)
    top = [w for w, _ in counts.most_common(top_n)]
    if len(top) < top_n:
        # supplement with adjectives if not enough nouns found
        adj_candidates = [w.lower() for w, t in tagged if t.startswith("JJ") and len(w) > 2]
        adj_candidates = remove_stopwords(adj_candidates)
        for w in adj_candidates:
            if w not in top:
                top.append(w)
            if len(top) >= top_n:
                break
    return top


def pos_summary(text: str):
    """POS distribution across the whole text."""
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    return pos_distribution(tagged)


def sentence_quality_indicators(text: str):
    """A few lightweight indicators of sentence quality (not a grammar check)."""
    sentences = sentence_tokenize(text)
    if not sentences:
        return {
            "avg_sentence_length": 0,
            "very_short_sentences": 0,
            "very_long_sentences": 0,
            "sentence_length_balance": "N/A",
        }
    lengths = [len(word_tokenize(s)) for s in sentences]
    avg_len = round(sum(lengths) / len(lengths), 1)
    very_short = sum(1 for l in lengths if l < 4)
    very_long = sum(1 for l in lengths if l > 25)
    if very_short == 0 and very_long == 0:
        balance = "Well balanced"
    elif very_short > very_long:
        balance = "Sentences may be too short/simple"
    else:
        balance = "Sentences may be too long/complex"
    return {
        "avg_sentence_length": avg_len,
        "very_short_sentences": very_short,
        "very_long_sentences": very_long,
        "sentence_length_balance": balance,
    }


def full_analysis(text: str):
    """Run the complete NLP analysis pipeline used by the NLP Analyzer page."""
    counts = basic_counts(text)
    diversity = vocabulary_diversity(text)
    repeats = repeated_words(text)
    fillers = detect_filler_words(text)
    read_label, read_score = readability_level(text)
    keywords = extract_keywords(text)
    pos_dist = pos_summary(text)
    quality = sentence_quality_indicators(text)

    return {
        **counts,
        "vocabulary_diversity": diversity,
        "repeated_words": repeats,
        "filler_words": fillers,
        "filler_word_count": sum(fillers.values()),
        "readability_label": read_label,
        "readability_score": read_score,
        "keywords": keywords,
        "pos_distribution": pos_dist,
        "sentence_quality": quality,
    }
