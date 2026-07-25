#!/usr/bin/env python3
"""
Hill-climb the linear-coefficient negativity ratio R_1 over gcd-reduced,
weight-matched, PRIMITIVE hive triples of fixed part-count r.  a_1 < 0 iff
R_1 > 1.  Sign of every Ehrhart coefficient is a stretch invariant, so we
always work with gcd-reduced representatives (stretches share R_1 but are
slower).  All arithmetic exact.

Usage: hillclimb_R1.py r  "lam" "mu" "nu"  [steps] [node_cap]
"""
import sys, os, json, time
from fractions import Fraction
from math import gcd
from functools import reduce

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "hstar_spread"))
from ehrhart import analyze
from classify_primitive import is_primitive


def reduce_triple(lam, mu, nu):
    g = reduce(gcd, [x for x in lam + mu + nu if x], 0)
    if g <= 1:
        return tuple(lam), tuple(mu), tuple(nu)
    return (tuple(x // g for x in lam), tuple(x // g for x in mu),
            tuple(x // g for x in nu))


def wd(p):
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and p[-1] >= 0


def canon(lam, mu, nu):
    lam, mu, nu = reduce_triple(list(lam), list(mu), list(nu))
    return (tuple(lam), tuple(mu), tuple(nu))


def neighbors(lam, mu, nu, r):
    """weight-matched moves keeping length r, weakly decreasing."""
    lam = list(lam) + [0] * (r - len(lam))
    mu = list(mu) + [0] * (r - len(mu))
    nu = list(nu)
    out = []
    # internal redistributions within lam / mu / nu (sum preserved)
    for P, which in ((lam, 'l'), (mu, 'm'), (nu, 'n')):
        for i in range(r):
            for j in range(r):
                if i == j:
                    continue
                Q = list(P)
                Q[i] += 1
                Q[j] -= 1
                if not wd(Q):
                    continue
                if which == 'l':
                    out.append((Q, mu, nu))
                elif which == 'm':
                    out.append((lam, Q, nu))
                else:
                    out.append((lam, mu, Q))
    # transfers: add 1 to lam_i and nu_k  (|lam|,|nu| both +1)
    for i in range(r):
        L = list(lam); L[i] += 1
        if not wd(L):
            continue
        for k in range(r):
            N = list(nu); N[k] += 1
            if wd(N):
                out.append((L, mu, N))
    for i in range(r):
        Mu = list(mu); Mu[i] += 1
        if not wd(Mu):
            continue
        for k in range(r):
            N = list(nu); N[k] += 1
            if wd(N):
                out.append((lam, Mu, N))
    # de-transfers: remove 1 from lam_i and nu_k
    for i in range(r):
        L = list(lam); L[i] -= 1
        if not wd(L):
            continue
        for k in range(r):
            N = list(nu); N[k] -= 1
            if wd(N):
                out.append((L, mu, N))
    for i in range(r):
        Mu = list(mu); Mu[i] -= 1
        if not wd(Mu):
            continue
        for k in range(r):
            N = list(nu); N[k] -= 1
            if wd(N):
                out.append((lam, Mu, N))
    # canonicalize + dedupe + validity
    seen = set()
    res = []
    for L, Mu, N in out:
        if sum(L) + sum(Mu) != sum(N):
            continue
        if any(x < 0 for x in L + Mu + N) or N[0] == 0:
            continue
        c = canon(L, Mu, N)
        if c in seen:
            continue
        seen.add(c)
        res.append(c)
    return res


def score(lam, mu, nu, node_cap, cache):
    key = (tuple(lam), tuple(mu), tuple(nu))
    if key in cache:
        return cache[key]
    r = len(nu)
    prim, msl, nsat = is_primitive(list(lam), list(mu), list(nu))
    if prim is None or not prim:
        cache[key] = None
        return None
    try:
        res = analyze(list(lam), list(mu), list(nu), node_cap=node_cap)
    except Exception:
        cache[key] = None
        return None
    r1 = res["R1"]
    val = (r1, res["degree"], res["M"], res["hstar"])
    cache[key] = val
    return val


def main():
    r = int(sys.argv[1])
    lam = tuple(int(x) for x in sys.argv[2].split(","))
    mu = tuple(int(x) for x in sys.argv[3].split(","))
    nu = tuple(int(x) for x in sys.argv[4].split(","))
    steps = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    node_cap = int(sys.argv[6]) if len(sys.argv) > 6 else 3 * 10 ** 9
    cache = {}
    lam, mu, nu = canon(lam, mu, nu)
    cur = score(lam, mu, nu, node_cap, cache)
    if cur is None:
        print("seed not primitive/positive; abort")
        return
    best = (cur[0], lam, mu, nu, cur)
    print("seed R1=%.6f d=%d M=%d nu=%s" % (float(cur[0]), cur[1], cur[2], nu))
    t0 = time.time()
    for step in range(steps):
        nbrs = neighbors(lam, mu, nu, r)
        improved = None
        for (L, Mu, N) in nbrs:
            s = score(L, Mu, N, node_cap, cache)
            if s is None or s[0] is None:
                continue
            if s[0] > best[0]:
                best = (s[0], L, Mu, N, s)
                improved = (L, Mu, N, s)
        if improved is None:
            print("local max at step %d: R1=%.6f nu=%s lam=%s mu=%s d=%d M=%d "
                  "(t=%.0fs, |cache|=%d)" %
                  (step, float(best[0]), best[3], best[1], best[2],
                   best[4][1], best[4][2], time.time() - t0, len(cache)))
            if best[0] > 1:
                print("*** R1 > 1  => a_1 < 0  => KTT COUNTEREXAMPLE ***")
                print("hstar=", best[4][3])
            break
        lam, mu, nu = improved[0], improved[1], improved[2]
        print("step %2d  R1=%.6f  d=%d M=%d nu=%s lam=%s mu=%s  (t=%.0fs)" %
              (step, float(improved[3][0]), improved[3][1], improved[3][2],
               nu, lam, mu, time.time() - t0), flush=True)
        if improved[3][0] > 1:
            print("*** R1 > 1 => a_1 < 0 => KTT COUNTEREXAMPLE ***")
            print("triple:", lam, mu, nu, "hstar=", improved[3][3])
            break
    print("FINAL best R1=%s (%.6f) nu=%s lam=%s mu=%s d=%d M=%d" %
          (str(best[0]), float(best[0]), best[3], best[1], best[2],
           best[4][1], best[4][2]))


if __name__ == "__main__":
    main()
