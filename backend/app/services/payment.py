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

'''
import razorpay
from app.core.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

def create_order(amount_rupees: int):
    order = client.order.create({
        "amount": amount_rupees * 100,  # paise
        "currency": "INR",
        "payment_capture": 1
    })
    return order
'''
