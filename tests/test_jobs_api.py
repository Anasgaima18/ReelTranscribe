import asyncio
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.jobs.queue import default_job_store, JobStatus
from backend.app.jobs.worker import process_transcription_job
from backend.app.asr.base import TranscriptResult, TranscriptChunk
from backend.app.captions.detector import CaptionDetectionResult
from backend.app.media.providers.base import MediaInfo

client = TestClient(app)

def test_job_submission_and_polling():
    # 1. Submit valid job
    resp = client.post("/v1/jobs", json={"source_type": "url", "url": "https://www.instagram.com/reel/C123/"})
    assert resp.status_code == 202
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    job_id = data["job_id"]

    # 2. Poll job status
    poll_resp = client.get(f"/v1/jobs/{job_id}")
    assert poll_resp.status_code == 200
    pdata = poll_resp.json()
    assert pdata["job_id"] == job_id
    # In TestClient, background tasks execute, so it transitions to a valid state
    assert pdata["status"] in ("queued", "downloading", "completed", "failed")

    # 3. Request result endpoint returns valid HTTP response (200, 202, or 500 depending on task state)
    res_resp = client.get(f"/v1/jobs/{job_id}/result")
    assert res_resp.status_code in (200, 202, 500)

@pytest.mark.asyncio
async def test_full_worker_pipeline_execution(tmp_path, monkeypatch):
    # Setup test dummy media
    test_media = tmp_path / "test_video.mp4"
    test_media.write_bytes(b"\x00" * 2048)

    # Mock resolver
    async def mock_download(url, target_dir):
        dest = target_dir / "downloaded.mp4"
        dest.write_bytes(b"\x00" * 2048)
        return MediaInfo(
            source_url=url,
            provider_name="instagram",
            title="Test Reel",
            duration_seconds=5.0,
            file_path=dest,
            has_audio=True
        )
    monkeypatch.setattr("backend.app.media.resolver.default_resolver.resolve_and_download", mock_download)

    # Mock audio extraction
    def mock_extract(src, dst, **kwargs):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b"RIFF" + b"\x00" * 500)
        return dst
    monkeypatch.setattr("backend.app.jobs.worker.extract_normalized_audio", mock_extract)

    # Mock ASR router
    async def mock_asr(audio_path, **kwargs):
        return TranscriptResult(
            raw_transcript="Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
            final_transcript="Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
            language_code="hi-en",
            language_probability=0.98,
            chunks=[
                TranscriptChunk(text="Guys aaj hum deployment", start_time=0.0, end_time=2.0),
                TranscriptChunk(text="but production mein issue aa gaya.", start_time=2.0, end_time=4.5)
            ],
            provider_name="sarvam",
            model_name="saaras:v4",
            confidence=0.98
        )
    monkeypatch.setattr("backend.app.asr.router.default_asr_router.transcribe", mock_asr)

    # Mock Caption detector: captions detected!
    def mock_caption_detect(media_path, **kwargs):
        return CaptionDetectionResult(
            captions_detected=True,
            caption_type="burned_in",
            confidence=0.92,
            details={"frames_analyzed": 10}
        )
    monkeypatch.setattr("backend.app.captions.detector.default_caption_detector.detect", mock_caption_detect)

    # Create job in store
    job = default_job_store.create_job(source_type="url", source_url="https://www.instagram.com/reel/C123/")

    # Run worker directly
    await process_transcription_job(job.job_id)

    # Verify completed job in store
    completed_job = default_job_store.get_job(job.job_id)
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.progress_percentage == 100

    res = completed_job.result
    assert res["job_id"] == job.job_id
    assert res["status"] == "completed"
    assert res["language"]["primary"] == "hi-en"
    assert res["transcription"]["provider"] == "sarvam"
    assert "Guys aaj hum deployment" in res["transcription"]["final"]
    assert res["captions"]["detected"] is True
    assert res["captions"]["type"] == "burned_in"
    assert res["captions"]["srt_available"] is True
    assert res["captions"]["srt_content"] is not None

    # Verify query via HTTP endpoint
    http_res = client.get(f"/v1/jobs/{job.job_id}/result")
    assert http_res.status_code == 200
    assert http_res.json()["captions"]["detected"] is True
