"""
Async Job Pipeline Execution Worker.
"""
import shutil
import asyncio
from pathlib import Path
from typing import Optional

from backend.app.config import settings
from backend.app.jobs.queue import default_job_store, JobStatus, JobRecord
from backend.app.media.resolver import default_resolver
from backend.app.media.probe import probe_media
from backend.app.media.ffmpeg import extract_normalized_audio
from backend.app.asr.router import default_asr_router
from backend.app.asr.scoring import default_quality_analyzer
from backend.app.asr.normalizer import SafeTranscriptNormalizer
from backend.app.captions.detector import default_caption_detector
from backend.app.captions.subtitles import default_subtitle_generator
from backend.app.core.errors import AppError, InternalError


async def process_transcription_job(job_id: str) -> None:
    job = default_job_store.get_job(job_id)
    if not job:
        return

    job_dir = settings.TEMP_DIR / f"job_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        media_file_path: Optional[Path] = None
        source_provider = "unknown"

        # 1. Ingestion / Download
        if job.source_type == "url" and job.source_url:
            default_job_store.update_status(job_id, JobStatus.DOWNLOADING, progress=15)
            media_info = await default_resolver.resolve_and_download(job.source_url, job_dir)
            media_file_path = media_info.file_path
            source_provider = media_info.provider_name
        elif job.source_type == "upload" and job.upload_file_path:
            src_p = Path(job.upload_file_path)
            if src_p.exists():
                dest_p = job_dir / src_p.name
                shutil.copy2(src_p, dest_p)
                media_file_path = dest_p
                source_provider = "direct_upload"
            else:
                raise AppError("MEDIA_NOT_FOUND", "Uploaded source media file was not found on server.")

        if not media_file_path or not media_file_path.exists():
            raise AppError("MEDIA_DOWNLOAD_FAILED", "Media file could not be located after retrieval.")

        # 2. Extract & Normalize Audio
        default_job_store.update_status(job_id, JobStatus.EXTRACTING_AUDIO, progress=30)
        norm_audio_path = job_dir / "audio_16k_mono.wav"
        extract_normalized_audio(media_file_path, norm_audio_path, sample_rate=16000, channels=1)

        # 3. Media Probe Duration
        probe = probe_media(media_file_path)
        duration_sec = probe.duration_seconds or 0.0

        # 4. Transcribe via ASR Router
        default_job_store.update_status(job_id, JobStatus.TRANSCRIBING, progress=50)
        transcript_res = await default_asr_router.transcribe(norm_audio_path)

        # 5. Quality Gate
        default_job_store.update_status(job_id, JobStatus.VALIDATING_TRANSCRIPT, progress=70)
        quality = default_quality_analyzer.evaluate(transcript_res, audio_duration_seconds=duration_sec)

        # 6. Normalize Transcript
        normalized = SafeTranscriptNormalizer.normalize(transcript_res.raw_transcript)

        # 7. Detect Captions
        default_job_store.update_status(job_id, JobStatus.DETECTING_CAPTIONS, progress=85)
        frames_dir = job_dir / "caption_frames"
        caption_res = default_caption_detector.detect(media_file_path, temp_frames_dir=frames_dir)

        # 8. Subtitle Generation (Conditional on original captions)
        default_job_store.update_status(job_id, JobStatus.GENERATING_SUBTITLES, progress=95)
        sub_dir = job_dir / "subtitles"
        srt_file, vtt_file = default_subtitle_generator.generate(
            chunks=transcript_res.chunks,
            captions_detected=caption_res.captions_detected,
            output_dir=sub_dir,
            base_name=f"transcript_{job_id}"
        )

        srt_content = srt_file.read_text(encoding="utf-8") if srt_file and srt_file.exists() else None
        vtt_content = vtt_file.read_text(encoding="utf-8") if vtt_file and vtt_file.exists() else None

        # Build Final Result Payload matching Section 27
        result_payload = {
            "job_id": job_id,
            "status": "completed",
            "source": {
                "type": job.source_type,
                "provider": source_provider,
                "url": job.source_url if job.source_type == "url" else None
            },
            "media": {
                "duration_seconds": round(duration_sec, 2),
                "audio_detected": probe.has_audio,
                "video_detected": probe.has_video
            },
            "language": {
                "primary": transcript_res.language_code,
                "probability": transcript_res.language_probability,
                "code_mixed": "hi-en" in transcript_res.language_code or transcript_res.metadata.get("mode") == "codemix"
            },
            "transcription": {
                "provider": transcript_res.provider_name,
                "model": transcript_res.model_name,
                "raw": normalized.raw_transcript,
                "final": normalized.final_transcript,
                "confidence": transcript_res.confidence,
                "fallback_used": transcript_res.fallback_used,
                "postprocessing_applied": normalized.postprocessing_applied,
                "quality_gate": {
                    "passed": quality.passed,
                    "score": quality.score,
                    "flags": quality.flags
                }
            },
            "captions": {
                "detected": caption_res.captions_detected,
                "type": caption_res.caption_type,
                "confidence": caption_res.confidence,
                "srt_content": srt_content,
                "vtt_content": vtt_content,
                "srt_available": bool(srt_content),
                "vtt_available": bool(vtt_content)
            }
        }

        default_job_store.update_status(
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result=result_payload
        )

    except AppError as e:
        default_job_store.update_status(
            job_id,
            JobStatus.FAILED,
            progress=100,
            error=e.to_dict()["error"]
        )
    except Exception as e:
        err = InternalError(f"Job failed during execution: {str(e)}")
        default_job_store.update_status(
            job_id,
            JobStatus.FAILED,
            progress=100,
            error=err.to_dict()["error"]
        )
    finally:
        # Guarantee Ephemeral Disk File Cleanup (Section 54)
        if not settings.DEBUG and job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
        # If there was an uploaded temp dir, clean it too
        if job.upload_file_path:
            up_dir = Path(job.upload_file_path).parent
            if up_dir.exists() and "upload_" in up_dir.name:
                shutil.rmtree(up_dir, ignore_errors=True)
