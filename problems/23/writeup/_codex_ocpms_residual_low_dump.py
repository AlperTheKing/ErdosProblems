"""Dump the two PMS-5 residual-low sibling rows."""

from fractions import Fraction as F

from _h import Bconn, dec
from _satzmu_conn import struct_for_side


G6 = "I?" + chr(96) + "FAo]]?"
ROWS = [
    ("1111000010", (4, 8, 6, 1, 7)),
    ("1110000110", (3, 8, 6, 1, 9)),
]


def adj_from_edges(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def main():
    n, E = dec(G6)
    adj = adj_from_edges(n, E)
    for side_s, P in ROWS:
        side = tuple(int(c) for c in side_s)
        assert Bconn(n, adj, side)
        st = struct_for_side(n, adj, side)
        M, cyc = st[0], st[4]
        pset = set(P)
        print("ROW", "side", side_s, "P", P, "M", tuple(M))
        total = F(0)
        for g in M:
            overlaps = [len(pset & set(Q)) for Q in cyc[g]]
            contrib = F(sum(overlaps), len(cyc[g]))
            total += contrib
            print(
                "  EDGE",
                g,
                "den",
                len(cyc[g]),
                "overlaps",
                overlaps,
                "contrib",
                contrib,
                "rows",
                [tuple(Q) for Q in cyc[g]],
            )
        print("  TOTAL", total, "deficit_from_32/3", F(32, 3) - total)


if __name__ == "__main__":
    main()
