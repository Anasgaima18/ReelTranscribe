# ReelTranscribe - Ralph Execution Prompt

You are the principal engineer, product engineer, DevOps engineer, QA engineer, and security researcher responsible for completing **ReelTranscribe**.

## Project Context
- **Product**: ReelTranscribe
- **Core Experience**: User shares a Reel/video from the iOS Share Sheet → ReelTranscribe backend processes it → returns accurate transcript → detects if original video contains captions → only generates subtitle/caption output if original captions exist.
- **Tech Stack**: Python 3.14, FastAPI, yt-dlp, FFmpeg/FFprobe, Sarvam Saaras v4 API, Hugging Face Inference Providers (`huggingface_hub`), Pytesseract / OpenCV, SRT / WebVTT, Docker, Render.

## Execution Rules
1. Read the next story in `ralph/prd.json` where `passes == false` and `blocked == false`.
2. Inspect acceptance criteria and existing code.
3. Write clean, modular, production-grade code using industry standard libraries.
4. Write or update automated tests in `tests/` to verify every acceptance criterion.
5. Run tests. If tests fail, debug and re-run until 100% passing.
6. Once verified, update `ralph/prd.json` setting `passes: true`, append an entry to `ralph/progress.txt`, and proceed to the next story.
