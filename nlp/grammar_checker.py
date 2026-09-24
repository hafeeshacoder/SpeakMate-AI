"""
nlp/grammar_checker.py
------------------------
A practical, RULE-BASED grammar checker (not a professional/commercial-grade
grammar engine). It detects common learner mistakes using pattern matching
over POS tags and simple word lists.

Detects:
    - subject-verb agreement issues
    - simple tense pattern issues
    - incorrect auxiliary usage
    - article mistakes
    - common preposition mistakes
    - common pronoun mistakes
    - basic sentence structure issues
    - other common learner mistakes
"""

import re
from nlp.preprocessing import word_tokenize, pos_tag, sentence_tokenize

THIRD_PERSON_SINGULAR_PRONOUNS = {"he", "she", "it"}
PLURAL_PRONOUNS = {"i", "you", "we", "they"}

# Common irregular "be" / "have" / "do" forms used to spot auxiliary errors
BE_FORMS = {"am", "is", "are", "was", "were", "be", "been", "being"}

VOWEL_SOUND_START = re.compile(r"^[aeiou]", re.IGNORECASE)
# Words that start with a vowel LETTER but consonant SOUND (use "a")
CONSONANT_SOUND_EXCEPTIONS = {"university", "european", "one", "user", "uniform", "unicorn", "unit"}
# Words that start with a consonant LETTER but vowel SOUND (use "an")
VOWEL_SOUND_EXCEPTIONS = {"hour", "honest", "honor", "heir"}

COMMON_PREPOSITION_ERRORS = {
    ("married", "with"): ("married", "to"),
    ("good", "on"): ("good", "at"),
    ("interested", "on"): ("interested", "in"),
    ("afraid", "from"): ("afraid", "of"),
    ("depend", "of"): ("depend", "on"),
    ("listen", "music"): (None, None),  # placeholder, handled separately
}

COMMON_PRONOUN_ERRORS = [
    (re.compile(r"\bme and (\w+)\b", re.IGNORECASE), "Consider using '{1} and I' instead of 'me and {1}' as the subject of a sentence."),
    (re.compile(r"\bhim and (\w+) (is|are|was|were|went|did)\b", re.IGNORECASE), None),
]


def _find_verb_after(tagged, index):
    """Find the next verb tag after a given index in a tagged sentence."""
    for i in range(index + 1, len(tagged)):
        word, tag = tagged[i]
        if tag.startswith("VB"):
            return i, word, tag
    return None, None, None


def check_subject_verb_agreement(sentence: str):
    """Detect simple present tense subject-verb agreement issues."""
    issues = []
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    for i, (word, tag) in enumerate(tagged):
        low = word.lower()
        if low in THIRD_PERSON_SINGULAR_PRONOUNS or (tag == "NN"):
            vi, vword, vtag = _find_verb_after(tagged, i)
            if vword is None:
                continue
            vlow = vword.lower()
            # He/She/It + base form verb (missing -s) e.g. "He go"
            base_forms = {"go", "do", "have", "like", "want", "need", "play", "study",
                          "work", "eat", "run", "make", "take", "come", "get", "know",
                          "think", "see", "say", "look", "believe", "live"}
            if low in THIRD_PERSON_SINGULAR_PRONOUNS and vlow in base_forms:
                corrected = vlow + ("es" if vlow.endswith(("o", "sh", "ch", "s", "x")) else "s")
                issues.append({
                    "issue": "Subject-Verb Agreement",
                    "detail": f"'{word} {vword}' may be incorrect.",
                    "suggestion": f"Consider: '{word} {corrected}' — with he/she/it in the simple present, "
                                  f"the main verb generally takes -s/-es.",
                })
    return issues


def check_auxiliary_usage(sentence: str):
    """Detect common auxiliary verb misuse, e.g., 'He don't like'."""
    issues = []
    low = sentence.lower()
    if re.search(r"\b(he|she|it)\s+don't\b", low):
        issues.append({
            "issue": "Auxiliary Usage",
            "detail": "'He/She/It don't' is likely incorrect.",
            "suggestion": "Use 'doesn't' with he/she/it in the simple present negative form.",
        })
    if re.search(r"\bi\s+is\b", low):
        issues.append({
            "issue": "Auxiliary Usage",
            "detail": "'I is' is incorrect.",
            "suggestion": "Use 'I am' — the verb 'to be' with 'I' is always 'am'.",
        })
    if re.search(r"\b(they|we|you)\s+was\b", low):
        issues.append({
            "issue": "Auxiliary Usage",
            "detail": "Plural subjects should not be paired with 'was'.",
            "suggestion": "Use 'were' with plural subjects like they/we/you.",
        })
    if re.search(r"\bhas\s+went\b|\bhave\s+went\b", low):
        issues.append({
            "issue": "Auxiliary Usage",
            "detail": "'has/have went' is incorrect.",
            "suggestion": "Use the past participle 'gone' after have/has: 'has gone'.",
        })
    return issues


