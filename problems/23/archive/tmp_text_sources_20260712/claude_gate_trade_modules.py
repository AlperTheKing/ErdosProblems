#!/usr/bin/env python3
"""MY independent gate of the 3 Codex trade-era modules: rebuild each (rc=0, no error) into my base cache,
then compile a probe importing all three with #print axioms on the key theorems. Honest-build discipline."""
import json
import os
import subprocess
import time
from pathlib import Path

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
env = os.environ.copy()
env["LEAN_PATH"] = str(build_root) + os.pathsep + env.get("LEAN_PATH", "")

MODULES = [
    "Gamma/SelectedRowEndpointAnchoring",
    "Gamma/CheckedCollisionDefectTrade",
    "Gamma/CheckedCollisionLexTrade",
]

def run_lean(rel):
    out = build_root / ("Erdos23Delta0/" + rel + ".olean")
    out.parent.mkdir(parents=True, exist_ok=True)
    p = src_root / ("Erdos23Delta0/" + rel + ".lean")
    cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(p)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(formal_root), env=env, capture_output=True,
                          encoding="utf-8", errors="replace")
    allout = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == 0 and "error:" not in allout.lower() and "sorryax" not in allout.lower()
    return ok, proc.returncode, round(time.time() - t0, 1), allout

results = {}
for m in MODULES:
    ok, rc, sec, out = run_lean(m)
    results[m] = dict(ok=ok, rc=rc, sec=sec)
    print(("OK  " if ok else "FAIL") + f" {m} rc={rc} {sec}s", flush=True)
    if not ok:
        Path(f"tmp/claude_gate_{Path(m).name}_err.txt").write_text(out, encoding="utf-8")

# probe
probe = src_root / "Erdos23Delta0/_claude_probe_trade_modules.lean"
probe.write_text(
    "import Erdos23Delta0.Gamma.SelectedRowEndpointAnchoring\n"
    "import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade\n"
    "import Erdos23Delta0.Gamma.CheckedCollisionLexTrade\n\n"
    "open Erdos23Delta0.Gamma in\n"
    "#print axioms Erdos23Delta0.Gamma.SelectedRowEndpointAnchoring.selectedRow_verts_injective\n",
    encoding="utf-8")
ok, rc, sec, out = run_lean("_claude_probe_trade_modules")
print(("OK  " if ok else "FAIL") + f" probe rc={rc} {sec}s", flush=True)
for line in out.splitlines():
    if "depends on axioms" in line or "sorryAx" in line:
        print(line, flush=True)
if not ok:
    Path("tmp/claude_gate_trade_probe_err.txt").write_text(out, encoding="utf-8")
Path("tmp/claude_gate_trade_modules_summary.json").write_text(json.dumps(results, indent=1))
