# ReelTranscribe Architecture

## System Overview

ReelTranscribe is a FastAPI-based backend service that provides high-accuracy multilingual transcription with conditional captioning. It is designed as a stateless API that can be deployed on resource-constrained environments (e.g., Render free tier with 512MB RAM) by offloading heavy inference to external providers.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS Shortcut Client                       │
│  Share Sheet → POST /v1/jobs → Poll → GET result            │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                  FastAPI Application                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ /health  │  │ /v1/jobs │  │/v1/media │                   │
│  │ Health   │  │ Jobs API │  │ Upload   │                   │
│  └──────────┘  └────┬─────┘  └──────────┘                  │
│                     │                                        │
│  ┌──────────────────▼────────────────────────────────────┐  │
│  │              Background Worker Pipeline                │  │
│  │                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │   Media      │  │   Audio     │  │    ASR       │  │  │
│  │  │   Resolver   │→│   FFmpeg    │→│    Router    │  │  │
│  │  │  (yt-dlp)   │  │  (16kHz)   │  │  (fallback) │  │  │
│  │  └─────────────┘  └─────────────┘  └──────┬───────┘  │  │
│  │                                           │           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────▼────────┐  │  │
│  │  │  Subtitle   │←│  Caption    │←│  Quality    │  │  │
│  │  │  Generator  │  │  Detector   │  │  Gate       │  │  │
│  │  │(conditional)│  │(dual-mode)  │  │  + Normaliz │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Middleware: Rate Limiter, Security Headers, CORS      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
┌────────┐    ┌────────────┐    ┌────────────┐
│ Sarvam │    │ HF Whisper │    │ Hinglish   │
│ API    │    │ Inference  │    │ Specialist │
│saaras:v4│   │ large-v3   │    │ Prime      │
└────────┘    └────────────┘    └────────────┘
```

## Data Flow

1. **Ingestion**: iOS Shortcut shares a URL → `POST /v1/jobs` with URL
2. **Resolution**: MediaResolver uses yt-dlp to download video with SSRF protection
3. **Extraction**: FFmpeg extracts and normalizes audio to 16kHz mono WAV
4. **Transcription**: ASR Router tries Sarvam → Whisper → Hinglish with cooldowns
5. **Validation**: Quality gate checks repetition, coverage, confidence
6. **Normalization**: SafeTranscriptNormalizer fixes punctuation without altering words
7. **Caption Detection**: ffprobe checks embedded streams; visual OCR checks burned-in
8. **Subtitle Generation**: Only generates SRT/VTT if original captions were detected
9. **Result**: Client polls until completed, retrieves structured JSON result

## Key Design Decisions

- **Stateless API**: No database required; in-memory job store for simplicity
- **External inference**: Heavy models run on external APIs, not in-process
- **Privacy-first**: Logs never contain transcripts, URLs, or credentials
- **Conditional captions**: Subtitles are only generated when source has captions
- **Verbatim preservation**: Normalizer never translates, adds, or removes spoken words
