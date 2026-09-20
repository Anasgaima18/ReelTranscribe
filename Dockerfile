# --- Build Stage ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime Stage ---
FROM python:3.12-slim

# Security: run as non-root user
RUN groupadd -r reeltranscribe && useradd -r -g reeltranscribe -d /app -s /sbin/nologin reeltranscribe

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY backend/ backend/
COPY benchmark/ benchmark/

# Create temp directory with correct permissions
RUN mkdir -p /app/temp && chown -R reeltranscribe:reeltranscribe /app

# Switch to non-root user
USER reeltranscribe

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
