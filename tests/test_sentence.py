"""Tests for sentence formation data and related NLP comparison logic."""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SENTENCE_QUESTIONS_FILE, VOCABULARY_FILE, COMMUNICATION_FILE, SPEAKING_FILE, INTERVIEW_FILE
from nlp.similarity import compute_similarity


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_sentence_questions_file_loads():
    exercises = _load(SENTENCE_QUESTIONS_FILE)
    assert isinstance(exercises, list)
    assert len(exercises) >= 40


def test_sentence_questions_required_fields():
    exercises = _load(SENTENCE_QUESTIONS_FILE)
    required = {"id", "type", "difficulty", "prompt", "data", "answer", "explanation"}
    for ex in exercises:
        assert required.issubset(set(ex.keys()))


def test_sentence_questions_all_seven_types_present():
    exercises = _load(SENTENCE_QUESTIONS_FILE)
    types_found = set(ex["type"] for ex in exercises)
    expected = {
        "arrange_words", "correct_sentence", "positive_to_negative",
        "statement_to_question", "change_tense", "complete_sentence", "situation_based",
    }
    assert expected.issubset(types_found)


def test_arrange_words_answer_uses_all_words():
    exercises = _load(SENTENCE_QUESTIONS_FILE)
    arrange = [e for e in exercises if e["type"] == "arrange_words"]
    assert len(arrange) > 0
    for ex in arrange:
        words = ex["data"]["words"]
        answer_words = re.findall(r"[A-Za-z']+", ex["answer"].lower())
        source_words = [w.lower() for w in words]
        assert sorted(answer_words) == sorted(source_words)


def test_similarity_used_for_open_ended_answers():
    exercises = _load(SENTENCE_QUESTIONS_FILE)
    situation = next(e for e in exercises if e["type"] == "situation_based")
    sim = compute_similarity("Hi, I am pleased to meet you today.", situation["answer"])
    assert sim is None or 0 <= sim <= 100


# ---------------- Vocabulary data ----------------

def test_vocabulary_file_loads_and_has_100_plus_words():
    words = _load(VOCABULARY_FILE)
    assert isinstance(words, list)
    assert len(words) >= 100


def test_vocabulary_required_fields():
    words = _load(VOCABULARY_FILE)
    required = {"id", "word", "meaning", "example", "synonym", "difficulty", "category"}
    for w in words:
        assert required.issubset(set(w.keys()))


def test_vocabulary_categories_present():
    words = _load(VOCABULARY_FILE)
    categories = set(w["category"] for w in words)
    expected = {"Daily English", "College", "Technology", "Workplace", "Communication", "Interview", "Professional English"}
    assert expected.issubset(categories)


# ---------------- Communication data ----------------

def test_communication_topics_file_loads():
    topics = _load(COMMUNICATION_FILE)
    assert isinstance(topics, list)
    assert len(topics) >= 10
    required = {"id", "category", "scenario", "suggested_opening", "practice_prompt", "example_response", "useful_phrases"}
    for t in topics:
        assert required.issubset(set(t.keys()))


# ---------------- Speaking data ----------------

def test_speaking_topics_file_loads_min_30():
    topics = _load(SPEAKING_FILE)
    assert isinstance(topics, list)
    assert len(topics) >= 30
    for t in topics:
        assert "title" in t and "prompt" in t and "category" in t


# ---------------- Interview data ----------------

def test_interview_questions_file_loads():
    data = _load(INTERVIEW_FILE)
    assert "hr_questions" in data
    assert "technical_topics" in data
    assert len(data["hr_questions"]) >= 30
    assert len(data["technical_topics"]) >= 5
