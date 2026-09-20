# ReelTranscribe Ralph Guardrails

The following non-negotiable engineering rules govern all implementations and iterations:

1. **Never expose secrets**: No API keys, authorization tokens, or credentials in git commits, responses, logs, or client responses.
2. **Never assume API behavior**: Verify API endpoints, request schemas, parameters, and responses against live testing and current documentation.
3. **Never mark stories passed without tests**: A story passes only after its acceptance criteria are objectively verified with passing automated tests.
4. **Never skip official documentation**: Follow current official docs for Apple Shortcuts/App Intents, Sarvam, Render, Hugging Face, etc.
5. **Never run huge models on Render free**: Render free web service has 512 MB RAM / 0.1 CPU; heavy ASR (Whisper Large) must be accessed via external APIs (Sarvam, Hugging Face router) or dedicated compute.
6. **Never generate captions when original captions are absent**: Only generate SRT/VTT if original embedded subtitles or burned-in captions are detected.
7. **Never translate transcript unless explicitly requested**: Preserve verbatim spoken language, slang, filler words, and Hindi/Hinglish code-switching in Latin or Indic script as spoken.
8. **Never silently change provider**: Log provider switches and fallbacks cleanly in job metadata.
9. **Never log private media**: Do not log raw video, raw audio, URLs, or private transcript content in standard logs.
10. **Never claim unsupported language support**: Only report supported languages verified by provider capabilities.
11. **Never fabricate benchmark results**: Benchmarks must run against actual test audio and calculate real WER, CER, latency, and costs.
12. **Never ignore failing tests**: If any test fails, diagnose the root cause, fix it, and re-verify before proceeding.
13. **Never modify unrelated existing project files**: Keep modifications focused on the target story and its dependencies.
14. **Use industry-standard tools**: Use `yt-dlp` for video extraction, `ffmpeg`/`ffprobe` for media processing, `srt`/`webvtt-py` for subtitle generation, `pytesseract`/`OpenCV` for OCR caption detection, and `huggingface_hub` for Hugging Face inference.
