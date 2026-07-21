#!/usr/bin/env python3
"""
hunt_reeve.py -- Reeve-directed local search in the r = 4 cell.

WHY THIS OBJECTIVE.  For a 3-dimensional polytope, writing the Ehrhart
polynomial in the h*-basis, P(n) = sum_i h*_i * C(n+3-i, 3), gives EXACTLY

    a_3 = (h*_0+h*_1+h*_2+h*_3)/6 = V/6 > 0
    a_2 = 1 + (h*_1 - h*_3)/2
    a_1 = (11 + 2*h*_1 - h*_2 + 2*h*_3) / 6
    a_0 = 1

so the ONLY Reeve-type coefficient is a_1, and a KTT counterexample in the
r = 4 cell requires

    h*_2  >  11 + 2*h*_1 + 2*h*_3.

(The Reeve tetrahedron T_q realises h* = (1,0,q-1,0), i.e. h*_2 = q-1 with
h*_1 = h*_3 = 0, and goes negative exactly at q = 13.)  This script therefore
hill-climbs on the exact score  s = 6*a_1 = 11 + 2h*_1 - h*_2 + 2h*_3  over
triples with dim Q = 3, with random restarts, unbounded part sizes and exact
arithmetic throughout.  s < 0 IS a counterexample and is printed immediately.

Absence of a hit proves nothing.
"""

import json
import os
import random
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PENALTY = Fraction(10 ** 6)


def norm(p):
    p = sorted((x for x in p if x > 0), reverse=True)
    return p


def score(lam, mu, nu):
    """(exact score, analysis).  Lower is better; < 0 means NEGATIVE a_1."""
    if sum(lam) + sum(mu) != sum(nu):
        return PENALTY * 10, None
    r = hive4.analyze(lam, mu, nu)
    if r["dim"] != 3:
        return PENALTY - r["dim"], r
    return 6 * r["poly"][1], r


def rand_state(rng, scale):
    while True:
        nu = norm([rng.randint(1, scale) for _ in range(4)])
        if len(nu) < 4:
            continue
        N = sum(nu)
        a = rng.randint(1, N - 1)
        lam, mu = [], []
        # random compositions with <= 4 parts
        for tgt, dst in ((a, lam), (N - a, mu)):
            rem = tgt
            for i in range(3):
                v = rng.randint(0, rem)
                dst.append(v)
                rem -= v
            dst.append(rem)
        lam, mu = norm(lam), norm(mu)
        if sum(lam) + sum(mu) == N and lam and mu:
            return lam, mu, nu


def neighbours(lam, mu, nu, rng, step):
    """Weight-preserving perturbations."""
    out = []
    L, M, U = list(lam) + [0] * 4, list(mu) + [0] * 4, list(nu) + [0] * 4
    L, M, U = L[:4], M[:4], U[:4]
    for _ in range(24):
        d = rng.choice([1, -1]) * rng.randint(1, step)
        i = rng.randrange(4)
        j = rng.randrange(4)
        which = rng.randrange(3)
        nl, nm, nu2 = list(L), list(M), list(U)
        if which == 0:      # move weight between lam and mu (nu fixed)
            nl[i] += d
            nm[j] -= d
        elif which == 1:    # grow lam and nu together
            nl[i] += d
            nu2[j] += d
        else:               # grow mu and nu together
            nm[i] += d
            nu2[j] += d
        if min(nl + nm + nu2) < 0:
            continue
        a, b, c = norm(nl), norm(nm), norm(nu2)
        if not c or len(c) != 4 or not a or not b:
            continue
        if sum(a) + sum(b) != sum(c):
            continue
        out.append((a, b, c))
    return out


def main(seconds=300, seed=20260721, scale=40, restarts=10 ** 9):
    rng = random.Random(seed)
    t0 = time.time()
    best = (PENALTY * 100, None, None)
    evals = 0
    hits = []
    dim3_best_h2 = (0, None)
    restart = 0
    while time.time() - t0 < seconds and restart < restarts:
        restart += 1
        lam, mu, nu = rand_state(rng, scale)
        s, r = score(lam, mu, nu)
        evals += 1
        stall = 0
        step = 3
        while stall < 60 and time.time() - t0 < seconds:
            improved = False
            for cand in neighbours(lam, mu, nu, rng, step):
                s2, r2 = score(*cand)
                evals += 1
                if r2 is not None and r2["dim"] == 3 and len(r2["hstar"]) > 2:
                    if r2["hstar"][2] > dim3_best_h2[0]:
                        dim3_best_h2 = (r2["hstar"][2], (cand, list(r2["hstar"])))
                if s2 < s:
                    lam, mu, nu = cand
                    s, r = s2, r2
                    improved = True
                    if s < 0:
                        hits.append((lam, mu, nu,
                                     [hive4._fmt_frac(c) for c in r["poly"]]))
                        print("*** NEGATIVE a_1 ***", lam, mu, nu,
                              [hive4._fmt_frac(c) for c in r["poly"]], flush=True)
                    break
            if not improved:
                stall += 1
                step = rng.choice([1, 1, 2, 3, 5, 8])
            else:
                stall = 0
            if s < best[0]:
                best = (s, (list(lam), list(mu), list(nu)),
                        list(r["hstar"]) if r else None)
    el = time.time() - t0
    print("evals=%d restarts=%d elapsed=%.1fs (%.0f evals/s)"
          % (evals, restart, el, evals / max(el, 1e-9)))
    print("best 6*a_1 = %s at %s  h* = %s"
          % (hive4._fmt_frac(best[0]) if best[0] < PENALTY else "no dim-3 found",
             best[1], best[2]))
    print("record h*_2 among dim-3 states: %s at %s"
          % (dim3_best_h2[0], dim3_best_h2[1]))
    print("NEGATIVE HITS: %d" % len(hits))
    with open(os.path.join(HERE, "hunt_reeve.json"), "w") as f:
        json.dump({"evals": evals, "seconds": round(el, 1),
                   "best_6a1": hive4._fmt_frac(best[0]) if best[0] < PENALTY else None,
                   "best_state": best[1], "best_hstar": best[2],
                   "record_hstar2": [dim3_best_h2[0], dim3_best_h2[1]],
                   "hits": hits}, f, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sec = float(sys.argv[1]) if len(sys.argv) > 1 else 300
    sd = int(sys.argv[2]) if len(sys.argv) > 2 else 20260721
    sc = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    sys.exit(main(sec, sd, sc))
