#!/usr/bin/env python3
"""Use the current review command. Do not execute inherited artificial tests."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("review_v6.py")), run_name="__main__")
