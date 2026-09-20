# REELTRANSCRIBE

## Autonomous Production Build Specification

You are the principal engineer, product engineer, DevOps engineer, QA engineer, security engineer, and technical researcher responsible for COMPLETING this project.

Do not merely generate a plan.

You must research, implement, test, debug, verify, document, and finish the entire project.

The product is called:

# ReelTranscribe

Core experience:

> User shares a Reel/video from the iOS Share Sheet → ReelTranscribe processes it → returns a highly accurate transcript → detects whether the ORIGINAL video contains captions → only when original captions are detected does it generate subtitle/caption output.

The system must prioritize:

1. Accuracy
2. Hindi/Hinglish/code-switching quality
3. Multilingual support
4. Reliability
5. Low cost
6. Privacy
7. Fast user experience
8. Cross-platform backend architecture
9. iOS Shortcut usability
10. Maintainability

Do NOT claim 100% transcription accuracy. Speech recognition cannot guarantee that. Engineer for maximum practical accuracy and measure it objectively.

---

# 1. ABSOLUTE RULE: NO ASSUMPTIONS

You MUST NOT assume anything.

Verify current information using official documentation or actual tests before implementing.

This applies to:

* APIs
* SDKs
* model names
* model capabilities
* licenses
* pricing
* rate limits
* file limits
* language support
* URL extraction
* Instagram behavior
* YouTube behavior
* TikTok behavior
* Apple Shortcut behavior
* Render capabilities
* Hugging Face inference availability
* package APIs
* authentication
* HTTP request formats
* response schemas
* model memory requirements

If something cannot be verified:

Mark it:

UNVERIFIED

Do not silently invent an implementation.

---

# 2. REQUIRED RALPH LOOP

You MUST use the current Ralph Loop implementation/skills from the official GitHub repository:

https://github.com/taberoajorge/ralph

The repository currently describes a PRD-driven autonomous loop that:

1. loads `prd.json`
2. selects the next incomplete story
3. builds the agent prompt
4. runs the coding agent
5. implements the story
6. runs tests
7. verifies the story
8. marks it passed
9. records failures
10. adds guardrails when necessary
11. retries failed work
12. continues until stories are complete or a genuine blocker exists

Do not manually pretend to use Ralph.

Actually inspect the current repository and install/use the compatible Ralph skills/scripts for the available Antigravity environment.

Reference:
https://github.com/taberoajorge/ralph

Before implementation:

```text
git clone https://github.com/taberoajorge/ralph
```

Do NOT blindly execute old commands.

First inspect the repository's CURRENT README, skills, scripts and installation instructions.

Determine the correct Ralph integration for the current environment.

Create and maintain:

```text
ralph/
  prd.json
  prompt.md
  guardrails.md
  progress.txt
```

If the current Ralph version requires a different structure, follow the current repository documentation.

---

# 3. RALPH EXECUTION POLICY

Break the entire product into small independently verifiable user stories.

Each story MUST have:

* ID
* title
* description
* acceptance criteria
* implementation notes
* tests
* verification requirements
* passes=false initially

Do not create one enormous story called:

"Build the application."

Instead create granular stories such as:

```text
RT-001 Repository initialization
RT-002 Backend architecture
RT-003 Health API
RT-004 URL ingestion
RT-005 Direct media ingestion
RT-006 FFmpeg pipeline
RT-007 Sarvam integration
RT-008 Whisper integration
RT-009 Hinglish specialist
RT-010 ASR router
RT-011 quality scoring
RT-012 transcript normalization
RT-013 caption detection
RT-014 subtitle generation
RT-015 iOS Shortcut
RT-016 error handling
RT-017 security
RT-018 observability
RT-019 deployment
RT-020 integration tests
RT-021 load tests
RT-022 documentation
RT-023 final acceptance
```

Use as many stories as necessary.

Never mark a story as passed just because code exists.

A story passes only after its acceptance criteria are objectively verified.

---

# 4. OFFICIAL DOCUMENTATION REQUIREMENT

Before implementing every external integration, inspect the CURRENT official documentation.

At minimum verify:

## Apple

Apple Shortcuts:

https://support.apple.com/guide/shortcuts/

Apple App Intents:

https://developer.apple.com/documentation/appintents

Apple App Shortcuts:

https://developer.apple.com/documentation/appintents/app-shortcuts

Apple App Intent:

https://developer.apple.com/documentation/appintents/appintent

Apple's current documentation states that shortcuts can be made available through the Share Sheet and can receive content from other apps.

Use the current Apple behavior rather than relying on old SiriKit/Intents APIs.

Apple's documentation explicitly identifies App Intents as the modern framework for exposing app actions to Shortcuts, Siri and system experiences.

