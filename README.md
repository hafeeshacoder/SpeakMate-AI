# 🗣️ SpeakMate AI

**Your Personal AI English Learning & Communication Coach**

SpeakMate AI is a Streamlit-based NLP application that helps students and job
seekers improve grammar, sentence formation, vocabulary, everyday
communication, speaking, and interview skills — with real, locally-computed
NLP analysis and optional AI-powered feedback via Groq.

---

## 1. Project Overview

SpeakMate AI is a single-user, database-free English learning app. A learner
selects an English level (Beginner → Advanced) purely for personalization —
**no feature is ever locked**. The app tracks XP, streaks, gamified levels,
and achievements locally using `st.session_state` and JSON files, and
performs genuine local NLP processing (not just an AI chatbot wrapper).

## 2. Objectives

- Give learners a safe space to practice grammar, vocabulary, sentence
  building, everyday communication, speaking, and interview answers.
- Demonstrate real, working NLP techniques (tokenization, POS tagging,
  lemmatization, TF-IDF, cosine similarity, readability, rule-based grammar
  checking) rather than relying purely on an external AI API.
- Provide transparent, explainable scoring — every score's formula is
  visible in the code and documented here.
- Work reliably with zero setup complexity: no database, no login, no
  mandatory API key.

## 3. Features

- **Home Dashboard** — greeting, XP, SpeakMate level, streak, daily goal,
  per-category progress bars, and a personalized "Today's Recommendation".
- **Grammar** — 185 questions across Foundation, Tenses, and Other Grammar
  categories (parts of speech, all 12 tenses, subject-verb agreement, active/
  passive voice, direct/indirect speech, conditionals, and more).
- **Sentence Formation** — 50 exercises: word arranging, sentence correction,
  positive↔negative, statement↔question, tense change, sentence completion,
  and situation-based writing, with NLP-based comparison for free-text answers.
- **Vocabulary** — 105+ words across 7 categories, with Word of the Day,
  flashcards, and a multiple-choice quiz. Learned words are tracked.
- **Communication** — 14 real-life scenarios (self-introduction, workplace,
  shopping, agreeing/disagreeing, etc.) with free-text response analysis.
