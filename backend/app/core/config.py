import os

# =========================
# LLM
# =========================
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# =========================
# STORAGE
# =========================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# =========================
# FREE PLAN
# =========================
FREE_TURNS = 5

# =========================
# PAID PLAN (CHANGE ONLY HERE)
# =========================
PAID_DURATION_MINUTES = int(os.getenv("PAID_DURATION_MINUTES", 1))
PAID_PRICE_RUPEES = int(os.getenv("PAID_PRICE_RUPEES", 1))

# =========================
# LINKS
# =========================
BOOKING_URL = "https://www.hummingmindslife.com/booktherapy"

COOLDOWN_MINUTES = 10


#payments
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

