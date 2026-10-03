from __future__ import annotations

import hashlib
import hmac
import secrets
import time

from config import settings

SESSION_COOKIE = "raya_session"


def create_session_token(*, now: int | None = None) -> str:
    current_time = now if now is not None else int(time.time())
    expires = current_time + settings.session_max_age
    payload = f"{expires}.{secrets.token_urlsafe(16)}"
    signature = hmac.new(
        settings.session_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}.{signature}"


def valid_session_token(token: str | None, *, now: int | None = None) -> bool:
    if not token or not settings.session_secret:
        return False
    try:
        expires_text, nonce, signature = token.split(".", maxsplit=2)
        expires = int(expires_text)
    except (TypeError, ValueError):
        return False
    current_time = now if now is not None else int(time.time())
    if not nonce or expires <= current_time:
        return False
    payload = f"{expires_text}.{nonce}"
    expected = hmac.new(
        settings.session_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(signature, expected)