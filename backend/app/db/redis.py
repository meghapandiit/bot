import os
import json
import redis

REDIS_URL = os.getenv("REDIS_URL")

# fallback in-memory store (dev mode)
_memory = {}

# create redis client once
_r = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None


def get_session(session_id: str) -> dict:
    # fallback mode
    if not _r:
        return _memory.get(session_id, {})

    data = _r.get(session_id)
    if not data:
        return {}

    try:
        return json.loads(data)
    except Exception:
        return {}


def set_session(session_id: str, session: dict):
    # fallback mode
    if not _r:
        _memory[session_id] = session
        return

    _r.set(session_id, json.dumps(session))
