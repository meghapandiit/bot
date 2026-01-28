from datetime import datetime, timedelta
from app.db.redis import get_session, set_session
from app.core.config import FREE_TURNS, PAID_DURATION_MINUTES, COOLDOWN_MINUTES


def get_stage(session_id):
    session = get_session(session_id)

    # =========================
    # ⏱ PAID AUTO EXPIRY (TIME BASED ONLY)
    # =========================
    if session.get("paid_active") and session.get("paid_started_at"):
        started = datetime.fromisoformat(session["paid_started_at"])
        if datetime.now() - started > timedelta(minutes=PAID_DURATION_MINUTES):
            session["paid_active"] = False
            session["paid_started_at"] = None
            session["turns"] = FREE_TURNS
            session["cooldown_until"] = (
                datetime.now() + timedelta(minutes=COOLDOWN_MINUTES)
            ).isoformat()
            session["stage"] = "closure"
            set_session(session_id, session)
            return "closure"

    # =========================
    # PAID SESSION → NO TURN COUNTING
    # =========================
    if session.get("paid_active"):
        session["stage"] = "paid"
        set_session(session_id, session)
        return "paid"

    # =========================
    # FREE SESSION → TURN BASED
    # =========================
    turns = session.get("turns", 0) + 1
    session["turns"] = turns

    if turns >= FREE_TURNS:
        session["stage"] = "closure"
        session["cooldown_until"] = (
            datetime.now() + timedelta(minutes=COOLDOWN_MINUTES)
        ).isoformat()
    else:
        session["stage"] = ["listening", "exploration", "insight", "technique"][min(turns - 1, 3)]

    set_session(session_id, session)
    return session["stage"]
