"""
Lightweight, rule-based intent detection for the chat endpoint.

Dr. Eezy's default behaviour for any message is the RAG/LLM answer pipeline in
chatbot.py. This module detects the ONE special case we short-circuit that
pipeline for: a request to generate a staff roster. Kept rule-based (regex,
not an LLM call) for the same reason as the CV parser — fast, free,
deterministic, and easy to explain live in a demo.
"""
import re
from datetime import date

ROSTER_INTENT_PATTERN = re.compile(
    r"\b(generate|create|build|make|produce)\b.{0,20}\broster\b"
    r"|\broster\b.{0,20}\b(generate|create|build|make|produce)\b",
    re.IGNORECASE,
)

DAYS_PATTERN = re.compile(r"(\d+)\s*-?\s*day", re.IGNORECASE)


def wants_roster(message: str) -> bool:
    return bool(ROSTER_INTENT_PATTERN.search(message))


def extract_roster_params(message: str) -> dict:
    """Best-effort extraction of how many days to roster for; defaults to 7
    days starting today if nothing more specific is said."""
    match = DAYS_PATTERN.search(message)
    num_days = int(match.group(1)) if match else 7
    num_days = max(1, min(num_days, 31))  # sane bounds for a demo
    return {"start_date": date.today(), "num_days": num_days}