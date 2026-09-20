import pytest
from backend.app.media.resolver import MediaResolver, default_resolver
from backend.app.media.providers.ytdlp_provider import (
    InstagramProvider,
    YouTubeProvider,
    TikTokProvider,
    DirectMediaProvider
)
from backend.app.core.errors import SSRFSecurityError

def test_resolver_routes_correct_provider():
    resolver = MediaResolver()

    p_ig = resolver.get_provider("https://www.instagram.com/reel/C123456/")
    assert isinstance(p_ig, InstagramProvider)

    p_yt = resolver.get_provider("https://www.youtube.com/shorts/abcdef123")
    assert isinstance(p_yt, YouTubeProvider)

    p_tk = resolver.get_provider("https://www.tiktok.com/@user/video/7123456789")
    assert isinstance(p_tk, TikTokProvider)

    p_direct = resolver.get_provider("https://example.com/videos/sample.mp4")
    assert isinstance(p_direct, DirectMediaProvider)

@pytest.mark.asyncio
async def test_resolver_rejects_ssrf_before_fetching():
    resolver = MediaResolver()
    with pytest.raises(SSRFSecurityError):
        await resolver.resolve_info("http://192.168.1.100/test.mp4")
