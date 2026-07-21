#!/usr/bin/env python3
"""
Overflow / correctness cross-check of the slab regime.

The slab census evaluates gap vectors in which SEVEN gaps are astronomically
large while g[1] and g[7] stay <= 4.  All of it is int64 integer arithmetic, so
it must be shown that the intermediate quantities (n*rhs, fibre lengths, L(3))
do not wrap.  Here the identical eval path (gapscan4.exe --one, the same
eval_gaps used by band10w2.exe) is compared against the fully independent exact
rational engine hive4.py on slab-shaped gap vectors with the free gaps pushed as
high as hive4.py can still enumerate.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, R4)
import hive4  # noqa: E402

GAPSCAN = os.path.join(R4, "gapscan4.exe")


def triple_from_gaps(g):
    a, b, c = g[0:3], g[3:6], g[6:9]
    D = (3 * c[2] + 2 * c[1] + c[0]) - (3 * a[2] + 2 * a[1] + a[0]) - (3 * b[2] + 2 * b[1] + b[0])
    if D % 4:
        return None
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = -k if k < 0 else 0
    lam = [l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4]
    mu = [b[2] + b[1] + b[0], b[2] + b[1], b[2], 0]
    nu = [n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4]
    return lam, mu, nu


def main():
    rng = random.Random(556677)
    rows, fails = [], []
    free = [0, 2, 3, 4, 5, 6, 8]
    vals = [0, 1, 2, 5, 13, 60, 300, 1500, 6000, 25000]
    tried = 0
    while len(rows) < 60 and tried < 400000:
        tried += 1
        g = [0] * 9
        for i in free:
            g[i] = rng.choice(vals)
        g[1] = rng.randint(1, 4)
        g[7] = rng.randint(1, 4)
        t3 = None
        for fix in range(4):                    # nudge g[0] into 4 | D
            g[0] = g[0] + (1 if fix else 0)
            t3 = triple_from_gaps(g)
            if t3 is not None:
                break
        if t3 is None:
            continue
        r = hive4.analyze(*t3)
        if r["dim"] != 3:
            continue
        p = subprocess.run([GAPSCAN, "--one"] + [str(x) for x in g],
                           capture_output=True, text=True)
        kv = dict(tok.split("=") for tok in p.stdout.split())
        got = (int(kv["L1"]), int(kv["L2"]), int(kv["L3"]),
               int(kv["6a1"]), int(kv["V"]))
        P = list(r["poly"]) + [Fraction(0)] * (4 - len(r["poly"]))
        exp = (r["L"][1], r["L"][2], r["L"][3], int(6 * P[1]),
               int(r["volume_normalized"]))
        rows.append({"g": g, "weight": sum(t3[2]), "L1": exp[0], "V": exp[4],
                     "6a1": exp[3], "match": got == exp})
        if got != exp:
            fails.append({"g": g, "scanner": got, "hive4": exp})
    out = {"n_checked": len(rows), "n_fail": len(fails), "fails": fails,
           "max_weight_checked": max(r["weight"] for r in rows) if rows else 0,
           "max_L1_checked": max(r["L1"] for r in rows) if rows else 0,
           "max_V_checked": max(r["V"] for r in rows) if rows else 0,
           "min_6a1_checked": min(r["6a1"] for r in rows) if rows else None,
           "verdict": "PASS" if not fails else "FAIL"}
    with open(os.path.join(HERE, "b10w2_slabxcheck.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