References:
https://support.apple.com/guide/shortcuts/run-a-shortcut-from-another-app-apd163eb9f95/ios

https://developer.apple.com/documentation/appintents/appintent

https://developer.apple.com/documentation/appintents/app-shortcuts

---

# 5. IOS SHORTCUT PRODUCT REQUIREMENT

The primary user interface MUST be an iOS Shortcut.

The user experience must be:

```text
Instagram / YouTube / Safari / Photos
              ↓
          Share button
              ↓
       ReelTranscribe
              ↓
         Processing
              ↓
          Transcript
```

Apple's Share Sheet integration must be used correctly.

The Shortcut must support shared input.

The Shortcut must accept, where available:

* URL
* video
* audio
* file
* shared media

Do not assume every application passes the same type of content.

The Shortcut must inspect the received input and determine whether it is:

```text
URL
FILE
VIDEO
AUDIO
TEXT
OTHER
```

Then route appropriately.

---

# 6. IOS SHORTCUT MUST BE SIMPLE

The user should NOT have to manually configure:

* language
* model
* API
* transcript mode
* provider
* fallback

The Shortcut should do this automatically.

Target flow:

```text
Receive Shared Input
        ↓
Detect Input Type
        ↓
Send to ReelTranscribe API
        ↓
Show Processing
        ↓
Receive Result
        ↓
Present Transcript
```

If captions are detected:

```text
Transcript
+
Captions detected
+
SRT
+
VTT
```

If captions are NOT detected:

```text
Transcript
```

Do NOT ask:

"Do you want captions?"

because the product requirement is:

> Generate captions only when the original video already contains captions.

---

# 7. IMPORTANT CAPTION REQUIREMENT

There are two types of captions:

## A. Embedded subtitle stream

The video container contains an actual subtitle stream.

Use FFprobe/media inspection to detect this.

## B. Burned-in captions

The captions are pixels embedded into the video.

They require visual detection/OCR.

The system MUST support both.

Do NOT confuse:

"transcription available"

with:

"original captions exist."

The decision must be:

```text
Original captions detected?
        │
   ┌────┴────┐
  YES        NO
   │          │
Generate      No
subtitle      subtitle
files
```

Do not generate subtitles for a video merely because speech was transcribed.

---

# 8. URL INGESTION

The backend must support URL input where technically and legally permitted.

Supported URL types should be configurable rather than hard-coded.

At minimum investigate:

* Instagram
* YouTube
* TikTok
* direct video URLs
* publicly accessible media URLs

Do NOT assume a public page URL gives direct media access.

Build:

```text
MediaResolver
```

with provider adapters:

```text
media/
  resolver.ts / resolver.py
  providers/
    direct/
    youtube/
    instagram/
    tiktok/
```

Every provider must:

1. validate URL
2. determine whether supported
3. resolve media if permitted
4. obtain temporary media
5. validate media
6. pass media to processing
7. clean up temporary data

If a platform prevents reliable/legal extraction, return a clear error instead of trying unsafe bypasses.

---

# 9. DIRECT FILE INGESTION

The backend must also support direct uploads.

Supported input:

```text
mp4
mov
webm
m4v
mp3
wav
m4a
aac
flac
ogg
opus
```

Do not assume.

Verify exact support against the selected API/model.

---

# 10. BACKEND

Recommended backend:

Python + FastAPI.

Reason:

* excellent audio/ML ecosystem
* FFmpeg integration
* Hugging Face ecosystem
* easy API development
* easy asynchronous processing

Structure:

```text
backend/
  app/
    main.py
    config.py

    api/
      health.py
      jobs.py
      transcriptions.py
      media.py

    core/
      security.py
      logging.py
      errors.py

    media/
      resolver.py
      downloader.py
      ffmpeg.py
      probe.py
      cleanup.py

    audio/
      preprocessing.py
      vad.py
      segmentation.py

    asr/
      base.py
      router.py
      sarvam.py
      whisper.py
      hinglish.py
      qwen.py
      scoring.py

    captions/
      detector.py
      ocr.py
      subtitle_stream.py
      srt.py
      vtt.py

    jobs/
      queue.py
      worker.py

    schemas/
      request.py
      response.py

  tests/
  Dockerfile
  requirements.txt
```

Use async APIs where appropriate.

Long-running transcription MUST NOT block a normal HTTP request.

---

# 11. JOB ARCHITECTURE

A transcription job should have states:

```text
queued
downloading
extracting_audio
preprocessing
detecting_language
transcribing
validating_transcript
detecting_captions
generating_subtitles
completed
failed
```

Expose:

```http
POST /v1/jobs
GET  /v1/jobs/{job_id}
GET  /v1/jobs/{job_id}/result
```

