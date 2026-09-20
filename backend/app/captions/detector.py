"""
Dual-mode Caption Detector for Embedded Streams and Burned-in Visual Captions.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

from backend.app.media.probe import probe_media
from backend.app.media.ffmpeg import sample_video_frames
from backend.app.captions.ocr import BurnedInCaptionDetector


@dataclass
class CaptionDetectionResult:
    captions_detected: bool
    caption_type: str  # "none" | "embedded" | "burned_in" | "both"
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)


class CaptionDetector:
    def __init__(self, visual_detector: Optional[BurnedInCaptionDetector] = None):
        self.visual_detector = visual_detector or BurnedInCaptionDetector()

    def detect(self, media_path: Path, temp_frames_dir: Optional[Path] = None) -> CaptionDetectionResult:
        if not media_path.exists():
            return CaptionDetectionResult(
                captions_detected=False,
                caption_type="none",
                confidence=0.0,
                details={"error": "Media file does not exist"}
            )

        # 1. Inspect Embedded Subtitle Streams via FFprobe
        probe = probe_media(media_path)
        has_embedded = probe.has_embedded_subtitles

        # 2. Inspect Burned-in Captions if video stream exists
        has_burned_in = False
        visual_confidence = 0.0
        frames_analyzed = 0

        if probe.has_video:
            frames_dir = temp_frames_dir or (media_path.parent / "frames_caption_check")
            frames = sample_video_frames(
                video_file=media_path,
                output_dir=frames_dir,
                fps=0.5,
                max_frames=20
            )
            frames_analyzed = len(frames)
            visual_analysis = self.visual_detector.analyze_frames(frames)
            has_burned_in = visual_analysis.has_burned_in_captions
            visual_confidence = visual_analysis.confidence

        # 3. Aggregate results
        if has_embedded and has_burned_in:
            c_type = "both"
            conf = max(0.95, visual_confidence)
            detected = True
        elif has_embedded:
            c_type = "embedded"
            conf = 1.0  # Stream existence is definitive
            detected = True
        elif has_burned_in:
            c_type = "burned_in"
            conf = visual_confidence
            detected = True
        else:
            c_type = "none"
            conf = 0.0
            detected = False

        return CaptionDetectionResult(
            captions_detected=detected,
            caption_type=c_type,
            confidence=round(conf, 3),
            details={
                "embedded_subtitles_found": has_embedded,
                "burned_in_captions_found": has_burned_in,
                "frames_analyzed": frames_analyzed
            }
        )


default_caption_detector = CaptionDetector()
