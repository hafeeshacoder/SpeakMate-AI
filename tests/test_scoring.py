"""Tests for nlp/scoring.py and utils/progress_manager.py (XP, levels, streaks)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import scoring
from utils import progress_manager
from config import SPEAKMATE_LEVELS, XP_RULES


def test_compute_practice_score_empty_text():
    result = scoring.compute_practice_score("")
    assert result["overall"] == 0.0


def test_compute_practice_score_has_all_components():
    text = "I really enjoy learning English every day. It helps me communicate better at work."
    result = scoring.compute_practice_score(text)
    components = result["components"]
    for key in ["grammar", "vocabulary", "sentence_quality", "fluency"]:
        assert key in components
        assert components[key] is None or 0 <= components[key] <= 100


def test_compute_practice_score_with_reference():
    text = "I want to talk about my favorite technology, which is my smartphone."
    result = scoring.compute_practice_score(text, reference_text="Talk about your favorite technology")
    assert result["components"]["topic_relevance"] is not None
    assert 0 <= result["overall"] <= 100


def test_compute_practice_score_weights_sum_close_to_one():
    text = "This is a simple test sentence for scoring purposes today."
    result = scoring.compute_practice_score(text)
    total_weight = sum(result["weights"].values())
    assert abs(total_weight - 1.0) < 0.01


def test_compute_practice_score_overall_in_range():
    text = "He go to college. He like his friends very much and enjoys studying computer science."
    result = scoring.compute_practice_score(text)
    assert 0 <= result["overall"] <= 100


# ---------------- Level system ----------------

def test_level_info_at_zero_xp():
    info = progress_manager.get_level_info(0)
    assert info["level_number"] == 1
    assert info["level_name"] == "First Steps"


def test_level_info_progression():
    info = progress_manager.get_level_info(150)
    assert info["level_number"] == 2
    assert info["level_name"] == "Beginner Speaker"


def test_level_info_max_level():
    info = progress_manager.get_level_info(5000)
    assert info["level_number"] == 10
    assert info["level_name"] == "English Master"
    assert info["progress_fraction"] == 1.0


def test_all_levels_are_ordered_by_xp_threshold():
    thresholds = [t for _, _, t in SPEAKMATE_LEVELS]
    assert thresholds == sorted(thresholds)


# ---------------- XP rules ----------------

def test_xp_rules_exist_for_all_categories():
    expected_categories = {
        "grammar", "vocabulary", "sentence_formation",
        "communication", "speaking", "interview", "daily_goal",
    }
    assert expected_categories.issubset(set(XP_RULES.keys()))
    for v in XP_RULES.values():
        assert v > 0


# ---------------- Grammar checker score helper ----------------

def test_grammar_score_helper_bounds():
    from nlp.grammar_checker import grammar_score_from_issues
    assert grammar_score_from_issues(10, 0) == 100.0
    assert grammar_score_from_issues(10, 40) == 0.0
    score = grammar_score_from_issues(10, 5)
    assert 0 <= score <= 100
