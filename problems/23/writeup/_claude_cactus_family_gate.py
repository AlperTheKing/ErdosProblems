"""Claude exact gate: cactus-packing lemma S1-S3 on generated cactus families.

Families:
  (a) k=1..8 vertex-disjoint blue-bridged gluings of the N=10 protected atom
      (Codex builder build_glued_protected_cells);
  (b) n=19 single-vertex contact pair (tight case of S3);
  (c) k=3 triple chain glued at two distinct vertices (u=28, c=1, tight);
  (d) k=3 mixed: contact pair + bridged single (u=29, c=2, tight).

Checks per instance (all exact, Fraction arithmetic):
  T0 triangle-free;
  T1 cells: |C_a|>=10, e_M(C_a)=2, delta_M(C_a)=0, pairwise |C_a cap C_b|<=1;
  T2 identity m = 2k + m_out (S1);
  T3 pair-disjointness: sum C(|C_a|,2) <= C(u,2) (S2);
  T4 contact graph is a forest with c components and u >= 9k + c (S3);
  T5 algebra (9k+1)^2 - 100k = (k-1)(81k-1) >= 0;
  T6 eta = N^2/25 - m; gross k <= eta and half-bank k <= eta/2;
  T7 the given cut is a TRUE max cut: exact per-copy decomposition bound
     maxcut(G) <= sum_copies maxcut(atom) + #bridges, attained by the given cut
     (single-atom max cut certified by full 2^10 enumeration).
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction
from itertools import combinations

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_slack_cage_unit_atom_boundary_dump import build_base_case, norm_edge
    from _codex_slack_cage_multi_protected_cell_stress import build_glued_protected_cells

BASE = build_base_case()
BN = BASE["n"]
BASE_EDGES = [tuple(sorted(e)) for e in BASE["edges"]]
BASE_SIDE = list(BASE["side"])


def atom_maxcut_exact():
    """Full enumeration of all 2^10 sides of the base atom."""
    best = 0
    for mask in range(1 << BN):
        cut = 0
        for u, v in BASE_EDGES:
            if ((mask >> u) & 1) != ((mask >> v) & 1):
                cut += 1
        best = max(best, cut)
    return best


ATOM_MAXCUT = atom_maxcut_exact()
assert ATOM_MAXCUT == len(BASE_EDGES) - 2, f"atom maxcut {ATOM_MAXCUT} != e-2"


def glue_copies(identifications, n_copies):
    """Disjoint copies of the atom with vertex identifications.

    identifications: list of ((copy_i, vert_i), (copy_j, vert_j)) merged pairs.
    Returns (n, edges, side, cells, n_bridges=0)."""
    # union-find over (copy, vertex)
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in identifications:
        union(a, b)
    labels = {}
    for c in range(n_copies):
        for v in range(BN):
            r = find((c, v))
            if r not in labels:
                labels[r] = len(labels)
    n = len(labels)

    def lab(c, v):
        return labels[find((c, v))]

    edges = set()
    for c in range(n_copies):
        for u, v in BASE_EDGES:
            edges.add(tuple(sorted((lab(c, u), lab(c, v)))))
    side = [None] * n
    for c in range(n_copies):
        for v in range(BN):
            s = BASE_SIDE[v]
            w = lab(c, v)
            if side[w] is None:
                side[w] = s
            else:
                assert side[w] == s, f"inconsistent glue side at copy {c} vert {v}"
    cells = []
    for c in range(n_copies):
        cells.append(frozenset(lab(c, v) for v in range(BN)))
    return n, sorted(edges), side, cells


def parse_disjoint(k):
    """Codex builder: k disjoint copies + k-1 blue bridges."""
    n, edges, side_str = build_glued_protected_cells(k)
    side = [int(c) for c in side_str]
    cells = [frozenset(range(i * BN, (i + 1) * BN)) for i in range(k)]
    return n, edges, side, cells, k - 1


def check_instance(name, n, edges, side, cells, n_bridges):
    k = len(cells)
    edges = [tuple(sorted(e)) for e in edges]
    eset = set(edges)
    assert len(eset) == len(edges)
    # T0 triangle-free
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for u, v in edges:
        assert not (adj[u] & adj[v]), f"{name}: triangle at edge {(u,v)}"
    bad = [e for e in edges if side[e[0]] == side[e[1]]]
    blue = [e for e in edges if side[e[0]] != side[e[1]]]
    m = len(bad)
    U = frozenset().union(*cells)
    u_sz = len(U)
    # T1 cells
    for a, C in enumerate(cells):
        assert len(C) >= 10, f"{name}: cell {a} too small"
        e_in = [e for e in bad if e[0] in C and e[1] in C]
        assert len(e_in) == 2, f"{name}: cell {a} e_M={len(e_in)}"
        crossing = [e for e in bad if (e[0] in C) != (e[1] in C)]
        assert not crossing, f"{name}: cell {a} delta_M={len(crossing)}"
    for a, b in combinations(range(k), 2):
        assert len(cells[a] & cells[b]) <= 1, f"{name}: cells {a},{b} share >=2"
    # T2 identity m = 2k + m_out
    m_out = len([e for e in bad if e[0] not in U and e[1] not in U])
    # bad edges with exactly one endpoint in U are excluded by delta_M=0 checks;
    # assert the partition is exact:
    m_in = len([e for e in bad if e[0] in U and e[1] in U])
    assert m_in + m_out == m, f"{name}: bad edge crossing U boundary"
    assert m == 2 * k + m_out, f"{name}: m={m} != 2k+m_out={2*k+m_out}"
    # T3 pair-disjointness
    pair_sum = sum(len(C) * (len(C) - 1) // 2 for C in cells)
    cap = u_sz * (u_sz - 1) // 2
    assert pair_sum <= cap, f"{name}: pair sum {pair_sum} > C(u,2)={cap}"
    # T4 contact forest + u >= 9k + c
    cedges = [(a, b) for a, b in combinations(range(k), 2) if cells[a] & cells[b]]
    parent = list(range(k))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    acyclic = True
    for a, b in cedges:
        ra, rb = find(a), find(b)
        if ra == rb:
            acyclic = False
        else:
            parent[ra] = rb
    assert acyclic, f"{name}: contact graph has a cycle (not proper cactus order)"
    c_comp = len({find(a) for a in range(k)})
    assert u_sz >= 9 * k + c_comp, f"{name}: u={u_sz} < 9k+c={9*k+c_comp}"
    # T5 algebra
    assert (9 * k + 1) ** 2 - 100 * k == (k - 1) * (81 * k - 1)
    assert (k - 1) * (81 * k - 1) >= 0
    # T6 eta bounds (exact)
    eta = Fraction(n * n, 25) - m
    assert k <= eta, f"{name}: gross k={k} > eta={eta}"
    assert Fraction(k) <= eta / 2, f"{name}: half-bank k={k} > eta/2={eta/2}"
    # T7 true max cut via decomposition
    n_copy_edges = k * len(BASE_EDGES)
    assert len(edges) == n_copy_edges + n_bridges, f"{name}: edge count mismatch"
    cut_val = len(blue)
    upper = k * ATOM_MAXCUT + n_bridges
    assert cut_val == upper, f"{name}: given cut {cut_val} != decomposition bound {upper}"
    tight34 = (u_sz == 9 * k + c_comp)
    print(
        f"CACTUS-GATE {name}: n={n} k={k} u={u_sz} c={c_comp} m={m} m_out={m_out} "
        f"eta={eta} half_bank_slack={eta/2 - k} cut={cut_val}=UB tight_u9kc={tight34}"
    )


def main():
    # (a) disjoint bridged gluings k=1..8
    for k in range(1, 9):
        n, edges, side, cells, nb = parse_disjoint(k)
        check_instance(f"disjoint-k{k}", n, edges, side, cells, nb)
    # (b) n=19 contact pair: copy0 vertex0 == copy1 vertex0 (side 0 both)
    n, edges, side, cells = glue_copies([(((0, 0)), ((1, 0)))], 2)
    assert n == 19
    check_instance("contact-pair-n19", n, edges, side, cells, 0)
    # (c) triple chain: copy0.v0==copy1.v0, copy1.v1==copy2.v0 (sides 0,0)
    n, edges, side, cells = glue_copies([((0, 0), (1, 0)), ((1, 1), (2, 0))], 3)
    assert n == 28
    check_instance("triple-chain-n28", n, edges, side, cells, 0)
    # (d) mixed: contact pair (copies 0,1) + single copy 2 bridged to copy 0.
    n, edges, side, cells = glue_copies([((0, 0), (1, 0))], 3)
    assert n == 29
    # add one blue bridge: copy0 vertex 2 (side 0) -- copy2 vertex 5 (side 1)
    # labels: with no identifications touching them, recompute via glue order.
    # copy0 verts 0..9 -> labels 0..9; copy1 verts: v0 merged -> label 0, others 10..18;
    # copy2 verts 19..28.
    bridge = tuple(sorted((2, 19 + 5)))
    edges = sorted(set(edges) | {bridge})
    assert side[2] != side[19 + 5], "bridge must be blue"
    check_instance("mixed-pair+single-n29", n, edges, side, cells, 1)
    print("PASS cactus-packing S1-S3 exact on all generated families")


if __name__ == "__main__":
    main()
