#!/usr/bin/env python3
"""Honest re-build of ALL new Codex gap#1 modules under Claude's harness (independent verification gate)."""
import json
from pathlib import Path
import os, subprocess, time

MODULES = [
    "Ell5GapLemmas", "Ell5DistancePrune", "BankedCutDominationExtras",
    "Ell5UnionCount", "Ell5GeodesicUnion", "Ell5FootprintCount",
    "Ell5HallSmall", "RCCPayloadFixtures", "RelaxedCoverBanked",
]
root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
env = os.environ.copy(); env["LEAN_PATH"] = str(build_root) + os.pathsep + env.get("LEAN_PATH", "")
results = {}
for mod in MODULES:
    p = src_root / "Erdos23Delta0" / f"{mod}.lean"
    if not p.exists():
        results[mod] = "MISSING"
        print(f"MISS {mod}", flush=True)
        continue
    out = build_root / "Erdos23Delta0" / f"{mod}.olean"
    cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(p)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(formal_root), env=env, capture_output=True, encoding="utf-8", errors="replace")
    sec = round(time.time() - t0, 1)
    allout = (proc.stdout or "") + "\n" + (proc.stderr or "")
    low = allout.lower()
    ok = (proc.returncode == 0) and ("error:" not in low) and ("sorryax" not in low)
    bad_axiom = any(("depends on axioms" in ln and not all(
        tok in "[propext, Classical.choice, Quot.sound]" or True for tok in [])) for ln in [])
    # collect axiom lines and check subset
    axlines = [ln for ln in allout.splitlines() if "depends on axioms" in ln]
    clean = all(("sorryAx" not in ln and "ofReduceBool" not in ln and "Lean.trustCompiler" not in ln) for ln in axlines)
    results[mod] = f"{'OK' if (ok and clean) else 'FAIL'} rc={proc.returncode} {sec}s axlines={len(axlines)}"
    print(f"{'OK  ' if (ok and clean) else 'FAIL'} {mod:28s} rc={proc.returncode} {sec}s probes={len(axlines)}", flush=True)
    if not (ok and clean):
        for ln in allout.splitlines():
            if "error" in ln.lower() or "sorryAx" in ln:
                print("   ", ln[:200], flush=True)
Path("tmp/claude_build_codex_modules_summary.json").write_text(json.dumps(results, indent=1))
print(json.dumps(results, indent=1))
