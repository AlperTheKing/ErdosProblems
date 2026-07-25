#!/usr/bin/env python3
"""FAM4 = ASYMMETRIC-WEIGHT family generator.

Family definition (used verbatim in the manifest):

    r      := len(nu) in {5,6,7}, nu has exactly r strictly positive parts
    lam,mu : partitions with at most r parts, |lam| + |mu| = |nu|
    ASYM   : |mu| >= ratio * |lam|   (default ratio = 2; the verified
             half-integral refuter lam=(2,2,1) mu=(4,3,2,1) has ratio 2)
    window : |nu| <= W_r

Cheap exact pre-conditions applied BEFORE any engine call (both are
theorems, not oracles: c(nu;lam,mu) > 0 forces lam_i <= nu_i and
mu_i <= nu_i componentwise, and |lam|+|mu| = |nu|).  No LP dimension
oracle, no simplex filter, anywhere.
"""
import argparse, itertools, random, sys


def partitions_exact_parts(N, k, maxpart=None):
    """partitions of N into exactly k positive parts, weakly decreasing."""
    if maxpart is None:
        maxpart = N
    if k == 0:
        if N == 0:
            yield ()
        return
    if N < k:
        return
    for first in range(min(maxpart, N - k + 1), 0, -1):
        for rest in partitions_exact_parts(N - first, k - 1, first):
            yield (first,) + rest


def partitions_atmost(N, k, maxpart=None):
    """partitions of N into at most k positive parts."""
    for j in range(0, k + 1):
        for p in partitions_exact_parts(N, j, maxpart):
            yield p


def contained(p, nu):
    for i, x in enumerate(p):
        if i >= len(nu) or x > nu[i]:
            return False
    return True


def gen(r, wmax, wmin, ratio, rng, per_nu_cap, lam_wmax):
    """yield (lam, mu, nu) of the asymmetric family for one r."""
    out = []
    for W in range(wmin, wmax + 1):
        for nu in partitions_exact_parts(W, r):
            # lam small: |lam| <= W/(1+ratio) and |lam| <= lam_wmax
            lmax = min(lam_wmax, W // (1 + ratio))
            cands = []
            for wl in range(1, lmax + 1):
                wm = W - wl
                if wm < ratio * wl:
                    continue
                lams = [l for l in partitions_atmost(wl, r) if contained(l, nu)]
                if not lams:
                    continue
                mus = [m for m in partitions_atmost(wm, r) if contained(m, nu)]
                if not mus:
                    continue
                for l in lams:
                    for m in mus:
                        cands.append((l, m, nu))
            if not cands:
                continue
            if len(cands) > per_nu_cap:
                cands = rng.sample(cands, per_nu_cap)
            out.extend(cands)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--wmin", type=int, required=True)
    ap.add_argument("--wmax", type=int, required=True)
    ap.add_argument("--ratio", type=int, default=2)
    ap.add_argument("--per-nu-cap", type=int, default=40)
    ap.add_argument("--lam-wmax", type=int, default=10)
    ap.add_argument("--total-cap", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=20260722)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed + 1000 * a.r)
    trips = gen(a.r, a.wmax, a.wmin, a.ratio, rng, a.per_nu_cap, a.lam_wmax)
    exhaustive = True
    if len(trips) > a.total_cap:
        trips = rng.sample(trips, a.total_cap)
        exhaustive = False
    with open(a.out, "w") as f:
        for (l, m, n) in trips:
            f.write("%s;%s;%s\n" % (",".join(map(str, l)),
                                    ",".join(map(str, m)),
                                    ",".join(map(str, n))))
    sys.stderr.write("r=%d wrote %d triples (per_nu_cap %d, total_cap hit=%s)\n"
                     % (a.r, len(trips), a.per_nu_cap, not exhaustive))


if __name__ == "__main__":
    main()
