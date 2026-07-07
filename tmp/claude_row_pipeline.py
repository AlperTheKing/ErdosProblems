#!/usr/bin/env python3
# Claude's source-basis chart-row pipeline: sparse_row_core -> modular_core_solve -> source_solution_check.
# Runs the same validated route Codex uses; emits claude-tagged artifacts for the ledger + my exact gate.
# Usage: python claude_row_pipeline.py <chart> <dominant>
import sys, subprocess, json, pathlib

chart = int(sys.argv[1]); dom = int(sys.argv[2])
band = "near_2s_minus_1"; support = "negative"
W = "problems/23/writeup"
tag = f"k{chart}_d{dom}_claude"
core = f"tmp/eq_odl1_rung2_core_{tag}.jsonl"
core_sum = f"tmp/eq_odl1_rung2_core_{tag}_summary.json"
sol = f"tmp/eq_odl1_rung2_source_solution_{tag}.jsonl"
mod_sum = f"tmp/eq_odl1_rung2_modular_{tag}.json"
chk = f"tmp/eq_odl1_rung2_source_solution_check_{tag}.json"

def run(cmd):
    print("RUN:", " ".join(cmd), flush=True)
    r = subprocess.run(cmd)
    return r.returncode

# 1) sparse row core (family objective, dynamic-markowitz selector — Codex's accepted method)
rc = run([sys.executable, "-B", f"{W}/_codex_eq_odl1_rung2_sparse_row_core.py",
          "--chart", str(chart), "--dominant", str(dom), "--band", band, "--support", support,
          "--objective", "family", "--selector", "dynamic-markowitz", "--time-limit", "400",
          "--export-core", core, "--summary", core_sum])
if rc != 0 or not pathlib.Path(core).exists():
    print(json.dumps({"row": tag, "stage": "core", "ok": False})); sys.exit(1)

# 2) modular exact solve (384-prime CRT)
rc = run([sys.executable, "-B", f"{W}/_codex_eq_odl1_rung2_modular_core_solve.py",
          "--core", core, "--prime-count", "384", "--store-solution", sol, "--summary", mod_sum])
if rc != 0 or not pathlib.Path(sol).exists():
    print(json.dumps({"row": tag, "stage": "modular", "ok": False})); sys.exit(2)

# 3) official exact source check
rc = run([sys.executable, "-B", f"{W}/_codex_eq_odl1_rung2_source_solution_check.py",
          "--chart", str(chart), "--dominant", str(dom), "--band", band, "--support", support,
          "--solution", sol, "--summary", chk])
res = {}
if pathlib.Path(chk).exists():
    res = json.load(open(chk))
print("CLAUDE_ROW_RESULT " + json.dumps({
    "row": tag, "chart": chart, "dominant": dom,
    "exact_ok": res.get("exact_ok"), "neg_residuals": res.get("full_negative_residual_count"),
    "neg_coeffs": res.get("solution_negative_count"), "nonzero_cols": res.get("nonzero_source_columns"),
    "check": chk, "solution": sol}))
