"""
RT-017: Application Security & Rate Limiting Tests.
"""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.rate_limit import (
    SlidingWindowRateLimiter,
    sanitize_filename,
    default_rate_limiter,
)


client = TestClient(app)


def test_security_headers_present():
    """Verify security headers are injected by SecurityHeadersMiddleware."""
    resp = client.get("/")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "max-age" in resp.headers.get("Strict-Transport-Security", "")


def test_rate_limiter_sliding_window():
    """Verify SlidingWindowRateLimiter blocks after threshold."""
    limiter = SlidingWindowRateLimiter(window_seconds=60.0)
    key = "test_client_ip_rt017"
    max_req = 3
    for i in range(max_req):
        assert limiter.is_allowed(key, max_req) is True
    # 4th request should be denied
    assert limiter.is_allowed(key, max_req) is False


def test_rate_limit_endpoint_exemption():
    """Health and root endpoints are exempt from rate limiting."""
    # These should always succeed regardless of rate limit state
    for _ in range(50):
        resp = client.get("/health")
        assert resp.status_code == 200
    for _ in range(50):
        resp = client.get("/")
        assert resp.status_code == 200


def test_sanitize_filename_traversal():
    """Verify path traversal and dangerous chars are stripped."""
    assert sanitize_filename("../../etc/passwd") == "etcpasswd"
    assert sanitize_filename("file\x00name.mp4") == "filename.mp4"
    assert sanitize_filename("normal_file.mp4") == "normal_file.mp4"
    assert sanitize_filename("") == "unnamed_media"
    assert sanitize_filename("a" * 200) == "a" * 100  # truncation


def test_sanitize_filename_special_chars():
    """Verify special/unicode characters are sanitized."""
    assert sanitize_filename("file name (1).mp4") == "file_name__1_.mp4"
    assert sanitize_filename("path\\to\\file.mp4") == "file.mp4"
