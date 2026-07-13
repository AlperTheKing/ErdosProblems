#!/usr/bin/env python3
"""Loader-corrected entry point for the exact R57 interface replay."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GATE_SOURCE = HERE / "inputs" / "r57_positive_defect_extension_gate" / "check_gate.py"
REPLAY_SOURCE = HERE / "r57_positive_defect_interface_countermodel.py"

# Python 3.12 dataclasses resolve string annotations through sys.modules.
# Register the exact gate module before the replay's second, local load.
spec = importlib.util.spec_from_file_location("r57_gate", GATE_SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load R57 exact gate")
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

runpy.run_path(str(REPLAY_SOURCE), run_name="__main__")
