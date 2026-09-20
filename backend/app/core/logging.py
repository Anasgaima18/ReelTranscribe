"""
Privacy-first structured JSON logging for ReelTranscribe.
Strictly omits raw audio paths, video URLs, and private transcript text from logs.
"""
import logging
import json
import time
import sys
from typing import Any, Dict, Optional


class PrivacyFilter(logging.Filter):
    """Strips sensitive fields from log records before emission."""

    REDACTED_KEYS = {
        "api_key", "token", "secret", "password", "authorization",
        "sarvam_api_key", "hf_token", "openai_api_key",
        "raw_transcript", "final_transcript", "transcript_text",
        "source_url", "media_url", "audio_path", "video_path",
        "file_path", "upload_file_path",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "data") and isinstance(record.data, dict):
            record.data = self._redact_dict(record.data)
        return True

    def _redact_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in d.items():
            if k.lower() in self.REDACTED_KEYS:
                cleaned[k] = "[REDACTED]"
            elif isinstance(v, dict):
                cleaned[k] = self._redact_dict(v)
            else:
                cleaned[k] = v
        return cleaned


class StructuredFormatter(logging.Formatter):
    """Outputs logs as single-line JSON for structured log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "data") and record.data:
            log_entry["data"] = record.data
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return json.dumps(log_entry, default=str)


def get_logger(name: str = "reeltranscribe") -> logging.Logger:
    """Returns a privacy-filtered structured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        handler.addFilter(PrivacyFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_job_event(
    logger: logging.Logger,
    event: str,
    job_id: str,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Logs a structured job lifecycle event with privacy filtering."""
    data = {"job_id": job_id, "event": event}
    if extra:
        data.update(extra)
    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn="", lno=0, msg=f"Job {event}",
        args=(), exc_info=None
    )
    record.data = data
    logger.handle(record)


default_logger = get_logger()
