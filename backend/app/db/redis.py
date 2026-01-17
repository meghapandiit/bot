import redis
import json
from app.core.config import REDIS_URL

r = redis.from_url(REDIS_URL, decode_responses=True)

def get_session(session_id: str):
    data = r.get(session_id)
    return json.loads(data) if data else {}

def set_session(session_id: str, data: dict):
    r.set(session_id, json.dumps(data), ex=60*60*24)
