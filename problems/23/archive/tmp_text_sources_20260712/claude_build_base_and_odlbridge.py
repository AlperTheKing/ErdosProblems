#!/usr/bin/env python3
"""Honest dep-order build of the Erdos23Delta0 base chain (00-12 through ODLFull) + BranchB/ODLBridge
(module 27). Reuses the green harness run_lean (lake env lean --root ... --o ... with LEAN_PATH=build_root,
cwd=formal-conjectures). green = returncode 0 AND no 'error:' in stderr. Stops at first failure.
Writes tmp/claude_lean_base_build_summary.json. No native_decide/sorry tolerated (source is greped separately).
"""
import sys, json, time, importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("bh", "problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py")
bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
build_root.mkdir(parents=True, exist_ok=True)

# dependency order (roadmap section 0, through ODLFull) + ODLBridge (module 27; deps only ODLFull)
order = ["Skeleton","Darts","Distances","Gamma","Row","BankL","BranchAInterface","PacketExchange",
         "CDCore","PolyCert","Bank0Algebra","CertGraph","ODLFull"]
mods = [src_root/"Erdos23Delta0"/(m+".lean") for m in order]
mods.append(src_root/"Erdos23Delta0"/"BranchB"/"ODLBridge.lean")

results = []
t_all = time.time()
for p in mods:
    if not p.exists():
        results.append({"module": str(p), "rc": -1, "ok": False, "err_tail": "SOURCE MISSING"})
        print(f"FAIL missing {p}", flush=True); break
    r = bh.run_lean(formal_root, src_root, build_root, p)
    lowered = r["stderr"].lower()
    ok = (r["returncode"] == 0) and ("error:" not in lowered)
    results.append({"module": r["module"], "rc": r["returncode"], "sec": r["seconds"], "ok": ok,
                    "err_tail": ("" if ok else r["stderr"][-1200:])})
    print(f"{'OK  ' if ok else 'FAIL'} {r['module']} rc={r['returncode']} {r['seconds']}s", flush=True)
    if not ok:
        print("STOP at first failure", flush=True); break

summary = {"build_root": str(build_root), "total_sec": round(time.time()-t_all, 1),
           "all_ok": all(x["ok"] for x in results) and len(results) == len(mods),
           "green_count": sum(1 for x in results if x["ok"]), "total": len(mods), "results": results}
Path("tmp/claude_lean_base_build_summary.json").write_text(json.dumps(summary, indent=1))
print(f"SUMMARY all_ok={summary['all_ok']} green={summary['green_count']}/{summary['total']} -> tmp/claude_lean_base_build_summary.json", flush=True)
