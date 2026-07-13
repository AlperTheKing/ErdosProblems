#!/usr/bin/env python3
"""Honest build of the Route-B assembly increment (RouteBAssembly.lean) against the cached base oleans in
tmp/claude_lean_o_base_v1. Reuses the green harness run_lean. green = returncode 0 AND no 'error:' in stderr.
Builds the dep tail (GammaAggregation, GammaChargeGraft) then RouteBAssembly, to be safe. Stops at first failure.
"""
import json, time, importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("bh", "problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py")
bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()
build_root.mkdir(parents=True, exist_ok=True)

mods = [src_root / "Erdos23Delta0" / (m + ".lean")
        for m in ["GammaAggregation", "GammaChargeGraft", "RouteBAssembly"]]

results = []
t_all = time.time()
for p in mods:
    if not p.exists():
        results.append({"module": str(p), "ok": False, "err_tail": "SOURCE MISSING"}); print(f"FAIL missing {p}", flush=True); break
    r = bh.run_lean(formal_root, src_root, build_root, p)
    ok = (r["returncode"] == 0) and ("error:" not in r["stderr"].lower())
    results.append({"module": r["module"], "rc": r["returncode"], "sec": r["seconds"], "ok": ok,
                    "err_tail": ("" if ok else r["stderr"][-2000:])})
    print(f"{'OK  ' if ok else 'FAIL'} {r['module']} rc={r['returncode']} {r['seconds']}s", flush=True)
    if not ok:
        print("STOP at first failure", flush=True); print(r["stderr"][-2000:], flush=True); break

summary = {"all_ok": all(x["ok"] for x in results) and len(results) == len(mods),
           "green": sum(1 for x in results if x["ok"]), "total": len(mods), "results": results}
Path("tmp/claude_build_routeb_summary.json").write_text(json.dumps(summary, indent=1))
print(f"SUMMARY all_ok={summary['all_ok']} green={summary['green']}/{summary['total']}", flush=True)
