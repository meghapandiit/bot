from datetime import datetime, timedelta

def abuse_guard(session: dict, memory: dict):
    """
    Returns:
    - None → continue normally
    - dict → override response
    """

    # =========================
    # 1️⃣ Emotional dependency guard
    # =========================
    dependency_phrases = [
        "only you",
        "don't leave",
        "stay with me",
        "only place",
        "only person",
        "i need you only",
        "talk to me only"
    ]

    last_msgs = session.get("history", [])[-5:]
    text = " ".join([m["content"].lower() for m in last_msgs if m["role"] == "user"])

    score = sum(1 for p in dependency_phrases if p in text)
    session["dependency_score"] = session.get("dependency_score", 0) + score

    if session["dependency_score"] >= 3:
        return {
            "reply": "I care about you, and I’m really glad you reached out 🤍 But it’s important you also have real people around you. You don’t have to handle everything alone.",
            "force_booking": True
        }

    # =========================
    # 2️⃣ Panic loop breaker
    # =========================
    if memory.get("state") == "panic":
        panic_count = session.get("panic_count", 0) + 1
        session["panic_count"] = panic_count

        if panic_count >= 5:
            return {
                "reply": "It sounds like the panic is still very strong. At this point, talking to a real person can really help ground you. Would you like me to help you connect?",
                "force_booking": True
            }
    else:
        session["panic_count"] = 0

    # =========================
    # 3️⃣ Free abuse guard (soft)
    # =========================
    if not session.get("paid_active"):
        msg_count = session.get("free_msg_count", 0) + 1
        session["free_msg_count"] = msg_count

        if msg_count > 30:
            return {
                "reply": "Let’s take a small pause here 🤍 You’ve shared a lot, and continuing with a real person might feel more supportive now.",
                "force_booking": True
            }

    return None
