"""
RT-022: Technical Documentation Tests.
Validates the presence, formatting, and essential sections of all docs.
"""
from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_readme_exists_and_complete():
    """Verify README.md exists and has all essential sections."""
    readme_path = PROJECT_ROOT / "README.md"
    assert readme_path.exists(), "README.md is missing"
    content = readme_path.read_text(encoding="utf-8")
    assert len(content) > 1000, "README.md is too short"
    assert "# ReelTranscribe" in content
    assert "Deployment" in content or "Architecture" in content
    assert "API" in content or "Quick Start" in content


def test_required_docs_exist():
    """Verify all 7 domain docs exist and are non-empty."""
    required_docs = [
        "architecture.md",
        "api.md",
        "ios-shortcut.md",
        "deployment.md",
        "providers.md",
        "security.md",
        "benchmarking.md",
    ]
    for doc in required_docs:
        doc_path = DOCS_ROOT / doc
        assert doc_path.exists(), f"Document docs/{doc} is missing"
        text = doc_path.read_text(encoding="utf-8")
        assert len(text.strip()) > 300, f"Document docs/{doc} is surprisingly short ({len(text)} bytes)"


def test_docs_contain_key_architectural_references():
    """Check that key components and configurations are documented."""
    arch_content = (DOCS_ROOT / "architecture.md").read_text(encoding="utf-8")
    assert "Sarvam" in arch_content
    assert "Whisper" in arch_content

    sec_content = (DOCS_ROOT / "security.md").read_text(encoding="utf-8")
    assert "SSRF" in sec_content
    assert "is_ip_allowed" in sec_content or "sanitize_filename" in sec_content

    bench_content = (DOCS_ROOT / "benchmarking.md").read_text(encoding="utf-8")
    assert "WER" in bench_content
