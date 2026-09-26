"""
app/core/client_ip.py
---------------------
Resolve the real client IP for rate limiting and session metadata.

X-Forwarded-For is client-controlled: a caller can send "X-Forwarded-For: 1.2.3.4"
and the proxy just appends the real address after it. Taking the leftmost entry
therefore lets anyone pick their own rate-limit bucket. We trust only the entry
appended by our own proxy chain (TRUSTED_PROXY_COUNT hops from the right).
"""

from __future__ import annotations

from fastapi import Request

from app.core.config import get_settings


def get_client_ip(request: Request) -> str:
    peer = request.client.host if request.client else "unknown"
    hops = get_settings().TRUSTED_PROXY_COUNT
    if hops <= 0:
        return peer

    header = request.headers.get("x-forwarded-for")
    if not header:
        return peer

    parts = [p.strip() for p in header.split(",") if p.strip()]
    if not parts:
        return peer
    if len(parts) < hops:
        return parts[0]
    return parts[-hops]
