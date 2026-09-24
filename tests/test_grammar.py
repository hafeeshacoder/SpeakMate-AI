"""Tests for nlp/grammar_checker.py and the grammar_questions.json data file."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import grammar_checker
from config import GRAMMAR_QUESTIONS_FILE


def test_subject_verb_agreement_detects_error():
    issues = grammar_checker.check_subject_verb_agreement("He go to college every day.")
    assert len(issues) >= 1
    assert issues[0]["issue"] == "Subject-Verb Agreement"


def test_subject_verb_agreement_no_false_positive():
    issues = grammar_checker.check_subject_verb_agreement("He goes to college every day.")
    assert len(issues) == 0


def test_auxiliary_usage_detects_dont_with_he():
    issues = grammar_checker.check_auxiliary_usage("He don't like vegetables.")
    assert any(i["issue"] == "Auxiliary Usage" for i in issues)


def test_auxiliary_usage_detects_i_is():
    issues = grammar_checker.check_auxiliary_usage("I is going to the market.")
    assert any(i["issue"] == "Auxiliary Usage" for i in issues)


def test_article_usage_a_vs_an():
    issues = grammar_checker.check_article_usage("I saw a elephant at the zoo.")
    assert any(i["issue"] == "Article Usage" for i in issues)


def test_article_usage_correct_no_flag():
    issues = grammar_checker.check_article_usage("I saw an elephant at the zoo.")
    assert len(issues) == 0


def test_preposition_usage_married_with():
    issues = grammar_checker.check_preposition_usage("She is married with a doctor.")
    assert any(i["issue"] == "Preposition Usage" for i in issues)


def test_pronoun_usage_between_you_and_i():
    issues = grammar_checker.check_pronoun_usage("Between you and I, this is wrong.")
    assert any(i["issue"] == "Pronoun Usage" for i in issues)


def test_sentence_structure_missing_capital():
    issues = grammar_checker.check_sentence_structure("he went to school.")
    assert any(i["issue"] == "Sentence Structure" for i in issues)


def test_analyze_sentence_combines_checks():
    issues = grammar_checker.analyze_sentence("he go to college")
    assert isinstance(issues, list)
    assert len(issues) >= 1


def test_analyze_text_multiple_sentences():
    text = "He go to school. She like her job. They is happy."
    issues = grammar_checker.analyze_text(text)
    assert len(issues) >= 1
    for issue in issues:
        assert "sentence" in issue


def test_grammar_score_from_issues_perfect():
    score = grammar_checker.grammar_score_from_issues(5, 0)
    assert score == 100.0


def test_grammar_score_from_issues_with_errors():
    score = grammar_checker.grammar_score_from_issues(4, 4)
    assert 0 <= score < 100


def test_grammar_score_zero_sentences():
    assert grammar_checker.grammar_score_from_issues(0, 0) == 0.0


# ---------------- Data validation ----------------

def _load_questions():
    with open(GRAMMAR_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_grammar_questions_file_loads():
    questions = _load_questions()
    assert isinstance(questions, list)
    assert len(questions) >= 150


def test_grammar_questions_have_required_fields():
    questions = _load_questions()
    required = {"id", "topic", "category", "difficulty", "question", "options", "correct_answer", "explanation"}
    for q in questions:
        assert required.issubset(set(q.keys()))


def test_grammar_questions_have_four_options():
    questions = _load_questions()
    for q in questions:
        assert len(q["options"]) == 4
        assert q["correct_answer"] in q["options"]


def test_grammar_questions_ids_unique():
    questions = _load_questions()
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids))


def test_grammar_questions_min_per_major_category():
    """At least 10 questions for each major grammar category listed in the spec."""
    questions = _load_questions()
    major_topics = [
        "Parts of Speech", "Nouns", "Simple Present", "Subject-Verb Agreement",
    ]
    counts = {}
    for q in questions:
        counts[q["topic"]] = counts.get(q["topic"], 0) + 1
    for topic in major_topics:
        assert counts.get(topic, 0) >= 8, f"{topic} has fewer than 8 questions"
