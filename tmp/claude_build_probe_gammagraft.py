#!/usr/bin/env python3
"""Build GammaChargeGraft against cached base oleans + axiom-probe gammaBetaProvider_of_chargeCert."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("bh", "problems/23/writeup/_codex_eq_odl1_rung2_lean_build.py")
bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)

root = Path(".").resolve()
formal_root = (root / "formal-conjectures").resolve()
src_root = (root / "problems/23/lean").resolve()
build_root = (root / "tmp/claude_lean_o_base_v1").resolve()

mod = src_root / "Erdos23Delta0" / "GammaChargeGraft.lean"
r = bh.run_lean(formal_root, src_root, build_root, mod)
low = r["stderr"].lower()
ok = (r["returncode"] == 0) and ("error:" not in low)
print(f"BUILD {'OK' if ok else 'FAIL'} rc={r['returncode']} {r['seconds']}s")
if not ok:
    print("STDERR:\n" + r["stderr"][-2500:])
else:
    probe = src_root / "Erdos23Delta0" / "_claude_probe_gammagraft.lean"
    probe.write_text("import Erdos23Delta0.GammaChargeGraft\n\n#print axioms Erdos23Delta0.GammaChargeGraft.gammaBetaProvider_of_chargeCert\n")
    rp = bh.run_lean(formal_root, src_root, build_root, probe)
    line = ""
    for L in (rp["stdout"] or "").splitlines():
        if "depends on axioms" in L or "does not depend on any axioms" in L:
            line = L.strip()
    print(f"AXIOMS rc={rp['returncode']}: {line}")
    if rp["returncode"] != 0:
        print("PROBE STDERR:\n" + rp["stderr"][-1500:])
