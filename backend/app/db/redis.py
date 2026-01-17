import os

REDIS_URL = os.getenv("REDIS_URL")

# fallback memory
_memory = {}

def get_session(session_id: str) -> dict:
    if not REDIS_URL:
        return _memory.get(session_id, {})

    import redis
    r = redis.from_url(REDIS_URL, decode_responses=True)
    data = r.get(session_id)
    return eval(data) if data else {}


def set_session(session_id: str, session: dict):
    if not REDIS_URL:
        _memory[session_id] = session
        return

    import redis
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.set(session_id, str(session))