- **Speaking Practice** — 32 topics with an optional microphone recorder
  (for the learner's own playback only) and full text-based analysis that
  always works, even if the microphone is unavailable or denied.
- **Interview Preparation** — 30 HR questions + 9 technical communication
  topics (Python, SQL, AI, ML, NLP, projects, etc.), each with a scored
  analysis and optional AI follow-up question.
- **NLP Analyzer** — a dedicated page for deep-diving into any paragraph:
  tokenization, POS distribution, lemmatization, TF-IDF keywords, optional
  cosine similarity to a reference text, readability, filler/repeated word
  detection, and rule-based grammar observations.
- **My Progress** — a full dashboard with charts, category scores, streaks,
  and achievement summary.
- **Achievements** — 10 real, activity-based achievements.
- **Settings** — change name/level/goal, and reset progress or profile with
  confirmation.

## 4. NLP Techniques Used (all implemented locally in `nlp/`)

- Text cleaning & normalization
- Sentence and word tokenization (NLTK, with regex fallback)
- Stopword removal
- POS-aware lemmatization (WordNet)
- Part-of-speech tagging and distribution
- Vocabulary diversity (type-token ratio)
- Repeated word and filler word detection
- Keyword extraction (POS-based + TF-IDF)
- TF-IDF vectorization and cosine similarity (scikit-learn)
- Readability scoring (`textstat`, with a heuristic fallback)
- Rule-based grammar checking (subject-verb agreement, auxiliary usage,
  article usage, preposition usage, pronoun usage, sentence structure)

All NLTK resources are downloaded automatically and safely on first use; if
a download ever fails (e.g., no internet at runtime), lightweight fallback
logic keeps every feature working without crashing.

## 5. Technology Stack

- Python 3.10+
- Streamlit (UI)
- NLTK (tokenization, POS tagging, lemmatization, stopwords)
- scikit-learn (TF-IDF, cosine similarity)
- textstat (readability)
- Groq API (optional AI feedback)
- JSON + `st.session_state` (no database)

## 6. Project Structure

```
SpeakMate-AI/
│
├── app.py                     # Main entry point & router
├── config.py                  # Central configuration & constants
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── pages/                     # One module per app section
│   ├── home.py
│   ├── grammar.py
│   ├── sentence_formation.py
│   ├── vocabulary.py
│   ├── communication.py
│   ├── speaking.py
│   ├── interview.py
│   ├── nlp_analyzer.py
│   ├── progress.py
│   ├── achievements.py
│   └── settings.py
│
├── nlp/                        # Local NLP engine
│   ├── preprocessing.py
│   ├── grammar_checker.py
│   ├── sentence_analyzer.py
│   ├── vocabulary_analyzer.py
│   ├── similarity.py
│   └── scoring.py
│
├── ai/
│   └── groq_client.py          # Optional Groq wrapper (graceful fallback)
│
├── data/                       # Real learning content (JSON)
│   ├── grammar_questions.json
│   ├── sentence_questions.json
│   ├── vocabulary.json
│   ├── communication_topics.json
│   ├── speaking_topics.json
│   ├── interview_questions.json
│   ├── progress.json           # created automatically at runtime
│   └── history.json            # created automatically at runtime
│
├── utils/
│   ├── progress_manager.py     # XP, streaks, levels, achievements
│   └── helpers.py               # CSS, data loaders, small utilities
│
├── assets/
│   └── logo.svg
│
├── .streamlit/
│   └── config.toml              # Light theme configuration
│
└── tests/
    ├── test_grammar.py
    ├── test_nlp.py
    ├── test_sentence.py
    └── test_scoring.py
```

## 7. Installation

```bash
# 1. Extract the ZIP and move into the folder
cd SpeakMate-AI

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 8. NLTK Setup

No manual setup is required. The first time `nlp/preprocessing.py` runs, it
automatically checks for and downloads the required NLTK resources
(`punkt`, `punkt_tab`, `averaged_perceptron_tagger`,
`averaged_perceptron_tagger_eng`, `wordnet`, `stopwords`, `omw-1.4`). If a
resource is already present, or if downloading fails (e.g., offline), the
app falls back to lightweight built-in logic instead of crashing.

## 9. Groq API Setup (optional)

SpeakMate AI works **fully without a Groq key** — every local NLP feature
(grammar checking, scoring, vocabulary, sentence formation, the NLP
Analyzer) works with zero configuration.

To enable optional AI-powered feedback:

1. Get a free API key at https://console.groq.com/keys
2. Copy `.env.example` to `.env`
3. Add your key:
   ```
   GROQ_API_KEY=your_actual_key_here
   ```

If the key is missing or a request fails for any reason, the app shows a
friendly message ("AI features are unavailable. Local NLP features are
still available.") and continues working normally.

## 10. Running Locally

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## 11. Deploying to Streamlit Cloud

1. Push this project to a GitHub repository (the `.env` file is git-ignored
   — never commit your real API key).
2. Go to https://share.streamlit.io and connect your repository.
3. Set the main file to `app.py`.
4. In the app's **Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_actual_key_here"
   ```
5. Deploy. Streamlit Cloud will install `requirements.txt` automatically.

**Note on persistence:** SpeakMate AI stores progress locally in
`data/progress.json` and `data/history.json` for convenience across page
refreshes. On Streamlit Cloud (and some other hosting platforms), the
container's filesystem is ephemeral and may reset on redeploys or after
periods of inactivity, so this local JSON persistence is **not guaranteed
to be permanent** in the cloud. The application is designed to work
perfectly either way — if the files are missing or reset, it simply starts
a fresh session using `st.session_state`, with no crashes or errors.

## 12. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | No | Enables optional AI-powered feedback, explanations, and follow-up questions. |
| `GROQ_MODEL` | No | Overrides the default Groq model (`llama-3.1-8b-instant`). |

## 13. How the Level System Works

There are **two separate, intentional systems**:

- **English Level** (Beginner → Advanced): chosen once during onboarding
  and editable anytime in Settings. It personalizes which topics are
  highlighted as "suggested" and never locks any content.
- **SpeakMate Level** (1–10, e.g. "First Steps" → "English Master"): a
  gamification level derived purely from total XP earned across all
  activities. See `config.SPEAKMATE_LEVELS` for exact XP thresholds.

## 14. How Scoring Works

The **SpeakMate Practice Score** is an application-specific learning score
(NOT an IELTS, TOEFL, CEFR, or any official proficiency certification). It
is a transparent weighted average, visible in `nlp/scoring.py`:

| Component | Weight |
|---|---|
| Grammar | 30% |
| Vocabulary | 20% |
| Sentence Quality | 20% |
| Topic Relevance | 20% |
| Fluency Indicators | 10% |

If no reference text is available for a given practice item, the Topic
Relevance weight is redistributed proportionally across the other four
components — a fake similarity score is never displayed.

**XP** is awarded per completed activity (Grammar +15, Vocabulary +10,
Sentence Formation +15, Communication +20, Speaking +25, Interview +30,
Daily Goal +25) and is deduplicated per activity instance so refreshing the
page does not farm XP.

## 15. Limitations

- The grammar checker is a **practical, rule-based checker** for common
  learner mistakes — it is not a professional-grade grammar engine (like
  Grammarly) and will not catch every possible error.
- The SpeakMate Practice Score is a **learning tool**, not an official
  English proficiency certification of any kind.
- Speech input is optional and used only for the learner's own playback;
  there is no built-in speech-to-text transcription, so analysis is always
  performed on typed text.
- Local JSON persistence may not survive redeploys on some cloud hosts (see
  Section 11).

## 16. Future Enhancements

- Optional speech-to-text integration for automatic transcription.
- Spaced-repetition scheduling for vocabulary review.
- Exportable progress reports (PDF/CSV).
- Multi-user support with lightweight authentication (would require
  reconsidering the "no database" constraint).
- Expanded grammar-error detection using a dependency-parsing library.

---

Built with Python, Streamlit, NLTK, and scikit-learn. No database. No
locked features. Light theme by default. 🎓
