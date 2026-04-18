#!/usr/bin/env python3
"""InsightEngine Pipeline Smoke Test

Validates that the pipeline infrastructure is healthy:
  1. All dependencies installed
  2. All skill SKILL.md files present and valid
  3. All scripts executable
  4. Output/tmp/input directories exist
  5. Save/resume state works
  6. validate_urls.py works

Usage:
    python3 scripts/smoke_test.py           # Run all checks
    python3 scripts/smoke_test.py --quick   # Skip slow checks
    python3 scripts/smoke_test.py --json    # Output as JSON
"""

import argparse
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

# ---------- Config ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".github" / "skills"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

REQUIRED_SKILLS = [
    "tong-hop", "thu-thap", "bien-soan",
    "tao-word", "tao-excel", "tao-slide",
    "tao-pdf", "tao-html", "tao-hinh",
    "thiet-ke", "kiem-tra", "cai-tien",
    "cai-dat", "skill-creator", "skill-forge",
]

REQUIRED_SCRIPTS = [
    "check_deps.py",
    "recalc.py",
    "save_state.py",
    "validate_urls.py",
]

REQUIRED_DIRS = ["output", "tmp", "input", "scripts"]

REQUIRED_PYTHON_PACKAGES = [
    ("docx", "python-docx"),
    ("openpyxl", "openpyxl"),
    ("pandas", "pandas"),
    ("reportlab", "reportlab"),
    ("jinja2", "Jinja2"),
    ("matplotlib", "matplotlib"),
    ("PIL", "Pillow"),
]

# ---------- Test Functions ----------

def check_directories() -> list[dict]:
    """Check required directories exist."""
    results = []
    for d in REQUIRED_DIRS:
        path = PROJECT_ROOT / d
        results.append({
            "test": f"dir:{d}",
            "pass": path.is_dir(),
            "detail": str(path) if path.is_dir() else f"MISSING: {path}",
        })
    return results


def check_skills() -> list[dict]:
    """Check all required skills have SKILL.md."""
    results = []
    for skill in REQUIRED_SKILLS:
        skill_file = SKILLS_DIR / skill / "SKILL.md"
        exists = skill_file.is_file()
        size = skill_file.stat().st_size if exists else 0
        results.append({
            "test": f"skill:{skill}",
            "pass": exists and size > 100,
            "detail": f"{size} bytes" if exists else "MISSING",
        })
    return results


def check_scripts() -> list[dict]:
    """Check all required scripts exist."""
    results = []
    for script in REQUIRED_SCRIPTS:
        path = SCRIPTS_DIR / script
        results.append({
            "test": f"script:{script}",
            "pass": path.is_file(),
            "detail": str(path) if path.is_file() else "MISSING",
        })
    return results


def check_python_packages() -> list[dict]:
    """Check required Python packages are importable."""
    results = []
    for module_name, pip_name in REQUIRED_PYTHON_PACKAGES:
        try:
            importlib.import_module(module_name)
            results.append({
                "test": f"pkg:{pip_name}",
                "pass": True,
                "detail": "installed",
            })
        except ImportError:
            results.append({
                "test": f"pkg:{pip_name}",
                "pass": False,
                "detail": f"NOT INSTALLED — pip3 install {pip_name}",
            })
    return results


def check_node_available() -> list[dict]:
    """Check Node.js is available (needed for pptxgenjs)."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        version = result.stdout.strip()
        return [{"test": "runtime:node", "pass": True, "detail": version}]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return [{"test": "runtime:node", "pass": False, "detail": "NOT FOUND"}]


def check_save_state() -> list[dict]:
    """Check save_state.py check command works."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "save_state.py"), "check"],
            capture_output=True, text=True, timeout=10,
            cwd=str(PROJECT_ROOT),
        )
        return [{
            "test": "state:check",
            "pass": result.returncode == 0,
            "detail": result.stdout.strip()[:100] or "OK",
        }]
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return [{"test": "state:check", "pass": False, "detail": str(e)}]


def check_validate_urls() -> list[dict]:
    """Check validate_urls.py works with sample URLs."""
    try:
        result = subprocess.run(
            [
                sys.executable, str(SCRIPTS_DIR / "validate_urls.py"),
                "--urls",
                "https://itviec.com/it-jobs/senior-dev-12345",
                "https://google.com/search?q=test",
                "--json",
            ],
            capture_output=True, text=True, timeout=10,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            classifications = [r.get("classification") for r in data.get("results", [])]
            expected = classifications == ["DIRECT", "SEARCH"]
            return [{
                "test": "validate_urls:classify",
                "pass": expected,
                "detail": f"Got: {classifications}" if not expected else "DIRECT+SEARCH correctly classified",
            }]
        return [{"test": "validate_urls:classify", "pass": False, "detail": result.stderr.strip()[:100]}]
    except Exception as e:
        return [{"test": "validate_urls:classify", "pass": False, "detail": str(e)}]


def check_skill_line_counts() -> list[dict]:
    """Check SKILL.md line counts (warn if >400)."""
    results = []
    for skill in REQUIRED_SKILLS:
        skill_file = SKILLS_DIR / skill / "SKILL.md"
        if skill_file.is_file():
            lines = sum(1 for _ in open(skill_file))
            results.append({
                "test": f"lines:{skill}",
                "pass": lines <= 500,
                "detail": f"{lines} lines" + (" ⚠️ >400" if lines > 400 else ""),
            })
    return results


# ---------- Runner ----------

def run_all(quick: bool = False) -> list[dict]:
    """Run all smoke tests."""
    results = []
    results.extend(check_directories())
    results.extend(check_skills())
    results.extend(check_scripts())
    results.extend(check_python_packages())
    results.extend(check_node_available())
    results.extend(check_skill_line_counts())
    if not quick:
        results.extend(check_save_state())
        results.extend(check_validate_urls())
    return results


def main():
    parser = argparse.ArgumentParser(description="InsightEngine smoke test")
    parser.add_argument("--quick", action="store_true", help="Skip slow checks")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = run_all(quick=args.quick)
    passed = sum(1 for r in results if r["pass"])
    failed = sum(1 for r in results if not r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({"total": total, "passed": passed, "failed": failed, "results": results}, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  InsightEngine Smoke Test — {passed}/{total} passed")
        print(f"{'='*60}\n")
        for r in results:
            icon = "✅" if r["pass"] else "❌"
            print(f"  {icon} {r['test']:40s} {r['detail']}")
        print(f"\n{'='*60}")
        if failed > 0:
            print(f"  ❌ {failed} FAILED — fix issues above before running pipeline")
        else:
            print(f"  ✅ ALL PASSED — pipeline ready")
        print(f"{'='*60}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
