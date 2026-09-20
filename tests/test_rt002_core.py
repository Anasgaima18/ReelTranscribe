import pytest
from fastapi.testclient import TestClient
from backend.app.config import settings
from backend.app.core.errors import (
    AppError,
    InvalidURLError,
    MediaNotFoundError,
    SSRFSecurityError,
    ASRFailedError
)
from backend.app.main import app

client = TestClient(app)

def test_settings_defaults():
    assert settings.APP_NAME == "ReelTranscribe"
    assert settings.MAX_FILE_SIZE_MB > 0
    assert settings.SARVAM_MODEL == "saaras:v4"
    assert settings.WHISPER_MODEL == "openai/whisper-large-v3"

def test_error_structure():
    err = InvalidURLError("Bad URL provided")
    d = err.to_dict()
    assert "error" in d
    assert d["error"]["code"] == "INVALID_URL"
    assert d["error"]["message"] == "Bad URL provided"
    assert d["error"]["retryable"] is False

    err2 = ASRFailedError("ASR timeout")
    d2 = err2.to_dict()
    assert d2["error"]["code"] == "ASR_FAILED"
    assert d2["error"]["retryable"] is True

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "ReelTranscribe"
    assert data["status"] == "operational"

def test_custom_exception_response():
    @app.get("/test-error")
    def trigger_error():
        raise SSRFSecurityError()

    resp = client.get("/test-error")
    assert resp.status_code == 403
    data = resp.json()
    assert data["error"]["code"] == "SSRF_PROHIBITED"
    assert "private or local network" in data["error"]["message"]
