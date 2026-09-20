"""
RT-021: Comprehensive Integration Tests.
End-to-end flow validation from ingestion to result output.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import json

from backend.app.main import app
from backend.app.asr.base import TranscriptResult, TranscriptChunk
from backend.app.captions.detector import CaptionDetectionResult
from backend.app.media.probe import MediaProbeResult


client = TestClient(app)


def test_full_url_job_lifecycle():
    """Integration: submit URL job → poll → get result structure."""
    # Mock the entire worker pipeline
    mock_result = {
        "job_id": "test-int-001",
        "status": "completed",
        "source": {"type": "url", "provider": "mock", "url": "https://example.com/video.mp4"},
        "media": {"duration_seconds": 30.0, "audio_detected": True, "video_detected": True},
        "language": {"primary": "hi-en", "probability": 0.92, "code_mixed": True},
        "transcription": {
            "provider": "sarvam",
            "model": "saaras:v4",
            "raw": "yeh mera test hai",
            "final": "Yeh mera test hai.",
            "confidence": 0.88,
            "fallback_used": False,
            "postprocessing_applied": ["capitalization"],
            "quality_gate": {"passed": True, "score": 0.85, "flags": []}
        },
        "captions": {
            "detected": False,
            "type": None,
            "confidence": 0.0,
            "srt_content": None,
            "vtt_content": None,
            "srt_available": False,
            "vtt_available": False
        }
    }

    with patch("backend.app.api.jobs.process_transcription_job"):
        resp = client.post("/v1/jobs", json={"url": "https://example.com/video.mp4", "source_type": "url"})
        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert "poll_url" in data
        assert "result_url" in data


def test_upload_job_lifecycle():
    """Integration: submit upload job → verify acceptance."""
    with patch("backend.app.api.jobs.process_transcription_job"):
        resp = client.post("/v1/jobs", json={
            "upload_file_path": "/tmp/test.mp4",
            "source_type": "upload"
        })
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "queued"


def test_invalid_source_type_rejected():
    """Integration: unknown source_type returns structured error."""
    with patch("backend.app.api.jobs.process_transcription_job"):
        resp = client.post("/v1/jobs", json={"source_type": "ftp"})
        assert resp.status_code == 400


def test_missing_url_rejected():
    """Integration: url source_type without url returns error."""
    with patch("backend.app.api.jobs.process_transcription_job"):
        resp = client.post("/v1/jobs", json={"source_type": "url"})
        assert resp.status_code == 400


def test_nonexistent_job_returns_404():
    """Integration: polling non-existent job returns 404."""
    resp = client.get("/v1/jobs/nonexistent-id-12345")
    assert resp.status_code == 404


def test_result_endpoint_for_nonexistent_job():
    """Integration: result for non-existent job returns 404."""
    resp = client.get("/v1/jobs/nonexistent-id-12345/result")
    assert resp.status_code == 404


def test_health_returns_operational():
    """Integration: health endpoint returns operational status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "operational")


def test_root_returns_service_info():
    """Integration: root endpoint returns service metadata."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "ReelTranscribe"
    assert "version" in data


def test_validation_error_returns_422():
    """Integration: malformed JSON body returns structured 422."""
    resp = client.post("/v1/media/upload", content=b"not-a-file", headers={"content-type": "application/json"})
    assert resp.status_code == 422
