"""PENTAGON LEMMA -- a complete, exact proof of the arc-cut conjecture for "pentagonal" measures.

LEMMA.  Let mu be a probability measure on R/Z and suppose supp(mu) can be cut into five
cyclically consecutive blocks B_1,...,B_5 (arcs, possibly empty) such that for every i the set
B_i u B_{i+1} contains NO edge (i.e. all its points are pairwise at distance <= 1/3).  Put
q_i = mu(B_i).  Then, with S_i := B_i u B_{i+1} an arc cut,

        ARCBOUND(mu)  <=  min_i value(S_i)  =  min_i e(B_{i+2}, B_{i+4})
                      <=  min_i q_{i+2} q_{i+4}
                      <=  ( prod_i q_i )^{2/5}   (AM-GM over the five products)
                      <=  ( 5^{-5} )^{2/5}  =  1/25 ,

with equality throughout iff q_i = 1/5 for all i and every distance-2 pair of blocks is
completely joined -- i.e. iff mu is a balanced blow-up of C5.

PROOF.  value(S_i) = e(S_i) + e(S_i^c).  e(S_i) = 0 by hypothesis.  S_i^c = B_{i+2} u B_{i+3} u
B_{i+4}, and inside it the pairs (B_{i+2},B_{i+3}) and (B_{i+3},B_{i+4}) are consecutive, hence
edge-free, and each block is edge-free; so e(S_i^c) = e(B_{i+2},B_{i+4}) <= q_{i+2} q_{i+4}.
The five numbers q_{i+2} q_{i+4}, i in Z_5, have product (prod q_i)^2, so their minimum is at
most (prod q_i)^{2/5}, and prod q_i <= 5^{-5} by AM-GM.  []

This module verifies the hypothesis and the whole chain exactly on every witness.
"""
from fractions import Fraction as F
from itertools import combinations
from P1_engine import Meas, gamma, WITNESSES, TARGET


def blocks_ok(mu, cuts):
    """cuts = sorted 5 indices t_0<...<t_4 in 0..n-1; block i = atoms[t_i .. t_{i+1}-1] cyclically.
    Returns list of blocks if every union of two consecutive blocks is edge-free, else None."""
    n = mu.n
    blocks = []
    for i in range(5):
        a, b = cuts[i], cuts[(i + 1) % 5]
        idx, k = [], a
        while k != b:
            idx.append(k)
            k = (k + 1) % n
        blocks.append(idx)
    for i in range(5):
        u = blocks[i] + blocks[(i + 1) % 5]
        for p, q in combinations(u, 2):
            if mu.adj[p][q]:
                return None
    return blocks


def pentagon_bound(mu):
    """search all 5-block cuts; return (best exact bound, blocks, q) or None if not pentagonal."""
    n = mu.n
    if n < 1:
        return None
    best = None
    for cuts in combinations(range(n), min(5, n)):
        cuts = list(cuts) + [cuts[-1]] * (5 - len(cuts))    # pad if n < 5 (empty blocks)
        cuts = sorted(set(cuts))
        while len(cuts) < 5:                                # duplicate cut => empty block
            cuts.append(cuts[-1])
        cuts = sorted(cuts)
        bl = blocks_ok(mu, cuts)
        if bl is None:
            continue
        q = [sum(mu.wt[k] for k in b) for b in bl]
        vals = []
        for i in range(5):
            e = sum(mu.wt[p] * mu.wt[r] for p in bl[(i + 2) % 5] for r in bl[(i + 4) % 5]
                    if mu.adj[p][r])
            vals.append(e)
        v = min(vals)
        if best is None or v < best[0]:
            best = (v, bl, q, vals)
    return best


def is_pentagonal(mu):
    return pentagon_bound(mu) is not None


if __name__ == '__main__':
    rows = [(name, gamma(m, w)) for name, m, w in WITNESSES]
    rows.append(("CE Wagner on G20 (item-7 killer)",
                 Meas([F(k, 20) for k in (0, 1, 6, 7, 12, 13, 14, 19)], [F(1, 8)] * 8)))
    rows.append(("CE Wagner equally spaced G8", gamma(8, [1] * 8)))
    rows.append(("C5 blow-up 5x2 (G10 pairs)", gamma(10, [1, 1, 0, 1, 1, 0, 1, 1, 0, 0])))
    print("PENTAGON LEMMA on the witnesses  (bound = min_i e(B_{i+2},B_{i+4}) <= 1/25 when it applies)\n")
    for tag, mu in rows:
        pb = pentagon_bound(mu)
        arc = mu.arcbound()
        if pb is None:
            print(f"{tag:32s} NOT pentagonal            ARCBOUND={float(arc):.6f}  "
                  f"A={float(mu.A):.6f}")
        else:
            v, bl, q, vals = pb
            prod = F(1)
            for qq in q:
                prod *= qq
            ok = v <= TARGET
            print(f"{tag:32s} pentagonal q={[str(x) for x in q]}")
            print(f"{'':32s}   bound={v}={float(v):.6f}  prod(q)={float(prod):.3e} "
                  f"<= 5^-5={float(F(1,5)**5):.3e}: {prod <= F(1,5)**5}   ARCBOUND={float(arc):.6f}"
                  f"   {'OK <=1/25' if ok else '*** > 1/25 ***'}")
            assert v >= arc, "pentagon bound is not an upper bound!"
            assert v <= TARGET, "pentagon bound exceeds 1/25 -- lemma is wrong!"
