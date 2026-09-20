# ReelTranscribe API Reference

## Base URL

```
https://your-domain.com
```

---

## `GET /`

Returns service metadata.

**Response:**
```json
{
  "service": "ReelTranscribe",
  "version": "1.0.0",
  "status": "operational"
}
```

---

## `GET /health`

Returns service health and provider availability.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "providers": {
    "sarvam": {"enabled": true, "configured": true},
    "whisper": {"enabled": true, "configured": true},
    "hinglish": {"enabled": true, "configured": true}
  }
}
```

---

## `POST /v1/jobs`

Submit a transcription job.

**Request Body:**
```json
{
  "url": "https://www.instagram.com/reel/ABC123/",
  "source_type": "url"
}
```

Or for uploads:
```json
{
  "upload_file_path": "/path/to/uploaded/file.mp4",
  "source_type": "upload"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "progress_percentage": 0,
  "poll_url": "/v1/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "result_url": "/v1/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890/result"
}
```

---

## `GET /v1/jobs/{job_id}`

Poll job status.

**Response:**
```json
{
  "job_id": "a1b2c3d4...",
  "status": "transcribing",
  "progress_percentage": 50,
  "created_at": 1695200000.0,
  "updated_at": 1695200030.0
}
```

**Status Values:** `queued`, `downloading`, `extracting_audio`, `transcribing`, `validating_transcript`, `detecting_captions`, `generating_subtitles`, `completed`, `failed`

---

## `GET /v1/jobs/{job_id}/result`

Get completed result.

**Response (200 OK, when completed):**
```json
{
  "job_id": "a1b2c3d4...",
  "status": "completed",
  "source": {
    "type": "url",
    "provider": "instagram",
    "url": "https://..."
  },
  "media": {
    "duration_seconds": 30.5,
    "audio_detected": true,
    "video_detected": true
  },
  "language": {
    "primary": "hi-en",
    "probability": 0.92,
    "code_mixed": true
  },
  "transcription": {
    "provider": "sarvam",
    "model": "saaras:v4",
    "raw": "yeh mera video hai...",
    "final": "Yeh mera video hai...",
    "confidence": 0.88,
    "fallback_used": false,
    "postprocessing_applied": ["capitalization", "spacing"],
    "quality_gate": {
      "passed": true,
      "score": 0.85,
      "flags": []
    }
  },
  "captions": {
    "detected": true,
    "type": "embedded",
    "confidence": 1.0,
    "srt_content": "1\n00:00:00,000 --> 00:00:05,000\nYeh mera video hai...",
    "vtt_content": "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nYeh mera video hai...",
    "srt_available": true,
    "vtt_available": true
  }
}
```

---

## `POST /v1/media/upload`

Direct file upload.

**Request:** `multipart/form-data` with `file` field.

**Supported formats:** mp4, mov, webm, m4v, mp3, wav, m4a, aac, flac, ogg, opus

**Size limit:** 100 MB (configurable via `MAX_FILE_SIZE_MB`)

---

## Error Responses

All errors follow the structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "retryable": false
  }
}
```

**Error Codes:**
| Code | HTTP | Description |
|------|------|-------------|
| `INVALID_URL` | 400 | URL is malformed or missing |
| `UNSUPPORTED_URL` | 400 | URL scheme not supported |
| `SSRF_PROHIBITED` | 403 | URL resolves to private/internal IP |
| `MEDIA_NOT_FOUND` | 404 | Media or job not found |
| `MEDIA_TOO_LARGE` | 413 | File exceeds size limit |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `ASR_FAILED` | 500 | All ASR providers failed |
| `ASR_RATE_LIMITED` | 429 | ASR provider rate limited |
| `QUALITY_CHECK_FAILED` | 422 | Transcript failed quality gate |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
