#!/usr/bin/env python3
"""Run #print axioms on branchB_to_coreODLGoal against the cached base oleans. Prints Lean stdout/stderr."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("bh", "problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py")
bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
probe = src_root / "Erdos23Delta0" / "_claude_axiom_probe_odlbridge.lean"

r = bh.run_lean(formal_root, src_root, build_root, probe)
print("RETURNCODE", r["returncode"])
print("=== STDOUT ===")
print(r["stdout"])
print("=== STDERR ===")
print(r["stderr"])
