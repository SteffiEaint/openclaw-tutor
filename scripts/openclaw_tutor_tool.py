#!/usr/bin/env python3
from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent.parent / "skills" / "tutor-system" / "scripts" / "tutor_tool.py"
runpy.run_path(str(TARGET), run_name="__main__")
