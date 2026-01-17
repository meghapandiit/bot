import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nlp" / "intent_keywords.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    INTENT_KEYWORDS = json.load(f)


def detect_intent(text: str) -> str:
    text = text.lower()
    scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        if score > 0:
            scores[intent] = score

    if not scores:
        return "general_support"

    return max(scores, key=scores.get)
