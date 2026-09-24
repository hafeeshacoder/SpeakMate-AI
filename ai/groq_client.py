"""
ai/groq_client.py
--------------------
Thin wrapper around the Groq API. Used ONLY for value-added AI features:
    - grammar explanations in natural language
    - conversational/personalized feedback
    - interview follow-up questions
    - improved sentence suggestions

If GROQ_API_KEY is missing, or any API call fails for any reason, the
application MUST continue to work using local NLP only. This module never
raises exceptions to its callers — it always returns a (success, text) tuple.
"""

from config import GROQ_API_KEY, GROQ_MODEL

UNAVAILABLE_MESSAGE = (
    "AI features are unavailable right now. Local NLP features are still fully available."
)


def is_configured() -> bool:
    return bool(GROQ_API_KEY)


def _get_client():
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY)
    except Exception:
        return None


def ask_groq(system_prompt: str, user_prompt: str, max_tokens: int = 400, temperature: float = 0.6):
    """
    Send a single-turn request to the Groq API.
    Returns (success: bool, text: str). Never raises.
    """
    client = _get_client()
    if client is None:
        return False, UNAVAILABLE_MESSAGE

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            return False, UNAVAILABLE_MESSAGE
        return True, content.strip()
    except Exception:
        return False, UNAVAILABLE_MESSAGE


def explain_grammar_point(topic: str, question: str, correct_answer: str) -> str:
    """AI-generated plain-language explanation of a grammar point."""
    system = (
        "You are a friendly, encouraging English teacher speaking to a non-native learner. "
        "Explain grammar points in 2-4 simple sentences. Avoid jargon where possible."
    )
    user = (
        f"Grammar topic: {topic}\n"
        f"Question: {question}\n"
        f"Correct answer: {correct_answer}\n"
        "Explain briefly why this answer is correct, in simple, encouraging language."
    )
    ok, text = ask_groq(system, user, max_tokens=200)
    return text


def conversational_feedback(scenario: str, user_response: str) -> str:
    """AI feedback on a communication/speaking response."""
    system = (
        "You are SpeakMate, a supportive AI English coach. Give short, specific, encouraging "
        "feedback (3-5 sentences) on grammar, vocabulary, and clarity. Never sound harsh."
    )
    user = f"Scenario: {scenario}\nLearner's response: {user_response}\nGive helpful feedback."
    ok, text = ask_groq(system, user, max_tokens=300)
    return text


def interview_followup(question: str, answer: str) -> str:
    """AI-generated interview feedback and a natural follow-up question."""
    system = (
        "You are an experienced, friendly interview coach. Review the candidate's answer, give "
        "brief constructive feedback (2-3 sentences), then ask ONE natural follow-up interview "
        "question. Format clearly with 'Feedback:' and 'Follow-up question:' labels."
    )
    user = f"Interview question: {question}\nCandidate's answer: {answer}"
    ok, text = ask_groq(system, user, max_tokens=300)
    return text


def improved_sentence_suggestion(original_sentence: str) -> str:
    """AI-generated improved/more natural version of a learner's sentence."""
    system = (
        "You are an English writing coach. Rewrite the learner's sentence to sound more natural "
        "and correct, then briefly explain the key change in one sentence."
    )
    user = f"Original sentence: {original_sentence}\nProvide an improved version and a short explanation."
    ok, text = ask_groq(system, user, max_tokens=200)
    return text
