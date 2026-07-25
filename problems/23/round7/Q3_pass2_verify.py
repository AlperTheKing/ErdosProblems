"""Q3 PASS 2 -- independent re-derivation of pass-1 headline numbers.

Usage: python Q3_pass2_verify.py <step>
steps: calib, tf10, mtf, prismcheck
"""
import sys
from collections import Counter
from fractions import Fraction
from Q3_pass2_core import (g6_decode, g6_encode, bip_unweighted, bip_weighted,
                           is_triangle_free, is_maximal_triangle_free, adj_masks,
                           c5_blowup, prism, petersen, circle_graph, dist_exact,
                           dist_greedy_ub, read_g6_file, blowup_edge)


def twin_quotient(n, edges):
    """collapse false twins (identical neighbourhoods); return (sizes, quotient edges)."""
    m = adj_masks(n, edges)
    classes = {}
    for v in range(n):
        classes.setdefault(m[v], []).append(v)
    keys = sorted(classes, key=lambda k: (-len(classes[k]), k))
    idx = {k: i for i, k in enumerate(keys)}
    sizes = [len(classes[k]) for k in keys]
    qe = set()
    for u, v in edges:
        a, b = idx[m[u]], idx[m[v]]
        if a != b:
            qe.add((min(a, b), max(a, b)))
    return sizes, sorted(qe)


def is_c5_blowup_shape(n, edges):
    """True iff twin-collapsing gives exactly C5 (as an unlabelled 5-cycle)."""
    sizes, qe = twin_quotient(n, edges)
    if len(sizes) != 5 or len(qe) != 5:
        return False, sizes, qe
    deg = Counter()
    for a, b in qe:
        deg[a] += 1
        deg[b] += 1
    return (all(deg[i] == 2 for i in range(5))), sizes, qe


def calib():
    print("=== calibration ===")
    for name, (n, e) in [("C5", c5_blowup([1] * 5)), ("C5[2]", c5_blowup([2] * 5)),
                         ("C5[3]", c5_blowup([3] * 5)), ("prism", prism()),
                         ("Petersen", petersen()), ("Grotzsch", grotzsch()),
                         ("Gamma8/Wagner", circle_graph(8)), ("Gamma11", circle_graph(11)),
                         ("Gamma14", circle_graph(14))]:
        tf = is_triangle_free(n, e)
        b = bip_unweighted(n, e)
        d = dist_exact(n, e) if n <= 16 else None
        print(f"{name:16s} n={n:3d} |E|={len(e):3d} tf={tf} bip={b} "
              f"psi={Fraction(b, n * n)} d={d}"
              + (f" d/N^2={Fraction(d, n*n)}" if d is not None else ""))


def grotzsch():
    # Mycielskian of C5
    n, e = c5_blowup([1] * 5)   # C5 on 0..4
    edges = list(e)
    for j in range(5):          # u_j = 5+j copies of j
        for (a, b) in e:
            if a == j:
                edges.append((5 + j, b))
            if b == j:
                edges.append((5 + j, a))
        edges.append((10, 5 + j))
    edges = sorted({(min(a, b), max(a, b)) for a, b in edges})
    return 11, edges


def tf10():
    print("=== all triangle-free graphs on 10 vertices ===")
    gs = read_g6_file("tf10.g6")
    print("count", len(gs))
    hist = Counter()
    best = []
    for n, e in gs:
        assert n == 10
        assert is_triangle_free(n, e), "corpus contains a triangle!"
        b = bip_unweighted(n, e)
        hist[b] += 1
        if b >= 4:
            best.append((b, n, e))
    print("bip histogram", dict(sorted(hist.items())))
    for b, n, e in best:
        ok, sizes, qe = is_c5_blowup_shape(n, e)
        print(f"  bip={b} |E|={len(e)} g6={g6_encode(n,e)} c5blowup={ok} "
              f"twinsizes={sizes} quotient={qe} dist={dist_exact(n,e)}")


def mtf():
    for N in range(9, 16):
        gs = read_g6_file(f"mtf{N}.g6")
        hist = Counter()
        top = []
        for n, e in gs:
            assert n == N
            assert is_maximal_triangle_free(n, e), f"not MTF: {g6_encode(n,e)}"
            b = bip_unweighted(n, e)
            hist[b] += 1
            top.append((b, n, e))
        mx = max(h for h in hist)
        top = [t for t in top if t[0] >= mx - 1]
        print(f"--- N={N} MTF count={len(gs)} hist={dict(sorted(hist.items()))} "
              f"max={mx}  N^2/25={Fraction(N*N,25)}")
        for b, n, e in sorted(top, reverse=True):
            ok, sizes, qe = is_c5_blowup_shape(n, e)
            d = dist_exact(n, e)
            print(f"    bip={b} |E|={len(e)} g6={g6_encode(n,e)} c5blowup={ok} "
                  f"twins={sizes} d={d} d/N^2={Fraction(d,n*n)} "
                  f"psi={Fraction(b,n*n)} R={Fraction(25*d, n*n-25*b) if n*n-25*b>0 else 'inf'}")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "calib"
    {"calib": calib, "tf10": tf10, "mtf": mtf}[step]()
