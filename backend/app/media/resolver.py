"""
Media Resolver orchestrator with SSRF security gate.
"""
from pathlib import Path
from typing import List
from backend.app.core.security import validate_url_security
from backend.app.core.errors import UnsupportedURLError
from backend.app.media.providers.base import BaseMediaProvider, MediaInfo
from backend.app.media.providers.ytdlp_provider import (
    InstagramProvider,
    YouTubeProvider,
    TikTokProvider,
    DirectMediaProvider
)


class MediaResolver:
    def __init__(self, providers: List[BaseMediaProvider] = None):
        self.providers = providers or [
            InstagramProvider(),
            YouTubeProvider(),
            TikTokProvider(),
            DirectMediaProvider()  # Catch-all
        ]

    def get_provider(self, url: str) -> BaseMediaProvider:
        for provider in self.providers:
            if provider.can_handle(url):
                return provider
        raise UnsupportedURLError(f"No media provider could handle the URL: {url}")

    async def resolve_info(self, url: str) -> MediaInfo:
        # 1. SSRF Security Check
        clean_url = validate_url_security(url)
        # 2. Select Provider
        provider = self.get_provider(clean_url)
        # 3. Extract Metadata
        return await provider.extract_info(clean_url)

    async def resolve_and_download(self, url: str, target_dir: Path) -> MediaInfo:
        # 1. SSRF Security Check
        clean_url = validate_url_security(url)
        # 2. Select Provider
        provider = self.get_provider(clean_url)
        # 3. Download to target directory
        return await provider.download(clean_url, target_dir)


default_resolver = MediaResolver()
