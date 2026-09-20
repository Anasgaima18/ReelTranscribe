"""
Base Media Provider Interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class MediaInfo:
    source_url: str
    provider_name: str
    title: Optional[str]
    duration_seconds: Optional[float]
    file_path: Optional[Path] = None
    has_audio: bool = True
    metadata: Optional[Dict[str, Any]] = None


class BaseMediaProvider(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Returns True if this provider can handle the given URL."""
        pass

    @abstractmethod
    async def extract_info(self, url: str) -> MediaInfo:
        """Extracts media metadata without downloading the full payload."""
        pass

    @abstractmethod
    async def download(self, url: str, target_dir: Path) -> MediaInfo:
        """Downloads media into target_dir and returns MediaInfo with file_path set."""
        pass
