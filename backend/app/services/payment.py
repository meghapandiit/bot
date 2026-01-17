import time
from app.db.redis import get_session, set_session
from app.core.config import PAID_MINUTES

def start_paid_session(session_id):
    session = get_session(session_id)
    session["paid_active"] = True
    session["paid_until"] = time.time() + PAID_MINUTES * 60
    set_session(session_id, session)

def is_paid_active(session_id):
    session = get_session(session_id)
    return session.get("paid_active") and time.time() < session.get("paid_until", 0)
