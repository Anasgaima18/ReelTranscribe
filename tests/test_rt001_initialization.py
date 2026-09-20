import os
import json
from pathlib import Path

def test_ralph_files_exist():
    workspace = Path(__file__).resolve().parent.parent
    ralph_dir = workspace / "ralph"
    assert (ralph_dir / "prd.json").is_file()
    assert (ralph_dir / "prompt.md").is_file()
    assert (ralph_dir / "guardrails.md").is_file()
    assert (ralph_dir / "progress.txt").is_file()

def test_prd_validity():
    workspace = Path(__file__).resolve().parent.parent
    prd_file = workspace / "ralph" / "prd.json"
    with open(prd_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["project"] == "ReelTranscribe"
    assert len(data["userStories"]) == 23
    assert data["userStories"][0]["id"] == "RT-001"

def test_ralph_skill_installed():
    workspace = Path(__file__).resolve().parent.parent
    skill_file = workspace / ".agents" / "skills" / "ralph" / "SKILL.md"
    assert skill_file.is_file()
    content = skill_file.read_text(encoding="utf-8")
    assert "name: ralph" in content

def test_directories_exist():
    workspace = Path(__file__).resolve().parent.parent
    assert (workspace / "backend" / "app").is_dir()
    assert (workspace / "ios").is_dir()
    assert (workspace / "benchmark").is_dir()
    assert (workspace / "docs").is_dir()
    assert (workspace / "tests").is_dir()
