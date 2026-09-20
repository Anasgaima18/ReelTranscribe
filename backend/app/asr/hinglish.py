"""
Hinglish Specialist ASR Provider (Oriserve Prime/Apex and ShunyaLabs Zero-STT).
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


class HinglishProvider(ASRProvider):
    name = "hinglish_specialist"
    ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

    SUPPORTED_MODELS = [
        "Oriserve/Whisper-Hindi2Hinglish-Prime",
        "Oriserve/Whisper-Hindi2Hinglish-Apex",
        "shunyalabs/zero-stt-hinglish"
    ]

    def __init__(
        self,
        token: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.token = token or settings.HF_TOKEN
        self.model_name = model_name or settings.HINGLISH_MODEL or self.SUPPORTED_MODELS[0]

    def is_available(self) -> bool:
        return bool(settings.HF_ENABLED and self.token)

    async def transcribe(
        self,
        audio_path: Path,
        language_code: Optional[str] = None,
        mode: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptResult:
        if not self.is_available():
            raise ASRProviderUnavailableError("Hinglish specialist provider is disabled or missing HF_TOKEN.")

        if not audio_path.exists():
            raise ASRFailedError(f"Audio file does not exist: {audio_path}")

        url = f"{self.ROUTER_BASE}/{self.model_name}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "audio/wav"
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()

                response = await client.post(
                    url,
                    headers=headers,
                    content=audio_bytes
                )
        except httpx.TimeoutException:
            raise ASRProviderUnavailableError("Hinglish specialist API request timed out.")
        except Exception as e:
            raise ASRFailedError(f"Network error calling Hinglish specialist API: {str(e)}")

        if response.status_code == 429:
            raise ASRRateLimitedError("Hinglish API rate limit reached.")
        elif response.status_code in (401, 403):
            raise ASRProviderUnavailableError("Hinglish API authorization failed.")
        elif response.status_code == 503:
            raise ASRProviderUnavailableError("Hinglish specialist model is loading on HF Inference.")
        elif response.status_code >= 500:
            raise ASRProviderUnavailableError(f"Hinglish specialist server error: {response.status_code}")
        elif response.status_code != 200:
            raise ASRFailedError(f"Hinglish specialist returned status {response.status_code}: {response.text}")

        res_json = response.json()
        raw_text = ""
        chunks: List[TranscriptChunk] = []

        if isinstance(res_json, dict):
            raw_text = res_json.get("text", "")
            raw_chunks = res_json.get("chunks", [])
            for c in raw_chunks:
                timestamps = c.get("timestamp", (0.0, 0.0))
                start = float(timestamps[0]) if timestamps and timestamps[0] is not None else 0.0
                end = float(timestamps[1]) if len(timestamps) > 1 and timestamps[1] is not None else start + 1.0
                chunks.append(
                    TranscriptChunk(
                        text=c.get("text", "").strip(),
                        start_time=start,
                        end_time=end
                    )
                )
        elif isinstance(res_json, list) and len(res_json) > 0:
            raw_text = res_json[0].get("generated_text", res_json[0].get("text", ""))

        return TranscriptResult(
            raw_transcript=raw_text.strip(),
            final_transcript=raw_text.strip(),
            language_code="hi-en",
            language_probability=0.96,
            chunks=chunks,
            provider_name=self.name,
            model_name=self.model_name,
            confidence=0.96,
            fallback_used=True,
            metadata={"specialization": "code_mixing_hinglish"}
        )
