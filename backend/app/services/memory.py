from datetime import datetime, timedelta
from app.db.redis import get_session, set_session

# =========================
# KEYWORDS
# =========================
PEOPLE_KEYS = ["mom","mother","dad","father","ex","boss","manager","friend","partner"]
THEME_KEYS = ["work","college","money","relationship","family","career","stress","job"]
EMOTION_KEYS = ["sad","anxious","tired","overwhelmed","lonely","confused","angry","panic"]
HINGLISH_HINTS = ["hai","hoon","nahi","kya","kyun","kaise","yaar"]
CASUAL_HINTS = ["joke","funny","timepass","bored","meme"]
PANIC_HINTS = ["panic","panicking","ghabra","saans","heart","can't breathe"]

# =========================
# DEFAULT MEMORY (VERY IMPORTANT)
# =========================
DEFAULT_MEMORY = {
    "people": [],
    "themes": [],
    "emotions": [],
    "language": "english",
    "mode": "support",
    "state": "calm",
    "night_stress": False,
    "pending_request": None,
    "paid_started_at": None,
    "last_updated": None
}

# =========================
# HELPERS
# =========================
def normalize_memory(memory: dict) -> dict:
    """Ensures all keys exist (fixes old Redis sessions)"""
    for k, v in DEFAULT_MEMORY.items():
        memory.setdefault(k, v)
    return memory

def detect_language(text):
    return "hinglish" if any(w in text for w in HINGLISH_HINTS) else "english"

def detect_mode(text):
    return "casual" if any(w in text for w in CASUAL_HINTS) else "support"

def detect_state(text):
    return "panic" if any(w in text for w in PANIC_HINTS) else "calm"

def is_night_time():
    h = datetime.now().hour
    return h >= 22 or h <= 5

# =========================
# EXTRACT
# =========================
def extract_memory(text):
    text = text.lower()
    return {
        "people": [p for p in PEOPLE_KEYS if p in text],
        "themes": [t for t in THEME_KEYS if t in text],
        "emotions": [e for e in EMOTION_KEYS if e in text],
        "language": detect_language(text),
        "mode": detect_mode(text),
        "state": detect_state(text),
        "night_stress": is_night_time() and ("stress" in text or "panic" in text),
        "last_updated": datetime.now().isoformat()
    }

# =========================
# DECAY
# =========================
def decay_memory(memory):
    if not memory.get("last_updated"):
        return memory

    last = datetime.fromisoformat(memory["last_updated"])
    delta = datetime.now() - last

    if delta > timedelta(minutes=20):
        memory["state"] = "calm"

    if delta > timedelta(minutes=10):
        memory["mode"] = "support"

    if delta > timedelta(hours=1):
        memory["emotions"] = memory["emotions"][-2:]

    memory["last_updated"] = datetime.now().isoformat()
    return memory

# =========================
# GET
# =========================
def get_memory(session_id):
    session = get_session(session_id)
    memory = normalize_memory(session.get("memory", {}))
    return decay_memory(memory)

# =========================
# UPDATE
# =========================
def update_memory(session_id, user_text):
    session = get_session(session_id)

    memory = normalize_memory(session.get("memory", {}))
    new = extract_memory(user_text)

    # merge lists
    for k in ["people", "themes", "emotions"]:
        for i in new[k]:
            if i not in memory[k]:
                memory[k].append(i)

    # language sticky
    if new["language"] != "english":
        memory["language"] = new["language"]

    # mode switch
    if new["mode"] == "casual":
        memory["mode"] = "casual"

    # panic sticky
    if memory["state"] != "panic":
        memory["state"] = new["state"]

    # night stress sticky
    if new["night_stress"]:
        memory["night_stress"] = True

    # pending request (VERY IMPORTANT for context)
    if "joke" in user_text.lower():
        memory["pending_request"] = user_text

    memory["last_updated"] = datetime.now().isoformat()

    session["memory"] = memory
    set_session(session_id, session)
