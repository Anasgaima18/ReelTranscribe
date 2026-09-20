# ASR Providers

## Provider Chain

ReelTranscribe uses a fallback chain: **Sarvam → Whisper → Hinglish Specialist**

If the primary provider fails (rate limit, timeout, error), the next provider is tried automatically.

## 1. Sarvam Saaras v4 (Primary)

- **Endpoint**: `https://api.sarvam.ai/speech-to-text`
- **Model**: `saaras:v4`
- **Modes**: `codemix` (default), `transcribe`, `verbatim`, `translate`, `translit`
- **Auth**: `api-subscription-key: <SARVAM_API_KEY>`
- **Strengths**: Best for Hindi, Hinglish code-switching, and Indic languages
- **Audio**: 16 kHz mono WAV recommended

## 2. Whisper Large v3 (Fallback)

- **Endpoint**: `https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3`
- **Auth**: `Authorization: Bearer <HF_TOKEN>`
- **Strengths**: Excellent multilingual coverage, strong English
- **Note**: Runs via HF Inference Providers (not in-memory on Render)

## 3. Hinglish Specialist (Fallback)

- **Model**: `Oriserve/Whisper-Hindi2Hinglish-Prime`
- **Endpoint**: HF Inference Providers router
- **Strengths**: Preserves Hindi-English code-switching in Latin script
- **Note**: Apache 2.0 licensed, fine-tuned from Whisper large-v3

## Cooldown Behavior

When a provider returns HTTP 429 (rate limit) or 503 (unavailable), it enters a 60-second cooldown. During cooldown, the router skips that provider and tries the next one.

## Adding New Providers

1. Create a new class in `backend/app/asr/` implementing `ASRProvider`
2. Implement `transcribe()`, `is_available()`, and `name` property
3. Add to the fallback list in `backend/app/asr/router.py`
