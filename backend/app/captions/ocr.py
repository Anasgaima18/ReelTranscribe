"""
Burned-in Caption Visual OCR and Edge Detector.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    Image = None
    ImageFilter = None
    ImageOps = None

from backend.app.config import settings


@dataclass
class VisualCaptionAnalysis:
    has_burned_in_captions: bool
    confidence: float
    detected_frames_count: int
    total_frames_count: int


class BurnedInCaptionDetector:
    """
    Detects hardcoded / burned-in captions in video frames.
    Focuses analysis on the bottom 35% bounding zone (where Reels/Shorts captions appear).
    """
    def __init__(
        self,
        bottom_crop_ratio: float = 0.35,
        confidence_threshold: float = None
    ):
        self.bottom_crop_ratio = bottom_crop_ratio
        self.confidence_threshold = (
            confidence_threshold if confidence_threshold is not None
            else settings.CAPTION_CONFIDENCE_THRESHOLD
        )

    def analyze_frame(self, frame_path: Path) -> Tuple[bool, float]:
        """
        Analyzes a single frame for high-contrast, structured text blocks in the caption region.
        """
        if not frame_path.exists() or Image is None:
            return False, 0.0

        try:
            with Image.open(frame_path) as img:
                width, height = img.size
                # Crop bottom 35%
                top_y = int(height * (1.0 - self.bottom_crop_ratio))
                caption_crop = img.crop((0, top_y, width, height)).convert("L")

                # Detect high-contrast text edges
                edges = caption_crop.filter(ImageFilter.FIND_EDGES)
                # Binarize edges
                threshold = 80
                binary_edges = edges.point(lambda p: 255 if p > threshold else 0)

                # Count edge pixels
                hist = binary_edges.histogram()
                white_pixels = hist[255] if len(hist) > 255 else 0
                total_pixels = caption_crop.width * caption_crop.height
                edge_density = white_pixels / max(1, total_pixels)

                # Text in video subtitles typically has edge density between 3.5% and 22%
                # with high horizontal line consistency
                is_text_like = 0.035 <= edge_density <= 0.22
                confidence = min(1.0, edge_density * 5.0) if is_text_like else 0.0

                return is_text_like, round(confidence, 3)
        except Exception:
            return False, 0.0

    def analyze_frames(self, frame_paths: List[Path]) -> VisualCaptionAnalysis:
        if not frame_paths:
            return VisualCaptionAnalysis(
                has_burned_in_captions=False,
                confidence=0.0,
                detected_frames_count=0,
                total_frames_count=0
            )

        detected_count = 0
        total_conf = 0.0

        for p in frame_paths:
            is_caption, conf = self.analyze_frame(p)
            if is_caption:
                detected_count += 1
                total_conf += conf

        detection_ratio = detected_count / len(frame_paths)
        avg_confidence = (total_conf / detected_count) if detected_count > 0 else 0.0
        combined_confidence = round(0.5 * detection_ratio + 0.5 * avg_confidence, 3)

        has_captions = detection_ratio >= 0.25 and combined_confidence >= self.confidence_threshold

        return VisualCaptionAnalysis(
            has_burned_in_captions=has_captions,
            confidence=combined_confidence if has_captions else 0.0,
            detected_frames_count=detected_count,
            total_frames_count=len(frame_paths)
        )
