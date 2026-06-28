"""Exact audit of GPT-Pro's pinned Wagner counterexample.

Target: falsify the broad CONSTANT-LOAD-SELFCAP / COMPONENT-BRIDGE lemmas:

  proper positive K/omega component C, T constant on C => lambda <= |C|
  and/or induced cut on G[C] is a maxcut.

This does NOT falsify the narrower saturated dangerous case T|C == N.
"""

from fractions import Fraction as F
from itertools import product

from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side


def build():
    # C vertices 0..7; anchors 8,9; for each i in C add path vertices.
    n = 26
    E = []
    # 8-cycle cut edges.
    for i in range(8):
        E.append((i, (i + 1) % 8))
    # Opposite matching bad edges in the chosen cut.
    for e in [(0, 4), (1, 5), (2, 6), (3, 7)]:
        E.append(e)
    # Anchor edge.
    E.append((8, 9))
    # Pins: even i attach to anchor 8; odd i attach to anchor 9.
    nextv = 10
    paths = []
    for i in range(8):
        p, q = nextv, nextv + 1
        nextv += 2
        a = 8 if i % 2 == 0 else 9
        E += [(i, p), (p, q), (q, a)]
        paths.append((i, p, q, a))
    assert nextv == n
    # Chosen side: parity on C, anchors opposite their pinned parity, paths alternating.
    side = [None] * n
    for i in range(8):
        side[i] = i % 2
    side[8] = 1  # opposite even C vertices
    side[9] = 0  # opposite odd C vertices
    for i, p, q, a in paths:
        side[p] = 1 - side[i]
        side[q] = side[i]
        assert side[a] == 1 - side[q]
    return n, E, side


def adj_from(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_triangle_free(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if adj[u] & adj[v]:
                return False
    return True


def cut_value(E, side):
    return sum(1 for u, v in E if side[u] != side[v])


def reduced_maxcut():
    """Exact maxcut by compressing each length-3 pin path.

    Terminals are C vertices 0..7 and anchors 8,9. Each pin contributes
    2 + [endpoint and anchor have opposite colors].
    """
    terminals = range(10)
    base_edges = []
    # C cycle plus bad matching plus anchor plus pin bonus edges.
    for i in range(8):
        base_edges.append((i, (i + 1) % 8, "cycle"))
    for e in [(0, 4), (1, 5), (2, 6), (3, 7)]:
        base_edges.append((e[0], e[1], "match"))
    base_edges.append((8, 9, "anchor"))
    for i in range(8):
        a = 8 if i % 2 == 0 else 9
        base_edges.append((i, a, "pinbonus"))

    best = -1
    best_sides = []
    for bits in product([0, 1], repeat=10):
        val = 16  # two guaranteed cut edges per pin path
        val += sum(1 for u, v, _ in base_edges if bits[u] != bits[v])
        if val > best:
            best = val
            best_sides = [bits]
        elif val == best:
            best_sides.append(bits)
    return best, best_sides


def main():
    n, E, side = build()
    adj = adj_from(n, E)
    print("=== pinned Wagner counterexample audit ===")
    print("N", n, "edges", len(E), "triangle_free", is_triangle_free(n, adj))
    print("chosen_cut", cut_value(E, side), "B_connected", Bconn(n, adj, side))
    best, best_sides = reduced_maxcut()
    term_side = tuple(side[:10])
    print("reduced_maxcut", best, "num_terminal_maxcuts", len(best_sides))
    print("chosen_terminal_is_max", term_side in best_sides)

    st = struct_for_side(n, adj, side)
    if st is None:
        print("struct_for_side=None")
        return
    M, ell, T, mu, cyc = st
    print("bad_edges", sorted(M), "ell", {e: ell[e] for e in sorted(M)})
    C = set(range(8))
    vals_C = sorted(set(T[v] for v in C))
    vals_out = sorted(set(T[v] for v in range(8, n)))
    print("T_C_values", vals_C, "T_out_values", vals_out)
    lam = vals_C[0]
    print("lambda", lam, "float", float(lam), "|C|", len(C), "selfcap_holds", lam <= len(C))

    # Positive K support: connect vertices co-occurring with positive p_f.
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for f, paths in cyc.items():
        supp = set()
        for P in paths:
            supp.update(P)
        supp = sorted(supp)
        for v in supp[1:]:
            union(supp[0], v)
    comps = {}
    for v in range(n):
        if T[v] > 0:
            comps.setdefault(find(v), []).append(v)
    print("positive_K_components", sorted(sorted(c) for c in comps.values()))

    # Induced cut on C.
    E_C = [(u, v) for u, v in E if u in C and v in C]
    side_C = [side[i] for i in range(8)]
    cut_C = cut_value(E_C, side_C)
    max_C = max(cut_value(E_C, bits) for bits in product([0, 1], repeat=8))
    print("cut_on_C", cut_C, "maxcut_C", max_C, "bridge_holds", cut_C == max_C)

    # Check shortest B-distances for bad edges are old length 4.
    print("bad_distances", {e: bdist_restr(adj, side, e[0], e[1]) for e in sorted(M)})


if __name__ == "__main__":
    main()
