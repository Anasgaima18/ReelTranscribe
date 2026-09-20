from pathlib import Path
from PIL import Image, ImageDraw
from backend.app.captions.ocr import BurnedInCaptionDetector
from backend.app.captions.detector import CaptionDetector
from backend.app.media.probe import ContainerProbeResult

def test_visual_caption_detector_plain_frame(tmp_path):
    detector = BurnedInCaptionDetector()

    # Create plain blank image (no text/captions)
    plain_img_path = tmp_path / "plain_frame.jpg"
    img = Image.new("RGB", (640, 480), color=(100, 150, 200))
    img.save(plain_img_path)

    is_text, conf = detector.analyze_frame(plain_img_path)
    assert is_text is False
    assert conf == 0.0

def test_visual_caption_detector_frame_with_captions(tmp_path):
    detector = BurnedInCaptionDetector()

    # Create image with high-contrast text lines in the bottom 35%
    caption_img_path = tmp_path / "caption_frame.jpg"
    img = Image.new("RGB", (640, 480), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Draw high-contrast striped text-like bars in lower third (y=380 to 440)
    for y in range(370, 430, 6):
        draw.line([(80, y), (560, y)], fill=(255, 255, 255), width=3)
    img.save(caption_img_path)

    is_text, conf = detector.analyze_frame(caption_img_path)
    assert is_text is True
    assert conf > 0.0

def test_caption_detector_aggregated(tmp_path, monkeypatch):
    detector = CaptionDetector()

    # Case 1: Neither embedded nor burned in
    def mock_probe_none(path):
        return ContainerProbeResult(
            duration_seconds=5.0,
            streams=[],
            has_audio=True,
            has_video=False,
            has_embedded_subtitles=False
        )

    monkeypatch.setattr("backend.app.captions.detector.probe_media", mock_probe_none)
    dummy_file = tmp_path / "media.mp4"
    dummy_file.write_bytes(b"\x00" * 100)

    res_none = detector.detect(dummy_file)
    assert res_none.captions_detected is False
    assert res_none.caption_type == "none"

    # Case 2: Embedded subtitles detected
    def mock_probe_embedded(path):
        return ContainerProbeResult(
            duration_seconds=5.0,
            streams=[],
            has_audio=True,
            has_video=False,
            has_embedded_subtitles=True
        )

    monkeypatch.setattr("backend.app.captions.detector.probe_media", mock_probe_embedded)
    res_emb = detector.detect(dummy_file)
    assert res_emb.captions_detected is True
    assert res_emb.caption_type == "embedded"
    assert res_emb.confidence == 1.0
