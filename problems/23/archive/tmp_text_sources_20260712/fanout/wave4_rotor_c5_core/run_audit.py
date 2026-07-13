#!/usr/bin/env python3
"""Launcher for audit_extraction.py's dynamically loaded dataclass module."""

import runpy
import sys
import types
from pathlib import Path


sys.modules.setdefault("wave4_p5_gate", types.ModuleType("wave4_p5_gate"))
runpy.run_path(str(Path(__file__).with_name("audit_extraction.py")), run_name="__main__")
