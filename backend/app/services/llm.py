from openai import OpenAI
from app.core.prompts import FREE_SUPPORT_PROMPT, PAID_SUPPORT_PROMPT
from app.core.config import OPENAI_MODEL
from app.services.memory import get_memory
from app.db.redis import get_session
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
client = OpenAI()


def is_night_time():
    hour = datetime.now().hour
    return hour >= 22 or hour <= 5


def format_memory(memory: dict) -> str:
    if not memory:
        return "No previous context."

    parts = []
    for k in ["people", "themes", "emotions"]:
        if memory.get(k):
            parts.append(f"{k.capitalize()}: {', '.join(memory[k])}")

    if memory.get("language"):
        parts.append(f"Language: {memory['language']}")
    if memory.get("mode"):
        parts.append(f"Mode: {memory['mode']}")
    if memory.get("state"):
        parts.append(f"State: {memory['state']}")
    if memory.get("night_stress"):
        parts.append("Night stress detected")

    return " | ".join(parts)


def generate_session_summary(memory: dict) -> str:
    summary = []
    if memory.get("themes"):
        summary.append(f"Themes: {', '.join(memory['themes'])}")
    if memory.get("emotions"):
        summary.append(f"Emotions: {', '.join(memory['emotions'])}")
    if memory.get("state") == "panic":
        summary.append("Panic occurred")
    if memory.get("night_stress"):
        summary.append("Night stress pattern")
    return " | ".join(summary) if summary else "No strong pattern yet."


def generate_reply(
    session_id: str,
    user_text: str,
    paid_user: bool,
    intent: str = None,
    distress: str = None,
    technique: dict = None
) -> str:

    session = get_session(session_id)
    history = session.get("history", [])
    memory = get_memory(session_id)

    if paid_user and memory.get("pending_request"):
        user_text = memory["pending_request"]
        memory["pending_request"] = None

    system_prompt = PAID_SUPPORT_PROMPT if paid_user else FREE_SUPPORT_PROMPT

    sleep_mode = is_night_time() and memory.get("night_stress")
    panic_mode = memory.get("state") == "panic"
    casual_mode = memory.get("mode") == "casual"

    user_prompt = f"""
User message:
"{user_text}"

Session summary:
{generate_session_summary(memory)}

Context:
{format_memory(memory)}

Intent: {intent}
Distress: {distress}
Technique: {technique.get("technique") if technique else "None"}

Modes:
Casual={casual_mode}, Panic={panic_mode}, Sleep={sleep_mode}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.6,
        messages=messages
    )

    return response.choices[0].message.content.strip()
