from pathlib import Path
import srt
import webvtt
from backend.app.asr.base import TranscriptChunk
from backend.app.captions.subtitles import SubtitleGenerator, SubtitleConfig

def test_subtitles_omitted_when_captions_not_detected(tmp_path):
    gen = SubtitleGenerator()
    chunks = [
        TranscriptChunk(text="Speech without original captions", start_time=0.0, end_time=2.0)
    ]
    srt_p, vtt_p = gen.generate(chunks, captions_detected=False, output_dir=tmp_path)
    assert srt_p is None
    assert vtt_p is None
    assert len(list(tmp_path.glob("*.srt"))) == 0
    assert len(list(tmp_path.glob("*.vtt"))) == 0

def test_subtitles_generated_when_captions_detected(tmp_path):
    gen = SubtitleGenerator()
    chunks = [
        TranscriptChunk(
            text="Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
            start_time=0.0,
            end_time=3.5
        ),
        TranscriptChunk(
            text="नमस्ते दोस्तों, यह एक परीक्षण उपशीर्षक है।",
            start_time=3.8,
            end_time=6.2
        )
    ]

    srt_p, vtt_p = gen.generate(chunks, captions_detected=True, output_dir=tmp_path)

    assert srt_p is not None and srt_p.is_file()
    assert vtt_p is not None and vtt_p.is_file()

    # Parse and validate with official srt parser
    srt_content = srt_p.read_text(encoding="utf-8")
    parsed_subs = list(srt.parse(srt_content))
    assert len(parsed_subs) == 2
    assert "Guys aaj hum deployment" in parsed_subs[0].content
    assert "नमस्ते दोस्तों" in parsed_subs[1].content

    # Parse and validate with official webvtt parser
    parsed_vtt = webvtt.read(str(vtt_p))
    assert len(parsed_vtt) == 2
    assert "00:00:00.000" in parsed_vtt[0].start
    assert "Guys aaj hum" in parsed_vtt[0].text

def test_line_wrapping_constraints():
    config = SubtitleConfig(max_chars_per_line=25, max_lines=2)
    gen = SubtitleGenerator(config=config)

    long_text = "This is a very long sentence that exceeds twenty five characters and will wrap across multiple lines cleanly."
    wrapped = gen.format_cue_text(long_text)
    lines = wrapped.split("\n")

    assert len(lines) <= 2
    for l in lines:
        assert len(l) <= 25
