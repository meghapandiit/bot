import streamlit as st
import requests
import uuid
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
API_URL = "http://127.0.0.1:8000/chat"  # FastAPI backend
PAID_DURATION_MINUTES = 5

st.set_page_config(
    page_title="Humming Minds Support Bot",
    layout="centered"
)

st.title("💬 Humming Minds Support Bot")

# =========================
# SESSION STATE INIT
# =========================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "closed" not in st.session_state:
    st.session_state.closed = False

if "paid_user" not in st.session_state:
    st.session_state.paid_user = False

if "paid_started_at" not in st.session_state:
    st.session_state.paid_started_at = None

# =========================
# CHECK PAID TIMER (frontend)
# =========================
if st.session_state.paid_started_at:
    if datetime.now() > st.session_state.paid_started_at + timedelta(minutes=PAID_DURATION_MINUTES):
        st.session_state.paid_started_at = None
        st.session_state.closed = True
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⏱ Your 5-minute session has ended. You can continue anytime."
        })

# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT BOX
# =========================
user_input = None
if not st.session_state.closed:
    user_input = st.chat_input("Type your message...")

# =========================
# SEND MESSAGE
# =========================
if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_input,
        "paid_user": st.session_state.paid_user
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        data = response.json()
        reply = data.get("reply", "⚠️ No reply from backend.")

        # closure from backend
        if data.get("show_booking") and not st.session_state.paid_user:
            st.session_state.closed = True

    except Exception as e:
        reply = f"⚠️ Backend error: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # 🔴 VERY IMPORTANT: reset paid flag
    st.session_state.paid_user = False

    st.rerun()

# =========================
# CLOSURE UI
# =========================
if st.session_state.closed:
    st.markdown("---")
    st.markdown("### Take the next step")
    st.markdown("👉 [Book a session](https://www.hummingmindslife.com/booktherapy)")

    if st.button("💬 Continue (₹1 / 5 min)"):
        st.session_state.closed = False
        st.session_state.paid_user = True
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Okay 😊 I’m here. Continue."
        })
        st.rerun()

