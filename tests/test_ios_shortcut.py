import json
from pathlib import Path

def test_ios_shortcut_workflow_definition():
    workspace = Path(__file__).resolve().parent.parent
    workflow_file = workspace / "ios" / "shortcut_workflow.json"
    assert workflow_file.is_file()

    with open(workflow_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["name"] == "ReelTranscribe"
    assert "URL" in data["accepted_types"]
    assert "Media" in data["accepted_types"]
    assert len(data["workflow_steps"]) >= 6

    # Verify key steps exist
    descriptions = [s.get("description", "") + s.get("action", "") for s in data["workflow_steps"]]
    desc_text = " ".join(descriptions).lower()
    assert "input" in desc_text
    assert "poll" in desc_text or "repeat" in desc_text
    assert "captions" in desc_text

def test_ios_documentation_exists():
    workspace = Path(__file__).resolve().parent.parent
    readme_file = workspace / "ios" / "README.md"
    assert readme_file.is_file()
    content = readme_file.read_text(encoding="utf-8")

    assert "Share Sheet" in content
    assert "Instagram" in content
    assert "YouTube" in content
    assert "SRT" in content
    assert "WebVTT" in content
