#!/usr/bin/env python3
"""
fam1_perturb.py -- ladder hunter 1 (family: the verified refuter cell and its
single-box / two-box perturbations).

Base cell:  lam = (2,2,1), mu = (k,3,2,1), nu = (k+1,4,3,2,1),  k >= 4.
This cell has d = 4, c = 5, h* = (1,0,1,0,0), Sum h* = 2, h*_1 = 0.

A "box move" is one of the six size-balance-preserving elementary moves
(|lam|+|mu| = |nu| must be maintained):
    (lam +box, nu +box) | (mu +box, nu +box) | (lam +box, mu -box)
    (lam -box, nu -box) | (mu -box, nu -box) | (lam -box, mu +box)
where +box adds 1 to a part (or appends a new part 1) and -box subtracts 1
(or deletes a trailing 1), always keeping a valid partition.

Two-box perturbations = all compositions of two box moves.

Screening uses ONLY the mandated LP-free instrument lpfree_screen.py.
No dimension oracle, no simplex filter, nothing discarded for shape.
All arithmetic exact.
"""
import sys, os, json, time, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpfree_screen as L


def plus_moves(p):
    """All partitions obtained by adding one box to p (tuple)."""
    out = []
    n = len(p)
    for i in range(n):
        if i == 0 or p[i - 1] > p[i]:
            q = list(p); q[i] += 1
            out.append(tuple(q))
    out.append(tuple(list(p) + [1]))
    return out


def minus_moves(p):
    """All partitions obtained by removing one box from p (tuple)."""
    out = []
    n = len(p)
    for i in range(n):
        below = p[i + 1] if i + 1 < n else 0
        v = p[i] - 1
        if v < below:
            continue
        if v == 0:
            if i == n - 1:
                out.append(tuple(p[:i]))
            continue
        q = list(p); q[i] = v
        out.append(tuple(q))
    return [q for q in out if len(q) > 0]


def box_moves(tri, maxlen_nu=6, maxlen_lm=6):
    """All triples one box move away from tri = (lam, mu, nu)."""
    lam, mu, nu = tri
    out = set()
    for L2 in plus_moves(lam):
        for N2 in plus_moves(nu):
            out.add((L2, mu, N2))
    for M2 in plus_moves(mu):
        for N2 in plus_moves(nu):
            out.add((lam, M2, N2))
    for L2 in plus_moves(lam):
        for M2 in minus_moves(mu):
            out.add((L2, M2, nu))
    for L2 in minus_moves(lam):
        for N2 in minus_moves(nu):
            out.add((L2, mu, N2))
    for M2 in minus_moves(mu):
        for N2 in minus_moves(nu):
            out.add((lam, M2, N2))
    for L2 in minus_moves(lam):
        for M2 in plus_moves(mu):
            out.add((L2, M2, nu))
    res = []
    for (a, b, c) in out:
        if len(c) > maxlen_nu or len(a) > maxlen_lm or len(b) > maxlen_lm:
            continue
        if sum(a) + sum(b) != sum(c):
            continue
        if len(a) > len(c) or len(b) > len(c):
            continue          # LR coeff is 0 unless both fit in r rows
        res.append((a, b, c))
    return res


def canon(tri):
    lam, mu, nu = tri
    a, b = (tuple(lam), tuple(mu))
    if b < a:
        a, b = b, a
    return (a, b, tuple(nu))


def base(k):
    return ((2, 2, 1), (k, 3, 2, 1), (k + 1, 4, 3, 2, 1))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--kmin", type=int, default=4)
    ap.add_argument("--kmax", type=int, default=40)
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk", type=int, default=400)
    ap.add_argument("--cap", type=int, default=10 ** 12)
    ap.add_argument("--maxlen-nu", type=int, default=6)
    ap.add_argument("--seed-file", default=None,
                    help="optional JSON list of [lam,mu,nu] to use as seeds "
                         "instead of the base cells")
    args = ap.parse_args()

    seeds = []
    if args.seed_file:
        for t in json.load(open(args.seed_file)):
            seeds.append((tuple(t[0]), tuple(t[1]), tuple(t[2])))
    else:
        seeds = [base(k) for k in range(args.kmin, args.kmax + 1)]

    seen = set()
    todo = []
    for s in seeds:
        c = canon(s)
        if c not in seen:
            seen.add(c); todo.append(s)
    frontier = list(todo)
    for _ in range(args.depth):
        nxt = []
        for t in frontier:
            for u in box_moves(t, maxlen_nu=args.maxlen_nu):
                c = canon(u)
                if c not in seen:
                    seen.add(c); nxt.append(u); todo.append(u)
        frontier = nxt
        sys.stderr.write("depth layer size %d, total %d\n" % (len(nxt), len(todo)))
        sys.stderr.flush()

    sys.stderr.write("total triples: %d\n" % len(todo))
    t0 = time.time()
    nneg = 0
    with open(args.out, "w") as fh:
        for i in range(0, len(todo), args.chunk):
            batch = todo[i:i + args.chunk]
            recs = L.screen_triples(batch, cap=args.cap)
            for r in recs:
                if r.get("neg"):
                    nneg += 1
                fh.write(json.dumps(r) + "\n")
            fh.flush()
            sys.stderr.write("  %d/%d  %.1fs  neg=%d\n"
                             % (min(i + args.chunk, len(todo)), len(todo),
                                time.time() - t0, nneg))
            sys.stderr.flush()
    sys.stderr.write("DONE %d triples, %d NEG, %.1fs\n"
                     % (len(todo), nneg, time.time() - t0))


if __name__ == "__main__":
    main()
