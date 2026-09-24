"""
utils/progress_manager.py
----------------------------
Manages all gamification state: XP, SpeakMate level, streaks, category
progress, and achievements. Uses st.session_state as the source of truth
during a session, and persists to data/progress.json and data/history.json
so progress can survive a page refresh on the same machine.

The app must run perfectly even if these JSON files do not exist or cannot
be written (e.g., some read-only deployment environments) — all file I/O
is wrapped in try/except with safe fallbacks.
"""

import json
import os
from datetime import date, datetime, timedelta

import streamlit as st

from config import (
    PROGRESS_FILE,
    HISTORY_FILE,
    XP_RULES,
    SPEAKMATE_LEVELS,
    ACHIEVEMENTS,
    DATA_DIR,
)

CATEGORIES = [
    "grammar", "vocabulary", "sentence_formation",
    "communication", "speaking", "interview",
]

DEFAULT_PROFILE = {
    "name": "",
    "english_level": None,
    "learning_goal": None,
    "daily_goal_minutes": 15,
    "onboarded": False,
    "xp": 0,
    "streak": {"current": 0, "longest": 0, "last_active_date": None},
    "daily_goal": {"date": None, "minutes_completed": 0, "met_count": 0, "awarded_today": False},
    "category_scores": {c: [] for c in CATEGORIES},
    "activity_counts": {c: 0 for c in CATEGORIES},
    "learned_words": [],
    "completed_item_ids": [],
    "achievements_unlocked": [],
    "created_at": None,
}


# ----------------------------------------------------------------------
# Disk I/O (safe / best-effort)
# ----------------------------------------------------------------------
def _ensure_data_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass


def _safe_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return default
                return json.loads(content)
    except Exception:
        pass
    return default


def _safe_save_json(path, data):
    try:
        _ensure_data_dir()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_profile_from_disk():
    data = _safe_load_json(PROGRESS_FILE, None)
    if not data:
        return None
    profile = dict(DEFAULT_PROFILE)
    profile.update(data)
    # Make sure nested defaults exist even in older saved files
    for c in CATEGORIES:
        profile["category_scores"].setdefault(c, [])
        profile["activity_counts"].setdefault(c, 0)
    return profile


def save_profile_to_disk(profile):
    _safe_save_json(PROGRESS_FILE, profile)


def log_history_event(event: dict):
    history = _safe_load_json(HISTORY_FILE, [])
    if not isinstance(history, list):
        history = []
    event["timestamp"] = datetime.now().isoformat(timespec="seconds")
    history.append(event)
    history = history[-200:]  # keep history file from growing unbounded
    _safe_save_json(HISTORY_FILE, history)


def load_history():
    history = _safe_load_json(HISTORY_FILE, [])
    if not isinstance(history, list):
        history = []
    return history


# ----------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------
def init_session_state():
    if "profile" not in st.session_state:
        loaded = load_profile_from_disk()
        if loaded is None:
            loaded = json.loads(json.dumps(DEFAULT_PROFILE))  # deep copy
            loaded["created_at"] = datetime.now().isoformat(timespec="seconds")
        st.session_state.profile = loaded

    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {}


def get_profile():
    init_session_state()
    return st.session_state.profile


def persist():
    """Persist the current session profile to disk (best-effort)."""
    save_profile_to_disk(st.session_state.profile)


# ----------------------------------------------------------------------
# Level system
# ----------------------------------------------------------------------
def get_level_info(xp: int):
    """Return (level_number, level_name, xp_into_level, xp_needed_for_next, progress_fraction)."""
    current = SPEAKMATE_LEVELS[0]
    next_level = None
    for i, (num, name, threshold) in enumerate(SPEAKMATE_LEVELS):
        if xp >= threshold:
            current = (num, name, threshold)
            next_level = SPEAKMATE_LEVELS[i + 1] if i + 1 < len(SPEAKMATE_LEVELS) else None
        else:
            break
    num, name, threshold = current
    if next_level:
        next_num, next_name, next_threshold = next_level
        span = next_threshold - threshold
        into = xp - threshold
        fraction = min(into / span, 1.0) if span > 0 else 1.0
        xp_needed = next_threshold - xp
    else:
        next_name = None
        fraction = 1.0
        xp_needed = 0
    return {
        "level_number": num,
        "level_name": name,
        "next_level_name": next_name,
        "xp_needed_for_next": max(xp_needed, 0),
        "progress_fraction": fraction,
    }


# ----------------------------------------------------------------------
# Streak system
# ----------------------------------------------------------------------
def update_streak():
    """Update the daily streak. Multiple activities on the same day do not increase it."""
    profile = get_profile()
    today = date.today().isoformat()
    streak = profile["streak"]
    last = streak.get("last_active_date")

    if last == today:
        return  # already counted today
    if last is None:
        streak["current"] = 1
    else:
        try:
            last_date = date.fromisoformat(last)
            if (date.today() - last_date) == timedelta(days=1):
                streak["current"] += 1
            else:
                streak["current"] = 1
        except Exception:
            streak["current"] = 1

    streak["last_active_date"] = today
    streak["longest"] = max(streak.get("longest", 0), streak["current"])
    profile["streak"] = streak


