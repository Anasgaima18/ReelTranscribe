"""
Health check and provider status endpoint.
"""
from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health():
    """
    Returns system status and provider availability.
    Guaranteed to never expose API tokens or private credentials.
    """
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "providers": {
            "sarvam": bool(settings.SARVAM_ENABLED and settings.SARVAM_API_KEY),
            "whisper": bool(settings.HF_ENABLED and settings.HF_TOKEN),
            "huggingface": bool(settings.HF_ENABLED and settings.HF_TOKEN),
            "elevenlabs": bool(settings.ELEVENLABS_ENABLED and settings.ELEVENLABS_API_KEY),
            "openai": bool(settings.OPENAI_ENABLED and settings.OPENAI_API_KEY),
            "google": bool(settings.GOOGLE_ENABLED and settings.GOOGLE_APPLICATION_CREDENTIALS)
        }
    }
