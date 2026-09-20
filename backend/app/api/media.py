"""
Direct media upload API endpoint.
"""
import uuid
import shutil
from pathlib import Path
from typing import Set
from fastapi import APIRouter, UploadFile, File, status
from backend.app.config import settings
from backend.app.core.errors import (
    MediaTooLargeError,
    UnsupportedURLError,
    AudioProcessingFailedError
)

router = APIRouter(prefix="/v1/media", tags=["Media"])

ALLOWED_EXTENSIONS: Set[str] = {
    ".mp4", ".mov", ".webm", ".m4v",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"
}

ALLOWED_MIME_PREFIXES = ("video/", "audio/", "application/ogg", "application/octet-stream")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media(file: UploadFile = File(...)):
    """
    Directly ingest video or audio file with strict format validation and size limits.
    """
    filename = file.filename or "upload.bin"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedURLError(
            f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Basic MIME validation
    content_type = (file.content_type or "").lower()
    if content_type and not any(content_type.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES):
        raise UnsupportedURLError(f"Unsupported Content-Type '{content_type}'.")

    upload_id = str(uuid.uuid4())
    upload_dir = settings.TEMP_DIR / f"upload_{upload_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_file = upload_dir / f"media{ext}"
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    total_bytes = 0

    try:
        with open(dest_file, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise MediaTooLargeError(
                        f"Uploaded file exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB."
                    )
                f_out.write(chunk)
    except MediaTooLargeError:
        # Cleanup immediately on abort
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
        raise
    except Exception as e:
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
        raise AudioProcessingFailedError(f"Failed writing uploaded media: {str(e)}")

    return {
        "upload_id": upload_id,
        "filename": filename,
        "extension": ext,
        "size_bytes": total_bytes,
        "file_path": str(dest_file)
    }
