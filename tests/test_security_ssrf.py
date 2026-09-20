import pytest
from backend.app.core.security import validate_url_security, is_ip_allowed
from backend.app.core.errors import (
    InvalidURLError,
    UnsupportedURLError,
    SSRFSecurityError
)

def test_ip_range_checks():
    # Private / Local IPs must be rejected
    assert is_ip_allowed("127.0.0.1") is False
    assert is_ip_allowed("10.0.0.1") is False
    assert is_ip_allowed("172.16.0.1") is False
    assert is_ip_allowed("192.168.1.1") is False
    assert is_ip_allowed("169.254.169.254") is False
    assert is_ip_allowed("::1") is False

    # Public IPs must be accepted
    assert is_ip_allowed("8.8.8.8") is True
    assert is_ip_allowed("1.1.1.1") is True
    assert is_ip_allowed("142.250.190.46") is True

def test_blocked_schemes():
    with pytest.raises(UnsupportedURLError):
        validate_url_security("ftp://example.com/video.mp4")

    with pytest.raises(UnsupportedURLError):
        validate_url_security("file:///etc/passwd")

    with pytest.raises(UnsupportedURLError):
        validate_url_security("gopher://127.0.0.1:70")

def test_blocked_hostnames_and_ssrf():
    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://localhost:8000/media")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://127.0.0.1/video.mp4")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://169.254.169.254/latest/meta-data/")

    with pytest.raises(SSRFSecurityError):
        validate_url_security("http://metadata.google.internal/computeMetadata/v1/")

def test_empty_and_malformed():
    with pytest.raises(InvalidURLError):
        validate_url_security("")

    with pytest.raises(InvalidURLError):
        validate_url_security("not a url")
