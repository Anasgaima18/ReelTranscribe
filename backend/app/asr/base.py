"""
Base ASR Provider Interface and Dataclasses.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class TranscriptChunk:
    text: str
    start_time: float
    end_time: float


@dataclass
class TranscriptResult:
    raw_transcript: str
    final_transcript: str
    language_code: str
    language_probability: float
    chunks: List[TranscriptChunk] = field(default_factory=list)
    provider_name: str = ""
    model_name: str = ""
    confidence: float = 1.0
    fallback_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ASRProvider(ABC):
    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Returns whether provider is enabled and configured with valid credentials."""
        pass

    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        language_code: Optional[str] = None,
        mode: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> TranscriptResult:
        """Transcribes the given audio file and returns standardized TranscriptResult."""
        pass
