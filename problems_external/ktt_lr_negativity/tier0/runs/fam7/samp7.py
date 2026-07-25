#!/usr/bin/env python3
"""Family-7 random sampler for larger |nu| (r parts), with the necessary
containment condition lam,mu <= nu componentwise.  Sampling only; every
record it produces is decided by the exact tier0 screen.
"""
import random, argparse


def rand_partition_le(bound, total, rng, tries=200):
    """random weakly-decreasing tuple p with 0<=p_i<=bound_i, sum p = total."""
    r = len(bound)
    for _ in range(tries):
        # random composition then sort desc, then clip to bound and repair
        p = [0] * r
        rem = total
        idx = list(range(r))
        for i in idx:
            hi = min(bound[i], rem)
            if i > 0:
                hi = min(hi, p[i - 1])
            lo = 0
            need = rem - sum(min(bound[j], hi) for j in range(i + 1, r))
            lo = max(0, need)
            if lo > hi:
                break
            p[i] = rng.randint(lo, hi)
            rem -= p[i]
        else:
            if rem == 0:
                return tuple(x for x in p if x > 0)
    return None


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--nlo", type=int, required=True)
    ap.add_argument("--nhi", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--cap", type=int, default=10 ** 12)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    seen = set()
    lines = []
    guard = 0
    while len(lines) < a.count and guard < a.count * 60:
        guard += 1
        N = rng.randint(a.nlo, a.nhi)
        # random nu: exactly r positive parts summing to N
        if N < a.r:
            continue
        nu = rand_partition_le([N] * a.r, N, rng)
        if nu is None or len(nu) != a.r:
            continue
        s = rng.randint(0, N)
        lam = rand_partition_le(list(nu), s, rng)
        if lam is None:
            continue
        mu = rand_partition_le(list(nu), N - s, rng)
        if mu is None:
            continue
        key = (lam, mu, nu)
        if key in seen:
            continue
        seen.add(key)
        lines.append("%s;%s;%s;%d" % (fmt(lam), fmt(mu), fmt(nu), a.cap))
    with open(a.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(len(lines))


if __name__ == "__main__":
    main()