For very short jobs where the selected API supports synchronous processing, synchronous execution may be used.

For longer processing:

```text
POST job
   ↓
202 Accepted
   ↓
job_id
   ↓
poll
```

Do not hold a mobile Shortcut HTTP request open indefinitely.

---

# 12. RENDER ARCHITECTURE

The backend will be deployed on Render.

Official Render documentation:

https://render.com/docs/your-first-deploy

https://render.com/docs/free

https://render.com/docs/background-workers

https://render.com/docs/service-types

Important:

Render's current free web service is:

```text
0.1 CPU
512 MB RAM
```

and free services spin down after 15 minutes of inactivity. Render explicitly states that free instances are intended for testing/hobby use and not production.

Therefore:

DO NOT attempt to run Whisper Large-v3 directly on the free Render web service.

Render should initially act as:

```text
API
orchestration
authentication
job management
provider routing
media coordination
```

Heavy ASR should be external/API-based or run on suitable compute.

Render's background-worker architecture should be considered if the deployment plan requires persistent asynchronous processing.

Do not assume a free Render background worker exists; current Render documentation says free instances are not available for background workers.

---

# 13. STORAGE

Do NOT depend on Render local filesystem for persistent data.

Render states that free web-service local filesystem changes are lost on restart/redeploy/spin-down.

Temporary media should:

```text
download
→ process
→ delete
```

Persistent application state should use an external database/storage system if required.

For V1, avoid storing user media permanently unless explicitly required.

Default:

```text
NO PERMANENT VIDEO STORAGE
NO PERMANENT AUDIO STORAGE
```

Store only:

* job metadata
* transcript if user opts in / required
* error metadata
* usage metadata

---

# 14. PRIMARY ASR — SARVAM

Use the current official Sarvam API documentation:

https://docs.sarvam.ai/api-reference/speech-to-text/transcribe

https://docs.sarvam.ai/api/getting-started/models/saaras

Sarvam currently documents:

```text
saaras:v3
saaras:v4
```

and states that Saaras v4 is the latest, supports Global + Indian English and 22 Indic languages, with modes including transcription, translation, verbatim, transliteration and code-mix.

Use current official documentation when implementing.

PRIMARY CANDIDATE:

```text
saaras:v4
```

Do NOT hard-code assumptions about whether `mode=codemix` is supported identically between v3 and v4.

The current REST documentation contains a limitation/naming inconsistency around mode applicability.

Therefore:

1. verify the live API behavior
2. run a real request
3. record actual behavior
4. implement according to verified behavior

For unknown input language:

```text
language_code = unknown
```

Sarvam documents automatic language detection and returns language probability.

Use timestamps when available.

Remember:

Sarvam REST timestamps are chunk/sentence-level, NOT individual word timestamps.

If word-level subtitle timing is required, use a different mechanism/model for alignment.

---

# 15. SARVAM INPUT PROCESSING

Sarvam currently documents support for formats including:

```text
WAV
MP3
AAC
AIFF
OGG
OPUS
FLAC
MP4/M4A
AMR
WMA
WebM
PCM
```

and states that 16 kHz audio works best.

Our preprocessing should therefore normalize appropriately when useful:

```text
mono
16 kHz
PCM/WAV
```

BUT:

Do not convert unnecessarily if the API accepts the source format and conversion would increase processing time or degrade quality.

Benchmark:

```text
original audio
vs
16kHz mono PCM
```

and document the result.

---

# 16. HINGLISH REQUIREMENT

This is one of the most important features.

The system MUST preserve code-switching.

Example:

Input speech:

"Guys aaj hum deployment karne wale hain but production mein issue aa gaya."

Desired transcript:

"Guys aaj hum deployment karne wale hain but production mein issue aa gaya."

NOT:

"Guys today we are going to deploy but there was an issue in production."

Do not translate unless explicitly requested.

Do not rewrite spoken language into polished English.

Do not hallucinate missing words.

Do not "improve" slang.

Do not remove filler words unless the user selects a cleaned transcript mode.

---

# 17. HINGLISH SPECIALIST

Benchmark and retain:

```text
Oriserve/Whisper-Hindi2Hinglish-Prime
Oriserve/Whisper-Hindi2Hinglish-Apex
```

Official Hugging Face:

https://huggingface.co/Oriserve/Whisper-Hindi2Hinglish-Prime

The current model card identifies Prime as Apache-2.0 and provides Transformers usage.

Do NOT assume it should always run.

Use it as a specialist fallback for:

```text
Hindi
English
Hindi-English code switching
Hinglish
```

---

# 18. UNIVERSAL LOCAL FALLBACK

Benchmark:

