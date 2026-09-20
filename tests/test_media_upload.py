import io
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_upload_valid_audio():
    # 1KB dummy audio
    dummy_wav = b"RIFF" + b"\x00" * 1000
    files = {"file": ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")}
    resp = client.post("/v1/media/upload", files=files)
    assert resp.status_code == 201
    data = resp.json()
    assert "upload_id" in data
    assert data["filename"] == "sample.wav"
    assert data["extension"] == ".wav"
    assert data["size_bytes"] == len(dummy_wav)
    assert Path(data["file_path"]).is_file()

    # Clean up generated test file
    Path(data["file_path"]).unlink(missing_ok=True)
    Path(data["file_path"]).parent.rmdir()

def test_upload_unsupported_extension():
    files = {"file": ("malicious.exe", io.BytesIO(b"MZ..."), "application/octet-stream")}
    resp = client.post("/v1/media/upload", files=files)
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "UNSUPPORTED_URL"
    assert "Unsupported file extension" in data["error"]["message"]

def test_upload_exceeding_size_limit():
    original_limit = settings.MAX_FILE_SIZE_MB
    try:
        # Temporarily set limit to 0 MB (exceeds anything over 0)
        settings.MAX_FILE_SIZE_MB = 0
        dummy_data = b"X" * 1024 * 1024
        files = {"file": ("huge.mp4", io.BytesIO(dummy_data), "video/mp4")}
        resp = client.post("/v1/media/upload", files=files)
        assert resp.status_code == 413
        data = resp.json()
        assert data["error"]["code"] == "MEDIA_TOO_LARGE"
    finally:
        settings.MAX_FILE_SIZE_MB = original_limit
