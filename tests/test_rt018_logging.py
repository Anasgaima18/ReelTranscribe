"""
RT-018: Observability & Privacy Logging Tests.
"""
import logging
from backend.app.core.logging import (
    PrivacyFilter,
    StructuredFormatter,
    get_logger,
    log_job_event,
)


def test_privacy_filter_redacts_sensitive_keys():
    """Verify that sensitive keys are redacted from log data."""
    pf = PrivacyFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="test", args=(), exc_info=None
    )
    record.data = {
        "job_id": "abc-123",
        "api_key": "sk-secret-123",
        "raw_transcript": "Hello world private text",
        "source_url": "https://instagram.com/reel/xyz",
        "provider": "sarvam",
        "latency_ms": 1200,
    }
    pf.filter(record)
    assert record.data["job_id"] == "abc-123"
    assert record.data["api_key"] == "[REDACTED]"
    assert record.data["raw_transcript"] == "[REDACTED]"
    assert record.data["source_url"] == "[REDACTED]"
    assert record.data["provider"] == "sarvam"
    assert record.data["latency_ms"] == 1200


def test_privacy_filter_redacts_nested():
    """Verify nested dict values are also redacted."""
    pf = PrivacyFilter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="test", args=(), exc_info=None
    )
    record.data = {
        "config": {
            "hf_token": "hf_abc123",
            "model": "whisper-large-v3",
        }
    }
    pf.filter(record)
    assert record.data["config"]["hf_token"] == "[REDACTED]"
    assert record.data["config"]["model"] == "whisper-large-v3"


def test_structured_formatter_outputs_json():
    """Verify StructuredFormatter produces valid JSON."""
    import json
    fmt = StructuredFormatter()
    record = logging.LogRecord(
        name="reeltranscribe", level=logging.INFO, pathname="", lineno=0,
        msg="Job started", args=(), exc_info=None
    )
    record.data = {"job_id": "test-001", "event": "transcribing"}
    output = fmt.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Job started"
    assert parsed["data"]["job_id"] == "test-001"


def test_get_logger_returns_configured_logger():
    """Verify get_logger returns a logger with the privacy filter."""
    logger = get_logger("test_rt018")
    assert logger.name == "test_rt018"
    assert len(logger.handlers) > 0
    filters = logger.handlers[0].filters
    assert any(isinstance(f, PrivacyFilter) for f in filters)


def test_log_job_event_no_crash():
    """Verify log_job_event runs without raising."""
    logger = get_logger("test_rt018_event")
    log_job_event(logger, "transcribing", "job-001", extra={"provider": "sarvam"})