```text
openai/whisper-large-v3
```

Hugging Face:

https://huggingface.co/openai/whisper-large-v3

Verify current:

* license
* languages
* memory
* inference requirements
* quantization options
* performance

Use `faster-whisper`/CTranslate2 where appropriate after verifying current compatibility.

Do not deploy the full model on a 512 MB Render free instance.

---

# 19. ADDITIONAL MODELS TO BENCHMARK

Do not permanently select models based on marketing.

Benchmark:

```text
openai/whisper-large-v3

Oriserve/Whisper-Hindi2Hinglish-Prime

Oriserve/Whisper-Hindi2Hinglish-Apex

shunyalabs/zero-stt-hinglish

Qwen/Qwen3-ASR-1.7B

IndicConformer variants
```

Use current Hugging Face model pages.

Hugging Face Inference Providers currently provide access to hundreds of models/providers through a unified API and document automatic provider selection/failover.

Do not assume free inference is unlimited.

Verify current:

* provider
* model availability
* free allowance
* rate limits
* latency
* file support

---

# 20. ASR ROUTER

Implement a provider-independent interface:

```python
class ASRProvider:
    async def transcribe(
        self,
        audio_path,
        language=None,
        mode=None,
        keyterms=None
    ) -> TranscriptResult:
        ...
```

Providers:

```text
SarvamProvider
WhisperProvider
HinglishProvider
QwenProvider
```

The router should be configurable.

Example:

```yaml
providers:
  primary:
    provider: sarvam
    model: saaras:v4

  fallbacks:
    - whisper-large-v3
    - hinglish-prime
    - qwen3-asr
```

Do NOT hard-code provider logic throughout the application.

---

# 21. QUALITY GATE

This is mandatory.

Do not trust one transcription blindly.

Create:

```text
TranscriptQualityAnalyzer
```

Signals may include:

* language probability
* transcript length
* speech duration
* speech coverage
* repeated tokens
* abnormal repetition
* empty output
* suspicious character distribution
* unsupported-language output
* confidence metrics where available
* disagreement between ASR providers
* VAD speech duration versus transcript duration

Example:

```text
Sarvam
 ↓
Quality analyzer
 ↓
high confidence
 → finish

low confidence
 → fallback

high disagreement
 → specialist fallback
```

Thresholds MUST be configurable.

Do not invent scientifically meaningful thresholds.

Initially use configurable heuristics and benchmark them.

---

# 22. DO NOT LET AN LLM INVENT THE TRANSCRIPT

An LLM may be used for limited post-processing.

Allowed:

* punctuation
* paragraph formatting
* obvious formatting correction
* preserving spoken language
* identifying obvious ASR anomalies

Not allowed:

* adding words
* translating
* rewriting
* summarizing
* hallucinating
* replacing unclear speech with plausible speech

The original ASR transcript must always be preserved.

Return:

```json
{
  "raw_transcript": "...",
  "final_transcript": "...",
  "postprocessing_applied": [...]
}
```

---

# 23. CAPTION DETECTION

Build two independent detectors.

## Subtitle stream detector

Use FFprobe/FFmpeg.

Detect:

```text
subtitle streams
text subtitle tracks
```

## Burned-in caption detector

Sample frames.

Do not OCR every frame.

Suggested architecture:

```text
video
 ↓
sample frames
 ↓
OCR
 ↓
detect repeated text
 ↓
detect consistent caption region
 ↓
caption confidence
```

Use an open-source OCR stack after benchmarking current options.

Candidate:

* PaddleOCR
* EasyOCR
* Tesseract
* OCR models on Hugging Face

Select based on multilingual support and actual tests.

Do not assume OCR accuracy.

---

# 24. CAPTION DETECTION OUTPUT

Return:

```json
{
  "captions_detected": true,
  "caption_type": "burned_in",
  "confidence": 0.93
}
```

Possible:

```text
none
embedded
burned_in
both
unknown
```

If confidence is below the configured threshold:

```text
unknown
```

Do not falsely claim captions exist.

---

# 25. SUBTITLE GENERATION

Only generate subtitle files if:

```text
captions_detected = true
```

Generate:

```text
.srt
.vtt
```

Use actual speech timestamps.

If the selected ASR only provides chunk timestamps, don't pretend they are word timestamps.

Subtitle generation must account for:

* maximum characters per line
* maximum lines
* minimum duration
* maximum duration
* sentence boundaries
* timestamp overlap
* Unicode
* RTL languages
* Indian scripts

Make these parameters configurable.

---

# 26. IMPORTANT DISTINCTION

If the original captions are burned into the video:

We are NOT extracting the original caption file.

We are creating a subtitle representation from the detected speech.

