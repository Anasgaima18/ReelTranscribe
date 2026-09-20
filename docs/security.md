# Security Architecture & Hardening

ReelTranscribe implements defense-in-depth security engineered for public API and media ingestion workflows.

## Threat Model

The service accepts arbitrary URLs and binary media files from untrusted iOS Shortcut and HTTP clients. The primary threat vectors are:

1. **Server-Side Request Forgery (SSRF)**: Attackers submitting URLs targeting internal cloud metadata services (`169.254.169.254`), container interfaces, or localhost networks.
2. **Denial of Service (DoS)**: Attackers submitting multi-gigabyte files or infinite media streams to exhaust server memory and disk space.
3. **Remote Code Execution (RCE) / Command Injection**: Malicious filenames or container parameters exploiting FFmpeg or underlying shell execution.
4. **Credential Leakage**: Leaking API tokens (`SARVAM_API_KEY`, `HF_TOKEN`, `API_SECRET`) in public health checks, logs, or error responses.
5. **Path Traversal**: Filenames containing `../` or null bytes designed to overwrite arbitrary host files.

---

## Security Controls

### 1. SSRF Mitigation (`backend/app/core/security.py`)

- **Strict URL Scheme Whitelist**: Only `http` and `https` schemes are accepted. All other schemes (`file://`, `gopher://`, `ftp://`) are rejected with `UnsupportedURLError`.
- **Hostname Blacklist**: Prohibits `localhost`, `metadata.google.internal`, `instance-data`, `169.254.169.254`, `metadata.azure.com`, and `.local` mDNS domains.
- **DNS Resolution Verification**: Before making outbound requests, ReelTranscribe resolves the destination hostname via `socket.getaddrinfo` and inspects all resolved IP candidates.
- **IP Address Validation (`is_ip_allowed`)**:
  - Drops IPv4 and IPv6 private blocks (RFC 1918, RFC 4193).
  - Drops loopback addresses (`127.0.0.0/8`, `::1`).
  - Drops link-local and cloud metadata addresses (`169.254.0.0/16`, `fe80::/10`).
  - Drops multicast and reserved blocks.

### 2. Media Upload & Filename Sanitization (`backend/app/core/rate_limit.py`, `backend/app/api/media.py`)

- **Streaming Size Enforcement**: Upload streams are metered chunk-by-chunk. If cumulative bytes exceed `MAX_FILE_SIZE_MB` (default: 100 MB), the connection is terminated immediately with HTTP 413.
- **Magic Byte & MIME Validation**: Uploaded files are validated against allowed audio/video MIME types (`video/mp4`, `video/quicktime`, `audio/mpeg`, `audio/wav`, etc.).
- **Filename Sanitization (`sanitize_filename`)**:
  - Strips null bytes (`\0`).
  - Strips path traversal sequences (`../`, `..`).
  - Strips directory separators.
  - Whitelists safe alphanumeric characters, underscores, dashes, and periods.
  - Truncates filenames to 100 characters.

### 3. Rate Limiting & Abuse Prevention (`backend/app/core/rate_limit.py`)

- **Sliding Window Rate Limiter**: Configurable per-client IP window tracking (default: 30 requests/minute).
- **Graceful Exemption**: Health (`/health`) and metadata (`/`) endpoints are exempt to allow container orchestrator probes.
- **HTTP 429 Responses**: Returns structured JSON error payloads with `Retry-After` header when limit is exceeded.

### 4. Credential Protection & Secret Masking (`backend/app/api/health.py`, `backend/app/core/logging.py`)

- **Health Check Masking**: The `/health` endpoint exposes only boolean availability flags (`sarvam: true/false`), never raw API keys, lengths, or substrings.
- **Log Redaction**: Structured JSON logging filters sensitive headers (`Authorization`, `X-API-Secret`) and environment variables.

### 5. HTTP Security Headers (`backend/app/core/rate_limit.py`)

Every response includes production-grade security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### 6. Container Isolation & Temporary Directory Hygiene (`backend/app/jobs/manager.py`)

- **Non-Root Execution**: Dockerfile specifies an unprivileged `appuser` (UID 1000).
- **Ephemeral Job Directories**: Each transcription job writes to an isolated UUID temporary directory under `/tmp/reeltranscribe/jobs/{job_id}`.
- **Guaranteed Cleanup**: Temporary directories are recursively removed in job `finally` blocks, even on failure or unhandled exceptions.
