"""Tests for the core NLP pipeline (nlp/preprocessing.py, sentence_analyzer.py)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import preprocessing, sentence_analyzer, similarity


def test_sentence_tokenize_basic():
    text = "I am a student. I love learning English. It is fun!"
    sentences = preprocessing.sentence_tokenize(text)
    assert len(sentences) == 3


def test_sentence_tokenize_empty():
    assert preprocessing.sentence_tokenize("") == []
    assert preprocessing.sentence_tokenize(None) == []


def test_word_tokenize_basic():
    tokens = preprocessing.word_tokenize("Hello, world! I'm learning.")
    assert "Hello" in tokens or "hello" in [t.lower() for t in tokens]
    assert len(tokens) > 0


def test_word_tokenize_lowercase():
    tokens = preprocessing.word_tokenize("Hello World", lowercase=True)
    assert tokens == [t.lower() for t in tokens]


def test_stopword_removal():
    tokens = ["I", "am", "going", "to", "the", "market"]
    filtered = preprocessing.remove_stopwords(tokens)
    assert "market" in [t.lower() for t in filtered] or "going" in [t.lower() for t in filtered]
    assert len(filtered) <= len(tokens)


def test_lemmatize_tokens():
    tokens = ["running", "studies", "better"]
    lemmas = preprocessing.lemmatize_tokens(tokens)
    assert len(lemmas) == len(tokens)
    assert all(isinstance(l, str) for l in lemmas)


def test_pos_tag_returns_pairs():
    tokens = ["She", "runs", "fast"]
    tagged = preprocessing.pos_tag(tokens)
    assert len(tagged) == len(tokens)
    for word, tag in tagged:
        assert isinstance(word, str)
        assert isinstance(tag, str)


def test_pos_distribution_counts():
    tagged = [("dog", "NN"), ("runs", "VBZ"), ("fast", "RB"), ("happy", "JJ")]
    dist = preprocessing.pos_distribution(tagged)
    assert dist["Nouns"] == 1
    assert dist["Verbs"] == 1
    assert dist["Adverbs"] == 1
    assert dist["Adjectives"] == 1


def test_basic_counts():
    text = "I love English. English is a global language."
    counts = sentence_analyzer.basic_counts(text)
    assert counts["sentence_count"] == 2
    assert counts["word_count"] > 0
    assert counts["unique_word_count"] > 0


def test_vocabulary_diversity_range():
    text = "The cat sat on the mat. The cat was happy."
    diversity = sentence_analyzer.vocabulary_diversity(text)
    assert 0 <= diversity <= 100


def test_repeated_words_detection():
    text = "project project project is a big big big task for everyone today"
    repeated = sentence_analyzer.repeated_words(text, min_count=3)
    assert "project" in repeated


def test_filler_word_detection():
    text = "So, um, I basically think that, like, this is actually a good idea."
    fillers = sentence_analyzer.detect_filler_words(text)
    assert sum(fillers.values()) > 0


def test_readability_returns_label():
    text = "I like to read books. It helps me learn new words."
    label, score = sentence_analyzer.readability_level(text)
    assert isinstance(label, str)
    assert label != ""


def test_extract_keywords_returns_list():
    text = "Artificial intelligence and machine learning are transforming technology and education."
    keywords = sentence_analyzer.extract_keywords(text)
    assert isinstance(keywords, list)
    assert len(keywords) > 0


def test_full_analysis_has_expected_keys():
    text = "I am studying computer science at college. I really enjoy programming."
    result = sentence_analyzer.full_analysis(text)
    expected_keys = {
        "word_count", "sentence_count", "unique_word_count", "avg_sentence_length",
        "vocabulary_diversity", "repeated_words", "filler_words", "filler_word_count",
        "readability_label", "readability_score", "keywords", "pos_distribution",
        "sentence_quality",
    }
    assert expected_keys.issubset(set(result.keys()))


def test_similarity_identical_texts_high():
    sim = similarity.compute_similarity(
        "I love studying machine learning and artificial intelligence",
        "I love studying machine learning and artificial intelligence",
    )
    assert sim is not None
    assert sim > 90


def test_similarity_unrelated_texts_low():
    sim = similarity.compute_similarity(
        "I love studying machine learning and artificial intelligence",
        "The weather today is sunny and warm outside",
    )
    assert sim is not None
    assert sim < 40


def test_similarity_empty_returns_none():
    assert similarity.compute_similarity("", "something") is None
    assert similarity.compute_similarity("something", "") is None


def test_top_tfidf_terms():
    text = "Python is a popular programming language used for data science and automation."
    terms = similarity.top_tfidf_terms(text)
    assert isinstance(terms, list)
