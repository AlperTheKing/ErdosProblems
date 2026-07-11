#!/usr/bin/env python3
"""Dep-resolving independent rebuild of the selection-era Codex modules into my base cache + axiom probes.
Honest-build discipline: rc=0 AND no 'error:' AND no sorryAx; probe #print axioms on key decls."""
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
    for _ in range(20):
        ok, rc, sec, out = run_lean(rel)
        if ok:
            print(f"OK   {rel} rc={rc} {sec}s (depth {depth})", flush=True)
            return True
        m = MISS.search(out)
        if not m:
            print(f"FAIL {rel} rc={rc} {sec}s (non-dep error)", flush=True)
            Path(f"tmp/claude_gate_sel_{Path(rel).name}_err.txt").write_text(out, encoding="utf-8")
            return False
        dep = m.group(1).replace("\\", "/")
        print(f"  ... {rel} needs {dep}; building dep first", flush=True)
        if not build_with_deps(dep, depth + 1, seen):
            return False
    return False


mods = ["Gamma/LiveMiddleSwapCrossOuter"]
results = {}
for m in mods:
    results[m] = build_with_deps(m)

print("DONE", flush=True)

