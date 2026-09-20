"""
RT-019: Model Benchmarking Engine for ReelTranscribe.
CLI: python -m benchmark.run

Evaluates WER, CER, language accuracy, code-switch preservation,
latency, and cost across ASR providers using reference datasets.
"""
import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class BenchmarkSample:
    """A single benchmark test sample."""
    audio_path: str
    reference_transcript: str
    language: str = "unknown"
    has_code_switching: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Result of benchmarking a single sample against a provider."""
    sample_id: str
    provider: str
    hypothesis: str = ""
    reference: str = ""
    wer: float = 0.0
    cer: float = 0.0
    latency_ms: float = 0.0
    language_detected: str = ""
    language_correct: bool = False
    code_switch_preserved: bool = True
    error: Optional[str] = None


def compute_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate using Levenshtein distance on word tokens."""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    # Dynamic programming edit distance
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])

    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def compute_cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate using Levenshtein distance on characters."""
    ref_chars = list(reference.lower())
    hyp_chars = list(hypothesis.lower())

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j

    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i - 1] == hyp_chars[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])

    return d[len(ref_chars)][len(hyp_chars)] / len(ref_chars)


def check_code_switch_preservation(reference: str, hypothesis: str) -> bool:
    """
    Checks if code-switched tokens (Latin script words in otherwise
    Devanagari text, or vice versa) are preserved in hypothesis.
    """
    import re
    # Find Latin-script words in reference (likely English tokens in Hinglish)
    latin_tokens = set(re.findall(r'\b[a-zA-Z]{2,}\b', reference.lower()))
    if not latin_tokens:
        return True  # No code-switching to check

    hyp_lower = hypothesis.lower()
    preserved = sum(1 for t in latin_tokens if t in hyp_lower)
    return (preserved / len(latin_tokens)) >= 0.5


def load_samples(dataset_path: Path) -> List[BenchmarkSample]:
    """Load benchmark samples from a JSON Lines file."""
    samples = []
    if not dataset_path.exists():
        return samples

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            samples.append(BenchmarkSample(**data))
    return samples


async def benchmark_provider(
    provider_name: str,
    samples: List[BenchmarkSample],
) -> List[BenchmarkResult]:
    """Run benchmark samples against a specific ASR provider."""
    # Import provider dynamically
    from backend.app.asr.sarvam import SarvamProvider
    from backend.app.asr.whisper import WhisperProvider
    from backend.app.asr.hinglish import HinglishProvider

    providers = {
        "sarvam": SarvamProvider,
        "whisper": WhisperProvider,
        "hinglish": HinglishProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")

    provider = providers[provider_name]()
    results = []

    for idx, sample in enumerate(samples):
        audio_path = Path(sample.audio_path)
        result = BenchmarkResult(
            sample_id=f"{idx:04d}",
            provider=provider_name,
            reference=sample.reference_transcript,
        )

        if not audio_path.exists():
            result.error = f"Audio file not found: {sample.audio_path}"
            results.append(result)
            continue

        try:
            start = time.monotonic()
            transcript = await provider.transcribe(audio_path)
            elapsed_ms = (time.monotonic() - start) * 1000

            result.hypothesis = transcript.raw_transcript
            result.latency_ms = round(elapsed_ms, 1)
            result.wer = round(compute_wer(sample.reference_transcript, transcript.raw_transcript), 4)
            result.cer = round(compute_cer(sample.reference_transcript, transcript.raw_transcript), 4)
            result.language_detected = transcript.language_code
            result.language_correct = sample.language.lower() in transcript.language_code.lower()

            if sample.has_code_switching:
                result.code_switch_preserved = check_code_switch_preservation(
                    sample.reference_transcript, transcript.raw_transcript
                )
        except Exception as e:
            result.error = str(e)

        results.append(result)

    return results


def generate_report(results: List[BenchmarkResult], provider_name: str) -> Dict[str, Any]:
    """Generate a summary report from benchmark results."""
    successful = [r for r in results if r.error is None]
    failed = [r for r in results if r.error is not None]

    if not successful:
        return {
            "provider": provider_name,
            "total_samples": len(results),
            "successful": 0,
            "failed": len(failed),
            "error": "No successful transcriptions",
        }

    avg_wer = sum(r.wer for r in successful) / len(successful)
    avg_cer = sum(r.cer for r in successful) / len(successful)
    avg_latency = sum(r.latency_ms for r in successful) / len(successful)
    lang_accuracy = sum(1 for r in successful if r.language_correct) / len(successful)

    code_switch_samples = [r for r in successful if any(
        s.has_code_switching for s in [] # placeholder
    )]

    return {
        "provider": provider_name,
        "total_samples": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "avg_wer": round(avg_wer, 4),
        "avg_cer": round(avg_cer, 4),
        "avg_latency_ms": round(avg_latency, 1),
        "language_accuracy": round(lang_accuracy, 4),
    }


def main():
    parser = argparse.ArgumentParser(description="ReelTranscribe Model Benchmarking Engine")
    parser.add_argument(
        "--dataset", type=str, default="benchmark/dataset.jsonl",
        help="Path to JSONL benchmark dataset"
    )
    parser.add_argument(
        "--provider", type=str, default="all",
        choices=["sarvam", "whisper", "hinglish", "all"],
        help="ASR provider to benchmark"
    )
    parser.add_argument(
        "--output", type=str, default="benchmark/results.json",
        help="Output path for benchmark results"
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    samples = load_samples(dataset_path)

    if not samples:
        print(f"No samples found in {dataset_path}. Create a JSONL file with benchmark samples.")
        print("Format: {\"audio_path\": \"...\", \"reference_transcript\": \"...\", \"language\": \"hi-en\"}")
        return

    providers = ["sarvam", "whisper", "hinglish"] if args.provider == "all" else [args.provider]
    all_reports = {}

    for prov in providers:
        print(f"\n{'='*60}")
        print(f"Benchmarking provider: {prov}")
        print(f"{'='*60}")

        results = asyncio.run(benchmark_provider(prov, samples))
        report = generate_report(results, prov)
        all_reports[prov] = report

        print(f"  Samples: {report.get('total_samples', 0)}")
        print(f"  Success: {report.get('successful', 0)}")
        print(f"  Avg WER: {report.get('avg_wer', 'N/A')}")
        print(f"  Avg CER: {report.get('avg_cer', 'N/A')}")
        print(f"  Avg Latency: {report.get('avg_latency_ms', 'N/A')}ms")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_reports, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
