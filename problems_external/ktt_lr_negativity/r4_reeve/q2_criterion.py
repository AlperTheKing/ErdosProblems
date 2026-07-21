#!/usr/bin/env python3
"""
q2_criterion.py -- THEORY QUESTION 2.

(1) Verify, exactly, the d=3 identities
        a3 = V/6,  a2 = 1 + (h*_1 - h*_3)/2,  a1 = (11 + 2h*_1 - h*_2 + 2h*_3)/6,  a0 = 1
    and the (c,V,i) form
        6*a1 = 3*(c + i) - V,      i = h*_3 = #interior lattice points,
    on (a) the Reeve family T_q and (b) every dim-3 r=4 hive polytope met.

(2) EXHAUSTIVE r=4 census collecting the FULL (c, V, h*) joint distribution, with
    special attention to the c = dim+1 = 4  (<=> h*_1 = 0) stratum: does c = 4
    force V = 1 (unimodular simplex) at r=4, as observed at r=5,6?

All arithmetic exact (int / Fraction).  No float anywhere.
"""

import json
import os
import sys
import time
from fractions import Fraction
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


# --------------------------------------------------------------- partitions
def parts_le(N, k):
    out = []

    def rec(rem, mx, cur):
        if rem == 0:
            out.append(tuple(cur))
            return
        if len(cur) == k:
            return
        for v in range(min(rem, mx), 0, -1):
            cur.append(v)
            rec(rem - v, v, cur)
            cur.pop()

    rec(N, N, [])
    return out


def interior_count(A, b, n=1):
    """#{x in Z^3 : A x < b strictly}  --  exact, brute force over the box."""
    V = hive4.vertices(A, b)
    if not V:
        return 0
    box = hive4.bounding_box(V)
    (x0, x1), (y0, y1), (z0, z1) = box
    cnt = 0
    for x in range(int(x0) - 1, int(x1) + 2):
        for y in range(int(y0) - 1, int(y1) + 2):
            for z in range(int(z0) - 1, int(z1) + 2):
                if all(hive4._dot(A[i], (x, y, z)) < b[i] * n for i in range(len(A))):
                    cnt += 1
    return cnt


# ------------------------------------------------------------- identity check
def check_identities(res, A=None, b=None, do_interior=False):
    """Return list of violated identity names (empty == all pass)."""
    bad = []
    if res["dim"] != 3:
        return bad
    P = res["poly"]
    while len(P) < 4:
        P = list(P) + [Fraction(0)]
    a0, a1, a2, a3 = P[0], P[1], P[2], P[3]
    h = res["hstar"]
    while len(h) < 4:
        h = list(h) + [0]
    Vol = res["volume_normalized"]
    c = res["c"]
    if a0 != 1:
        bad.append("a0!=1")
    if a3 != Fraction(Vol, 6):
        bad.append("a3!=V/6")
    if a2 != 1 + Fraction(h[1] - h[3], 2):
        bad.append("a2!=1+(h1-h3)/2")
    if a1 != Fraction(11 + 2 * h[1] - h[2] + 2 * h[3], 6):
        bad.append("a1!=(11+2h1-h2+2h3)/6")
    if 6 * a1 != 3 * (c + h[3]) - Vol:
        bad.append("6a1!=3(c+h3)-V")
    if h[1] != c - 4:
        bad.append("h1!=c-4")
    if sum(h) != Vol:
        bad.append("sum h*!=V")
    if h[3] > h[1]:
        bad.append("HIBI h3>h1 VIOLATED")
    if do_interior and A is not None:
        i = interior_count(A, b)
        if i != h[3]:
            bad.append("interior!=h3")
        if 6 * a1 != 3 * (c + i) - Vol:
            bad.append("6a1!=3(c+i)-V")
    return bad


# ------------------------------------------------------------------- workers
def _job(args):
    """One nu; returns (dimhist, dim3 records, identity failures)."""
    N, nu = args
    recs = []
    fails = []
    dimhist = Counter()
    for a in range(0, N + 1):
        La = parts_le(a, 4) if a > 0 else [()]
        Lb = parts_le(N - a, 4) if N - a > 0 else [()]
        for lam in La:
            for mu in Lb:
                if lam < mu:          # symmetry c(nu;lam,mu)=c(nu;mu,lam)
                    continue
                H = hive4.build_hive4(lam, mu, nu)
                if not H["ok"]:
                    dimhist[-1] += 1
                    continue
                res = hive4.analyze_polytope(H["A"], H["b"])
                d = res["dim"]
                dimhist[d] += 1
                if d != 3:
                    continue
                bad = check_identities(res)
                if bad or not res["verified"] or not res["vol_crosscheck"] \
                        or not res["deg_eq_dim"] or res["max_denominator"] != 1:
                    fails.append({"lam": lam, "mu": mu, "nu": nu, "bad": bad,
                                  "verified": res["verified"],
                                  "vol_cross": res["vol_crosscheck"],
                                  "deg_eq_dim": res["deg_eq_dim"],
                                  "maxden": res["max_denominator"]})
                h = list(res["hstar"]) + [0] * (4 - len(res["hstar"]))
                recs.append((res["c"], int(res["volume_normalized"]),
                             tuple(h[:4]),
                             int(6 * res["poly"][1]) if len(res["poly"]) > 1 else None,
                             lam, mu, nu, bool(res["neg"])))
    return dimhist, recs, fails


