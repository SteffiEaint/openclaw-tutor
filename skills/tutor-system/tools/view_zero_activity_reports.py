#!/usr/bin/env python3
"""View persisted zero-activity reports without rerunning the workflow."""
from _common import run
import sys

run("zero_activity_reports", *sys.argv[1:])
