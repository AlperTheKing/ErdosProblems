#!/usr/bin/env python3
"""Fast RANDOM sampler for the fam4 asymmetric-weight family at large weight.

Same family definition as gen_fam4.py (|mu| >= ratio*|lam|, nu with exactly
r positive parts, lam,mu <= r parts, lam,mu componentwise <= nu), but the
triples are drawn uniformly at random instead of enumerated, so the large-
weight window is reachable.  SAMPLED, not exhaustive.
"""
import argparse, random, sys


def rand_partition_exact(N, k, rng):
    """random partition of N into exactly k positive parts (not uniform;
    uniform enough for a search sweep)."""
    if N < k:
        return None
    cuts = sorted(rng.sample(range(1, N), k - 1)) if k > 1 else []
    parts = []
    prev = 0
    for c in cuts + [N]:
        parts.append(c - prev)
        prev = c
    parts.sort(reverse=True)
    return tuple(parts)


def rand_sub_partition(W, nu, r, rng, tries=40):
    """random partition of W with <= r parts, componentwise <= nu."""
    for _ in range(tries):
        k = rng.randint(1, min(r, W))
        p = rand_partition_exact(W, k, rng)
        if p is None:
            continue
        if all(p[i] <= nu[i] for i in range(len(p))):
            return p
    # greedy fallback
    rem = W
    p = []
    for i in range(r):
        take = min(nu[i], rem)
        if i + 1 < r:
            take = min(take, rem)
        p.append(take)
        rem -= take
        if rem == 0:
            break
    if rem != 0:
        return None
    p = tuple(x for x in p if x > 0)
    if not p or any(p[i] < p[i + 1] for i in range(len(p) - 1)):
        return None
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--wmin", type=int, required=True)
    ap.add_argument("--wmax", type=int, required=True)
    ap.add_argument("--ratio", type=int, default=2)
    ap.add_argument("--n", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=424242)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed + a.r)
    seen = set()
    with open(a.out, "w") as f:
        guard = 0
        while len(seen) < a.n and guard < a.n * 60:
            guard += 1
            W = rng.randint(a.wmin, a.wmax)
            nu = rand_partition_exact(W, a.r, rng)
            if nu is None:
                continue
            wlmax = W // (1 + a.ratio)
            if wlmax < 1:
                continue
            wl = rng.randint(1, wlmax)
            wm = W - wl
            lam = rand_sub_partition(wl, nu, a.r, rng)
            if lam is None:
                continue
            mu = rand_sub_partition(wm, nu, a.r, rng)
            if mu is None:
                continue
            key = (lam, mu, nu)
            if key in seen:
                continue
            seen.add(key)
            f.write("%s;%s;%s\n" % (",".join(map(str, lam)),
                                    ",".join(map(str, mu)),
                                    ",".join(map(str, nu))))
    sys.stderr.write("r=%d sampled %d triples (guard %d)\n"
                     % (a.r, len(seen), guard))


if __name__ == "__main__":
    main()
