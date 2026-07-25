#!/usr/bin/env python3
"""fam12 CONTROL sampler -- unbiased random hive triples, r = 5..7.

Two strata, both reported separately:

  A ("raw")   : lam, mu random partitions with <= r parts; nu a random
                partition of |lam|+|mu| into exactly r positive parts,
                built with NO knowledge of LR feasibility.  Measures the
                raw nonempty rate.
  B ("domint"): lam, mu as above; nu obtained from lam+mu by a random
                number of downward box moves (row i -> row j>i) keeping
                weak decrease, i.e. a random point of the dominance
                interval [lam u mu, lam+mu].  This conditions toward
                NONEMPTY hive polytopes but is blind to h*, c, d, and to
                every tier-0 criterion -- it never looks at the polytope.

Nothing here inspects h*_1, h*_d, TIER0 or JACKPOT: the sampler cannot
bias the measured base rates.
"""
import argparse
import random
import sys


def rand_partition_leq(r, M, rng):
    """random partition with at most r parts, each in 0..M (sorted desc)."""
    v = sorted((rng.randint(0, M) for _ in range(r)), reverse=True)
    while v and v[-1] == 0:
        v.pop()
    return v


def pad(p, r):
    return list(p) + [0] * (r - len(p))


def rand_partition_exact(S, r, rng):
    """random partition of S into exactly r POSITIVE parts (S >= r)."""
    if S < r:
        return None
    # r-1 random cut points -> composition -> sort desc
    cuts = sorted(rng.sample(range(1, S), r - 1)) if r > 1 else []
    parts, prev = [], 0
    for cpt in cuts:
        parts.append(cpt - prev)
        prev = cpt
    parts.append(S - prev)
    parts.sort(reverse=True)
    return parts


def down_moves(nu, k, rng):
    """apply up to k random single-box moves row i -> row j>i, keeping
    weakly decreasing and all parts >= 0."""
    v = list(nu)
    r = len(v)
    for _ in range(k):
        cands = []
        for i in range(r):
            for j in range(i + 1, r):
                w = list(v)
                w[i] -= 1
                w[j] += 1
                if w[i] < 0:
                    continue
                if all(w[t] >= w[t + 1] for t in range(r - 1)) and w[-1] >= 0:
                    cands.append(w)
        if not cands:
            break
        v = rng.choice(cands)
    return v


def gen(n, seed, rmin, rmax, mmin, mmax, stratum):
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < 400 * n:
        tries += 1
        r = rng.randint(rmin, rmax)
        M = rng.randint(mmin, mmax)
        lam = rand_partition_leq(r, M, rng)
        mu = rand_partition_leq(r, M, rng)
        if not lam or not mu:
            continue
        S = sum(lam) + sum(mu)
        if S < r:
            continue
        if stratum == "raw":
            nu = rand_partition_exact(S, r, rng)
            if nu is None:
                continue
        else:
            base = [a + b for a, b in zip(pad(lam, r), pad(mu, r))]
            k = rng.randint(0, 3 * r)
            nu = down_moves(base, k, rng)
            while nu and nu[-1] == 0:
                nu.pop()
            if len(nu) != r:
                continue
        if len(nu) != r or nu[-1] <= 0:
            continue
        if sum(lam) + sum(mu) != sum(nu):
            continue
        out.append((lam, mu, nu))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=12)
    ap.add_argument("--rmin", type=int, default=5)
    ap.add_argument("--rmax", type=int, default=7)
    ap.add_argument("--mmin", type=int, default=2)
    ap.add_argument("--mmax", type=int, default=12)
    ap.add_argument("--stratum", choices=["raw", "domint"], default="domint")
    ap.add_argument("--cap", type=str, default="")
    ap.add_argument("--out", type=str, default="")
    a = ap.parse_args()
    trips = gen(a.n, a.seed, a.rmin, a.rmax, a.mmin, a.mmax, a.stratum)
    lines = []
    for lam, mu, nu in trips:
        s = "%s;%s;%s" % (",".join(map(str, lam)), ",".join(map(str, mu)),
                          ",".join(map(str, nu)))
        if a.cap:
            s += ";" + a.cap
        lines.append(s)
    txt = "\n".join(lines) + "\n"
    if a.out:
        open(a.out, "w").write(txt)
        sys.stderr.write("wrote %d triples to %s\n" % (len(lines), a.out))
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
