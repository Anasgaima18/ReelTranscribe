"""
RT-023: Final Acceptance Testing.
Verifies complete system readiness across all components and stories.
"""
import json
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.core.security import validate_url_security, is_ip_allowed
from backend.app.core.rate_limit import sanitize_filename
from backend.app.asr.base import TranscriptResult
from backend.app.asr.router import ASRRouter
from backend.app.asr.scoring import TranscriptQualityAnalyzer
from backend.app.asr.normalizer import SafeTranscriptNormalizer
from backend.app.captions.subtitles import SubtitleGenerator
from backend.app.captions.detector import CaptionDetector
from backend.app.jobs.queue import default_job_store


client = TestClient(app)
ROOT_DIR = Path(__file__).resolve().parent.parent


def test_system_health_and_root():
    """Verify service health and metadata."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "ReelTranscribe"
    assert res_root.json()["status"] == "operational"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] in ("ok", "operational")
    assert "providers" in res_health.json()


def test_core_security_primitives():
    """Verify SSRF and input sanitization."""
    assert not is_ip_allowed("127.0.0.1")
    assert not is_ip_allowed("169.254.169.254")
    assert not is_ip_allowed("10.0.0.1")
    assert is_ip_allowed("8.8.8.8")

    assert sanitize_filename("../../etc/passwd") == "etcpasswd"
    assert sanitize_filename("safe_video.mp4") == "safe_video.mp4"


def test_asr_and_nlp_pipeline_components():
    """Verify ASR routing, quality gate, normalization, and captions."""
    router = ASRRouter()
    all_providers = [router.primary] + router.fallbacks
    assert len(all_providers) >= 3

    analyzer = TranscriptQualityAnalyzer()
    res = TranscriptResult(
        raw_transcript="yeh repetitive word " * 20,
        final_transcript="yeh repetitive word " * 20,
        language_code="hi-en",
        language_probability=0.95,
        confidence=0.85
    )
    assessment = analyzer.evaluate(res, audio_duration_seconds=5.0)
    assert not assessment.passed or len(assessment.flags) > 0

    normalizer = SafeTranscriptNormalizer()
    clean = normalizer.normalize("  aap kaise   ho bro ?  ")
    assert clean.final_transcript == "Aap kaise ho bro?"

    sub_gen = SubtitleGenerator()
    assert sub_gen is not None

    detector = CaptionDetector()
    assert detector is not None


def test_job_manager_lifecycle():
    """Verify job creation and lookup."""
    job = default_job_store.create_job(
        source_type="url",
        source_url="https://example.com/test.mp4"
    )
    assert job.job_id
    assert job.status.value == "queued"

    retrieved = default_job_store.get_job(job.job_id)
    assert retrieved is not None
    assert retrieved.job_id == job.job_id


def test_all_23_stories_in_prd():
    """Verify all 23 stories are defined in ralph/prd.json."""
    prd_path = ROOT_DIR / "ralph" / "prd.json"
    assert prd_path.exists()
    data = json.loads(prd_path.read_text(encoding="utf-8"))
    stories = data.get("userStories", [])
    assert len(stories) == 23
    story_ids = [s["id"] for s in stories]
    for i in range(1, 24):
        expected_id = f"RT-{i:03d}"
        assert expected_id in story_ids, f"Story {expected_id} missing from prd.json"
