#!/usr/bin/env python3
"""Wave 3: local perturbation of the h*_1 == 0 near-misses.

A record with h*_1 = 0 has c = d+1 lattice points and (by the exact
reformulation h*_d - h*_1 = (d+1) - B) exactly B = d+1 of them on the
relative boundary.  It becomes a TIER0 hit the moment ONE boundary lattice
point is traded for an interior one.  This script emits every triple within
L1-distance 1..2 of such a seed (single part +-1 in lam / mu / nu, keeping
|lam| + |mu| = |nu| and all three weakly decreasing and nonnegative), plus
the 2- and 3-fold "shift" variants nu + (k,k,...,k)/ lam + (k,...).
"""
import argparse, glob, json, os, sys


def ok_part(p):
    p = [x for x in p if x > 0]
    return all(p[i] >= p[i + 1] for i in range(len(p) - 1)) and len(p) > 0


def norm(p):
    return tuple(x for x in p if x > 0)


def bump(p, i, delta, rmax):
    q = list(p) + [0] * (rmax - len(p))
    if i >= len(q):
        return None
    q[i] += delta
    if q[i] < 0:
        return None
    q = [x for x in q if x > 0]
    if not q or any(q[j] < q[j + 1] for j in range(len(q) - 1)):
        return None
    return tuple(q)


def neighbours(lam, mu, nu):
    r = len(nu)
    out = set()
    # move mass: +1 in one part of lam (or mu) and +1 in one part of nu
    for (which, src) in (("lam", lam), ("mu", mu)):
        for i in range(r):
            b = bump(src, i, 1, r)
            if b is None:
                continue
            for j in range(r):
                nb = bump(nu, j, 1, r)
                if nb is None or len(nb) != r:
                    continue
                if which == "lam":
                    out.add((b, tuple(mu), nb))
                else:
                    out.add((tuple(lam), b, nb))
            # and -1 elsewhere in the same partition (weight preserving)
            for j in range(r):
                if j == i:
                    continue
                b2 = bump(b, j, -1, r)
                if b2 is None:
                    continue
                if which == "lam":
                    out.add((b2, tuple(mu), tuple(nu)))
                else:
                    out.add((tuple(lam), b2, tuple(nu)))
    # weight-preserving moves inside nu
    for i in range(r):
        a = bump(nu, i, 1, r)
        if a is None:
            continue
        for j in range(r):
            if j == i:
                continue
            b = bump(a, j, -1, r)
            if b is None or len(b) != r:
                continue
            out.add((tuple(lam), tuple(mu), b))
    # uniform shifts of nu together with lam or mu (k = 1,2)
    for k in (1, 2):
        shift = tuple(x + k for x in nu)
        for (which, src) in (("lam", lam), ("mu", mu)):
            s2 = tuple(x + k for x in list(src) + [0] * (r - len(src)))
            s2 = tuple(x for x in s2 if x > 0)
            if which == "lam":
                if sum(s2) + sum(mu) == sum(shift):
                    out.add((s2, tuple(mu), shift))
            else:
                if sum(lam) + sum(s2) == sum(shift):
                    out.add((tuple(lam), s2, shift))
    good = []
    for (l, m, n) in out:
        if not (l and m and n):
            continue
        if sum(l) + sum(m) != sum(n):
            continue
        if len(n) != r:
            continue
        if len(l) > r or len(m) > r:
            continue
        # necessary for c>0 (theorem, not an oracle)
        if any(l[i] > n[i] for i in range(len(l))):
            continue
        if any(m[i] > n[i] for i in range(len(m))):
            continue
        good.append((l, m, n))
    return good


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--dmin", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=1)
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(__file__))
    seeds = []
    for dd in a.dirs:
        for fn in sorted(glob.glob(os.path.join(base, dd, "*.jsonl"))):
            for line in open(fn):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("status") != "OK":
                    continue
                if r.get("hstar_1") == 0 and r.get("d", 0) >= a.dmin:
                    seeds.append((tuple(r["lam"]), tuple(r["mu"]),
                                  tuple(r["nu"])))
    seeds = list(dict.fromkeys(seeds))
    frontier = set(seeds)
    allt = set(seeds)
    for _ in range(a.rounds):
        nxt = set()
        for s in frontier:
            for t in neighbours(*s):
                if t not in allt:
                    nxt.add(t)
        allt |= nxt
        frontier = nxt
    with open(a.out, "w") as f:
        for (l, m, n) in sorted(allt):
            f.write("%s;%s;%s\n" % (",".join(map(str, l)),
                                    ",".join(map(str, m)),
                                    ",".join(map(str, n))))
    sys.stderr.write("seeds=%d emitted=%d\n" % (len(seeds), len(allt)))


if __name__ == "__main__":
    main()
