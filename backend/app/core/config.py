import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

FREE_TURNS = 5
PAID_MINUTES = 30
PRICE_RUPEES = 30

BOOKING_URL = "https://www.hummingmindslife.com/booktherapy"
