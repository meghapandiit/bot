import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nlp" / "safety_keywords.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    SAFETY_KEYWORDS = json.load(f)

def check_risk(text: str) -> str:
    text = text.lower()

    for category, phrases in SAFETY_KEYWORDS.items():
        for phrase in phrases:
            if phrase in text:
                return "high"

    return "low"
