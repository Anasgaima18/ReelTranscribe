"""
Safe Transcript Normalizer preserving spoken vocabulary and code-switching.
"""
import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class NormalizedTranscript:
    raw_transcript: str
    final_transcript: str
    postprocessing_applied: List[str] = field(default_factory=list)


class SafeTranscriptNormalizer:
    @staticmethod
    def normalize(raw_text: str) -> NormalizedTranscript:
        if not raw_text:
            return NormalizedTranscript(raw_transcript="", final_transcript="", postprocessing_applied=[])

        applied: List[str] = []
        text = raw_text

        # 1. Collapse multiple whitespace and tabs
        collapsed = re.sub(r"[ \t]+", " ", text).strip()
        if collapsed != text:
            applied.append("WHITESPACE_COLLAPSE")
            text = collapsed

        # 2. Fix space before punctuation (e.g. "word , another" -> "word, another")
        punct_spaced = re.sub(r"\s+([,\.!\?;:])", r"\1", text)
        if punct_spaced != text:
            applied.append("PUNCTUATION_SPACING_FIX")
            text = punct_spaced

        # 3. Ensure space after punctuation if missing (e.g. "word.another" -> "word. another")
        missing_space = re.sub(r"([,\.!\?;:])([A-Za-z0-9])", r"\1 \2", text)
        if missing_space != text:
            applied.append("PUNCTUATION_FOLLOWING_SPACE")
            text = missing_space

        # 4. Capitalize first letter of sentences
        def cap_sentence(m):
            return m.group(1) + m.group(2).upper()

        capitalized = re.sub(r"(^|[.!?]\s+)([a-z])", cap_sentence, text)
        if capitalized != text:
            applied.append("SENTENCE_CAPITALIZATION")
            text = capitalized

        return NormalizedTranscript(
            raw_transcript=raw_text,
            final_transcript=text,
            postprocessing_applied=applied
        )
