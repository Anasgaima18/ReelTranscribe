# ReelTranscribe iOS Shortcut & Share Sheet Integration

ReelTranscribe is engineered around a frictionless mobile experience:
**One simple tap from the iOS Share Sheet — everything else is completely automatic.**

---

## Features
- **Zero Configuration**: No language selection, model picking, or prompt engineering required.
- **Universal Input**: Automatically handles Instagram Reels, YouTube Shorts, TikTok videos, Safari web pages, Photos app videos, Voice Memos, and audio files.
- **Intelligent Caption Handling**:
  - If original video has captions: displays transcript + generated **SRT** & **WebVTT** subtitle files.
  - If original video does NOT have captions: displays transcript only. Does not fabricate subtitles.
- **Native Actions**: Copy to Clipboard, Share to other apps, Save to Files.

---

## Installation & Setup

### Method 1: Import Shortcut into Apple Shortcuts App
1. Open the **Shortcuts** app on your iPhone or iPad (iOS 16+ or iOS 17/18+ recommended).
2. Tap the `+` button in the top right to create a new Shortcut.
3. Rename the Shortcut to **`ReelTranscribe`**.
4. Tap the **(i)** Info button at the bottom and enable:
   - **Show in Share Sheet**
   - Under "Receive", check: **URLs, Safari web pages, Media, Photos, Files, Text**.
5. Add the following action steps as specified below.

---

## Detailed Shortcut Action Sequence

### 1. Receive Input
- **Action**: `Get Details of Shortcut Input`
- If Input is a URL or text containing `http`:
  - Set variable `InputType` = `url`
  - Set variable `TargetURL` = `Shortcut Input`
- If Input is a Media file / Video / Audio:
  - Set variable `InputType` = `upload`
  - Set variable `TargetFile` = `Shortcut Input`

### 2. Connect to ReelTranscribe Backend
- Set variable `BackendURL` = `https://your-reeltranscribe-app.onrender.com` (or your custom domain).

### 3. Submit Job
- **If `InputType` is `url`**:
  - **Action**: `Get Contents of URL`
  - URL: `BackendURL/v1/jobs`
  - Method: `POST`
  - Request Body: `JSON`
    - `source_type`: `url`
    - `url`: `TargetURL`
  - Save response as `JobResponse`
  - Set variable `JobID` = `JobResponse.job_id`

- **If `InputType` is `upload`**:
  - **Action**: `Get Contents of URL`
  - URL: `BackendURL/v1/media/upload`
  - Method: `POST`
  - Request Body: `Form`
    - `file`: `TargetFile`
  - Save response as `UploadResponse`
  - Then POST to `BackendURL/v1/jobs` with JSON:
    - `source_type`: `upload`
    - `upload_file_path`: `UploadResponse.file_path`
  - Set variable `JobID` = `JobResponse.job_id`

### 4. Background Polling Loop
- **Action**: `Repeat` 25 times:
  - `Wait` 2 seconds
  - `Get Contents of URL`: `BackendURL/v1/jobs/{JobID}`
  - Save as `PollStatus`
  - If `PollStatus.status` is `completed` or `failed`:
    - `Exit Repeat`
- End Repeat

### 5. Fetch Final Results
- **Action**: `Get Contents of URL`: `BackendURL/v1/jobs/{JobID}/result`
- Save as `FinalResult`

### 6. Display Result & Provide Actions
- Format text:
  ```text
  ReelTranscribe
  ✓ Transcription complete
  Language: [FinalResult.language.primary]

  Transcript:
  [FinalResult.transcription.final]
  ```

- **Check Captions**:
  - If `FinalResult.captions.detected` is `true`:
    - Append text:
      ```text
      Captions:
      ✓ Original captions detected in video.
      Subtitle files generated: SRT & WebVTT.
      ```
    - Show Menu:
      - **Copy Transcript** -> `Copy to Clipboard`
      - **Share Transcript** -> `Share`
      - **Save SRT Subtitles** -> Create text file named `captions.srt` from `FinalResult.captions.srt_content` and `Save File`
      - **Save WebVTT Subtitles** -> Create text file named `captions.vtt` from `FinalResult.captions.vtt_content` and `Save File`
  - If `FinalResult.captions.detected` is `false`:
    - Append text:
      ```text
      Captions:
      No original captions detected. Subtitle files were not generated.
      ```
    - Show Menu:
      - **Copy Transcript** -> `Copy to Clipboard`
      - **Share Transcript** -> `Share`

---

## How to Use from Instagram, YouTube, Safari, and Photos

1. **Instagram Reel**:
   - Tap the **Share** paper-airplane button on any Reel.
   - Tap **Share via...**
   - Tap **ReelTranscribe**.
   - Watch the notification appear with your completed transcript.

2. **YouTube Shorts**:
   - Tap **Share** -> **More** -> **ReelTranscribe**.

3. **Photos / Saved Video**:
   - Open any video in the Photos app -> Tap the Share button -> **ReelTranscribe**.
