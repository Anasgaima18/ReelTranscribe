"""
In-memory Job Store and State Machine for ReelTranscribe.
"""
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
import time
import uuid


class JobStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    EXTRACTING_AUDIO = "extracting_audio"
    PREPROCESSING = "preprocessing"
    TRANSCRIBING = "transcribing"
    VALIDATING_TRANSCRIPT = "validating_transcript"
    DETECTING_CAPTIONS = "detecting_captions"
    GENERATING_SUBTITLES = "generating_subtitles"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRecord(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.QUEUED
    progress_percentage: int = 0
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    source_type: str = "url"  # "url" | "upload"
    source_url: Optional[str] = None
    upload_file_path: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class JobStore:
    def __init__(self):
        self._jobs: Dict[str, JobRecord] = {}

    def create_job(
        self,
        source_type: str = "url",
        source_url: Optional[str] = None,
        upload_file_path: Optional[str] = None
    ) -> JobRecord:
        job = JobRecord(
            source_type=source_type,
            source_url=source_url,
            upload_file_path=upload_file_path
        )
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self._jobs.get(job_id)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int = 0,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Optional[JobRecord]:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.status = status
        job.progress_percentage = progress
        job.updated_at = time.time()
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        return job


default_job_store = JobStore()
