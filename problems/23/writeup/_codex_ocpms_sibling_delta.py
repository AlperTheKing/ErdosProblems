"""Contribution deltas for sibling rows that are equality-atom supergraphs."""

from collections import Counter
from fractions import Fraction as F

from _h import Bconn, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_ocpms_sibling_embedding import (
    EQ,
    SIB,
    image_edges,
    image_path,
    norm,
    overloaded_rows,
    side_image,
    subgraph_embeddings,
)


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def struct_by_side(g6, side_string):
    n, E = dec(g6)
    adj = adj_from_edges(n, E)
    side = tuple(int(c) for c in side_string)
    assert Bconn(n, adj, side)
    st = struct_for_side(n, adj, side)
    assert st is not None
    return st


def contributions(g6, side_string, P):
    st = struct_by_side(g6, side_string)
    M, cyc = st[0], st[4]
    pset = set(P)
    out = {}
    for g in M:
        out[norm(g)] = F(1, len(cyc[g])) * sum(
            len(pset & set(Q)) for Q in cyc[g]
        )
    return out


def edge_image(edge, mp):
    a, b = edge
    return norm((mp[a], mp[b]))


def main():
    eq_rows = overloaded_rows(EQ)
    sib_rows = overloaded_rows(SIB)
    embs = subgraph_embeddings(eq_rows[0]["E"], sib_rows[0]["E"])
    delta_counter = Counter()
    total_counter = Counter()
    matched = 0
    for sr in sib_rows:
        for er in eq_rows:
            for mp in embs:
                if side_image(er["side"], mp) != sr["side"]:
                    continue
                mapped_p = image_path(er["P"], mp)
                if mapped_p != sr["P"] and tuple(reversed(mapped_p)) != sr["P"]:
                    continue
                if image_edges(er["M"], mp) != sr["M"]:
                    continue
                extra = sr["E"] - image_edges(er["E"], mp)
                if not extra or not extra <= sr["B"]:
                    continue
                eqc = contributions(EQ, er["side"], er["P"])
                sibc = contributions(SIB, sr["side"], sr["P"])
                deltas = []
                for e, val in sorted(eqc.items()):
                    im = edge_image(e, mp)
                    d = val - sibc[im]
                    deltas.append(d)
                matched += 1
                delta_counter[tuple(sorted(deltas))] += 1
                total_counter[sum(deltas)] += 1
                print(
                    "MATCH",
                    "sib_side",
                    sr["side"],
                    "sib_P",
                    sr["P"],
                    "eq_minus_sib",
                    sum(deltas),
                    "edge_deltas",
                    tuple(deltas),
                    "extra",
                    sorted(extra),
                )
                break
            else:
                continue
            break
    print("matched", matched)
    print("delta_multisets")
    for k, v in delta_counter.items():
        print(v, k)
    print("total_deltas")
    for k, v in total_counter.items():
        print(v, k)


if __name__ == "__main__":
    main()
