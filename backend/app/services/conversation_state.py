from app.db.redis import get_session, set_session
from app.core.config import FREE_TURNS

def get_stage(session_id):
    session = get_session(session_id)
    turns = session.get("turns", 0) + 1
    session["turns"] = turns

    if session.get("paid_active"):
        stage = "paid"
    elif turns >= FREE_TURNS:
        stage = "closure"
    else:
        stage = ["listening", "exploration", "insight", "technique"][min(turns-1, 3)]

    session["stage"] = stage
    set_session(session_id, session)
    return stage
