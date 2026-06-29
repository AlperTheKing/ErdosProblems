"""Show that the naked positive-extra tail bound is not a local theorem.

The N=26 nested path/detour witness has an interior-overlap caught by both
tails.  Adding cut leaves to tail vertices keeps the graph triangle-free,
keeps the same P-contained overlap, but increases the non-path cut-boundary
term.  Thus the proof of (M) cannot rely on the raw positive-extra <= 2
statement unless extra hypotheses are added; a closed-tail switch or a
max-cut-local argument is needed.
"""

from _closed_tail_switch_gate import b_closed_tail
from _M_tailswitch_gate import build_pd, boundary_dB, boundary_gain, tri_free
from _h import Bconn
from _satzmu_conn import struct_for_side


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def add_cut_leaves(n, edges, side, attachments):
    edges = list(edges)
    side = list(side)
    for parent, count in attachments:
        for _ in range(count):
            leaf = n
            n += 1
            edges.append((min(parent, leaf), max(parent, leaf)))
            side.append(side[parent] ^ 1)
    return n, sorted(set(edges)), side


def add_cut_path(n, edges, side, u, v, length):
    """Add an internally disjoint all-cut path of the given edge length."""
    assert (side[u] ^ side[v]) == (length & 1)
    edges = list(edges)
    side = list(side)
    prev = u
    for _ in range(1, length):
        x = n
        n += 1
        side.append(side[prev] ^ 1)
        edges.append((min(prev, x), max(prev, x)))
        prev = x
    edges.append((min(prev, v), max(prev, v)))
    return n, edges, side


def overlap_record(n, edges, side):
    adj = adj_from_edges(n, edges)
    assert tri_free(n, adj)
    assert Bconn(n, adj, side)
    st = struct_for_side(n, adj, side)
    assert st is not None
    M, _ell, _T, _mu, cyc = st

    f = (0, 12)
    P = cyc[f][0]
    left = set(P[:3])
    right = set(P[6:])
    closed_left = b_closed_tail(n, adj, side, P, left)
    closed_right = b_closed_tail(n, adj, side, P, right)
    gain_l = boundary_gain(n, adj, side, left)
    gain_r = boundary_gain(n, adj, side, right)
    closed_gain_l = boundary_gain(n, adj, side, closed_left)
    closed_gain_r = boundary_gain(n, adj, side, closed_right)
    extra = (boundary_dB(n, adj, side, left) - 1) + (
        boundary_dB(n, adj, side, right) - 1
    )
    return {
        "n": n,
        "M": M,
        "P": P,
        "left_gain": gain_l,
        "right_gain": gain_r,
        "gain_sum": gain_l + gain_r,
        "closed_left_gain": closed_gain_l,
        "closed_right_gain": closed_gain_r,
        "closed_gain_sum": closed_gain_l + closed_gain_r,
        "positive_extra": extra,
    }


def main():
    n0, edges0 = build_pd(12, [(0, 8), (2, 6)])
    side0 = [v % 2 for v in range(n0)]

    cases = [
        ("base", []),
        ("one left cut leaf", [(0, 1)]),
        ("six tail cut leaves", [(0, 3), (8, 3)]),
    ]
    for name, attachments in cases:
        n, edges, side = add_cut_leaves(n0, edges0, side0, attachments)
        rec = overlap_record(n, edges, side)
        print(f"{name}: {rec}", flush=True)

    n, edges, side = n0, list(edges0), list(side0)
    for _ in range(2):
        n, edges, side = add_cut_path(n, edges, side, 0, 3, 5)
        n, edges, side = add_cut_path(n, edges, side, 8, 5, 5)
    rec = overlap_record(n, sorted(set(edges)), side)
    print(f"two symmetric long detours per tail: {rec}", flush=True)


if __name__ == "__main__":
    main()
