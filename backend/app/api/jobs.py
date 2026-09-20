"""
Job Lifecycle Management and Polling API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, status, Path as FPath
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse

from backend.app.jobs.queue import default_job_store, JobStatus
from backend.app.jobs.worker import process_transcription_job
from backend.app.core.errors import InvalidURLError, MediaNotFoundError

router = APIRouter(prefix="/v1/jobs", tags=["Jobs"])


class JobCreateRequest(BaseModel):
    url: Optional[str] = None
    upload_file_path: Optional[str] = None
    source_type: str = "url"  # "url" | "upload"


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_transcription_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Submits a video URL or uploaded media for transcription.
    Returns 202 Accepted with job_id immediately so mobile clients don't hang.
    """
    if request.source_type == "url":
        if not request.url:
            raise InvalidURLError("A valid URL must be provided for url source_type.")
        job = default_job_store.create_job(source_type="url", source_url=request.url)
    elif request.source_type == "upload":
        if not request.upload_file_path:
            raise MediaNotFoundError("upload_file_path is required for upload source_type.")
        job = default_job_store.create_job(source_type="upload", upload_file_path=request.upload_file_path)
    else:
        raise InvalidURLError(f"Unknown source_type '{request.source_type}'. Must be 'url' or 'upload'.")

    # Enqueue background processing
    background_tasks.add_task(process_transcription_job, job.job_id)

    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress_percentage": job.progress_percentage,
        "poll_url": f"/v1/jobs/{job.job_id}",
        "result_url": f"/v1/jobs/{job.job_id}/result"
    }


@router.get("/{job_id}")
async def get_job_status(job_id: str = FPath(...)):
    """
    Polls the current status and progress of a transcription job.
    """
    job = default_job_store.get_job(job_id)
    if not job:
        raise MediaNotFoundError(f"Job with ID '{job_id}' not found.")

    response = {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress_percentage": job.progress_percentage,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }
    if job.error:
        response["error"] = job.error
    return response


@router.get("/{job_id}/result")
async def get_job_result(job_id: str = FPath(...)):
    """
    Retrieves the final structured transcription and captioning output.
    """
    job = default_job_store.get_job(job_id)
    if not job:
        raise MediaNotFoundError(f"Job with ID '{job_id}' not found.")

    if job.status == JobStatus.COMPLETED:
        return job.result
    elif job.status == JobStatus.FAILED:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": job.error or {"code": "JOB_FAILED", "message": "Job processing failed."}}
        )
    else:
        # Still processing
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "job_id": job.job_id,
                "status": job.status.value,
                "progress_percentage": job.progress_percentage,
                "message": "Job is still actively processing. Please continue polling."
            }
        )
