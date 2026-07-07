#!/usr/bin/env python3
"""Extend the honest build to the full existing 19-module base (tail: GammaAggregation..A1ProperWrapper)
into the SAME cached olean tree tmp/claude_lean_o_base_v1, then run #print axioms on the key theorems.
green = rc 0 AND no 'error:'. Writes tmp/claude_lean_base_tail_summary.json."""
import importlib.util, json, time
from pathlib import Path

spec = importlib.util.spec_from_file_location("bh", "problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py")
bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()

tail = ["GammaAggregation", "CSPResolution", "FCBridge", "Seed3Door", "A1MaskSymmetry", "A1ProperWrapper"]
mods = [src_root / "Erdos23Delta0" / (m + ".lean") for m in tail]

results = []
t0 = time.time()
for p in mods:
    r = bh.run_lean(formal_root, src_root, build_root, p)
    ok = (r["returncode"] == 0) and ("error:" not in r["stderr"].lower())
    results.append({"module": r["module"], "rc": r["returncode"], "sec": r["seconds"], "ok": ok,
                    "err_tail": ("" if ok else r["stderr"][-1500:])})
    print(f"{'OK  ' if ok else 'FAIL'} {r['module']} rc={r['returncode']} {r['seconds']}s", flush=True)
    if not ok:
        print("STOP at first failure", flush=True); break

# axiom probes on key theorems (only if the tail built, since FCBridge is needed)
probes = {}
if all(x["ok"] for x in results):
    probe_targets = {
        "fcForm_official_bridge": "Erdos23Delta0.CertGraph.erdos23_fcForm_of_bipartization",
        "erdos23_delta0_conditional": "Erdos23Delta0.CertGraph.erdos23_delta0",
        "gammaUpper_chargeV2": "Erdos23Delta0.GammaAggregation.gammaUpper_from_chargeCertV2",
    }
    for label, thm in probe_targets.items():
        pf = src_root / "Erdos23Delta0" / f"_claude_probe_{label}.lean"
        # import the module that hosts the theorem: CertGraph theorems live in FCBridge/CertGraph; import both roots
        pf.write_text("import Erdos23Delta0.FCBridge\nimport Erdos23Delta0.GammaAggregation\n\n#print axioms " + thm + "\n")
        r = bh.run_lean(formal_root, src_root, build_root, pf)
        line = ""
        for L in (r["stdout"] or "").splitlines():
            if "depends on axioms" in L or "does not depend on any axioms" in L:
                line = L.strip()
        probes[label] = {"thm": thm, "rc": r["returncode"], "axioms_line": line,
                         "stderr_tail": r["stderr"][-400:] if r["returncode"] != 0 else ""}
        print(f"AXIOMS {label}: rc={r['returncode']} {line}", flush=True)

summary = {"build_root": str(build_root), "total_sec": round(time.time() - t0, 1),
           "tail_all_ok": all(x["ok"] for x in results) and len(results) == len(mods),
           "results": results, "axiom_probes": probes}
Path("tmp/claude_lean_base_tail_summary.json").write_text(json.dumps(summary, indent=1))
print(f"SUMMARY tail_all_ok={summary['tail_all_ok']} -> tmp/claude_lean_base_tail_summary.json", flush=True)
