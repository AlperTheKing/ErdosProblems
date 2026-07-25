#!/usr/bin/env python3
"""Targeted generator: hive triples likely to be FULL-dimensional.
Enforces lam_i <= nu_i, mu_i <= nu_i, strict-ish decrease, |lam|+|mu|=|nu|."""
import random, sys


def rand_strict(r, lo, hi, rng):
    v = sorted({rng.randint(lo, hi) for _ in range(r * 3)}, reverse=True)
    while len(v) < r:
        v.append(max(0, (v[-1] - 1) if v else 1))
        v = sorted(set(v), reverse=True)
    return v[:r]


def gen(r, N, count, seed=1):
    rng = random.Random(seed)
    out = set()
    tries = 0
    while len(out) < count and tries < count * 400:
        tries += 1
        nu = rand_strict(r, 1, N, rng)
        if len(nu) != r or nu[-1] < 1:
            continue
        S = sum(nu)
        # lam: componentwise <= nu, r or r-1 parts
        lam = sorted([rng.randint(0, nu[i]) for i in range(r)], reverse=True)
        lam = [x for x in lam if x > 0]
        a = sum(lam)
        b = S - a
        if b < 1 or a < 1:
            continue
        # mu: componentwise <= nu, sum exactly b
        mu = [0] * r
        rem = b
        for i in range(r):
            hi = min(nu[i], rem, mu[i - 1] if i else nu[0])
            if hi <= 0:
                break
            lo = max(0, rem - sum(nu[i + 1:]))
            if lo > hi:
                break
            mu[i] = rng.randint(lo, hi)
            rem -= mu[i]
        if rem != 0:
            continue
        mu = [x for x in mu if x > 0]
        if not mu:
            continue
        if sum(lam) + sum(mu) != S:
            continue
        out.add((tuple(lam), tuple(mu), tuple(nu)))
    return sorted(out)


if __name__ == "__main__":
    r = int(sys.argv[1]); N = int(sys.argv[2]); c = int(sys.argv[3])
    sd = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    for lam, mu, nu in gen(r, N, c, sd):
        print("%s;%s;%s" % (",".join(map(str, lam)), ",".join(map(str, mu)),
                            ",".join(map(str, nu))))
