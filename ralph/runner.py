"""
Ralph Loop Story Runner & PRD Manager for ReelTranscribe.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RALPH_DIR = Path(__file__).resolve().parent
PRD_PATH = RALPH_DIR / "prd.json"
PROGRESS_PATH = RALPH_DIR / "progress.txt"
GUARDRAILS_PATH = RALPH_DIR / "guardrails.md"


def load_prd() -> dict:
    with open(PRD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_prd(prd: dict) -> None:
    with open(PRD_PATH, "w", encoding="utf-8") as f:
        json.dump(prd, f, indent=2)


def get_next_story(prd: dict) -> dict | None:
    for story in prd.get("userStories", []):
        if not story.get("passes", False) and not story.get("blocked", False):
            return story
    return None


def mark_story_passed(story_id: str, changes_summary: str, tests_summary: str) -> None:
    prd = load_prd()
    found = False
    for story in prd.get("userStories", []):
        if story["id"] == story_id:
            story["passes"] = True
            story["notes"] = f"Passed at {datetime.now(timezone.utc).isoformat()}: {tests_summary}"
            found = True
            break

    if not found:
        print(f"Error: Story {story_id} not found in PRD.")
        sys.exit(1)

    save_prd(prd)

    # Append to progress.txt
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    next_story = get_next_story(prd)
    next_id = next_story["id"] if next_story else "ALL COMPLETE"

    log_entry = (
        f"[{timestamp}] {story_id} | Changes: {changes_summary} | "
        f"Tests: {tests_summary} | Status: PASSED | Next: {next_id}\n"
    )
    with open(PROGRESS_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Successfully marked {story_id} as PASSED. Next story: {next_id}")


def status() -> None:
    prd = load_prd()
    stories = prd.get("userStories", [])
    passed = sum(1 for s in stories if s.get("passes", False))
    total = len(stories)
    print(f"\n================ REELTRANSCRIBE RALPH STATUS ================")
    print(f"Progress: {passed}/{total} stories completed ({passed/total*100:.1f}%)")
    print("-------------------------------------------------------------")
    for s in stories:
        flag = "[PASS]" if s.get("passes") else ("[BLOCKED]" if s.get("blocked") else "[TODO]")
        print(f"{flag} {s['id']}: {s['title']}")
    next_s = get_next_story(prd)
    if next_s:
        print(f"\n>>> NEXT ACTIVE STORY: {next_s['id']} - {next_s['title']}")
    else:
        print("\n>>> ALL STORIES COMPLETED!")
    print("=============================================================\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status()
    elif len(sys.argv) > 3 and sys.argv[1] == "pass":
        mark_story_passed(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "All tests passed")
    else:
        status()
