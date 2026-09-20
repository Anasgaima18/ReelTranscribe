"""
Conditional Subtitle Generator producing valid SRT and WebVTT files.
"""
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import List, Tuple, Optional
import textwrap
import srt
import webvtt

from backend.app.asr.base import TranscriptChunk


@dataclass
class SubtitleConfig:
    max_chars_per_line: int = 42
    max_lines: int = 2
    min_duration_seconds: float = 0.8
    max_duration_seconds: float = 7.0


class SubtitleGenerator:
    def __init__(self, config: Optional[SubtitleConfig] = None):
        self.config = config or SubtitleConfig()

    def format_cue_text(self, text: str) -> str:
        """
        Splits text into lines respecting max_chars_per_line and max_lines.
        Preserves Unicode, Devanagari, and special scripts without corrupting characters.
        """
        lines = textwrap.wrap(
            text.strip(),
            width=self.config.max_chars_per_line,
            break_long_words=False,
            break_on_hyphens=False
        )
        if len(lines) > self.config.max_lines:
            lines = lines[:self.config.max_lines]
        return "\n".join(lines)

    def generate(
        self,
        chunks: List[TranscriptChunk],
        captions_detected: bool,
        output_dir: Path,
        base_name: str = "captions"
    ) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Generates SRT and VTT files ONLY if captions_detected is True.
        Returns (srt_path, vtt_path) if generated, else (None, None).
        """
        # STRICT REQUIREMENT: Only generate subtitles when original captions exist
        if not captions_detected:
            return None, None

        if not chunks:
            return None, None

        output_dir.mkdir(parents=True, exist_ok=True)
        srt_items: List[srt.Subtitle] = []

        last_end = 0.0

        for idx, chunk in enumerate(chunks, start=1):
            start_sec = max(chunk.start_time, last_end)
            end_sec = max(chunk.end_time, start_sec + self.config.min_duration_seconds)

            # Cap max duration
            if end_sec - start_sec > self.config.max_duration_seconds:
                end_sec = start_sec + self.config.max_duration_seconds

            last_end = end_sec

            cue_text = self.format_cue_text(chunk.text)
            if not cue_text:
                continue

            sub_item = srt.Subtitle(
                index=idx,
                start=timedelta(seconds=start_sec),
                end=timedelta(seconds=end_sec),
                content=cue_text
            )
            srt_items.append(sub_item)

        if not srt_items:
            return None, None

        # 1. Compose and write SRT
        srt_content = srt.compose(srt_items)
        srt_path = output_dir / f"{base_name}.srt"
        srt_path.write_text(srt_content, encoding="utf-8")

        # 2. Write WebVTT
        vtt_path = output_dir / f"{base_name}.vtt"
        # Convert SRT items to WebVTT format
        vtt = webvtt.WebVTT()
        for item in srt_items:
            # Format timedelta to HH:MM:SS.mmm
            def td_to_vtt_time(td: timedelta) -> str:
                total_seconds = int(td.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                millis = td.microseconds // 1000
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"

            caption = webvtt.Caption(
                start=td_to_vtt_time(item.start),
                end=td_to_vtt_time(item.end),
                text=item.content.split("\n")
            )
            vtt.captions.append(caption)

        vtt.save(str(vtt_path))

        return srt_path, vtt_path


default_subtitle_generator = SubtitleGenerator()
