from pathlib import Path
import pytest
from backend.app.asr.base import ASRProvider, TranscriptResult
from backend.app.asr.router import ASRRouter
from backend.app.core.errors import ASRRateLimitedError, ASRFailedError


class MockProvider(ASRProvider):
    def __init__(self, name: str, should_fail: bool = False, is_rate_limited: bool = False, available: bool = True):
        self.name = name
        self.should_fail = should_fail
        self.is_rate_limited = is_rate_limited
        self._available = available
        self.call_count = 0

    def is_available(self) -> bool:
        return self._available

    async def transcribe(self, audio_path: Path, language_code=None, mode=None, prompt=None) -> TranscriptResult:
        self.call_count += 1
        if self.is_rate_limited:
            raise ASRRateLimitedError(f"{self.name} rate limit reached")
        if self.should_fail:
            raise ASRFailedError(f"{self.name} failed")
        return TranscriptResult(
            raw_transcript=f"Transcript from {self.name}",
            final_transcript=f"Transcript from {self.name}",
            language_code="en",
            language_probability=0.99,
            provider_name=self.name,
            model_name="mock-model",
            fallback_used=False
        )


@pytest.mark.asyncio
async def test_router_primary_success(tmp_path):
    dummy_wav = tmp_path / "dummy.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 100)

    p1 = MockProvider("primary_sarvam")
    p2 = MockProvider("fallback_whisper")

    router = ASRRouter(primary_provider=p1, fallback_providers=[p2])
    res = await router.transcribe(dummy_wav)

    assert res.provider_name == "primary_sarvam"
    assert res.fallback_used is False
    assert p1.call_count == 1
    assert p2.call_count == 0


@pytest.mark.asyncio
async def test_router_fallback_on_rate_limit(tmp_path):
    dummy_wav = tmp_path / "dummy.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 100)

    p1 = MockProvider("primary_sarvam", is_rate_limited=True)
    p2 = MockProvider("fallback_whisper")

    router = ASRRouter(primary_provider=p1, fallback_providers=[p2], cooldown_seconds=30.0)
    res = await router.transcribe(dummy_wav)

    assert res.provider_name == "fallback_whisper"
    assert res.fallback_used is True
    assert res.metadata["provider_trail"] == ["primary_sarvam", "fallback_whisper"]
    assert p1.call_count == 1
    assert p2.call_count == 1

    # Verify primary is now in cooldown and won't be queried on immediate next call
    res2 = await router.transcribe(dummy_wav)
    assert res2.provider_name == "fallback_whisper"
    assert p1.call_count == 1  # Not called again because of cooldown!


@pytest.mark.asyncio
async def test_router_all_fail(tmp_path):
    dummy_wav = tmp_path / "dummy.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 100)

    p1 = MockProvider("primary_sarvam", should_fail=True)
    p2 = MockProvider("fallback_whisper", should_fail=True)

    router = ASRRouter(primary_provider=p1, fallback_providers=[p2])
    with pytest.raises(ASRFailedError) as excinfo:
        await router.transcribe(dummy_wav)
    assert "All ASR providers failed" in str(excinfo.value)
