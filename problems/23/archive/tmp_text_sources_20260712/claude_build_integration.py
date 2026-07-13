#!/usr/bin/env python3
"""Integration build: all 7 session modules loaded together via _claude_integration_check.lean."""
import json
from pathlib import Path
import os, subprocess, time

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
out = build_root / "Erdos23Delta0" / "_claude_integration_check.olean"
env = os.environ.copy(); env["LEAN_PATH"] = str(build_root) + os.pathsep + env.get("LEAN_PATH", "")
p = src_root / "Erdos23Delta0" / "_claude_integration_check.lean"
cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(p)]
t0 = time.time()
proc = subprocess.run(cmd, cwd=str(formal_root), env=env, capture_output=True, encoding="utf-8", errors="replace")
sec = round(time.time() - t0, 1)
allout = (proc.stdout or "") + "\n" + (proc.stderr or "")
low = allout.lower()
ok = (proc.returncode == 0) and ("error:" not in low) and ("sorryax" not in low)
Path("tmp/claude_integration_err.txt").write_text("RC=%d sec=%s\n=OUT=\n%s" % (proc.returncode, sec, allout), encoding="utf-8")
print(f"{'OK  ' if ok else 'FAIL'} integration rc={proc.returncode} {sec}s (log tmp/claude_integration_err.txt)", flush=True)
for line in allout.splitlines():
    if "error" in line.lower() or "sorry" in line.lower():
        try: print(line)
        except Exception: pass
Path("tmp/claude_build_integration_summary.json").write_text(json.dumps({"ok": ok, "rc": proc.returncode, "sec": sec}, indent=1))
