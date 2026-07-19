"""In-memory session-based key store with TTL."""

import time
import uuid

TTL_SECONDS = 86400  # 24 hours

_store: dict[str, dict] = {}


def create_session(provider: str, api_key: str, model: str | None = None, base_url: str | None = None) -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "provider": provider,
        "api_key": api_key,
        "model": model or "",
        "base_url": base_url or "",
        "created_at": time.time(),
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    data = _store.get(session_id)
    if data is None:
        return None
    if time.time() - data["created_at"] > TTL_SECONDS:
        del _store[session_id]
        return None
    return data


def clear_session(session_id: str) -> None:
    _store.pop(session_id, None)


def cleanup_expired() -> int:
    now = time.time()
    expired = [sid for sid, data in _store.items() if now - data["created_at"] > TTL_SECONDS]
    for sid in expired:
        del _store[sid]
    return len(expired)
