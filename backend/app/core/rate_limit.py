"""
Application rate limiting and input sanitization defenses.
"""
import re
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.config import settings
from backend.app.core.errors import RateLimitExceededError


class SlidingWindowRateLimiter:
    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_key: str, max_requests: int) -> bool:
        now = time.time()
        window_start = now - self.window_seconds

        # Prune older entries
        req_times = [t for t in self._requests[client_key] if t > window_start]
        self._requests[client_key] = req_times

        if len(req_times) >= max_requests:
            return False

        self._requests[client_key].append(now)
        return True


default_rate_limiter = SlidingWindowRateLimiter()


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes arbitrary filenames, stripping path traversal sequences, null bytes, and unsafe characters.
    """
    if not filename:
        return "unnamed_media"
    cleaned = filename.replace("\0", "")
    if "\\" in cleaned:
        cleaned = cleaned.split("\\")[-1]
    # Remove traversal sequences
    cleaned = cleaned.replace("../", "").replace("..", "")
    # Remove forward slashes
    cleaned = cleaned.replace("/", "")
    # Whitelist safe characters
    cleaned = re.sub(r"[^a-zA-Z0-9_\.\-]", "_", cleaned)
    return cleaned[:100] or "sanitized_media"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exempt health endpoint from rate limiting
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown_client"
        auth_header = request.headers.get("authorization", "")
        key = auth_header if auth_header else client_ip

        if not default_rate_limiter.is_allowed(key, settings.RATE_LIMIT_PER_MINUTE):
            err = RateLimitExceededError()
            return err.to_response()

        return await call_next(request)
