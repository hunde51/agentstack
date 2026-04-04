import json
import os
import re
from typing import Dict, List

import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _chat_key(user_id: str) -> str:
    return f"chat:{user_id}"


def _memory_key(user_id: str) -> str:
    return f"memory:{user_id}"


def redis_ping() -> bool:
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False


def save_message(user_id: str, role: str, content: str) -> None:
    message = {"role": role, "content": content}
    redis_client.rpush(_chat_key(user_id), json.dumps(message))


def get_chat_history(user_id: str) -> List[Dict[str, str]]:
    raw_items = redis_client.lrange(_chat_key(user_id), 0, -1)
    history: List[Dict[str, str]] = []
    for item in raw_items:
        parsed = json.loads(item)
        if isinstance(parsed, dict) and "role" in parsed and "content" in parsed:
            history.append({"role": str(parsed["role"]), "content": str(parsed["content"])})
    return history


def extract_memory(user_text: str) -> Dict[str, object]:
    updates: Dict[str, object] = {}

    name_match = re.search(r"\bmy name is\s+([A-Za-z][A-Za-z\s'-]{1,40})", user_text, re.IGNORECASE)
    if name_match:
        updates["name"] = name_match.group(1).strip()

    like_match = re.search(r"\bi like\s+(.+)", user_text, re.IGNORECASE)
    if like_match:
        value = like_match.group(1).strip().rstrip(".?!")
        if value:
            updates.setdefault("likes", [])
            updates["likes"].append(value)

    return updates


def save_memory(user_id: str, memory_update: Dict[str, object]) -> None:
    if not memory_update:
        return

    existing = get_memory(user_id)

    if "name" in memory_update:
        existing["name"] = memory_update["name"]

    if "likes" in memory_update:
        likes = existing.get("likes", [])
        for item in memory_update["likes"]:
            if item not in likes:
                likes.append(item)
        existing["likes"] = likes

    redis_client.set(_memory_key(user_id), json.dumps(existing))


def get_memory(user_id: str) -> Dict[str, object]:
    raw = redis_client.get(_memory_key(user_id))
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}
