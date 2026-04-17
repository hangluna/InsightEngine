#!/usr/bin/env python3
"""
InsightEngine — Session State Manager
Atomic read/write of pipeline session state to tmp/.session-state.json

Usage:
  python3 scripts/save_state.py init   --request "..." --plan '{"input_sources":...}' [--version 1.0]
  python3 scripts/save_state.py update --step <name> --output-file <path> [--notes "..."]
  python3 scripts/save_state.py complete
  python3 scripts/save_state.py read
  python3 scripts/save_state.py archive

All operations are atomic: write to .session-state.json.tmp → rename to .session-state.json
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path("tmp/.session-state.json")
VERSION = "1.0"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load() -> dict:
    """Load existing state or raise if missing."""
    if not STATE_FILE.exists():
        print(f"ERROR: State file not found: {STATE_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(state: dict) -> None:
    """Atomic write: write to .tmp then rename."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = STATE_FILE.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp_path.rename(STATE_FILE)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new session state file."""
    plan = json.loads(args.plan) if args.plan else {}

    # Build pending steps from plan routing
    pending = []
    output_format = plan.get("output_format", "word")
    format_map = {
        "word": "tao-word",
        "excel": "tao-excel",
        "slides": "tao-slide",
        "pdf": "tao-pdf",
        "html": "tao-html",
    }
    pending = ["thu-thap", "bien-soan", format_map.get(output_format, "tao-word")]
    if plan.get("needs_charts"):
        pending.append("tao-hinh")

    state = {
        "session_id": str(uuid.uuid4()),
        "version": args.version or VERSION,
        "created_at": _now(),
        "updated_at": _now(),
        "status": "in_progress",
        "request": args.request,
        "plan": plan,
        "completed_steps": [],
        "pending_steps": pending,
        "output_files": [],
    }
    _save(state)
    print(f"✅ State initialized: {STATE_FILE} (session: {state['session_id'][:8]})")


def cmd_update(args: argparse.Namespace) -> None:
    """Mark a step as completed and move it from pending to completed."""
    state = _load()

    step_record = {
        "step": args.step,
        "completed_at": _now(),
        "output_file": args.output_file or "",
        "notes": args.notes or "",
    }
    state["completed_steps"].append(step_record)

    # Remove from pending
    state["pending_steps"] = [s for s in state["pending_steps"] if s != args.step]

    # Track output file
    if args.output_file:
        state["output_files"].append(args.output_file)

    state["updated_at"] = _now()
    _save(state)
    print(
        f"✅ Step '{args.step}' saved"
        + (f" → {args.output_file}" if args.output_file else "")
        + f"  (pending: {state['pending_steps'] or 'none'})"
    )


def cmd_complete(args: argparse.Namespace) -> None:
    """Mark the pipeline as successfully completed."""
    state = _load()
    state["status"] = "completed"
    state["completed_at"] = _now()
    state["updated_at"] = _now()
    state["pending_steps"] = []
    _save(state)
    print(f"✅ Pipeline marked complete — {STATE_FILE}")


def cmd_read(args: argparse.Namespace) -> None:
    """Print current state summary."""
    state = _load()
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_archive(args: argparse.Namespace) -> None:
    """Archive current state file with timestamp suffix."""
    if not STATE_FILE.exists():
        print("No state file to archive.", file=sys.stderr)
        sys.exit(0)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    archive_path = STATE_FILE.with_name(f".session-state.{ts}.json")
    STATE_FILE.rename(archive_path)
    print(f"✅ Archived: {archive_path}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="save_state.py",
        description="InsightEngine session state manager (atomic JSON writes)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Start a new pipeline session")
    p_init.add_argument("--request", required=True, help="Original user request string")
    p_init.add_argument("--plan", default="{}", help="JSON plan object (as string)")
    p_init.add_argument("--version", default=VERSION, help="InsightEngine version")

    # update
    p_update = sub.add_parser("update", help="Record a completed sub-skill step")
    p_update.add_argument("--step", required=True, help="Step name (e.g. thu-thap)")
    p_update.add_argument("--output-file", default="", help="Path to output file produced")
    p_update.add_argument("--notes", default="", help="Optional notes")

    # complete
    sub.add_parser("complete", help="Mark pipeline as completed")

    # read
    sub.add_parser("read", help="Print current state as JSON")

    # archive
    sub.add_parser("archive", help="Archive current state file with timestamp")

    args = parser.parse_args()
    dispatch = {
        "init": cmd_init,
        "update": cmd_update,
        "complete": cmd_complete,
        "read": cmd_read,
        "archive": cmd_archive,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
