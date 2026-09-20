# Benchmarking & Accuracy Evaluation

ReelTranscribe includes a standardized benchmark harness designed to evaluate Word Error Rate (WER), Character Error Rate (CER), and Hinglish code-switching fidelity across ASR providers.

## Evaluation Methodology

Transcribing code-switched Hindi-English (Hinglish) content poses unique challenges:
1. **Script Mixing**: Models frequently translate Hindi words into English or transliterate English words into Devanagari script.
2. **Homophonic Ambiguity**: Colloquial Hindi words phonetically transcribed in Latin script (e.g., "bhai", "yaar", "achha") vary widely in spelling.
3. **Repetition & Hallucination Loops**: Low-confidence audio segments can trigger looping phrases in autoregressive decoder architectures.

The benchmark harness tests:
- **WER (Word Error Rate)**: Normalized word edit distance via Levenshtein DP.
- **CER (Character Error Rate)**: Normalized character edit distance for phonetic alignment.
- **Code-Switching Preservation**: Verifies that mixed English and Hindi tokens in Roman script are preserved verbatim without unwanted translation.

---

## Test Dataset

The benchmark suite includes curated ground-truth clips under `benchmark/samples/` representing:
1. **Pure Hindi (Latin/Devanagari)**: Standard conversational Hindi.
2. **Hinglish Code-Switched**: Fast-paced tech/lifestyle Reels with frequent intra-sentential language shifts.
3. **Pure English**: Standard international English spoken with Indian inflection.
4. **Noisy/Music Background**: Reels with heavy background music and sound effects.

---

## Running Benchmarks

Run the evaluation script via Python:

```bash
python -m benchmark.run
```

To run the automated regression tests:

```bash
pytest tests/test_rt019_benchmark.py -v
```

---

## Metric Calculation

### Word Error Rate (WER)
$$\text{WER} = \frac{S + D + I}{N}$$
Where:
- $S$: Substitutions
- $D$: Deletions
- $I$: Insertions
- $N$: Total words in reference ground truth

### Code-Switching Accuracy
The evaluation harness computes the token intersection ratio for key code-switched words:
$$\text{CS Accuracy} = \frac{|\text{Spoken English Tokens} \cap \text{Transcribed English Tokens}|}{|\text{Spoken English Tokens}|}$$

---

## Target SLAs

| Metric | Target | Fail Threshold |
| :--- | :--- | :--- |
| Hinglish WER | < 18.0% | > 25.0% |
| English WER | < 12.0% | > 18.0% |
| Code-Switching Retention | > 92.0% | < 85.0% |
| Processing Speed (RTF) | < 0.5x Realtime | > 1.0x Realtime |