The UI should say:

```text
Original captions detected
Generated subtitle file from transcript
```

not:

```text
Original captions extracted
```

unless an actual subtitle stream was extracted.

---

# 27. OUTPUT API

Return a structured result:

```json
{
  "job_id": "...",
  "status": "completed",

  "source": {
    "type": "url",
    "provider": "instagram"
  },

  "media": {
    "duration_seconds": 61.2,
    "audio_detected": true
  },

  "language": {
    "primary": "hi-IN",
    "probability": 0.97,
    "code_mixed": true
  },

  "transcription": {
    "provider": "sarvam",
    "model": "saaras:v4",
    "raw": "...",
    "final": "...",
    "confidence": "...",
    "fallback_used": false
  },

  "captions": {
    "detected": true,
    "type": "burned_in",
    "confidence": 0.91,
    "srt_url": "...",
    "vtt_url": "..."
  }
}
```

Do not expose API keys.

---

# 28. IOS SHORTCUT OUTPUT

The Shortcut should present:

```text
ReelTranscribe

✓ Transcription complete

Language:
Hindi + English

Transcript:

...

Captions:
✓ Original captions detected

Files:
• Transcript
• SRT
• VTT
```

Actions should allow:

```text
Copy Transcript
Share Transcript
Save Transcript
Save SRT
Save VTT
```

If no captions:

```text
✓ Transcript ready

No original captions detected.
Subtitle files were not generated.
```

---

# 29. PRIVACY

Default policy:

DO NOT permanently retain uploaded videos.

Temporary media:

```text
download
→ process
→ delete
```

Do not log:

* raw audio
* video
* transcript contents

unless explicitly enabled for debugging.

Logs should contain:

```text
job_id
provider
model
duration
processing time
status
error code
fallback
```

Never log:

```text
API keys
authorization headers
raw media
private URLs
full transcripts
```

---

# 30. SECURITY

Implement:

* HTTPS only in production
* request size limits
* URL validation
* SSRF protection
* private IP blocking for URL fetchers
* timeout limits
* download size limits
* media duration limits
* file-type verification
* MIME verification
* filename sanitization
* temporary-file cleanup
* rate limiting
* authentication strategy
* API key protection
* secret management
* CORS restrictions
* security headers

Especially protect the URL resolver against SSRF.

Never allow arbitrary internal network requests.

---

# 31. API RATE LIMITING

Implement application-level rate limiting.

Example configurable:

```text
requests_per_minute
jobs_per_day
max_video_duration
max_file_size
```

Do not hard-code these without documenting why.

---

# 32. COST CONTROL

The system must be designed for a free-first strategy.

Provider priority:

```text
1. Sarvam free/trial allocation where available
2. Open-source/self-hosted inference
3. Hugging Face inference/free allocation where currently available
4. Other verified free API allocation
5. Paid provider only if explicitly enabled
```

Do not silently incur charges.

Every provider must have:

```text
enabled
disabled
daily_limit
monthly_limit
```

Example:

```yaml
providers:
  sarvam:
    enabled: true
    monthly_minutes: 200

  elevenlabs:
    enabled: false

  openai:
    enabled: false
```

Actual limits must be based on current official provider documentation.

---

# 33. PROVIDER FAILOVER

Implement:

```text
Provider unavailable
        ↓
fallback

Rate limited
        ↓
fallback

timeout
        ↓
fallback

quality failure
        ↓
fallback
```

But do NOT repeatedly retry expensive APIs.

Use:

```text
exponential backoff
max retries
provider cooldown
```

---

# 34. ELEVENLABS

Treat ElevenLabs Scribe as an optional provider/benchmark.

Do NOT make it the default because the objective is free/open infrastructure.

Implement it behind:

```text
ELEVENLABS_ENABLED=false
```

Verify the current official API documentation before implementation.

Never assume its current pricing or free allowance.

---

# 35. GOOGLE

Google Speech-to-Text/Chirp may be an optional fallback/benchmark.

Do not enable billing automatically.

Require:

```text
GOOGLE_STT_ENABLED=false
```

unless explicitly configured.

Verify current official Google Cloud documentation before implementation.

---

# 36. HUGGING FACE

Use Hugging Face for:

* model discovery
* model downloads
* local model execution where practical
* optional Inference Providers
* benchmark experiments

Official documentation:

https://huggingface.co/docs/inference-providers

Hugging Face currently documents:

* unified inference API
* multiple providers
* automatic provider selection
* provider failover
* free tier
* provider-specific availability

Verify current conditions before relying on free inference.

---

# 37. MODEL BENCHMARKING SYSTEM

Build a benchmark command:

```bash
python -m benchmark.run
```

Input:

