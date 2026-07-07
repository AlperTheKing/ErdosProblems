#!/usr/bin/env python3
"""Exact-solve an existing feasibility-basis core -> convert -> official source check.
Usage: python claude_exact_from_core.py <core.jsonl> <chart> <dom> <band> <support> <tag>
"""
import sys, json, subprocess
from pathlib import Path
core, chart, dom, band, support, tag = sys.argv[1:7]
sol = f"tmp/eq_odl1_rung2_sol_{tag}.jsonl"
modsum = f"tmp/eq_odl1_rung2_modsum_{tag}.json"
srcsol = f"tmp/eq_odl1_rung2_srcsol_{tag}.jsonl"
chk = f"tmp/eq_odl1_rung2_check_{tag}.json"

def run(cmd):
    print("RUN", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd]).returncode

run([sys.executable, "-B", "tmp/claude_modular_solve_parallel.py", "--core", core,
     "--prime-count", "512", "--workers", "48", "--store-solution", sol, "--summary", modsum])
if not Path(sol).exists():
    print("EXACT_RESULT " + json.dumps({"tag": tag, "stage": "modular", "ok": False})); sys.exit(1)
run([sys.executable, "-B", "tmp/claude_core_to_source.py", core, sol, srcsol])
run([sys.executable, "-B", "problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py",
     "--chart", chart, "--dominant", dom, "--band", band, "--support", support,
     "--solution", srcsol, "--summary", chk])
res = json.load(open(chk)) if Path(chk).exists() else {}
print("EXACT_RESULT " + json.dumps({"tag": tag, "exact_ok": res.get("exact_ok"),
      "neg_res": res.get("full_negative_residual_count"), "neg_coeff": res.get("solution_negative_count"),
      "nz": res.get("nonzero_source_columns"), "check": chk}))
