# iOS Shortcut Guide

## Overview

ReelTranscribe integrates with iOS via the Share Sheet. When you share a Reel, video, or audio file, the Shortcut sends it to your ReelTranscribe backend, polls for completion, and copies the transcript to your clipboard.

## Installation

1. Open **Shortcuts** app on your iPhone/iPad
2. Tap **+** to create a new Shortcut
3. Name it **ReelTranscribe**
4. Enable **Show in Share Sheet**
5. Set accepted types: **URLs, Media, Files**

## Shortcut Steps

### Step 1: Receive Share Sheet Input
- Action: **Receive input from Share Sheet**
- Input types: URLs, Media, Files, Text

### Step 2: Determine Input Type
- **If** input is a URL:
  - Set `source_type` = `"url"`
  - Set `payload` = `{"url": "<input>", "source_type": "url"}`
- **Otherwise** (file/media):
  - Upload file via `POST /v1/media/upload`
  - Set `source_type` = `"upload"`
  - Set `payload` = `{"upload_file_path": "<response.path>", "source_type": "upload"}`

### Step 3: Submit Job
- Action: **Get Contents of URL**
- URL: `https://your-server.onrender.com/v1/jobs`
- Method: `POST`
- Headers: `Content-Type: application/json`
- Body: `payload` from Step 2

### Step 4: Extract Job ID
- Action: **Get Dictionary Value** for key `job_id`

### Step 5: Poll Until Complete
- Action: **Repeat** (max 60 times)
  - **Wait** 3 seconds
  - **Get Contents of URL**: `https://your-server.onrender.com/v1/jobs/{job_id}`
  - **Get Dictionary Value** for key `status`
  - **If** status is `completed` → **Exit Repeat**
  - **If** status is `failed` → **Show Alert** "Transcription failed" → **Exit Repeat**

### Step 6: Get Result
- Action: **Get Contents of URL**: `https://your-server.onrender.com/v1/jobs/{job_id}/result`
- Extract `transcription.final` from response

### Step 7: Output
- **Copy to Clipboard**: transcript text
- **Show Notification**: "Transcript ready! Copied to clipboard."
- Optionally: **Share Sheet** to send transcript elsewhere

## Configuration

Replace `https://your-server.onrender.com` with your actual deployment URL.

## Tips

- The shortcut polls every 3 seconds for up to 3 minutes
- For long videos, increase the repeat count
- The free Render tier may need a cold-start wake-up (first request takes ~30s)