# ----------------------------------------------------------------------
# XP + activity recording
# ----------------------------------------------------------------------
def award_xp(category: str, unique_key: str = None):
    """
    Award XP for a category activity. If unique_key is provided, XP is only
    awarded once per unique_key per profile (prevents refresh farming).
    Returns the amount of XP actually awarded (0 if already awarded).
    """
    profile = get_profile()
    amount = XP_RULES.get(category, 10)

    if unique_key:
        if unique_key in profile["completed_item_ids"]:
            return 0
        profile["completed_item_ids"].append(unique_key)
        # Keep this list from growing without bound
        profile["completed_item_ids"] = profile["completed_item_ids"][-2000:]

    profile["xp"] = profile.get("xp", 0) + amount
    if category in profile["activity_counts"]:
        profile["activity_counts"][category] += 1

    update_streak()
    _update_daily_goal_progress()
    check_and_unlock_achievements()
    persist()
    log_history_event({"type": "xp_award", "category": category, "amount": amount})
    return amount


def record_category_score(category: str, score: float):
    """Record a 0-100 score for a category (used for progress bars)."""
    profile = get_profile()
    if category in profile["category_scores"]:
        profile["category_scores"][category].append(score)
        profile["category_scores"][category] = profile["category_scores"][category][-50:]
    persist()


def get_category_progress(category: str) -> float:
    """Average recent score for a category, defaulting to a gentle starting value."""
    profile = get_profile()
    scores = profile["category_scores"].get(category, [])
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 1)


def _update_daily_goal_progress(minutes: int = 3):
    """Approximate daily-goal minutes based on activity (each activity ~= a few minutes)."""
    profile = get_profile()
    today = date.today().isoformat()
    dg = profile.get("daily_goal", dict(DEFAULT_PROFILE["daily_goal"]))
    if dg.get("date") != today:
        dg = {"date": today, "minutes_completed": 0, "met_count": dg.get("met_count", 0), "awarded_today": False}
    dg["minutes_completed"] += minutes
    goal = profile.get("daily_goal_minutes", 15)
    if dg["minutes_completed"] >= goal and not dg["awarded_today"]:
        dg["awarded_today"] = True
        dg["met_count"] = dg.get("met_count", 0) + 1
        profile["xp"] = profile.get("xp", 0) + XP_RULES.get("daily_goal", 25)
    profile["daily_goal"] = dg


def learn_word(word: str):
    profile = get_profile()
    if word not in profile["learned_words"]:
        profile["learned_words"].append(word)
        check_and_unlock_achievements()
        persist()


# ----------------------------------------------------------------------
# Achievements
# ----------------------------------------------------------------------
def check_and_unlock_achievements():
    profile = get_profile()
    unlocked = set(profile["achievements_unlocked"])
    counts = profile["activity_counts"]
    total_activities = sum(counts.values())

    rules = {
        "first_practice": total_activities >= 1,
        "grammar_starter": counts.get("grammar", 0) >= 5,
        "word_collector": len(profile["learned_words"]) >= 20,
        "sentence_builder": counts.get("sentence_formation", 0) >= 10,
        "conversation_starter": counts.get("communication", 0) >= 5,
        "speaking_champion": counts.get("speaking", 0) >= 10,
        "interview_ready": counts.get("interview", 0) >= 10,
        "seven_day_speaker": profile["streak"].get("current", 0) >= 7,
        "daily_champion": profile.get("daily_goal", {}).get("met_count", 0) >= 5,
        "consistency_star": total_activities >= 50,
    }

    newly_unlocked = []
    for key, achieved in rules.items():
        if achieved and key not in unlocked:
            unlocked.add(key)
            newly_unlocked.append(key)

    profile["achievements_unlocked"] = list(unlocked)
    return newly_unlocked


def get_achievements_status():
    profile = get_profile()
    unlocked = set(profile["achievements_unlocked"])
    result = []
    for a in ACHIEVEMENTS:
        result.append({**a, "unlocked": a["key"] in unlocked})
    return result


# ----------------------------------------------------------------------
# Reset
# ----------------------------------------------------------------------
def reset_progress(keep_profile_info=False):
    profile = get_profile()
    name = profile.get("name", "")
    level = profile.get("english_level")
    goal = profile.get("learning_goal")
    daily = profile.get("daily_goal_minutes", 15)

    fresh = json.loads(json.dumps(DEFAULT_PROFILE))
    fresh["created_at"] = datetime.now().isoformat(timespec="seconds")

    if keep_profile_info:
        fresh["name"] = name
        fresh["english_level"] = level
        fresh["learning_goal"] = goal
        fresh["daily_goal_minutes"] = daily
        fresh["onboarded"] = True

    st.session_state.profile = fresh
    persist()


def reset_profile_full():
    """Full reset including name/level/onboarding — returns to welcome screen."""
    fresh = json.loads(json.dumps(DEFAULT_PROFILE))
    fresh["created_at"] = datetime.now().isoformat(timespec="seconds")
    st.session_state.profile = fresh
    persist()
    st.session_state.current_page = "home"


# ----------------------------------------------------------------------
# Overall progress helpers
# ----------------------------------------------------------------------
def get_overall_progress() -> float:
    """Average of all category progress values, for the dashboard's overall bar."""
    values = [get_category_progress(c) for c in CATEGORIES]
    non_zero = [v for v in values if v > 0]
    if not non_zero:
        return 0.0
    return round(sum(non_zero) / len(non_zero), 1)


def get_weakest_category():
    """Return the category with the lowest progress (that has at least been attempted, or grammar by default)."""
    values = {c: get_category_progress(c) for c in CATEGORIES}
    attempted = {c: v for c, v in values.items() if v > 0}
    if not attempted:
        return "grammar"
    return min(attempted, key=attempted.get)
