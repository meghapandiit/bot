from app.db.redis import get_session, set_session

# Simple keyword maps (safe + editable)
PEOPLE_KEYS = ["mom", "mother", "dad", "father", "ex", "boss", "manager", "friend", "partner"]
THEME_KEYS = ["work", "college", "money", "relationship", "family", "career", "stress"]
EMOTION_KEYS = ["sad", "anxious", "tired", "overwhelmed", "lonely", "confused", "angry"]
HINGLISH_HINTS = ["hai", "hoon", "nahi", "kya", "kyun", "kaise", "yaar"]


def detect_language(text: str):
    text = text.lower()
    for w in HINGLISH_HINTS:
        if w in text:
            return "hinglish"
    return "english"


def extract_memory(text: str) -> dict:
    text = text.lower()

    memory = {
        "people": [],
        "themes": [],
        "emotions": [],
        "language": detect_language(text)
    }

    for p in PEOPLE_KEYS:
        if p in text:
            memory["people"].append(p)

    for t in THEME_KEYS:
        if t in text:
            memory["themes"].append(t)

    for e in EMOTION_KEYS:
        if e in text:
            memory["emotions"].append(e)

    return memory


def get_memory(session_id: str) -> dict:
    return get_session(session_id).get("memory", {})


def update_memory(session_id: str, user_text: str):
    session = get_session(session_id)
    memory = session.get("memory", {
        "people": [],
        "themes": [],
        "emotions": [],
        "language": "english"
    })

    new_mem = extract_memory(user_text)

    # merge lists safely
    for key in ["people", "themes", "emotions"]:
        for item in new_mem[key]:
            if item not in memory[key]:
                memory[key].append(item)

    # always update language
    memory["language"] = new_mem["language"]

    session["memory"] = memory
    set_session(session_id, session)
