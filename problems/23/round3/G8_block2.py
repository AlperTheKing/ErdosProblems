"""G8: shrink the candidate cut family for a geometric-mean certificate on And(3)
by intersecting active cut sets over MANY exact maximisers.

A maximiser of psi is produced by any induced subgraph W with a surjective
homomorphism f: H[W] -> C5 and any weight vector x supported on W with
x(f^{-1}(i)) = 1/5 for every i (then psi(x) <= min_i (1/5)(1/5) = 1/25, and >= 1/25
holds automatically whenever the value is attained -- verified exactly below).
Every cut in the support of a geometric-mean certificate must be ACTIVE
(value exactly 1/25) at every such point.
"""
import sys, itertools
from fractions import Fraction
from G8_graphs import andrasfai

C5adj = [[abs(i - j) % 5 in (1, 4) for j in range(5)] for i in range(5)]


def all_cuts(n, edges):
    out = []
    for mask in range(1 << (n - 1)):
        side = [0] * n
        for v in range(1, n):
            side[v] = (mask >> (v - 1)) & 1
        out.append((mask, [(u, v) for (u, v) in edges if side[u] == side[v]]))
    return out


def psi_exact(cuts, x):
    best = None
    for _, mono in cuts:
        s = sum(x[u] * x[v] for (u, v) in mono)
        if best is None or s < best:
            best = s
    return best


def active(cuts, x, val):
    return set(mask for mask, mono in cuts
               if sum(x[u] * x[v] for (u, v) in mono) == val)


def maximiser_points(n, edges, cuts):
    """all surjective homs W -> C5 for induced W, with several weight splittings."""
    adj = [[False] * n for _ in range(n)]
    for (u, v) in edges:
        adj[u][v] = adj[v][u] = True
    pts = []
    for W in range(1, 1 << n):
        Wl = [v for v in range(n) if (W >> v) & 1]
        if len(Wl) < 5:
            continue
        sub = [(u, v) for (u, v) in edges if ((W >> u) & 1) and ((W >> v) & 1)]
        # all homs W -> C5
        for assign in itertools.product(range(5), repeat=len(Wl)):
            f = dict(zip(Wl, assign))
            if len(set(assign)) != 5:
                continue
            if any(not C5adj[f[u]][f[v]] for (u, v) in sub):
                continue
            classes = [[v for v in Wl if f[v] == i] for i in range(5)]
            # splittings: uniform inside each class, and all-mass-on-one-vertex
            splits = [tuple(Fraction(1, 5 * len(c)) for _ in c) for c in classes]
            x = [Fraction(0)] * n
            for c, sp in zip(classes, splits):
                for v, s in zip(c, sp):
                    x[v] = s
            pts.append(tuple(x))
            for choice in itertools.product(*[range(len(c)) for c in classes]):
                x = [Fraction(0)] * n
                for c, j in zip(classes, choice):
                    x[c[j]] = Fraction(1, 5)
                pts.append(tuple(x))
    return sorted(set(pts))


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    n, conn, adj, edges = andrasfai(k)
    cuts = all_cuts(n, edges)
    pts = maximiser_points(n, edges, cuts)
    target = Fraction(1, 25)
    good = [x for x in pts if psi_exact(cuts, x) == target]
    print(f"And({k}) n={n}: {len(pts)} candidate C5-blow-up points, "
          f"{len(good)} of them have psi EXACTLY 1/25")
    inter = None
    for x in good:
        a = active(cuts, x, target)
        inter = a if inter is None else (inter & a)
    print(f"intersection of active cut sets over all {len(good)} exact maximisers: {len(inter)}")
    for mask in sorted(inter)[:10]:
        side = [0] * n
        for v in range(1, n):
            side[v] = (mask >> (v - 1)) & 1
        mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
        print(f"   cut {''.join(map(str,side))} |mono|={len(mono)} mono={mono}")
    if not inter:
        print("=> BLOCKED: no cut is active at every maximiser, so NO fixed distribution w")
        print("   over cuts can satisfy  psi(x) <= prod_j q_{S_j}(x)^{w_j} <= 1/25.")
