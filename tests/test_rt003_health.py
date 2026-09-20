from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "providers" in data

    providers = data["providers"]
    assert "sarvam" in providers
    assert "whisper" in providers
    assert "huggingface" in providers
    assert isinstance(providers["sarvam"], bool)
    assert isinstance(providers["whisper"], bool)

def test_health_no_secrets_exposed():
    # Set a dummy secret in settings to test exposure
    original_sarvam_key = settings.SARVAM_API_KEY
    original_hf_token = settings.HF_TOKEN
    try:
        settings.SARVAM_API_KEY = "sk-super-secret-sarvam-key-12345"
        settings.HF_TOKEN = "hf-super-secret-token-67890"

        resp = client.get("/health")
        content_str = resp.text

        assert "sk-super-secret-sarvam-key-12345" not in content_str
        assert "hf-super-secret-token-67890" not in content_str
        assert "secret" not in content_str.lower()
        assert "token" not in content_str.lower()
        assert "key" not in content_str.lower()

        data = resp.json()
        assert data["providers"]["sarvam"] is True
        assert data["providers"]["whisper"] is True
    finally:
        settings.SARVAM_API_KEY = original_sarvam_key
        settings.HF_TOKEN = original_hf_token
