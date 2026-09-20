"""
Provider-independent ASR Router with fallback chain and cooldown management.
"""
import time
from pathlib import Path
from typing import List, Optional, Dict
from backend.app.core.errors import ASRFailedError, ASRRateLimitedError, ASRProviderUnavailableError
from backend.app.asr.base import ASRProvider, TranscriptResult
from backend.app.asr.sarvam import SarvamProvider
from backend.app.asr.whisper import WhisperProvider
from backend.app.asr.hinglish import HinglishProvider


class ASRRouter:
    def __init__(
        self,
        primary_provider: Optional[ASRProvider] = None,
        fallback_providers: Optional[List[ASRProvider]] = None,
        cooldown_seconds: float = 60.0
    ):
        self.primary = primary_provider or SarvamProvider()
        self.fallbacks = fallback_providers if fallback_providers is not None else [
            WhisperProvider(),
            HinglishProvider()
        ]
        self.cooldown_seconds = cooldown_seconds
        self._provider_cooldowns: Dict[str, float] = {}

    def _is_in_cooldown(self, provider_name: str) -> bool:
        expiry = self._provider_cooldowns.get(provider_name, 0.0)
        return time.time() < expiry

    def _set_cooldown(self, provider_name: str, duration: Optional[float] = None) -> None:
        dur = duration if duration is not None else self.cooldown_seconds
        self._provider_cooldowns[provider_name] = time.time() + dur

    def get_candidate_providers(self) -> List[ASRProvider]:
        candidates: List[ASRProvider] = []
        all_providers = [self.primary] + self.fallbacks

        for prov in all_providers:
            if prov.is_available() and not self._is_in_cooldown(prov.name):
                candidates.append(prov)
        return candidates

    async def transcribe(
        self,
        audio_path: Path,
        language_code: Optional[str] = None,
        mode: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptResult:
        candidates = self.get_candidate_providers()
        if not candidates:
            raise ASRFailedError("No active ASR providers are currently available (all disabled or cooling down).")

        errors: List[str] = []
        provider_trail: List[str] = []

        for idx, provider in enumerate(candidates):
            provider_trail.append(provider.name)
            try:
                result = await provider.transcribe(
                    audio_path=audio_path,
                    language_code=language_code,
                    mode=mode,
                    prompt=prompt
                )
                # If we succeeded on a fallback provider (idx > 0), record fallback
                if idx > 0 or provider != self.primary:
                    result.fallback_used = True
                result.metadata["provider_trail"] = provider_trail
                return result
            except (ASRRateLimitedError, ASRProviderUnavailableError) as e:
                # Trigger temporary cooldown on rate limit or server unavail
                self._set_cooldown(provider.name)
                errors.append(f"{provider.name}: {str(e)}")
            except Exception as e:
                errors.append(f"{provider.name}: {str(e)}")

        raise ASRFailedError(f"All ASR providers failed. Errors: {'; '.join(errors)}")


default_asr_router = ASRRouter()
