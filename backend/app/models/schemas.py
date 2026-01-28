from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str
    paid_user: Optional[bool] = False


class ChatResponse(BaseModel):
    reply: str
    show_booking: bool = False
    booking_url: Optional[str] = None
    show_pay: bool = False

