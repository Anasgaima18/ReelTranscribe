from backend.app.asr.base import TranscriptResult
from backend.app.asr.scoring import TranscriptQualityAnalyzer

def test_quality_gate_clean_transcript():
    analyzer = TranscriptQualityAnalyzer()
    res = TranscriptResult(
        raw_transcript="Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
        final_transcript="Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
        language_code="hi-en",
        language_probability=0.95,
        confidence=0.95
    )
    assessment = analyzer.evaluate(res, audio_duration_seconds=5.0)
    assert assessment.passed is True
    assert assessment.score >= 0.80
    assert len(assessment.flags) == 0

def test_quality_gate_detects_abnormal_repetition():
    analyzer = TranscriptQualityAnalyzer()
    # 20 repetitions of hallucinated loop
    repeated_text = "thank you for watching " * 20
    res = TranscriptResult(
        raw_transcript=repeated_text,
        final_transcript=repeated_text,
        language_code="en",
        language_probability=0.90,
        confidence=0.90
    )
    assessment = analyzer.evaluate(res, audio_duration_seconds=15.0)
    assert assessment.passed is False
    assert "ABNORMAL_REPETITION" in assessment.flags

def test_quality_gate_detects_suspiciously_low_coverage():
    analyzer = TranscriptQualityAnalyzer()
    res = TranscriptResult(
        raw_transcript="hello",
        final_transcript="hello",
        language_code="en",
        language_probability=0.90,
        confidence=0.90
    )
    # 1 word for 60 seconds of speech
    assessment = analyzer.evaluate(res, audio_duration_seconds=60.0)
    assert "SUSPICIOUSLY_LOW_SPEECH_COVERAGE" in assessment.flags

def test_quality_gate_empty_transcript():
    analyzer = TranscriptQualityAnalyzer()
    res = TranscriptResult(
        raw_transcript="",
        final_transcript="",
        language_code="en",
        language_probability=0.0,
        confidence=0.0
    )
    assessment = analyzer.evaluate(res, audio_duration_seconds=10.0)
    assert assessment.passed is False
    assert "EMPTY_TRANSCRIPT" in assessment.flags
