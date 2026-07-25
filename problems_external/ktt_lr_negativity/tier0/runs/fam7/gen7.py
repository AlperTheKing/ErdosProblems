#!/usr/bin/env python3
"""Family 7 generator: hive triples (lam;mu;nu) batch lines for tier0_screen.
Interior-point hunt: we want h*_d > 0 at minimal c, so we sweep small |nu|
first and grow.  r = len(nu).
"""
import random, argparse


def parts_at_most(N, k):
    out = []

    def rec(rem, maxp, cur):
        if rem == 0:
            out.append(tuple(cur))
            return
        if len(cur) == k:
            return
        for p in range(min(rem, maxp), 0, -1):
            if p * (k - len(cur)) < rem:
                break
            cur.append(p)
            rec(rem - p, p, cur)
            cur.pop()

    rec(N, N, [])
    return out


def contains(nu, lam):
    for i, x in enumerate(lam):
        if i >= len(nu) or x > nu[i]:
            return False
    return True


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def gen(r, Nlo, Nhi, cap=10 ** 12, limit=None, seed=0, seen=None):
    rng = random.Random(seed)
    if seen is None:
        seen = set()
    lines = []
    for N in range(Nlo, Nhi + 1):
        nus = [p for p in parts_at_most(N, r) if len(p) == r]
        for nu in nus:
            for a in range(0, N // 2 + 1):
                b = N - a
                for lam in parts_at_most(a, r):
                    if not contains(nu, lam):
                        continue
                    for mu in parts_at_most(b, r):
                        if not contains(nu, mu):
                            continue
                        key = (lam, mu, nu)
                        if key in seen:
                            continue
                        seen.add(key)
                        lines.append("%s;%s;%s;%d" % (fmt(lam), fmt(mu), fmt(nu), cap))
    if limit is not None and len(lines) > limit:
        rng.shuffle(lines)
        lines = lines[:limit]
    return lines


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--nlo", type=int, required=True)
    ap.add_argument("--nhi", type=int, required=True)
    ap.add_argument("--cap", type=int, default=10 ** 12)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lines = gen(a.r, a.nlo, a.nhi, a.cap, a.limit, a.seed)
    with open(a.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(len(lines))
