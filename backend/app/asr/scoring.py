"""
Transcript Quality Gate and Hallucination Analyzer.
"""
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional
from backend.app.config import settings
from backend.app.asr.base import TranscriptResult


@dataclass
class QualityAssessment:
    passed: bool
    score: float
    repetition_ratio: float
    words_per_second: Optional[float]
    flags: List[str] = field(default_factory=list)


class TranscriptQualityAnalyzer:
    def __init__(
        self,
        min_confidence: Optional[float] = None,
        max_repetition_ratio: Optional[float] = None,
        min_wps: float = 0.1,
        max_wps: float = 7.0
    ):
        self.min_confidence = min_confidence if min_confidence is not None else settings.MIN_CONFIDENCE_THRESHOLD
        self.max_repetition_ratio = (
            max_repetition_ratio if max_repetition_ratio is not None else settings.MAX_REPETITION_RATIO
        )
        self.min_wps = min_wps
        self.max_wps = max_wps

    def _calculate_repetition_ratio(self, words: List[str], n: int = 3) -> float:
        if len(words) < n * 2:
            return 0.0

        # Calculate n-gram repetition
        ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
        if not ngrams:
            return 0.0

        counts = Counter(ngrams)
        most_common_count = counts.most_common(1)[0][1]
        # Ratio of repetitions of the most common n-gram relative to total n-grams
        return (most_common_count * n) / len(words)

    def evaluate(
        self,
        transcript_result: TranscriptResult,
        audio_duration_seconds: Optional[float] = None
    ) -> QualityAssessment:
        text = transcript_result.raw_transcript.strip()
        flags: List[str] = []
        score = 1.0

        # 1. Empty transcript check
        if not text:
            return QualityAssessment(
                passed=False,
                score=0.0,
                repetition_ratio=0.0,
                words_per_second=0.0,
                flags=["EMPTY_TRANSCRIPT"]
            )

        words = re.findall(r"\w+", text.lower())
        word_count = len(words)

        if word_count == 0:
            return QualityAssessment(
                passed=False,
                score=0.0,
                repetition_ratio=0.0,
                words_per_second=0.0,
                flags=["NO_ALPHANUMERIC_WORDS"]
            )

        # 2. Check repetition loops (1-gram and 3-gram)
        rep_ratio_3 = self._calculate_repetition_ratio(words, n=3)
        rep_ratio_1 = self._calculate_repetition_ratio(words, n=1)
        max_rep = max(rep_ratio_3, rep_ratio_1)

        if max_rep > self.max_repetition_ratio:
            flags.append("ABNORMAL_REPETITION")
            score -= 0.45

        # 3. Audio duration vs word count coverage check
        wps = None
        if audio_duration_seconds and audio_duration_seconds > 0:
            wps = word_count / audio_duration_seconds
            if audio_duration_seconds > 10.0 and wps < self.min_wps:
                flags.append("SUSPICIOUSLY_LOW_SPEECH_COVERAGE")
                score -= 0.30
            elif wps > self.max_wps:
                flags.append("SUSPICIOUSLY_HIGH_TOKEN_BURST")
                score -= 0.30

        # 4. Confidence / Language probability check
        if transcript_result.confidence < self.min_confidence:
            flags.append("LOW_CONFIDENCE")
            score -= 0.25

        if transcript_result.language_probability < self.min_confidence:
            flags.append("LOW_LANGUAGE_PROBABILITY")
            score -= 0.15

        final_score = max(0.0, min(1.0, score))
        passed = final_score >= self.min_confidence and ("ABNORMAL_REPETITION" not in flags)

        return QualityAssessment(
            passed=passed,
            score=round(final_score, 3),
            repetition_ratio=round(max_rep, 3),
            words_per_second=round(wps, 2) if wps is not None else None,
            flags=flags
        )


default_quality_analyzer = TranscriptQualityAnalyzer()
