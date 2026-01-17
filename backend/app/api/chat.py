from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation_state import get_stage
from app.services.memory import update_memory
from app.services.llm import generate_reply
from app.services.payment import is_paid_active
from app.services.safety import check_risk
from app.core.prompts import CLOSURE_MESSAGE
from app.core.config import BOOKING_URL
from app.core.constants import CRISIS_MESSAGE

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 🔴 1. CRISIS OVERRIDE (HARD STOP, NO LLM)
    risk = check_risk(req.message)
    if risk == "high":
        return ChatResponse(
            reply=CRISIS_MESSAGE,
            show_booking=True,
            booking_url=BOOKING_URL,
            show_pay=False
        )

    # 2️⃣ update memory from user message
    update_memory(req.session_id, req.message)

    # 3️⃣ determine stage
    stage = get_stage(req.session_id)

    # 4️⃣ check paid status
    paid_active = is_paid_active(req.session_id)

    # 5️⃣ closure (STRICT on 5th message)
    if stage == "closure" and not paid_active:
        return ChatResponse(
            reply=CLOSURE_MESSAGE,
            show_booking=True,
            booking_url=BOOKING_URL,
            show_pay=True
        )

    # 6️⃣ generate reply
    reply = generate_reply(
        session_id=req.session_id,
        user_text=req.message,
        paid_user=paid_active
    )

    return ChatResponse(reply=reply)
