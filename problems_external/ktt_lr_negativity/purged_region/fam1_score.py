#!/usr/bin/env python3
"""Rescore fam1 records with the THEORY1 functionals.

M1 := sum_j h*_j (2j-(d+1))          -> [n^{d-1}]P < 0  iff  M1 > 0
S  := min_{1<=k<=d-1} d! [n^k]P      -> negativity iff S < 0  (integer-valued)
s  := deg h*
"""
import sys, json
from fractions import Fraction
from fam1_target import coeff_vectors

_cv = {}
def cv(d):
    if d not in _cv:
        _cv[d] = coeff_vectors(d)
    return _cv[d]

def score(r):
    d = r["d"]; h = r["hstar"]
    fac = 1
    for i in range(2, d + 1):
        fac *= i
    rows = cv(d)
    S = None; Sk = None
    for k in range(1, d):
        v = sum(rows[k][j] * h[j] for j in range(d + 1)) * fac
        if S is None or v < S:
            S = v; Sk = k
    M1 = sum(h[j] * (2 * j - (d + 1)) for j in range(d + 1))
    s = max([j for j in range(d + 1) if h[j]] or [0])
    return S, Sk, M1, s

if __name__ == "__main__":
    bestM1 = None; bestS = None; bestS_h1z = None; bests = None
    bestV_h1z = None; n = 0
    for p in sys.argv[1:]:
        for line in open(p):
            r = json.loads(line)
            if r.get("status") != "OK" or not r.get("d") or r["d"] < 2:
                continue
            n += 1
            S, Sk, M1, s = score(r)
            tag = [r["lam"], r["mu"], r["nu"]]
            rec = {"S": str(S), "k": Sk, "M1": M1, "s": s, "d": r["d"],
                   "hstar": r["hstar"], "V": r["hstar_sum"],
                   "h1": r["hstar_1"], "triple": tag}
            if bestM1 is None or M1 > bestM1["M1"]:
                bestM1 = rec
            if bestS is None or S < Fraction(bestS["S"]):
                bestS = rec
            if r["hstar_1"] == 0:
                if bestS_h1z is None or S < Fraction(bestS_h1z["S"]):
                    bestS_h1z = rec
                if bestV_h1z is None or r["hstar_sum"] > bestV_h1z["V"] or \
                   (r["hstar_sum"] == bestV_h1z["V"] and s > bestV_h1z["s"]):
                    bestV_h1z = rec
                if bests is None or s > bests["s"]:
                    bests = rec
    print(json.dumps({"n": n, "max_M1": bestM1, "min_S": bestS,
                      "min_S_at_h1_0": bestS_h1z, "max_s_at_h1_0": bests,
                      "max_V_at_h1_0": bestV_h1z}, indent=1))
