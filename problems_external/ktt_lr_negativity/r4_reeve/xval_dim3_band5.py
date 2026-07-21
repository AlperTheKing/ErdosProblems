#!/usr/bin/env python3
"""
xval_dim3_band5.py -- targeted cross-validation on the ONLY stratum where a
negative Ehrhart coefficient is possible: dim Q = 3.

Draws random band triples, uses census_band5.exe --check to find the dim-3 ones,
then re-computes each with the reference engine hive4.py and demands exact
agreement on dim, L(0..5), V, h*, P.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from xval_band5 import parts_le4, contained  # noqa: E402


def main(want=600, seed=7770721, wlo=33, whi=38, pool=400000):
    rng = random.Random(seed)
    cache = {}

    def P(n):
        if n not in cache:
            cache[n] = parts_le4(n)
        return cache[n]

    def s(p):
        t = [x for x in p if x > 0]
        return ",".join(map(str, t)) if t else "0"

    samples = []
    tries = 0
    while len(samples) < pool and tries < 40 * pool:
        tries += 1
        W = rng.randint(wlo, whi)
        nu = rng.choice(P(W))
        a = rng.randint(0, W)
        lam = rng.choice(P(a))
        mu = rng.choice(P(W - a))
        if not (contained(lam, nu) and contained(mu, nu)):
            continue
        samples.append((lam, mu, nu))

    bf = os.path.join(HERE, "_xval_pool.txt")
    with open(bf, "w") as f:
        for lam, mu, nu in samples:
            f.write("%s;%s;%s\n" % (s(lam), s(mu), s(nu)))
    exe = os.path.join(HERE, "census_band5.exe")
    out = subprocess.run([exe, "--check", bf], capture_output=True, text=True, check=True).stdout
    lines = out.splitlines()
    d3 = [(t, l) for t, l in zip(samples, lines) if " dim=3 " in l]
    rng.shuffle(d3)
    d3 = d3[:want]

    bad = []
    for (lam, mu, nu), line in d3:
        fields = {}
        for tok in line.split("|", 1)[1].split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                fields[k] = v
        cL = [int(x) for x in fields["L"].split(",")]
        cV = int(fields["V"])
        cH = [int(x) for x in fields["hstar"].split(",")]
        c6a1 = int(fields["6a1"])
        c2a2 = int(fields["2a2"])
        cden = int(fields["den"])
        cnv = int(fields["nv"])

        r = hive4.analyze(list(lam), list(mu), list(nu))
        errs = []
        if r["dim"] != 3:
            errs.append("dim %s" % r["dim"])
        if list(r["L"]) != cL:
            errs.append("L %s vs %s" % (cL, list(r["L"])))
        if Fraction(cV) != r["volume_normalized"]:
            errs.append("V %s vs %s" % (cV, r["volume_normalized"]))
        if cH != list(r["hstar"]):
            errs.append("h* %s vs %s" % (cH, list(r["hstar"])))
        poly = r["poly"]
        if Fraction(c6a1, 6) != poly[1] or Fraction(c2a2, 2) != poly[2] or Fraction(cV, 6) != poly[3]:
            errs.append("P %s vs %s" % ([Fraction(c6a1, 6), Fraction(c2a2, 2), Fraction(cV, 6)], poly))
        if not r["verified"] or not r["vol_crosscheck"]:
            errs.append("hive4 internal audit")
        if r.get("max_denominator", 1) != cden:
            errs.append("den %d vs %d" % (cden, r.get("max_denominator", 1)))
        if r["n_vertices"] != cnv:
            errs.append("nv %d vs %d" % (cnv, r["n_vertices"]))
        if errs:
            bad.append((lam, mu, nu, errs))

    print("pool sampled (containment-satisfying): %d" % len(samples))
    print("dim-3 found in pool                 : %d" % sum(1 for l in lines if " dim=3 " in l))
    print("dim-3 cross-validated vs hive4.py   : %d" % len(d3))
    print("MISMATCHES                          : %d" % len(bad))
    for b in bad[:20]:
        print("   ", b)
    with open(os.path.join(HERE, "runs", "band5", "xval_dim3_report.json"), "w") as f:
        json.dump({"pool": len(samples), "checked": len(d3), "mismatches": len(bad),
                   "seed": seed, "detail": [[list(x[0]), list(x[1]), list(x[2]), x[3]] for x in bad[:50]]},
                  f, indent=1)
    print("XVAL-DIM3:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    sys.exit(main(w))