```text
benchmark/audio/
benchmark/reference/
```

Output:

```text
benchmark/results/
```

Test:

```text
Whisper Large-v3
Hinglish Prime
Hinglish Apex
Zero-STT-Hinglish
Qwen3-ASR
IndicConformer
Sarvam
```

Where API access exists.

Metrics:

```text
WER
CER
language detection accuracy
code-switch preservation
processing time
cost
failure rate
```

Do not invent scores.

Use real test data.

---

# 38. TEST DATA

Create a small controlled benchmark dataset.

Categories:

```text
English
Hindi
Hinglish
Kannada
Kannada-English
Tamil
Tamil-English
Telugu
Telugu-English
Malayalam
Marathi
Bengali
Gujarati
Punjabi
Odia
Urdu
```

Audio conditions:

```text
clean
music
background noise
echo
fast speech
slow speech
multiple speakers
overlapping speakers
technical terminology
proper nouns
slang
```

Do not use copyrighted/private content irresponsibly.

Use recordings you have permission to test.

---

# 39. ACCEPTANCE CRITERIA

The project is NOT complete until:

## iOS

* Shortcut appears in Share Sheet
* accepts supported shared inputs
* handles URL input
* handles direct media input
* shows progress
* returns transcript
* can copy/share result
* handles errors cleanly

Apple confirms that Share Sheet-enabled shortcuts can process content from other apps.

## Backend

* API works
* job lifecycle works
* provider routing works
* fallbacks work
* rate limiting works
* cleanup works
* errors are structured

## ASR

* Sarvam integration verified
* Whisper fallback verified
* Hinglish specialist verified
* model router verified
* quality gate verified

## Captions

* embedded subtitle detection works
* burned-in caption detection works
* no captions → no subtitle generation
* captions → SRT/VTT generated

## Security

* SSRF protections tested
* upload limits tested
* secrets not logged
* temporary files cleaned

## Deployment

* Render deployment works
* environment variables documented
* health endpoint works
* logs work
* restart behavior tested

---

# 40. HEALTH ENDPOINT

Implement:

```http
GET /health
```

Return:

```json
{
  "status": "ok",
  "version": "...",
  "providers": {
    "sarvam": true,
    "whisper": true,
    "huggingface": true
  }
}
```

Do not expose secrets or provider credentials.

---

# 41. OBSERVABILITY

Implement structured logging.

Each job:

```text
job_id
request_id
provider
model
duration
processing_time
fallback
status
error
```

Track:

```text
ASR provider success rate
fallback rate
average processing time
caption detection rate
provider errors
```

Do not log private transcript contents by default.

---

# 42. DOCUMENTATION

Create:

```text
README.md

docs/
  architecture.md
  api.md
  ios-shortcut.md
  deployment.md
  providers.md
  models.md
  security.md
  benchmarking.md
  troubleshooting.md
```

README must contain:

```text
What it does
Architecture
Local setup
Environment variables
Provider setup
Running locally
Running tests
Running benchmarks
Deploying to Render
Creating the iOS Shortcut
Troubleshooting
Privacy
Limitations
```

---

# 43. ENVIRONMENT VARIABLES

Create:

```text
.env.example
```

Never commit secrets.

Potential variables:

```text
APP_ENV=
API_SECRET=
SARVAM_API_KEY=
HF_TOKEN=
ELEVENLABS_API_KEY=
GOOGLE_APPLICATION_CREDENTIALS=
OPENAI_API_KEY=

SARVAM_ENABLED=
HF_ENABLED=
ELEVENLABS_ENABLED=
GOOGLE_ENABLED=
OPENAI_ENABLED=

MAX_FILE_SIZE_MB=
MAX_DURATION_SECONDS=

RATE_LIMIT_PER_MINUTE=
```

Only include providers actually implemented.

---

# 44. DOCKER

Create a production Dockerfile.

Requirements:

* Python version verified against current dependencies
* FFmpeg installed
* non-root user
* minimal image
* health check
* graceful shutdown
* no secrets in image
* deterministic dependency installation

---

# 45. CI/CD

Create GitHub Actions.

At minimum:

```text
lint
type check
unit tests
integration tests
security checks
Docker build
```

Do not deploy if tests fail.

---

# 46. ERROR HANDLING

Every error should have:

```json
{
  "error": {
    "code": "MEDIA_DOWNLOAD_FAILED",
    "message": "Unable to retrieve the media.",
    "retryable": false
  }
}
```

Possible error classes:

