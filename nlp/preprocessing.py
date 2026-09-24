"""
nlp/preprocessing.py
---------------------
Core, local NLP preprocessing built on NLTK. This module never crashes the
application — if an NLTK resource is missing, it is downloaded silently on
first use, and simple regex-based fallbacks are used if a download fails
(e.g., no internet access at runtime).

Implements:
    - text cleaning
    - sentence tokenization
    - word tokenization
    - lowercasing
    - stopword handling
    - lemmatization
    - POS tagging
"""

import re
import string
import functools

_NLTK_READY = False
_NLTK_ERROR = None


def _ensure_nltk_resources():
    """Download required NLTK resources once, silently, with graceful fallback."""
    global _NLTK_READY, _NLTK_ERROR
    if _NLTK_READY:
        return True
    try:
        import nltk

        resources = [
            ("tokenizers/punkt", "punkt"),
            ("tokenizers/punkt_tab", "punkt_tab"),
            ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
            ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
            ("corpora/wordnet", "wordnet"),
            ("corpora/stopwords", "stopwords"),
            ("corpora/omw-1.4", "omw-1.4"),
        ]
        for path, pkg in resources:
            try:
                nltk.data.find(path)
            except LookupError:
                try:
                    nltk.download(pkg, quiet=True)
                except Exception:
                    pass
        _NLTK_READY = True
        return True
    except Exception as e:  # pragma: no cover
        _NLTK_ERROR = str(e)
        _NLTK_READY = False
        return False


# ----------------------------------------------------------------------
# Fallback (regex-based) implementations used only if NLTK is unavailable
# ----------------------------------------------------------------------
_FALLBACK_STOPWORDS = set("""
a an the and or but if then so to of in on at for with without from by
is are was were be been being am do does did have has had this that
these those i you he she it we they my your his her its our their not
no as be can could should would will shall may might must than too
very just also about into over under again further once here there
""".split())

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z']+")


def clean_text(text: str) -> str:
    """Basic text cleaning: strip, normalize whitespace, remove stray control chars."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u200b", "")
    return text


def sentence_tokenize(text: str):
    """Split text into sentences, with a regex fallback."""
    text = clean_text(text)
    if not text:
        return []
    if _ensure_nltk_resources():
        try:
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(text)
        except Exception:
            pass
    # Fallback
    sentences = _SENT_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def word_tokenize(text: str, lowercase: bool = False):
    """Split text into word tokens (words only, punctuation excluded), with fallback."""
    text = clean_text(text)
    if not text:
        return []
    tokens = None
    if _ensure_nltk_resources():
        try:
            from nltk.tokenize import word_tokenize as nltk_word_tokenize
            raw = nltk_word_tokenize(text)
            tokens = [t for t in raw if any(c.isalpha() for c in t)]
        except Exception:
            tokens = None
    if tokens is None:
        tokens = _WORD_RE.findall(text)
    if lowercase:
        tokens = [t.lower() for t in tokens]
    return tokens


def get_stopwords():
    if _ensure_nltk_resources():
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words("english"))
        except Exception:
            pass
    return _FALLBACK_STOPWORDS


def remove_stopwords(tokens):
    sw = get_stopwords()
    return [t for t in tokens if t.lower() not in sw]


@functools.lru_cache(maxsize=1)
def _get_lemmatizer():
    if _ensure_nltk_resources():
        try:
            from nltk.stem import WordNetLemmatizer
            return WordNetLemmatizer()
        except Exception:
            return None
    return None


def _penn_to_wordnet(tag: str):
    """Convert a Penn Treebank POS tag to a WordNet POS tag for better lemmatization."""
    if tag.startswith("J"):
        return "a"
    if tag.startswith("V"):
        return "v"
    if tag.startswith("N"):
        return "n"
    if tag.startswith("R"):
        return "r"
    return "n"


def lemmatize_tokens(tokens):
    """Lemmatize a list of tokens using POS-aware WordNet lemmatization, with fallback."""
    if not tokens:
        return []
    lemmatizer = _get_lemmatizer()
    if lemmatizer is None:
        # Fallback: very light suffix stripping
        out = []
        for t in tokens:
            low = t.lower()
            for suf in ("ing", "ed", "es", "s"):
                if low.endswith(suf) and len(low) - len(suf) >= 3:
                    low = low[: -len(suf)]
                    break
            out.append(low)
        return out

    tags = pos_tag(tokens)
    lemmas = []
    for word, tag in tags:
        wn_tag = _penn_to_wordnet(tag)
        try:
            lemmas.append(lemmatizer.lemmatize(word.lower(), wn_tag))
        except Exception:
            lemmas.append(word.lower())
    return lemmas


# Simple fallback POS tagger based on common suffix/word patterns
def _fallback_pos_tag(tokens):
    tagged = []
    for t in tokens:
        low = t.lower()
        if low in ("the", "a", "an"):
            tag = "DT"
        elif low in ("is", "am", "are", "was", "were", "be", "been", "being"):
            tag = "VB"
        elif low in ("i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"):
            tag = "PRP"
        elif low.endswith("ly"):
            tag = "RB"
        elif low.endswith("ing") or low.endswith("ed"):
            tag = "VBG"
        elif low.endswith("ous") or low.endswith("ful") or low.endswith("ive") or low.endswith("al"):
            tag = "JJ"
        elif low.endswith("s") and len(low) > 3:
            tag = "NNS"
        else:
            tag = "NN"
        tagged.append((t, tag))
    return tagged


def pos_tag(tokens):
    """Return list of (word, POS tag) tuples, using NLTK's Penn Treebank tagger with fallback."""
    if not tokens:
        return []
    if _ensure_nltk_resources():
        try:
            import nltk
            return nltk.pos_tag(tokens)
        except Exception:
            pass
    return _fallback_pos_tag(tokens)


def pos_distribution(tagged_tokens):
    """Aggregate POS tags into readable categories: Nouns, Verbs, Adjectives, Adverbs, Other."""
    dist = {"Nouns": 0, "Verbs": 0, "Adjectives": 0, "Adverbs": 0, "Other": 0}
    for _, tag in tagged_tokens:
        if tag.startswith("NN"):
            dist["Nouns"] += 1
        elif tag.startswith("VB"):
            dist["Verbs"] += 1
        elif tag.startswith("JJ"):
            dist["Adjectives"] += 1
        elif tag.startswith("RB"):
            dist["Adverbs"] += 1
        else:
            dist["Other"] += 1
    return dist


def is_ready():
    """Whether NLTK resources loaded successfully (informational only)."""
    return _NLTK_READY, _NLTK_ERROR
