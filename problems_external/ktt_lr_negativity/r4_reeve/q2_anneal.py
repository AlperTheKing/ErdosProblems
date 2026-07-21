#!/usr/bin/env python3
"""
q2_anneal.py -- direct minimisation of the EXACT negativity score at r=4.

Score to minimise:   S = 6*a_1 = 3*(c + i) - V      (i = h*_3 = #interior pts)
A KTT counterexample in the r=4 cell is exactly  S < 0.
Secondary target: the c=4 stratum (S = 12 - V there, so V >= 13 wins outright).

Simulated annealing over (lam, mu, nu) with unbounded part sizes; all exact.
"""
import json
import os
import random
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def score(lam, mu, nu):
    H = hive4.build_hive4(lam, mu, nu)
    if not H["ok"]:
        return None
    A, b = H["A"], H["b"]
    V = hive4.vertices(A, b)
    if not V or hive4._affine_rank(V) != 3:
        return None
    box = hive4.bounding_box(V)
    L = [1] + [hive4.lattice_count(A, b, n, box) for n in range(1, 4)]
    P = hive4.interpolate(L)
    Vol = int(hive4.normalized_volume(A, b, V))
    return (6 * P[1], L[1], Vol)


def norm(p):
    p = sorted((x for x in p if x > 0), reverse=True)
    return tuple(p)


def perturb(rng, lam, mu, nu, amp):
    lam = list(lam) + [0] * (4 - len(lam))
    mu = list(mu) + [0] * (4 - len(mu))
    nu = list(nu) + [0] * (4 - len(nu))
    for _ in range(rng.randint(1, 3)):
        which = rng.randrange(3)
        i = rng.randrange(4)
        d = rng.randint(1, amp) * rng.choice([1, -1])
        if which == 0:
            lam[i] += d
            nu[rng.randrange(4)] += d
        elif which == 1:
            mu[i] += d
            nu[rng.randrange(4)] += d
        else:
            j = rng.randrange(4)
            nu[i] += d
            nu[j] -= d
    if any(x < 0 for x in lam + mu + nu):
        return None
    lam, mu, nu = norm(lam), norm(mu), norm(nu)
    if len(nu) != 4:
        return None
    if sum(lam) + sum(mu) != sum(nu):
        return None
    return lam, mu, nu


def _run(args):
    seed, iters, amp = args
    rng = random.Random(seed)
    best = (Fraction(10 ** 9), None)
    bestc4 = (0, None)
    cur = ((3, 2, 1), (3, 2, 1), (5, 4, 2, 1))
    curs = score(*cur)
    evals = 0
    for it in range(iters):
        if curs is None:
            cur = ((3, 2, 1), (3, 2, 1), (5, 4, 2, 1))
            curs = score(*cur)
            continue
        cand = perturb(rng, *cur, amp)
        if cand is None:
            continue
        s = score(*cand)
        evals += 1
        if s is None:
            continue
        T = max(Fraction(1, 10), Fraction(30 * (iters - it), iters))
        if s[0] <= curs[0] or rng.random() < 0.02:
            cur, curs = cand, s
        if s[0] < best[0]:
            best = (s[0], (cand, s))
        if s[1] == 4 and s[2] > bestc4[0]:
            bestc4 = (s[2], (cand, s))
        if it % 400 == 399:
            cur = ((3, 2, 1), (3, 2, 1), (5, 4, 2, 1)) if rng.random() < 0.3 else cur
            curs = score(*cur)
    return best, bestc4, evals


def main(iters=4000, procs=58, amp=6, seed0=99001):
    t0 = time.time()
    jobs = [(seed0 + i, iters, amp) for i in range(procs)]
    best = (Fraction(10 ** 9), None)
    bestc4 = (0, None)
    ev = 0
    with Pool(procs) as pool:
        for b, b4, e in pool.imap_unordered(_run, jobs):
            ev += e
            if b[1] and b[0] < best[0]:
                best = b
            if b4[1] and b4[0] > bestc4[0]:
                bestc4 = b4
    dt = time.time() - t0
    print(f"exact evaluations: {ev}   ({dt:.0f}s)")
    print("min 6a1 = 3(c+i)-V  [NEGATIVE would be the counterexample]:", best[0])
    print("   at", best[1])
    print("max V over the c==4 stratum [V>=13 would be a Reeve counterexample]:", bestc4[0])
    print("   at", bestc4[1])
    json.dump({"evals": ev, "seconds": dt, "min_6a1": str(best[0]),
               "argmin": str(best[1]), "max_V_c4": bestc4[0],
               "argmax_c4": str(bestc4[1])},
              open(os.path.join(HERE, "q2_anneal.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 4000))
