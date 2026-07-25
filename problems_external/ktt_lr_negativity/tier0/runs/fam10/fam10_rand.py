#!/usr/bin/env python3
"""fam10_rand.py -- random pool for r >= 6 (the exhaustive pool is too large).
Uniform-ish random (lam,mu,nu) with nu having exactly r parts, |lam|+|mu|=|nu|,
lam,mu contained in nu.  Keeps c >= 2 via one exact engine-A call.
SAMPLED, not exhaustive -- stated as such in the manifest.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fam10_pool import engine_batch, fmt, CAP    # noqa: E402


def rand_partition(N, k, rng):
    """random partition of N into exactly k positive parts (rejection on comps)."""
    if k < 1 or N < k:
        return None
    for _ in range(200):
        cuts = sorted(rng.sample(range(1, N), k - 1)) if k > 1 else []
        parts = []
        prev = 0
        for c in cuts + [N]:
            parts.append(c - prev)
            prev = c
        parts.sort(reverse=True)
        return tuple(parts)
    return None


def rand_sub(nu, a, rng):
    """random partition of a with <= len(nu) parts, contained in nu, or None."""
    n = len(nu)
    for _ in range(60):
        k = rng.randint(1, n)
        p = rand_partition(a, k, rng)
        if p is None or len(p) > n:
            continue
        if all(p[i] <= nu[i] for i in range(len(p))):
            return p
    return None


def main(argv):
    r = int(argv[1]); Nlo = int(argv[2]); Nhi = int(argv[3])
    target = int(argv[4]); dst = argv[5]
    seed = int(argv[6]) if len(argv) > 6 else 20260722
    rng = random.Random(seed)
    seen = set()
    trips = []
    tries = 0
    while len(trips) < target and tries < target * 400:
        tries += 1
        N = rng.randint(Nlo, Nhi)
        nu = rand_partition(N, r, rng)
        if nu is None or len(nu) != r:
            continue
        a = rng.randint(1, N - 1)
        lam = rand_sub(nu, a, rng)
        mu = rand_sub(nu, N - a, rng)
        if lam is None or mu is None:
            continue
        key = (lam, mu, nu)
        if key in seen:
            continue
        seen.add(key)
        trips.append(key)
    print("generated %d (tries %d)" % (len(trips), tries), flush=True)
    idx = 0
    keep = empty = one = 0
    with open(dst, "w", encoding="utf-8") as f:
        CH = 100000
        for s in range(0, len(trips), CH):
            chunk = trips[s:s + CH]
            out = engine_batch(["%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), CAP)
                                for (l, m, v) in chunk])
            for (l, m, v), tok in zip(chunk, out):
                try:
                    c = int(tok)
                except ValueError:
                    continue
                if c == 0:
                    empty += 1
                    continue
                if c == 1:
                    one += 1
                    continue
                f.write(json.dumps({"idx": idx, "lam": list(l), "mu": list(m),
                                    "nu": list(v), "c": c}) + "\n")
                idx += 1
                keep += 1
    print(json.dumps({"gen": len(trips), "keep": keep, "empty": empty,
                      "c_eq_1": one}), flush=True)


if __name__ == "__main__":
    main(sys.argv)
