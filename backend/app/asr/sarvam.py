"""
Sarvam AI Saaras v4 Speech-to-Text Provider.
"""
from pathlib import Path
from typing import Optional, List
import httpx

from backend.app.config import settings
from backend.app.core.errors import (
    ASRProviderUnavailableError,
    ASRRateLimitedError,
    ASRFailedError
)
from backend.app.asr.base import ASRProvider, TranscriptResult, TranscriptChunk


class SarvamProvider(ASRProvider):
    name = "sarvam"
    ENDPOINT = "https://api.sarvam.ai/speech-to-text"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        default_mode: Optional[str] = None
    ):
        self.api_key = api_key if api_key is not None else settings.SARVAM_API_KEY
        self.model = model or settings.SARVAM_MODEL or "saaras:v4"
        self.default_mode = default_mode or settings.SARVAM_MODE or "codemix"

    def is_available(self) -> bool:
        return bool(settings.SARVAM_ENABLED and self.api_key)

    async def transcribe(
        self,
        audio_path: Path,
        language_code: Optional[str] = None,
        mode: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptResult:
        if not self.is_available():
            raise ASRProviderUnavailableError("Sarvam provider is disabled or missing SARVAM_API_KEY.")

        if not audio_path.exists():
            raise ASRFailedError(f"Audio file does not exist: {audio_path}")

        lang = language_code or "unknown"
        target_mode = mode or self.default_mode

        headers = {
            "api-subscription-key": self.api_key
        }

        data = {
            "model": self.model,
            "mode": target_mode,
            "language_code": lang,
            "with_timestamps": "true"
        }
        if prompt:
            data["prompt"] = prompt

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                with open(audio_path, "rb") as f:
                    files = {
                        "file": (audio_path.name, f, "audio/wav")
                    }
                    response = await client.post(
                        self.ENDPOINT,
                        headers=headers,
                        data=data,
                        files=files
                    )
        except httpx.TimeoutException:
            raise ASRProviderUnavailableError("Sarvam API request timed out.")
        except Exception as e:
            raise ASRFailedError(f"Network error calling Sarvam API: {str(e)}")

        if response.status_code == 429:
            raise ASRRateLimitedError("Sarvam API rate limit exceeded.")
        elif response.status_code in (401, 403):
            raise ASRProviderUnavailableError("Sarvam API authentication failed.")
        elif response.status_code >= 500:
            raise ASRProviderUnavailableError(f"Sarvam API server error: {response.status_code}")
        elif response.status_code != 200:
            raise ASRFailedError(f"Sarvam API returned error {response.status_code}: {response.text}")

        res_json = response.json()
        raw_text = res_json.get("transcript", "")
        detected_lang = res_json.get("language_code", lang)
        lang_prob = float(res_json.get("language_probability", 0.95))

        chunks: List[TranscriptChunk] = []
        raw_chunks = res_json.get("timestamps", [])
        for c in raw_chunks:
            chunks.append(
                TranscriptChunk(
                    text=c.get("text", "").strip(),
                    start_time=float(c.get("start_time_seconds", 0.0)),
                    end_time=float(c.get("end_time_seconds", 0.0))
                )
            )

        return TranscriptResult(
            raw_transcript=raw_text,
            final_transcript=raw_text,
            language_code=detected_lang,
            language_probability=lang_prob,
            chunks=chunks,
            provider_name=self.name,
            model_name=self.model,
            confidence=lang_prob,
            metadata={"mode": target_mode}
        )