def check_article_usage(sentence: str):
    """Detect basic 'a' vs 'an' article mistakes."""
    issues = []
    tokens = sentence.split()
    for i, tok in enumerate(tokens[:-1]):
        low = tok.lower().strip(".,!?")
        nxt = tokens[i + 1].strip(".,!?").lower()
        if low == "a" and (VOWEL_SOUND_START.match(nxt) and nxt not in CONSONANT_SOUND_EXCEPTIONS):
            issues.append({
                "issue": "Article Usage",
                "detail": f"'a {nxt}' may be incorrect.",
                "suggestion": f"Use 'an {nxt}' since '{nxt}' starts with a vowel sound.",
            })
        if low == "an" and (not VOWEL_SOUND_START.match(nxt) and nxt not in VOWEL_SOUND_EXCEPTIONS):
            issues.append({
                "issue": "Article Usage",
                "detail": f"'an {nxt}' may be incorrect.",
                "suggestion": f"Use 'a {nxt}' since '{nxt}' starts with a consonant sound.",
            })
    return issues


def check_preposition_usage(sentence: str):
    """Detect a handful of common fixed-preposition mistakes."""
    issues = []
    low = sentence.lower()
    checks = [
        ("married with", "married to", "The fixed expression is 'married to', not 'married with'."),
        ("good on", "good at", "The fixed expression is 'good at' (a subject/skill), not 'good on'."),
        ("interested on", "interested in", "The fixed expression is 'interested in', not 'interested on'."),
        ("afraid from", "afraid of", "The fixed expression is 'afraid of', not 'afraid from'."),
        ("depend of", "depend on", "The fixed expression is 'depend on', not 'depend of'."),
        ("discuss about", "discuss", "'Discuss' does not need 'about' — it is directly followed by the topic."),
        ("explain me", "explain to me", "'Explain' requires 'to' before the person: 'explain to me'."),
    ]
    for wrong, right, expl in checks:
        if wrong in low:
            issues.append({"issue": "Preposition Usage", "detail": f"'{wrong}' may be incorrect.",
                            "suggestion": f"Consider '{right}'. {expl}"})
    return issues


def check_pronoun_usage(sentence: str):
    """Detect a handful of common pronoun mistakes."""
    issues = []
    low = sentence.lower()
    if re.search(r"\bme and \w+ (is|are|went|like|has|have)\b", low):
        issues.append({
            "issue": "Pronoun Usage",
            "detail": "'Me and ___' used as a subject may be incorrect.",
            "suggestion": "Use the subject pronoun 'I' — for example, '___ and I' rather than 'Me and ___'.",
        })
    if re.search(r"\bbetween you and i\b", low):
        issues.append({
            "issue": "Pronoun Usage",
            "detail": "'Between you and I' is a common mistake.",
            "suggestion": "After a preposition like 'between', use the object pronoun: 'between you and me'.",
        })
    if re.search(r"\bits a\b|\bits the\b", low) and "it's" not in low:
        issues.append({
            "issue": "Pronoun Usage",
            "detail": "'its' may be confused with 'it's'.",
            "suggestion": "Use 'it's' (it is) if you mean a contraction, not the possessive 'its'.",
        })
    return issues


def check_sentence_structure(sentence: str):
    """Detect a few very basic sentence-structure issues."""
    issues = []
    stripped = sentence.strip()
    if stripped and not stripped[0].isupper() and stripped[0].isalpha():
        issues.append({
            "issue": "Sentence Structure",
            "detail": "The sentence does not start with a capital letter.",
            "suggestion": "Begin sentences with a capital letter for standard written English.",
        })
    if stripped and stripped[-1] not in ".!?\"'":
        issues.append({
            "issue": "Sentence Structure",
            "detail": "The sentence may be missing ending punctuation.",
            "suggestion": "End sentences with a period, question mark, or exclamation mark.",
        })
    tokens = word_tokenize(stripped)
    if len(tokens) < 2:
        issues.append({
            "issue": "Sentence Structure",
            "detail": "The sentence seems too short to express a complete idea.",
            "suggestion": "Try to include a subject and a verb to form a complete sentence.",
        })
    return issues


def analyze_sentence(sentence: str):
    """Run all grammar checks on a single sentence and return combined issues."""
    issues = []
    issues += check_subject_verb_agreement(sentence)
    issues += check_auxiliary_usage(sentence)
    issues += check_article_usage(sentence)
    issues += check_preposition_usage(sentence)
    issues += check_pronoun_usage(sentence)
    issues += check_sentence_structure(sentence)
    return issues


def analyze_text(text: str):
    """Run grammar analysis across all sentences in a longer text."""
    sentences = sentence_tokenize(text)
    all_issues = []
    for sent in sentences:
        sent_issues = analyze_sentence(sent)
        for issue in sent_issues:
            issue["sentence"] = sent
        all_issues.extend(sent_issues)
    return all_issues


def grammar_score_from_issues(num_sentences: int, num_issues: int) -> float:
    """Compute a 0-100 grammar score based on issue density (used by scoring.py)."""
    if num_sentences <= 0:
        return 0.0
    issue_rate = num_issues / num_sentences
    score = max(0.0, 100.0 - (issue_rate * 25.0))
    return round(min(score, 100.0), 1)
