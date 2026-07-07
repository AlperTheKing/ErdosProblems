#!/usr/bin/env python3
"""End-to-end HiGHS-free feasibility-basis cert pipeline for one broad row.
  extract (Clarabel-support + rank-aware QR basis) -> parallel modular solve -> convert -> source check.
Usage: python claude_febasis_pipeline.py <chart> <dom> [band] [support] [tau]
Emits FEBASIS_RESULT {json} with exact_ok / neg_residuals / neg_coeffs.
"""
import sys, json, subprocess
from pathlib import Path

chart = sys.argv[1]; dom = sys.argv[2]
band = sys.argv[3] if len(sys.argv) > 3 else "near_2s_minus_1"
support = sys.argv[4] if len(sys.argv) > 4 else "negative"
tau = sys.argv[5] if len(sys.argv) > 5 else "1e-4"
tag = f"k{chart}_d{dom}_febc"
core = f"tmp/eq_odl1_rung2_core_{tag}.jsonl"
sol = f"tmp/eq_odl1_rung2_sol_{tag}.jsonl"
modsum = f"tmp/eq_odl1_rung2_modsum_{tag}.json"
srcsol = f"tmp/eq_odl1_rung2_srcsol_{tag}.jsonl"
chk = f"tmp/eq_odl1_rung2_check_{tag}.json"


def run(cmd):
    print("RUN", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd]).returncode

# 1) extract rank-aware basis core
run([sys.executable, "-B", "tmp/claude_febasis_clarabel.py", chart, dom, band, support, core, tau])
if not Path(core).exists():
    print("FEBASIS_RESULT " + json.dumps({"row": f"{chart}/{dom}", "stage": "extract", "ok": False})); sys.exit(1)
# check square from the core meta (dim) — modular solve needs a square system
# 2) parallel exact modular solve
rc = run([sys.executable, "-B", "tmp/claude_modular_solve_parallel.py", "--core", core,
          "--prime-count", "384", "--workers", "48", "--store-solution", sol, "--summary", modsum])
if not Path(sol).exists():
    print("FEBASIS_RESULT " + json.dumps({"row": f"{chart}/{dom}", "stage": "modular", "ok": False})); sys.exit(2)
# 3) convert col -> source_col
run([sys.executable, "-B", "tmp/claude_core_to_source.py", core, sol, srcsol])
# 4) official exact source check
run([sys.executable, "-B", "problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py",
     "--chart", chart, "--dominant", dom, "--band", band, "--support", support,
     "--solution", srcsol, "--summary", chk])
res = {}
if Path(chk).exists():
    res = json.load(open(chk))
print("FEBASIS_RESULT " + json.dumps({
    "row": f"{chart}/{dom}", "exact_ok": res.get("exact_ok"),
    "neg_residuals": res.get("full_negative_residual_count"),
    "neg_coeffs": res.get("solution_negative_count"),
    "nonzero_cols": res.get("nonzero_source_columns"), "check": chk, "core": core}))
