#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ADAPTER = ROOT / "skills" / "tutor-system" / "scripts" / "tutor_tool.py"

def run(command, *args):
    result = subprocess.run(
        [sys.executable, str(ADAPTER), command, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
