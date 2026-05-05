import re
from typing import List, Tuple

# ------------------------------------------------------------------
# Category regex patterns – each returns a tuple (category, extracted_content)
# ------------------------------------------------------------------
_CATEGORY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # identity / name
    ("identity", re.compile(r"\b(?:my name is|call me|i am|i'm)\s+([A-Za-z]+)\b", re.I)),
    # project name
    ("project", re.compile(r"\b(?:working on|building|developing|my project is|i am building)\s+([A-Za-z0-9_\-]+)\b", re.I)),
    # AI model / provider preference
    ("model", re.compile(r"\b(?:i (?:use|prefer|like) )?(?:groq|claude|gpt|openai|anthropic|gemini)\b", re.I)),
    # preferred model with "instead of" replacement detection
    ("model", re.compile(r"\b(?:i now use|i switched to|i changed to)\s+([A-Za-z0-9]+)\b", re.I)),
    # startup / business name
    ("startup", re.compile(r"\b(?:my startup is|company is|business is)\s+([A-Za-z0-9_\-]+)\b", re.I)),
    # goal / ambition
    ("goal", re.compile(r"\b(?:i want to|my goal is|i am planning to)\s+(.+?)\b[.!?]", re.I)),
    # skill / expertise
    ("skill", re.compile(r"\b(?:i am skilled at|i know|i have experience with|i am proficient in)\s+([A-Za-z0-9_\-]+)\b", re.I)),
    # location / city / country
    ("location", re.compile(r"\b(?:i live in|based in|from)\s+([A-Za-z ,]+)\b", re.I)),
]

# Helper to clean extracted strings
def _clean(text: str) -> str:
    return text.strip().strip('.!?')


def extract_memories(text: str) -> List[Tuple[str, str]]:
    """Extract (category, content) facts from a raw user message.
    The function returns a list of tuples; duplicate categories are allowed –
    the upsert logic will later replace older entries.
    """
    cleaned = _clean(text)
    if not cleaned:
        return []
    results: List[Tuple[str, str]] = []
    for category, pattern in _CATEGORY_PATTERNS:
        for match in pattern.finditer(cleaned):
            # Some patterns capture the fact in a group; others just match the keyword.
            if match.lastindex:
                fact = _clean(match.group(1))
            else:
                fact = match.group(0).strip()
            if fact:
                results.append((category, fact))
    return results
