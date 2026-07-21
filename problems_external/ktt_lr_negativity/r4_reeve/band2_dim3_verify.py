#!/usr/bin/env python3
"""
band2_dim3_verify.py -- EXHAUSTIVE independent verification of the entire
negativity-capable stratum of band 2.

deg P = dim Q, and an Ehrhart polynomial of a polytope of dimension <= 2 has no
negative coefficient; so in the r=4 cell only dim-3 triples can ever produce a
KTT counterexample.  This script takes EVERY dim-3 triple found in the
exhaustive band W = |nu| in [15,20] pass and recomputes the stretched LR numbers
c(n*nu; n*lam, n*mu) for n = 1,2,3 with BOTH external exact engines
(A = lr_hive.exe, B = engineB_lrrule.py, batch mode), comparing to the polytope
engine's P(n).  Any disagreement is a hard failure.

Also aggregates the dim-3 statistics: h*_2 histogram, min a_1, max V, max V at
h*_1 = 0, and every negative-coefficient triple.
"""

import glob
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402

ENG = os.path.join(os.path.dirname(HERE), "engine")
EXE_A = os.path.join(ENG, "lr_hive.exe")
EXE_B = os.path.join(ENG, "engineB_lrrule.py")
D = os.path.join(HERE, "runs", "band2")
CAP = 10 ** 9


def pstr(p):
    p = [x for x in p if x > 0]
    return ",".join(str(x) for x in p) if p else "0"


def main(nmax=3):
    recs = []
    for fp in sorted(glob.glob(os.path.join(D, "dim3_*.jsonl"))):
        with open(fp) as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
    print("dim-3 triples in band:", len(recs))

    fails = []
    for n in range(1, nmax + 1):
        bf = os.path.join(D, "_verify_n%d.batch" % n)
        with open(bf, "w") as f:
            for r in recs:
                f.write("%s;%s;%s;%d\n" % (pstr([x * n for x in r["lam"]]),
                                           pstr([x * n for x in r["mu"]]),
                                           pstr([x * n for x in r["nu"]]), CAP))
        outA = subprocess.run([EXE_A, "--batch", bf], capture_output=True,
                              text=True).stdout.split()
        outB = subprocess.run([sys.executable, EXE_B, "--batch", bf],
                              capture_output=True, text=True).stdout.split()
        assert len(outA) == len(recs), (len(outA), len(recs))
        assert len(outB) == len(recs), (len(outB), len(recs))
        for r, a, b in zip(recs, outA, outB):
            Pn = hive4.polyval([Fraction(c) for c in r["poly"]], n)
            if not (a == b == str(Pn)):
                fails.append({"lam": r["lam"], "mu": r["mu"], "nu": r["nu"],
                              "n": n, "P": str(Pn), "A": a, "B": b})
        print("n=%d: %d comparisons, %d failures so far" % (n, len(recs), len(fails)),
              flush=True)

    # dim-3 aggregate statistics
    h2hist = {}
    Vhist = {}
    negs = [r for r in recs if r["neg"]]
    min_a1 = None
    maxV = None
    maxVz = None
    audit_bad = [r for r in recs if not (r["verified"] and r["vol_ok"] and r["deg_ok"])]
    hstar_neg = [r for r in recs if r["hstar_neg"]]
    nonlat = [r for r in recs if r["max_den"] > 1]
    for r in recs:
        h2 = r["hstar"][2]
        h2hist[h2] = h2hist.get(h2, 0) + 1
        V = int(r["V"])
        Vhist[V] = Vhist.get(V, 0) + 1
        a1 = Fraction(r["a1"])
        if min_a1 is None or a1 < min_a1[0]:
            min_a1 = (a1, r)
        if maxV is None or V > int(maxV["V"]):
            maxV = r
        if r["hstar"][1] == 0 and (maxVz is None or V > int(maxVz["V"])):
            maxVz = r
    out = {
        "band": "W = |nu| in [15,20]",
        "dim3_triples": len(recs),
        "stretch_levels_checked": list(range(1, nmax + 1)),
        "comparisons": len(recs) * nmax * 2,
        "engine_disagreements": len(fails),
        "disagreement_list": fails[:50],
        "internal_audit_failures": len(audit_bad),
        "hstar_negative_entries": len(hstar_neg),
        "non_lattice_polytopes": len(nonlat),
        "hstar2_histogram": {str(k): h2hist[k] for k in sorted(h2hist)},
        "volume_histogram": {str(k): Vhist[k] for k in sorted(Vhist)},
        "min_a1_dim3": [str(min_a1[0]), min_a1[1]] if min_a1 else None,
        "max_volume_dim3": maxV,
        "max_volume_hstar1_zero_dim3": maxVz,
        "negatives": negs,
        "n_negatives": len(negs),
        "note": ("a_1 < 0 for a 3-dim lattice polytope requires "
                 "h*_2 >= 13 + 2 h*_1 + 2 h*_3 (from 6 a_1 = 11 + 2h*_1 - h*_2 + 2h*_3), "
                 "hence h*_2 >= 13 and normalized volume >= 14."),
    }
    with open(os.path.join(D, "dim3_verify.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("negatives", "disagreement_list")}, indent=1))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
