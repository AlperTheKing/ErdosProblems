#!/usr/bin/env python3
"""Negativity-margin sweep driven by engine C (exact Ehrhart, no counting).

For each hive polytope it records the EXACT h*-vector and the EXACT monomial
coefficients of P, plus the two criterion statistics of (F1):

    u_j   = 2j - (d+1)
    m1    = <u>            ;  a_{d-1} < 0  iff  m1 > 0
    m2    = <u^2>          ;  a_{d-2} < 0  iff  m2 < (d+1)/3

`ratio` = m2 / ((d+1)/3):  the campaign-wide distance to the cheapest realistic
negativity.  ratio < 1 is a counterexample to KTT at the a_{d-2} coefficient.
`minc`  = the smallest monomial coefficient actually observed (exact Fraction).
"""
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ehr import ehrhart  # noqa: E402


def stats(r):
    d = r["d"]
    hs = r["hstar"]
    tot = sum(hs)
    m1 = Fraction(sum(hs[j] * (2 * j - d - 1) for j in range(d + 1)), tot)
    m2 = Fraction(sum(hs[j] * (2 * j - d - 1) ** 2 for j in range(d + 1)), tot)
    thr = Fraction(d + 1, 3)
    minc = min(Fraction(x) for x in r["coeffs"])
    return dict(m1=str(m1), m2=str(m2), ratio=float(m2 / thr) if thr else None,
                minc=str(minc), minc_f=float(minc), mass=tot)


def profile(lam, mu, nu, vol_cap=3 * 10 ** 5, seed=1):
    try:
        r = ehrhart(lam, mu, nu, seed=seed, vol_cap=vol_cap)
    except Exception as e:
        return dict(status="ERR", err=repr(e), lam=lam, mu=mu, nu=nu)
    r["lam"], r["mu"], r["nu"] = lam, mu, nu
    if r["status"] == "OK" and r["d"] >= 1:
        r.update(stats(r))
    return r


# ------------------------------------------------------------------ generators
def rand_part(rng, r, hi):
    p = sorted((rng.randint(1, hi) for _ in range(r)), reverse=True)
    return p


def gen_triple(rng, r, hi):
    """Random (lam, mu, nu) with |lam|+|mu|=|nu|, len(nu)=r, nu a partition."""
    a = rng.randint(2, r)
    bq = rng.randint(2, r)
    lam = rand_part(rng, a, hi)
    mu = rand_part(rng, bq, hi)
    W = sum(lam) + sum(mu)
    # nu: random composition into r weakly decreasing parts summing to W
    for _ in range(60):
        cuts = sorted(rng.randint(0, W) for _ in range(r - 1))
        parts = []
        prev = 0
        for c in cuts + [W]:
            parts.append(c - prev)
            prev = c
        nu = sorted(parts, reverse=True)
        if sum(nu) == W and nu[0] <= max(lam[0] + mu[0], 1) and nu[-1] >= 0:
            return lam, mu, nu
    return None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=5)
    ap.add_argument("--hi", type=int, default=8)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--volcap", type=int, default=300000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    best = []
    out = open(a.out, "w") if a.out else None
    nok = 0
    for i in range(a.n):
        t = gen_triple(rng, a.r, a.hi)
        if not t:
            continue
        r = profile(*t, vol_cap=a.volcap, seed=a.seed + i)
        if r["status"] != "OK" or r.get("d", 0) < 2 or r.get("c", 0) == 0:
            continue
        nok += 1
        if out:
            out.write(json.dumps(r) + "\n")
        best.append((r["ratio"], r["minc_f"], r["lam"], r["mu"], r["nu"], r["d"],
                     r["c"], r["volume"], r["hstar"]))
        if r["minc_f"] < 0:
            print("!!! NEGATIVE COEFFICIENT", json.dumps(r))
    best.sort()
    print(json.dumps(dict(r=a.r, tried=a.n, ok=nok,
                          best_ratio=best[0][0] if best else None)))
    for row in best[:12]:
        print("ratio=%.3f minc=%.4f lam=%s mu=%s nu=%s d=%d c=%d V=%s h*=%s"
              % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    if out:
        out.close()


if __name__ == "__main__":
    main()
