from fastapi import APIRouter, Request
from app.core.limiter import limiter
from datetime import datetime
from app.models.schemas import ChatRequest, ChatResponse
from app.services.intent import detect_intent
from app.services.distress import detect_distress
from app.services.cbt_engine import select_cbt
from app.services.safety import check_risk
from app.services.memory import update_memory
from app.services.llm import generate_reply
from app.services.conversation_state import get_stage
from app.db.redis import get_session, set_session
from app.services.abuse_guard import abuse_guard
from app.core.constants import CRISIS_MESSAGE
from app.core.config import BOOKING_URL
from app.core.prompts import CLOSURE_MESSAGE

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
@limiter.limit("30/minute")
def chat_endpoint(req: ChatRequest, request: Request):

    # =========================
    # ENSURE SESSION
    # =========================
    session = get_session(req.session_id)
    if not session:
        session = {
            "history": [],
            "memory": {},
            "turns": 0,
            "paid_active": False,
            "paid_started_at": None,
            "closure_shown": False
        }
        set_session(req.session_id, session)

    # =========================
    # RATE LIMIT BYPASS FOR PAID
    # =========================
    if session.get("paid_active"):
        request.state._rate_limit_exempt = True

    # =========================
    # CRISIS OVERRIDE
    # =========================
    if check_risk(req.message) == "high":
        return ChatResponse(
            reply=CRISIS_MESSAGE,
            show_booking=True,
            booking_url=BOOKING_URL,
            show_pay=False
        )

    # =========================
    # MEMORY UPDATE
    # =========================
    update_memory(req.session_id, req.message)

    session = get_session(req.session_id)
    memory = session.get("memory", {})

    # =========================
    # 🌿 PANIC BREATHING OVERRIDE
    # =========================
    if memory.get("state") == "panic":
        return ChatResponse(
            reply=(
                "I’m here with you 🤍\n\n"
                "Let’s slow this moment together:\n"
                "Inhale 4… hold 4… exhale 6…\n"
                "Do it once slowly with me 🌱"
            )
        )

    # =========================
    # ABUSE GUARD
    # =========================
    guard = abuse_guard(session, memory)
    set_session(req.session_id, session)

    if guard:
        return ChatResponse(
            reply=guard["reply"],
            show_booking=guard.get("force_booking", False),
            booking_url=BOOKING_URL if guard.get("force_booking") else None,
            show_pay=guard.get("force_booking", False)
        )

    # =========================
    # SAVE USER HISTORY
    # =========================
    history = session.get("history", [])
    history.append({"role": "user", "content": req.message})
    session["history"] = history[-15:]
    set_session(req.session_id, session)

    # =========================
    # SIGNAL DETECTION
    # =========================
    intent = detect_intent(req.message)
    distress = detect_distress(req.message)
    cbt = select_cbt(intent, distress)

    # =========================
    # BOOKING INTENT (ONLY WHEN ASKED)
    # =========================
    if intent == "seeking_support":
        return ChatResponse(
            reply="You can book a session here whenever you’re ready:\n👉 https://www.hummingmindslife.com/booktherapy",
            show_booking=True,
            booking_url=BOOKING_URL,
            show_pay=False
        )

    # =========================
    # START / RESTART PAID SESSION
    # =========================
    if req.paid_user:
        session["paid_active"] = True
        session["paid_started_at"] = datetime.now().isoformat()
        session["closure_shown"] = False
        set_session(req.session_id, session)

    # =========================
    # STAGE CONTROL
    # =========================
    stage = get_stage(req.session_id)

    # =========================
    # CLOSURE (ONCE PER CYCLE)
    # =========================
    if stage == "closure" and not session.get("paid_active") and not session.get("closure_shown"):
        session["closure_shown"] = True
        set_session(req.session_id, session)
        return ChatResponse(
            reply=CLOSURE_MESSAGE,
            show_booking=True,
            booking_url=BOOKING_URL,
            show_pay=True
        )

    # =========================
    # GENERATE LLM REPLY
    # =========================
    reply = generate_reply(
        session_id=req.session_id,
        user_text=req.message,
        paid_user=session.get("paid_active", False),
        intent=intent,
        distress=distress,
        technique=cbt
    )

    # =========================
    # 🌸 GRATITUDE NUDGE (SAFE)
    # =========================
    if distress == "low" and session.get("turns", 0) % 6 == 0:
        reply += "\n\n🌸 Before we continue, want to name 1 small thing you’re grateful for today?"

    # =========================
    # SAVE ASSISTANT HISTORY
    # =========================
    session = get_session(req.session_id)
    history = session.get("history", [])
    history.append({"role": "assistant", "content": reply})
    session["history"] = history[-15:]
    set_session(req.session_id, session)

    return ChatResponse(reply=reply)