```text
INVALID_URL
UNSUPPORTED_URL
MEDIA_NOT_FOUND
MEDIA_PRIVATE
MEDIA_DOWNLOAD_FAILED
MEDIA_TOO_LARGE
MEDIA_TOO_LONG
NO_AUDIO
AUDIO_PROCESSING_FAILED
ASR_PROVIDER_UNAVAILABLE
ASR_RATE_LIMITED
ASR_FAILED
QUALITY_CHECK_FAILED
CAPTION_DETECTION_FAILED
SUBTITLE_GENERATION_FAILED
INTERNAL_ERROR
```

Do not expose internal stack traces to users.

---

# 47. NO FAKE FEATURES

Do not implement fake UI such as:

```text
"99.9% accuracy"
"AI confidence: 99%"
```

unless the value is backed by a real metric.

Do not fabricate:

* accuracy
* language support
* processing time
* provider availability
* caption confidence

---

# 48. MODEL SELECTION POLICY

Initial candidate priority:

```text
PRIMARY:
Sarvam Saaras v4

GENERAL FALLBACK:
Whisper Large-v3

HINGLISH FALLBACK:
Whisper-Hindi2Hinglish-Prime

LIGHTWEIGHT HINGLISH:
Whisper-Hindi2Hinglish-Apex

BENCHMARK:
Qwen3-ASR

INDIAN LANGUAGE LOCAL:
IndicConformer

OPTIONAL EXTERNAL:
Google
ElevenLabs
OpenAI
```

This is NOT a permanent accuracy ranking.

The benchmark must be allowed to change the ranking.

Make the ranking configurable.

---

# 49. DO NOT OVERENGINEER V1

Do NOT immediately build:

* accounts
* payments
* social profiles
* dashboards
* mobile apps
* fancy frontend
* analytics dashboard
* subscription system

The first product is:

```text
iOS Shortcut
+
API
+
media processing
+
ASR
+
fallback
+
caption detection
+
SRT/VTT
```

That's it.

---

# 50. FUTURE CROSS-PLATFORM SUPPORT

The backend must remain platform-independent.

Future clients:

```text
iOS Shortcut
iOS app
Android app
macOS
Windows
Web
Chrome extension
```

must all be able to use:

```text
POST /v1/jobs
GET /v1/jobs/{id}
GET /v1/jobs/{id}/result
```

Do not put business logic inside the iOS Shortcut.

The Shortcut is only a client/orchestrator.

---

# 51. DESKTOP

Do not build a desktop client in V1.

But ensure API compatibility with desktop clients.

A future desktop client should be able to:

```text
paste URL
upload video
drag/drop video
receive transcript
download SRT/VTT
```

without changing backend architecture.

---

# 52. ANDROID

Do not build Android V1.

But expose a normal HTTPS REST API that an Android share-target can eventually use.

---

# 53. DATABASE

Avoid unnecessary persistent database complexity in V1.

If job persistence is required:

Use a small relational schema.

Example:

```text
jobs
providers
provider_usage
benchmark_runs
```

Do not store media in the database.

Do not store binary video/audio blobs in PostgreSQL.

---

# 54. TEMPORARY FILE LIFECYCLE

Every job must have:

```text
temp/job_id/
  source
  audio
  frames
  subtitles
```

After completion/failure:

```text
cleanup()
```

must execute.

Also implement a startup cleanup process for orphaned temporary files.

---

# 55. MEDIA LIMITS

Make limits configurable:

```text
MAX_VIDEO_SIZE
MAX_VIDEO_DURATION
MAX_AUDIO_SIZE
MAX_URL_RESPONSE_SIZE
```

Reject early.

Do not download a 5 GB file just to discover it exceeds the limit.

Use streaming/HEAD/content-length where safely available.

---

# 56. URL SECURITY

The URL resolver is security-sensitive.

Implement:

* allowlist supported schemes
* only HTTPS/HTTP if justified
* reject localhost
* reject loopback
* reject private IP ranges
* reject link-local
* reject metadata endpoints
* prevent redirects into private networks
* limit redirects
* DNS rebinding protection where appropriate
* timeout
* response size limit

Test SSRF explicitly.

---

# 57. RALPH GUARDRAILS

Create guardrails covering:

```text
Never expose secrets.
Never assume API behavior.
Never mark stories passed without tests.
Never skip official documentation.
Never run huge models on Render free.
Never generate captions when original captions are absent.
Never translate transcript unless explicitly requested.
Never silently change provider.
Never log private media.
Never claim unsupported language support.
Never fabricate benchmark results.
Never ignore failing tests.
Never modify unrelated existing project files.
```

---

# 58. RALPH PROGRESS FILE

Maintain:

```text
ralph/progress.txt
```

After every iteration record:

```text
date/time
story
what changed
tests run
tests passed
problems
next action
```

Keep it concise.

---

# 59. GIT

Use meaningful commits.

Example:

