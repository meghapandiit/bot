import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nlp" / "distress_keywords.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DISTRESS_KEYWORDS = json.load(f)


def detect_distress(text: str) -> str:
    text = text.lower()

    for phrase in DISTRESS_KEYWORDS["high"]:
        if phrase in text:
            return "high"

    for phrase in DISTRESS_KEYWORDS["medium"]:
        if phrase in text:
            return "medium"

    return "low"