parts_le_cache = {}


def main(nmax=22, nmin=4, procs=60):
    t0 = time.time()
    jobs = []
    for N in range(nmin, nmax + 1):
        parts_le_cache[N] = None
        for nu in parts_le(N, 4):
            if len(nu) != 4:
                continue
            jobs.append((N, nu))
    dimhist = Counter()
    allrecs = []
    allfails = []
    with Pool(procs) as pool:
        for dh, recs, fails in pool.imap_unordered(_job, jobs, chunksize=1):
            dimhist.update(dh)
            allrecs.extend(recs)
            allfails.extend(fails)
    dt = time.time() - t0

    ntot = sum(dimhist.values())
    print(f"triples examined : {ntot}   ({dt:.1f}s, nmax={nmax})")
    print(f"dim histogram    : {dict(sorted(dimhist.items()))}")
    print(f"identity/audit failures : {len(allfails)}")
    for f in allfails[:10]:
        print("   FAIL", f)

    dim3 = allrecs
    print(f"dim-3 polytopes  : {len(dim3)}")
    negs = [r for r in dim3 if r[7]]
    print(f"NEGATIVE COEFFS  : {len(negs)}")
    for r in negs[:20]:
        print("   NEG", r)

    # --- the c = 4 stratum (h*_1 = 0) ------------------------------------
    c4 = [r for r in dim3 if r[0] == 4]
    volhist = Counter(r[1] for r in c4)
    print(f"\n=== c = 4 (h*_1 = 0) stratum: {len(c4)} polytopes ===")
    print(f"volume distribution V -> count : {dict(sorted(volhist.items()))}")
    big = [r for r in c4 if r[1] >= 2]
    print(f"c=4 with V >= 2  : {len(big)}")
    for r in big[:40]:
        print("   BIG", r)

    # --- global (c,V) picture -------------------------------------------
    cvhist = Counter((r[0], r[1]) for r in dim3)
    print(f"\ndistinct (c,V) pairs : {len(cvhist)}")
    print("min c :", min(r[0] for r in dim3), " max c :", max(r[0] for r in dim3))
    print("min V :", min(r[1] for r in dim3), " max V :", max(r[1] for r in dim3))
    # necessary screen V > 3c
    surv = [r for r in dim3 if r[1] > 3 * r[0]]
    print(f"triples passing the necessary screen V > 3c : {len(surv)}")
    ratio = max(dim3, key=lambda r: Fraction(r[1], r[0]))
    print("max V/c :", Fraction(ratio[1], ratio[0]), "at", ratio[4], ratio[5], ratio[6],
          "h*=", ratio[2], " (need > 3)")
    m = min(dim3, key=lambda r: r[3])
    print("min 6a1 :", m[3], "at", m[4], m[5], m[6], "h*=", m[2], "c=", m[0], "V=", m[1])
    print("record h*_2 :", max(r[2][2] for r in dim3))

    out = {
        "nmax": nmax, "seconds": dt, "triples": ntot,
        "dimhist": {str(k): v for k, v in sorted(dimhist.items())},
        "audit_failures": len(allfails),
        "dim3_count": len(dim3),
        "negatives": len(negs),
        "c4_count": len(c4),
        "c4_volume_distribution": {str(k): v for k, v in sorted(volhist.items())},
        "c4_with_V_ge_2": [[list(r[4]), list(r[5]), list(r[6]), r[0], r[1], list(r[2])]
                           for r in big],
        "cv_pairs": sorted([list(k) + [v] for k, v in cvhist.items()]),
        "min_6a1": m[3],
        "max_V_over_c": str(Fraction(ratio[1], ratio[0])),
        "screen_survivors": len(surv),
    }
    with open(os.path.join(HERE, f"q2_census_{nmax}.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote", os.path.join(HERE, f"q2_census_{nmax}.json"))
    return 0


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    sys.exit(main(nmax, procs=procs))
