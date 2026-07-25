#!/usr/bin/env python3
"""
hunt.py -- dedicated TIER-0 / JACKPOT hunt.

TARGET (exact reformulation, proved in the report):
    h*_d - h*_1 = (d + 1) - #(lattice points on the relative boundary of Q)
so JACKPOT (h*_d > h*_1) <=> Q has AT MOST d lattice points on its relative
boundary, and TIER0 <=> c = d+1 with at least one RELATIVE-INTERIOR lattice pt.

STAGE A (no LP, exact ints): enumerate all integer hives; let
    T = { rhombi tight at EVERY integer hive }.
A lattice point p can be in relint(Q) only if tight(p) = T (necessary, since
implicit-equalities ⊆ T ⊆ tight(p) when p ∈ relint).  So
    n_int_lat := #{p : tight(p) == T}   >=  true #interior
    n_bdy_lat := c - n_int_lat          <=  true #boundary
Screen keeps triples with n_int_lat >= 1 and n_bdy_lat <= BDY_MAX; because
n_bdy_lat under-estimates the true boundary count the screen cannot miss a
JACKPOT with #bdry <= BDY_MAX.  (Nothing here is a mathematical verdict; all
survivors go to the exact stage.)
"""
import sys, json, random, itertools, collections
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from hive_struct import build, slacks, enumerate_hives, affine_rank


def stageA(lam, mu, nu, cap=4000):
    P = build(lam, mu, nu)
    if P is None: return None
    pts = enumerate_hives(P, cap)
    if pts is None or len(pts) == 0: return None
    c = len(pts)
    S = [slacks(P, p) for p in pts]
    ncon = len(P["cons"])
    T = frozenset(k for k in range(ncon) if all(s[k] == 0 for s in S))
    n_int = 0
    for s in S:
        if frozenset(k for k in range(ncon) if s[k] == 0) == T:
            n_int += 1
    # rank of T-rows -> d >= D - rank(T)
    rows = [[P["cons"][k][0][i] for i in range(P["D"])] for k in T]
    dlo = P["D"] - (affine_rank([[0]*P["D"]] + rows) if rows else 0)
    return dict(c=c, D=P["D"], n_int_lat=n_int, n_bdy_lat=c - n_int,
                d_lower=dlo, nT=len(T))


def gen_triples(r, nmax, count, seed):
    """random partitions with r parts for nu, and lam,mu with |lam|+|mu|=|nu|."""
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < count and tries < count * 200:
        tries += 1
        # random weakly decreasing nu with r parts
        nu = sorted([rng.randint(1, nmax) for _ in range(r)], reverse=True)
        N = sum(nu)
        kl = rng.randint(1, r)
        km = rng.randint(1, r)
        lam = sorted([rng.randint(0, nmax) for _ in range(kl)], reverse=True)
        lam = [x for x in lam if x > 0]
        if not lam: continue
        L = sum(lam)
        if L >= N: continue
        M = N - L
        # random mu with km parts summing to M, weakly decreasing, <= nu[0]
        mu = []
        rem = M
        for i in range(km):
            hi = min(rem, nu[0], mu[-1] if mu else nu[0])
            if hi <= 0: break
            lo = max(1, -(-rem // (km - i)) if i < km - 1 else rem)
            lo = min(lo, hi)
            v = rng.randint(lo, hi) if hi > lo else hi
            mu.append(v); rem -= v
            if rem == 0: break
        if rem != 0 or not mu: continue
        if any(mu[i] < mu[i+1] for i in range(len(mu)-1)): continue
        out.append((lam, mu, nu))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=12)
    ap.add_argument("--count", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cap", type=int, default=4000)
    ap.add_argument("--bdymax", type=int, default=40)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    trips = gen_triples(a.r, a.nmax, a.count, a.seed)
    fh = open(a.out, "w") if a.out else sys.stdout
    nz = 0; kept = 0; best = None
    for lam, mu, nu in trips:
        try:
            r = stageA(lam, mu, nu, a.cap)
        except Exception:
            continue
        if r is None: continue
        nz += 1
        if r["n_int_lat"] >= 1:
            score = r["d_lower"] + 1 - r["n_bdy_lat"]   # optimistic JACKPOT score
            if best is None or score > best[0]:
                best = (score, lam, mu, nu, r)
            if r["n_bdy_lat"] <= a.bdymax:
                kept += 1
                r.update(lam=lam, mu=mu, nu=nu, score=score)
                fh.write(json.dumps(r) + "\n"); fh.flush()
    sys.stderr.write("nonempty=%d kept=%d best=%s\n" % (nz, kept, json.dumps(best) if best else "none"))
