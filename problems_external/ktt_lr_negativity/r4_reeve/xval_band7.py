#!/usr/bin/env python3
"""Cross-validate band7.exe records against hive4.py (independent Python engine).

Input lines:  lam;mu;nu;L1;L2;L3;6a1;V;h1   (space-separated parts inside a field)
Checks, exactly:
  hive4.L[1..3] == L1,L2,L3
  hive4 poly coefficients: 6*a1 and 6*a3 == V
  hive4.hstar[1] == h1  (when dim == 3)
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402


def main(path):
    bad = []
    n = 0
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        f = line.split(";")
        lam = tuple(int(x) for x in f[0].split())
        mu = tuple(int(x) for x in f[1].split())
        nu = tuple(int(x) for x in f[2].split())
        L1, L2, L3, six_a1, V, h1 = (int(x) for x in f[3:9])
        r = hive4.analyze(lam, mu, nu)
        n += 1
        errs = []
        if r["L"][1] != L1 or r["L"][2] != L2 or r["L"][3] != L3:
            errs.append("L mismatch %s vs (%d,%d,%d)" % (r["L"][1:4], L1, L2, L3))
        if not r["verified"]:
            errs.append("hive4 degree-3 verification failed")
        P = list(r["poly"]) + [Fraction(0)] * 4
        if 6 * P[1] != six_a1:
            errs.append("a1 mismatch %s vs %d/6" % (P[1], six_a1))
        if 6 * P[3] != V:
            errs.append("V mismatch %s vs %d/6" % (P[3], V))
        if r["dim"] == 3 and r["hstar"][1] != h1:
            errs.append("h1 mismatch %s vs %d" % (r["hstar"][1], h1))
        if errs:
            bad.append((lam, mu, nu, errs))
    print("checked=%d  mismatches=%d" % (n, len(bad)))
    for b in bad[:20]:
        print("BAD", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
