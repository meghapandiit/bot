from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    show_booking: bool = False
    booking_url: Optional[str] = None
    show_pay: bool = False

