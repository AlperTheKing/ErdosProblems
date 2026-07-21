#!/usr/bin/env python3
"""
band10 wave-2 RECORD VERIFICATION (exact).

 (a) the c = 4 (h*_1 = 0) record found by the geometric-ladder census, verified
     by hive4.py (full Ehrhart) and by LR engines A and B on the stretched
     counts n = 1,2,3;
 (b) the max-normalized-volume record from the K = 1e9 structural census,
     verified by hive4.py (exact vertices + exact triangulated volume).  Its
     lattice-point count is NOT computed -- direct enumeration is infeasible at
     that size, and no float substitute is acceptable.
 (c) an unbounded-weight family exhibiting the c = 4 record at arbitrary weight.
"""
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", ".."))
ENG = os.path.abspath(os.path.join(R4, "..", "engine"))
sys.path.insert(0, R4)
import hive4  # noqa: E402

LRA = os.path.join(ENG, "lr_hive.exe")
LRB = os.path.join(ENG, "engineB_lrrule.py")


def triple_from_gaps(g):
    a, b, c = g[0:3], g[3:6], g[6:9]
    Aw = 3 * a[2] + 2 * a[1] + a[0]
    Bw = 3 * b[2] + 2 * b[1] + b[0]
    Cw = 3 * c[2] + 2 * c[1] + c[0]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = -k if k < 0 else 0
    lam = [l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4]
    mu = [b[2] + b[1] + b[0], b[2] + b[1], b[2], 0]
    nu = [n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4]
    assert sum(lam) + sum(mu) == sum(nu)
    return lam, mu, nu


def lr(exe_python, lam, mu, nu, n, cap="1000000000"):
    sl = ",".join(str(n * x) for x in lam)
    sm = ",".join(str(n * x) for x in mu)
    sn = ",".join(str(n * x) for x in nu)
    if exe_python == "A":
        p = subprocess.run([LRA, sl, sm, sn, cap], capture_output=True, text=True)
    else:
        p = subprocess.run([sys.executable, LRB, sl, sm, sn, cap],
                           capture_output=True, text=True)
    return p.stdout.strip().split()[-1] if p.stdout.strip() else "ERR"


out = {}

# ------------------------------------------------------------------ (a)
g_c4 = [32, 316, 10, 10, 100, 10, 3, 316, 1]
lam, mu, nu = triple_from_gaps(g_c4)
r = hive4.analyze(lam, mu, nu)
out["c4_record"] = {
    "gaps": g_c4, "lam": lam, "mu": mu, "nu": nu, "weight": sum(nu),
    "dim": r["dim"], "c": r["c"], "V": str(r["volume_normalized"]),
    "hstar": r["hstar"], "L": r["L"],
    "poly": [str(x) for x in r["poly"]],
    "a1": str(r["poly"][1]), "neg": r["neg"],
    "interp_verified_at_n4_n5": r["verified"],
    "engineA": [lr("A", lam, mu, nu, n) for n in (1, 2, 3)],
    "engineB": [lr("B", lam, mu, nu, n) for n in (1, 2, 3)],
}

# ------------------------------------------------------------------ (b)
g_bigV = [856499689, 477922233, 491912248,
          618707896, 484217855, 943146889,
          975959810, 990929336, 936756106]
lam2, mu2, nu2 = triple_from_gaps(g_bigV)
H = hive4.build_hive4(lam2, mu2, nu2)
Vt = hive4.vertices(H["A"], H["b"])
vol = hive4.normalized_volume(H["A"], H["b"], Vt)
out["maxV_record"] = {
    "gaps": g_bigV, "lam": lam2, "mu": mu2, "nu": nu2, "weight": sum(nu2),
    "n_vertices": len(Vt),
    "dim": hive4._affine_rank(Vt),
    "max_vertex_denominator": max(hive4.denominators(Vt)),
    "V_normalized_exact": str(vol),
    "V_agrees_with_scanner": str(vol) == "103813825188771821384673875",
    "note": ("lattice-point count not enumerated at this size; only the exact "
             "vertex set and exact triangulated volume are certified here"),
}

# ------------------------------------------------------------------ (c)
fam = []
for t in (0, 10 ** 3, 10 ** 6, 10 ** 9, 10 ** 12):
    lamt = [x + t for x in lam]
    nut = [x + t for x in nu]
    rt = hive4.analyze(lamt, mu, nut)
    fam.append({"t": t, "weight": sum(nut), "c": rt["c"],
                "V": str(rt["volume_normalized"]), "hstar": rt["hstar"],
                "poly": [str(x) for x in rt["poly"]], "neg": rt["neg"]})
out["unbounded_weight_family"] = {
    "family": "lam + t*1^4, mu fixed, nu + t*1^4 (weight-preserving translation)",
    "rows": fam,
}

with open(os.path.join(HERE, "b10w2_records.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
