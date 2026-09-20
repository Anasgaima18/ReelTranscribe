# ReelTranscribe

A privacy-preserving, production-grade transcription and captioning system engineered for high-accuracy multilingual and Hindi/Hinglish code-switching speech recognition.

## Core Experience

**User shares a Reel/video from iOS Share Sheet → ReelTranscribe processes it → returns a highly accurate transcript → detects whether the original video contains captions → only when original captions are detected does it generate subtitle/caption output.**

## Key Features

- **Multi-provider ASR**: Sarvam Saaras v4 (primary), Whisper Large v3 (fallback), Hinglish specialist models
- **Automatic fallback chain**: If primary provider fails, seamlessly falls back to next available provider
- **Hindi/Hinglish code-switching**: Preserves code-mixed speech without translating
- **Caption detection**: Dual-mode detection (embedded streams + burned-in visual OCR)
- **Conditional subtitles**: SRT/VTT output only when original video has captions
- **Privacy-first logging**: Never logs transcripts, URLs, or API keys
- **iOS Shortcut integration**: Share Sheet → background processing → clipboard result
- **SSRF protection**: Strict URL validation blocking private/internal IPs and DNS rebinding

## Quick Start

### Prerequisites

- Python 3.12+
- FFmpeg installed and on PATH
- yt-dlp installed (`pip install yt-dlp`)

### Installation

```bash
git clone <repo-url>
cd REELSTRANSCRIBE
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
SARVAM_API_KEY=your_sarvam_api_key
HF_TOKEN=your_huggingface_token
API_SECRET=your_api_secret
APP_ENV=development
```

### Run

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Run Benchmarks

```bash
python -m benchmark.run --dataset benchmark/dataset.jsonl --provider all
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check with provider status |
| `POST` | `/v1/jobs` | Submit transcription job (URL or upload) |
| `GET` | `/v1/jobs/{id}` | Poll job status |
| `GET` | `/v1/jobs/{id}/result` | Get completed result |
| `POST` | `/v1/media/upload` | Direct file upload |

## Architecture

```
iOS Share Sheet → POST /v1/jobs {url} → Background Worker Pipeline:
  1. Media Resolution (yt-dlp with SSRF guard)
  2. Audio Extraction (FFmpeg → 16kHz mono WAV)
  3. ASR Transcription (Sarvam → Whisper → Hinglish fallback)
  4. Quality Gate (repetition, coverage, confidence checks)
  5. Safe Normalization (preserve verbatim, fix punctuation)
  6. Caption Detection (embedded streams + visual OCR)
  7. Conditional Subtitle Generation (SRT/VTT)
  → Poll GET /v1/jobs/{id} until completed
  → GET /v1/jobs/{id}/result for final output
```

## Deployment

### Docker

```bash
docker compose up --build
```

### Render (Free Tier)

Push to GitHub and connect to Render. The `render.yaml` blueprint auto-configures the deployment with health checks and env vars.

> **Note**: Render free tier has 512MB RAM. Whisper cannot run in-memory — it's offloaded to external APIs (Sarvam, HF Inference Providers).

## Documentation

- [Architecture](docs/architecture.md) — System design and component flow
- [API Reference](docs/api.md) — Full endpoint documentation
- [iOS Shortcut Guide](docs/ios-shortcut.md) — Installation and usage
- [Deployment Guide](docs/deployment.md) — Docker, Render, and production setup
- [Providers](docs/providers.md) — ASR provider configuration
- [Security](docs/security.md) — SSRF protection and rate limiting
- [Benchmarking](docs/benchmarking.md) — WER/CER evaluation
- [Troubleshooting](docs/troubleshooting.md) — Common issues and fixes

## License

MIT
