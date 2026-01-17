from openai import OpenAI
from app.core.prompts import FREE_SUPPORT_PROMPT, PAID_SUPPORT_PROMPT
from app.core.config import OPENAI_MODEL
from app.services.memory import get_memory

client = OpenAI()


def format_memory(memory: dict) -> str:
    if not memory:
        return "No previous context."

    parts = []

    if memory.get("people"):
        parts.append(f"People mentioned: {', '.join(memory['people'])}")

    if memory.get("themes"):
        parts.append(f"Main themes: {', '.join(memory['themes'])}")

    if memory.get("emotions"):
        parts.append(f"Common emotions: {', '.join(memory['emotions'])}")

    if memory.get("language"):
        parts.append(f"Preferred language: {memory['language']}")

    return " | ".join(parts)


def generate_reply(
    session_id: str,
    user_text: str,
    paid_user: bool
) -> str:
    memory = get_memory(session_id)
    memory_context = format_memory(memory)

    system_prompt = PAID_SUPPORT_PROMPT if paid_user else FREE_SUPPORT_PROMPT

    user_prompt = f"""
User message:
"{user_text}"

Remembered context (use gently, only if relevant):
{memory_context}

Rules:
- Sound like a caring friend, not a professional
- Keep response short and natural
- Mirror language (English / Hinglish)
- Use memory naturally, never repeat it directly
- Ask at most ONE open-ended question
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.6,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()
