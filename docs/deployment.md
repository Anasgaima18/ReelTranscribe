# Deployment Guide

## Local Development

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

```bash
# Build and run
docker compose up --build

# Or standalone
docker build -t reeltranscribe .
docker run -p 8000:8000 --env-file .env reeltranscribe
```

The Dockerfile uses:
- Multi-stage build (builder + runtime)
- Non-root user (`reeltranscribe`)
- Built-in HEALTHCHECK on `/health`
- FFmpeg pre-installed

## Render (Free Tier)

1. Push your repo to GitHub
2. Connect repo to [Render](https://render.com)
3. Render auto-detects `render.yaml` and configures:
   - Python 3.12 runtime
   - Health check on `/health`
   - Environment variables (set secrets in Render dashboard)
4. Set secret env vars in Render dashboard:
   - `SARVAM_API_KEY`
   - `HF_TOKEN`

### Free Tier Constraints
- 0.1 CPU, 512 MB RAM
- Spins down after 15 min inactivity (cold starts ~30s)
- Ephemeral filesystem (temp files cleaned on restart)
- Whisper CANNOT run in-memory — offloaded to HF Inference API

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SARVAM_API_KEY` | Yes | `""` | Sarvam AI API key |
| `HF_TOKEN` | Yes | `""` | Hugging Face token |
| `API_SECRET` | Recommended | `""` | API authentication secret |
| `APP_ENV` | No | `development` | Environment name |
| `RATE_LIMIT_PER_MINUTE` | No | `30` | Max requests per minute per client |
| `MAX_FILE_SIZE_MB` | No | `100` | Max upload file size |
| `MAX_DURATION_SECONDS` | No | `300` | Max media duration (5 min) |
