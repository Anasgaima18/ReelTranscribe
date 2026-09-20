"""
Structured error definitions for ReelTranscribe.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> dict:
        data = {
            "error": {
                "code": self.code,
                "message": self.message,
                "retryable": self.retryable
            }
        }
        if self.details:
            data["error"]["details"] = self.details
        return data

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=self.to_dict()
        )


# Predefined concrete error classes
class InvalidURLError(AppError):
    def __init__(self, message: str = "The provided URL is invalid or malformed."):
        super().__init__(code="INVALID_URL", message=message, status_code=status.HTTP_400_BAD_REQUEST)

class UnsupportedURLError(AppError):
    def __init__(self, message: str = "The provided URL domain or scheme is not supported."):
        super().__init__(code="UNSUPPORTED_URL", message=message, status_code=status.HTTP_400_BAD_REQUEST)

class SSRFSecurityError(AppError):
    def __init__(self, message: str = "Access to private or local network resources is strictly prohibited."):
        super().__init__(code="SSRF_PROHIBITED", message=message, status_code=status.HTTP_403_FORBIDDEN)

class MediaNotFoundError(AppError):
    def __init__(self, message: str = "The requested media could not be located."):
        super().__init__(code="MEDIA_NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)

class MediaPrivateError(AppError):
    def __init__(self, message: str = "The requested media is private or requires authentication."):
        super().__init__(code="MEDIA_PRIVATE", message=message, status_code=status.HTTP_403_FORBIDDEN)

class MediaDownloadFailedError(AppError):
    def __init__(self, message: str = "Unable to retrieve the media from the source."):
        super().__init__(code="MEDIA_DOWNLOAD_FAILED", message=message, status_code=status.HTTP_502_BAD_GATEWAY, retryable=True)

class MediaTooLargeError(AppError):
    def __init__(self, message: str = "The media file exceeds the maximum allowed upload size."):
        super().__init__(code="MEDIA_TOO_LARGE", message=message, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

class MediaTooLongError(AppError):
    def __init__(self, message: str = "The media duration exceeds the maximum allowed duration."):
        super().__init__(code="MEDIA_TOO_LONG", message=message, status_code=status.HTTP_400_BAD_REQUEST)

class NoAudioError(AppError):
    def __init__(self, message: str = "The media contains no audio stream to transcribe."):
        super().__init__(code="NO_AUDIO", message=message, status_code=status.HTTP_400_BAD_REQUEST)

class AudioProcessingFailedError(AppError):
    def __init__(self, message: str = "Failed to extract or normalize audio track."):
        super().__init__(code="AUDIO_PROCESSING_FAILED", message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ASRProviderUnavailableError(AppError):
    def __init__(self, message: str = "ASR service provider is currently unavailable."):
        super().__init__(code="ASR_PROVIDER_UNAVAILABLE", message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, retryable=True)

class ASRRateLimitedError(AppError):
    def __init__(self, message: str = "ASR provider rate limit reached."):
        super().__init__(code="ASR_RATE_LIMITED", message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS, retryable=True)

class ASRFailedError(AppError):
    def __init__(self, message: str = "Speech transcription failed."):
        super().__init__(code="ASR_FAILED", message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, retryable=True)

class QualityCheckFailedError(AppError):
    def __init__(self, message: str = "Transcript failed quality validation gate."):
        super().__init__(code="QUALITY_CHECK_FAILED", message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class CaptionDetectionFailedError(AppError):
    def __init__(self, message: str = "Failed during caption detection analysis."):
        super().__init__(code="CAPTION_DETECTION_FAILED", message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubtitleGenerationFailedError(AppError):
    def __init__(self, message: str = "Failed to generate subtitle files."):
        super().__init__(code="SUBTITLE_GENERATION_FAILED", message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RateLimitExceededError(AppError):
    def __init__(self, message: str = "Client rate limit exceeded. Please wait before submitting more requests."):
        super().__init__(code="RATE_LIMIT_EXCEEDED", message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS, retryable=True)

class InternalError(AppError):
    def __init__(self, message: str = "An unexpected internal server error occurred."):
        super().__init__(code="INTERNAL_ERROR", message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, retryable=True)
