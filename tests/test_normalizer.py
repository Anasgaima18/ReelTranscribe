from backend.app.asr.normalizer import SafeTranscriptNormalizer

def test_preserves_hinglish_code_switching():
    raw = "guys aaj hum deployment karne wale hain  ,but production mein issue aa gaya."
    res = SafeTranscriptNormalizer.normalize(raw)

    assert res.raw_transcript == raw
    assert "guys" in res.final_transcript.lower()
    assert "aaj hum deployment" in res.final_transcript
    assert "production mein issue" in res.final_transcript
    assert "PUNCTUATION_SPACING_FIX" in res.postprocessing_applied
    assert "WHITESPACE_COLLAPSE" in res.postprocessing_applied

def test_sentence_capitalization_and_spacing():
    raw = "hello world.this is a test  !are we ready ?"
    res = SafeTranscriptNormalizer.normalize(raw)

    assert res.final_transcript == "Hello world. This is a test! Are we ready?"
    assert "SENTENCE_CAPITALIZATION" in res.postprocessing_applied
    assert "PUNCTUATION_FOLLOWING_SPACE" in res.postprocessing_applied

def test_empty_string():
    res = SafeTranscriptNormalizer.normalize("")
    assert res.raw_transcript == ""
    assert res.final_transcript == ""
    assert len(res.postprocessing_applied) == 0