```text
feat(api): initialize transcription API
feat(media): add media resolver
feat(asr): integrate Sarvam
feat(asr): add Whisper fallback
feat(captions): detect subtitle streams
feat(captions): add burned-in caption detection
feat(shortcut): add share-sheet workflow
test(asr): add Hinglish benchmark
fix(router): handle Sarvam timeout
```

Do not create giant commits containing the entire application.

---

# 60. RALPH LOOP COMPLETION CONDITION

Continue Ralph iterations until:

```text
ALL REQUIRED STORIES:
passes = true
```

AND:

```text
all automated tests pass
```

AND:

```text
integration tests pass
```

AND:

```text
Docker build passes
```

AND:

```text
security checks pass
```

AND:

```text
iOS Shortcut integration is documented/tested
```

AND:

```text
deployment documentation is complete
```

AND:

```text
no known critical bugs remain
```

If a genuine external blocker exists, do NOT fake completion.

Record:

```text
BLOCKED
```

with:

* exact blocker
* evidence
* what was attempted
* required external action
* workaround if available

---

# 61. FINAL ACCEPTANCE TEST

At the end, perform a real end-to-end test:

```text
iPhone
 ↓
Instagram/Safari/Photos
 ↓
Share
 ↓
ReelTranscribe Shortcut
 ↓
Render API
 ↓
Media resolution
 ↓
FFmpeg
 ↓
ASR
 ↓
quality gate
 ↓
caption detection
 ↓
result
 ↓
iPhone
```

Test at least:

1. English Reel
2. Hindi Reel
3. Hinglish Reel
4. English + Hindi code switching
5. Indian regional language
6. noisy Reel
7. Reel with burned-in captions
8. Reel without captions
9. unsupported/private URL
10. direct video upload

Record actual results.

---

# 62. FINAL DELIVERABLES

At completion, the repository must contain:

```text
backend/
ios/
benchmark/
docs/
tests/
ralph/
Dockerfile
docker-compose.yml
.env.example
README.md
```

The exact structure may change if engineering research proves a better architecture.

The repository must include:

* working backend
* working ASR routing
* fallbacks
* caption detection
* subtitle generation
* iOS Shortcut instructions
* API documentation
* deployment instructions
* benchmark system
* security documentation
* tests
* CI
* Ralph PRD
* Ralph guardrails
* Ralph progress

---

# 63. FINAL REPORT TO ME

When all Ralph iterations are complete, provide a concise final report containing:

## Architecture

What was actually built.

## Models

Which models were actually tested.

## Winner

Do NOT call something the "best" based on assumption.

Report measured results.

## Fallback chain

Show:

```text
Primary
→ fallback
→ specialist
→ final fallback
```

## Costs

Separate:

```text
free/self-hosted
API usage
potential paid usage
Render
storage
```

## iOS Shortcut

Explain exactly how to install/use it.

## Deployment

Provide exact Render configuration.

## Tests

Report:

```text
tests passed
tests failed
integration tests
security tests
benchmark results
```

## Known limitations

Be brutally honest.

Do not hide limitations.

---

# 64. MOST IMPORTANT ENGINEERING PRINCIPLE

Build the product around this philosophy:

```text
ONE SIMPLE USER ACTION
        ↓
SHARE REEL
        ↓
EVERYTHING ELSE AUTOMATIC
```

The user should NOT care:

* which ASR model ran
* which API was used
* which language was detected
* whether fallback happened
* whether the audio was normalized
* whether OCR ran
* whether Sarvam or Whisper won

They should simply receive:

```text
ACCURATE TRANSCRIPT
```

and, only when the original video actually contains captions:

```text
SRT
VTT
```

The backend should make the intelligent decisions.

The iOS Shortcut should remain extremely simple.

---

# START NOW

Do NOT ask me to provide the architecture again.

Do NOT ask me to choose the models again.

Do NOT stop after creating the PRD.

Your first actions must be:

1. Inspect current workspace.
2. Inspect available tools/skills.
3. Clone/inspect the current Ralph GitHub repository.
4. Install/configure the appropriate Ralph skill for the current Antigravity environment.
5. Inspect all current official documentation for Apple Shortcuts/App Intents, Sarvam, Render, Hugging Face and the selected ASR models.
6. Create the Ralph PRD.
7. Create guardrails.
8. Create progress tracking.
9. Break the project into executable stories.
10. Begin the Ralph loop.
11. Implement.
12. Test.
13. Debug.
14. Re-test.
15. Continue until the acceptance criteria are actually satisfied.

Do not substitute assumptions for research.

Do not stop at a prototype unless a specific external blocker makes production completion impossible.

The goal is a working, tested, deployable ReelTranscribe system.
