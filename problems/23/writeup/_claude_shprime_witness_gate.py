"""Claude exact gate: (SH') peel invariant m_out <= r^2/25 + d/2 on witnesses
with NONEMPTY R carrying bad edges (all prior cactus-gate instances had m_out=0).

Witnesses (built from the N=10 protected atom, m=2, maxcut=10):
  W1 atom + disjoint C5:        N=15, k=1, m_out=1, d=0  -> SH' TIGHT (1 <= 1).
  W2 atom + blue-bridged C5:    N=15, k=1, m_out=1, d=1  -> 1 <= 3/2.
  W3 two bridged atoms + bridged C5: N=25, k=2, m_out=1, d=2 (one inter-atom
     bridge + one atom-C5 bridge; both count in delta_B(U,R)? NO - the
     inter-atom bridge is inside U. d counts U<->R only = 1).  1 <= 25/25+1/2.
  W4 atom + C5 bridged TWICE (two blue bridges to different atoms... here to
     the same atom from different C5 vertices): d=2, m_out=1 -> 1 <= 1+1.

Exact checks per witness:
  X0 triangle-free; cut is TRUE max (decomposition bound: components/bridges);
  X1 cell axioms for the k declared cells; delta_M(U)=0 (no bad U<->R edge);
  X2 m_out, d exact; SH' inequality with Fractions;
  X3 exchange mechanics: beta(G[R]) by full enumeration; for the optimal
     coloring psi of R: b(psi) + b(psi_bar) == d over boundary edges; the
     better orientation has boundary damage <= d/2; modified-cut bad count
     >= current bad count (maximality comparison, verifying Lemma 1's chain
     on the instance);
  X4 Lemma 2 arithmetic: eta >= 2k - d/2 given (N^2-r^2)/25 >= 4k; k-d <= eta/2.
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction
from itertools import combinations

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_slack_cage_unit_atom_boundary_dump import build_base_case

BASE = build_base_case()
BN = BASE["n"]
BASE_EDGES = [tuple(sorted(e)) for e in BASE["edges"]]
BASE_SIDE = list(BASE["side"])

# C5 on 5 vertices with the standard near-balanced cut (sides 0,1,0,1,0):
# edges (0,1),(1,2),(2,3),(3,4),(4,0); bad edge = (4,0) (sides 0,0).
C5_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
C5_SIDE = [0, 1, 0, 1, 0]


def maxcut_enum(n, edges):
    best = 0
    for mask in range(1 << (n - 1)):  # fix vertex n-1 on side 0
        cut = 0
        for u, v in edges:
            su = (mask >> u) & 1 if u < n - 1 else 0
            sv = (mask >> v) & 1 if v < n - 1 else 0
            if su != sv:
                cut += 1
        best = max(best, cut)
    return best


ATOM_MAXCUT = maxcut_enum(BN, BASE_EDGES)
C5_MAXCUT = maxcut_enum(5, C5_EDGES)
assert ATOM_MAXCUT == 10 and C5_MAXCUT == 4


def build(n_atoms, atom_bridges, c5_links):
    """n_atoms disjoint atom copies; atom_bridges = list of (copyA, vA, copyB, vB)
    blue inter-atom bridges; c5_links = list of (copy, atom_vertex, c5_vertex)
    blue bridges from an atom to ONE appended C5. Returns instance dict."""
    edges = []
    side = []
    for i in range(n_atoms):
        off = i * BN
        edges.extend((u + off, v + off) for u, v in BASE_EDGES)
        side.extend(BASE_SIDE)
    c5_off = n_atoms * BN
    edges.extend((u + c5_off, v + c5_off) for u, v in C5_EDGES)
    side.extend(C5_SIDE)
    n = c5_off + 5
    nb_in_U = 0
    for ca, va, cb, vb in atom_bridges:
        a, b = ca * BN + va, cb * BN + vb
        assert side[a] != side[b], "inter-atom bridge must be blue"
        edges.append(tuple(sorted((a, b))))
        nb_in_U += 1
    nb_UR = 0
    for c, va, vc in c5_links:
        a, b = c * BN + va, c5_off + vc
        assert side[a] != side[b], "U-R bridge must be blue"
        edges.append(tuple(sorted((a, b))))
        nb_UR += 1
    cells = [frozenset(range(i * BN, (i + 1) * BN)) for i in range(n_atoms)]
    return dict(n=n, edges=sorted(edges), side=side, cells=cells,
                n_bridges=nb_in_U + nb_UR, R=frozenset(range(c5_off, c5_off + 5)))


def check(name, inst):
    n, edges, side, cells = inst["n"], inst["edges"], inst["side"], inst["cells"]
    R = inst["R"]
    k = len(cells)
    U = frozenset().union(*cells)
    assert U | R == frozenset(range(n)) and not (U & R)
    r = len(R)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # X0 triangle-free + true max via decomposition (edge sets of atom copies,
    # C5, and bridges partition E; each part's max attained by the given cut)
    for u, v in edges:
        assert not (adj[u] & adj[v]), f"{name}: triangle"
    bad = [e for e in edges if side[e[0]] == side[e[1]]]
    blue = [e for e in edges if side[e[0]] != side[e[1]]]
    cut_val = len(blue)
    upper = k * ATOM_MAXCUT + C5_MAXCUT + inst["n_bridges"]
    assert cut_val == upper, f"{name}: cut {cut_val} != decomposition UB {upper}"
    # X1 cell axioms + delta_M(U)=0
    for i, C in enumerate(cells):
        assert len([e for e in bad if e[0] in C and e[1] in C]) == 2
        assert not [e for e in bad if (e[0] in C) != (e[1] in C)]
    for a, b in combinations(range(k), 2):
        assert len(cells[a] & cells[b]) <= 1
    assert not [e for e in bad if (e[0] in U) != (e[1] in U)], f"{name}: bad U-R edge"
    # X2 m_out, d, SH'
    m = len(bad)
    m_out = len([e for e in bad if e[0] in R and e[1] in R])
    assert m == 2 * k + m_out
    d = len([e for e in blue if (e[0] in U) != (e[1] in U)])
    shp_rhs = Fraction(r * r, 25) + Fraction(d, 2)
    assert Fraction(m_out) <= shp_rhs, f"{name}: SH' fails {m_out} > {shp_rhs}"
    # X3 exchange mechanics: enumerate ALL optimal colorings of G[R]
    Rl = sorted(R)
    ridx = {v: i for i, v in enumerate(Rl)}
    redges = [(ridx[u], ridx[v]) for u, v in edges if u in R and v in R]
    beta_R = None
    best_masks = []
    for mask in range(1 << r):
        bad_in = sum(1 for u, v in redges if ((mask >> u) & 1) == ((mask >> v) & 1))
        if beta_R is None or bad_in < beta_R:
            beta_R, best_masks = bad_in, [mask]
        elif bad_in == beta_R:
            best_masks.append(mask)
    assert Fraction(beta_R) <= Fraction(r * r, 25), f"{name}: beta(G[R])={beta_R} > r^2/25"
    boundary = [e for e in blue if (e[0] in U) != (e[1] in U)]
    ok_exchange = False
    for mask in best_masks:
        def bcount(mm):
            c = 0
            for u, v in boundary:
                uu, vv = (u, v) if u in U else (v, u)
                sv = (mm >> ridx[vv]) & 1
                if sv == side[uu]:
                    c += 1
            return c
        b1, b2 = bcount(mask), bcount(mask ^ ((1 << r) - 1))
        assert b1 + b2 == d, f"{name}: orientation identity {b1}+{b2}!={d}"
        dmg = min(b1, b2)
        assert Fraction(dmg) <= Fraction(d, 2)
        modified_bad = len([e for e in bad if e[0] in U and e[1] in U]) + beta_R + dmg
        assert modified_bad >= m, f"{name}: maximality violated by exchange!"
        ok_exchange = True
    assert ok_exchange
    # X4 Lemma 2 arithmetic on the instance
    eta = Fraction(n * n, 25) - m
    if Fraction(n * n - r * r, 25) >= 4 * k:
        assert eta >= 2 * k - Fraction(d, 2), f"{name}: Lemma2 chain fails"
        assert Fraction(k - d) <= eta / 2, f"{name}: k-d > eta/2"
        l2 = "holds"
    else:
        l2 = "packing-premise-absent"
    print(
        f"SHPRIME {name}: n={n} k={k} r={r} m={m} m_out={m_out} d={d} "
        f"beta_R={beta_R} SH'={m_out}<={shp_rhs} eta={eta} lemma2={l2} "
        f"opt_colorings={len(best_masks)}"
    )


def main():
    # W1: disjoint C5 (d=0, SH' tight)
    check("W1-atom+C5-disjoint", build(1, [], []))
    # W2: one blue bridge atom.v0(side0) -- C5.v1(side1)
    check("W2-atom+C5-bridge1", build(1, [], [(0, 0, 1)]))
    # W3: two atoms bridged (0.v0 -- 1.v5), C5 bridged to atom0 (0.v5 -- C5.v0)
    check("W3-2atoms+C5", build(2, [(0, 0, 1, 5)], [(0, 5, 0)]))
    # W4: C5 double-bridged to atom (0.v0 -- C5.v1, 0.v5 -- C5.v0): d=2
    check("W4-atom+C5-bridge2", build(1, [], [(0, 0, 1), (0, 5, 0)]))
    print("PASS SH' witness gate: invariant + exchange mechanics exact on all witnesses")


if __name__ == "__main__":
    main()
