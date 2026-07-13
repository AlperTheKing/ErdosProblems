#!/usr/bin/env python3
"""Dependency-resolving rebuild of the trade-era modules into my base cache (iterative: on 'object file X does
not exist', build X first). Then the axiom probe. Honest-build discipline."""
import json
import os
import re
import subprocess
import time
from pathlib import Path

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
env = os.environ.copy()
env["LEAN_PATH"] = str(build_root) + os.pathsep + env.get("LEAN_PATH", "")

MISS = re.compile(r"object file '.*?[\\/]Erdos23Delta0[\\/](.+?)\.olean' of module")


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


def build_with_deps(rel, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if rel in seen:
        return False
    seen.add(rel)
    for _ in range(15):
        ok, rc, sec, out = run_lean(rel)
        if ok:
            print(f"OK   {rel} rc={rc} {sec}s (depth {depth})", flush=True)
            return True
        m = MISS.search(out)
        if not m:
            print(f"FAIL {rel} rc={rc} {sec}s (non-dep error)", flush=True)
            Path(f"tmp/claude_gate2_{Path(rel).name}_err.txt").write_text(out, encoding="utf-8")
            return False
        dep = m.group(1).replace("\\", "/")
        print(f"  ... {rel} needs {dep}; building dep first", flush=True)
        if not build_with_deps(dep, depth + 1, seen):
            return False
    return False


results = {}
for m in ["Gamma/CheckedCollisionDefectTrade", "Gamma/CheckedCollisionLexTrade"]:
    results[m] = build_with_deps(m)

probe = src_root / "Erdos23Delta0/_claude_probe_trade_modules.lean"
probe.write_text(
    "import Erdos23Delta0.Gamma.SelectedRowEndpointAnchoring\n"
    "import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade\n"
    "import Erdos23Delta0.Gamma.CheckedCollisionLexTrade\n\n"
    "#print axioms Erdos23Delta0.Gamma.SelectedRowEndpointAnchoring.selectedRow_verts_injective\n",
    encoding="utf-8")
ok, rc, sec, out = run_lean("_claude_probe_trade_modules")
print(("OK  " if ok else "FAIL") + f" probe rc={rc} {sec}s", flush=True)
for line in out.splitlines():
    if "depends on axioms" in line or "sorryAx" in line:
        print(line, flush=True)
if not ok:
    Path("tmp/claude_gate2_probe_err.txt").write_text(out, encoding="utf-8")
Path("tmp/claude_gate_trade_modules2_summary.json").write_text(json.dumps(results, indent=1))
