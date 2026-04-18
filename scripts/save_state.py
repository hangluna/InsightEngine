#!/usr/bin/env python3
"""Session state manager for InsightEngine pipeline.

Commands:
    python3 scripts/save_state.py check        # Check if a session state exists
    python3 scripts/save_state.py save <json>   # Save current state (JSON string or @file)
    python3 scripts/save_state.py resume-plan   # Return pending steps as JSON
    python3 scripts/save_state.py archive       # Archive current state and start fresh
    python3 scripts/save_state.py update --step <name> [--output-file <path>]  # Update step status
    python3 scripts/save_state.py complete      # Mark pipeline as completed

State file: tmp/.session-state.json

Enhanced Schema (v2 — Phase 9):
    raw_prompt: str             # Original user request
    intent_classification: str  # synthesis | creation | research | design | data_collection | mixed
    analyzed_requirements: dict # Expanded dimensions from analysis
    generated_plan: dict        # Workflow plan from strategist
    step_states: list           # Per-step: {name, status, input_summary, output_summary, started_at, completed_at}
    audit_test_cases: list      # Dynamic test cases from auditor
    score_history: list         # [{attempt, score, failing_tests}]
    created_skills: list        # Runtime-created skills/agents
    output_files: list          # [{path, hash, format, size}]
    status: str                 # IN_PROGRESS | COMPLETED | FAILED
    schema_version: int         # 2
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Resolve project root relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "tmp" / ".session-state.json"
ARCHIVE_DIR = PROJECT_ROOT / "tmp" / "archives"


def ensure_dirs():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> Optional[dict]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def cmd_check():
    state = load_state()
    if state is None:
        print("NO_STATE")
        return

    status = state.get("status", "UNKNOWN")
    if status == "COMPLETED":
        print("COMPLETED")
        return

    # IN_PROGRESS — show summary
    print(f"IN_PROGRESS")
    print(f"Request: {state.get('original_request', 'N/A')[:200]}")
    print(f"Current step: {state.get('current_step', 'N/A')}")
    print(f"Started: {state.get('started_at', 'N/A')}")
    completed = state.get("completed_steps", [])
    pending = state.get("pending_steps", [])
    print(f"Completed: {len(completed)} steps — {', '.join(completed)}")
    print(f"Pending: {len(pending)} steps — {', '.join(pending)}")


def cmd_save(data_arg: str):
    ensure_dirs()
    if data_arg.startswith("@"):
        # Read from file
        filepath = Path(data_arg[1:])
        data = json.loads(filepath.read_text(encoding="utf-8"))
    else:
        data = json.loads(data_arg)

    data["updated_at"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STATE_SAVED: {STATE_FILE}")


def cmd_resume_plan():
    state = load_state()
    if state is None:
        print(json.dumps({"error": "NO_STATE"}, ensure_ascii=False))
        sys.exit(1)

    pending = state.get("pending_steps", [])
    plan = {
        "original_request": state.get("original_request", ""),
        "current_step": state.get("current_step", ""),
        "pending_steps": pending,
        "execution_plan": state.get("execution_plan", {}),
        "content_depth": state.get("content_depth", "comprehensive"),
    }
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def cmd_archive():
    state = load_state()
    if state is None:
        print("NO_STATE — nothing to archive")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = ARCHIVE_DIR / f"session-state_{timestamp}.json"
    shutil.copy2(STATE_FILE, archive_path)
    STATE_FILE.unlink()
    print(f"ARCHIVED: {archive_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: save_state.py <check|save|resume-plan|archive> [data]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        cmd_check()
    elif command == "save":
        if len(sys.argv) < 3:
            print("Error: save requires a JSON argument")
            sys.exit(1)
        cmd_save(sys.argv[2])
    elif command == "resume-plan":
        cmd_resume_plan()
    elif command == "archive":
        cmd_archive()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
