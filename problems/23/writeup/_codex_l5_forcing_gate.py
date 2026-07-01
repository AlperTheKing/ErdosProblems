"""Natural stretched-core L=5 forcing gate.

Build the Codex/Claude nested L/(L+2) core family and enumerate maximum
cuts for the feasible small cases.  The gate records whether the intended
two terminal bad edges survive in a gamma-minimum connected-B max cut, or
whether the graph collapses to a one-bad-edge cut on the shared corridor.

This is not the proof.  It is a sanity gate for the proposed L=5-forcing
mechanism: L>5 cores have a universal shared B-edge hitting all intended
core rows, so max-cut should move the badness there instead of preserving
the two intended terminal bad edges.
"""

import argparse
from collections import Counter

from _h import Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _bdef_construct import is_triangle_free


def edge(a, b):
    return (a, b) if a < b else (b, a)


def build_stretch(L):
    assert L >= 5 and L % 2 == 1
    names = []
    for name in ("s", "u", "x", "v", "a0", "a1"):
        names.append(name)
    for i in range(L - 4):
        names.append(f"c{i}")
    names += ["b0", "b1", "t"]
    idx = {name: i for i, name in enumerate(names)}
    E = []

    def add(a, b):
        E.append(edge(idx[a], idx[b]))

    # f0 rows: s-a_i-c...-b_j-t
    add("s", "a0")
    add("s", "a1")
    add("a0", "c0")
    add("a1", "c0")
    for i in range(L - 5):
        add(f"c{i}", f"c{i+1}")
    last_c = f"c{L-5}"
    add(last_c, "b0")
    add(last_c, "b1")
    add("b0", "t")
    add("b1", "t")

    # f1 prefix/suffix: u-a1 + shared middle + t-x-v
    add("u", "a1")
    add("t", "x")
    add("x", "v")

    # Intended terminal bad edges in the constructed coordinate system.
    add("s", "t")
    add("u", "v")
    intended = {edge(idx["s"], idx["t"]), edge(idx["u"], idx["v"])}

    # Edges in the shared corridor that every intended row uses.
    shared = set()
    shared.add(edge(idx["a1"], idx["c0"]))
    for i in range(L - 5):
        shared.add(edge(idx[f"c{i}"], idx[f"c{i+1}"]))
    shared.add(edge(idx[last_c], idx["b0"]))
    shared.add(edge(idx[last_c], idx["b1"]))
    # The last branching means not every row uses both b0/t and b1/t.
    # Universal row edges exclude the two branch-to-t edges.
    universal = set(shared)
    # The a1-c0 edge is not used by f0 rows via a0, so the true all-row
    # intersection for both bad edges starts at c0-c1 when L>5.
    if L == 5:
        universal = set()
    else:
        universal = {edge(idx[f"c{i}"], idx[f"c{i+1}"]) for i in range(L - 5)}

    # Intended coordinate cut: all listed B-edges are cut, while s-t and u-v
    # are monochromatic.  Set s,t,u,v to side 0 and alternate along paths.
    intended_side = [None] * len(names)
    for name in ("s", "t", "u", "v"):
        intended_side[idx[name]] = 0
    intended_side[idx["x"]] = 1
    intended_side[idx["a0"]] = 1
    intended_side[idx["a1"]] = 1
    for i in range(L - 4):
        intended_side[idx[f"c{i}"]] = i % 2
    intended_side[idx["b0"]] = 1
    intended_side[idx["b1"]] = 1
    assert all(x is not None for x in intended_side)

    return len(names), E, names, intended, universal, tuple(intended_side)


def bad_edges_for_side(E, side):
    return frozenset(edge(a, b) for a, b in E if side[a] == side[b])


def scan_L(L):
    n, E, names, intended, universal, intended_side = build_stretch(L)
    adj = adj_from_edges(n, E)
    assert is_triangle_free(n, E)
    maxcuts = list(maxcut_all(n, adj))
    records = []
    for side in maxcuts:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, _T, _mu, _cyc = st
        gamma = sum(ell[f] ** 2 for f in M)
        bad = bad_edges_for_side(E, side)
        records.append((gamma, bad, side, tuple(sorted((f, ell[f]) for f in M))))
    if not records:
        return {
            "L": L,
            "n": n,
            "maxcuts": len(maxcuts),
            "connB": 0,
            "triangle_free": True,
        }
    min_gamma = min(r[0] for r in records)
    gmin = [r for r in records if r[0] == min_gamma]
    hist = Counter(r[1] for r in gmin)
    intended_survives = any(intended <= r[1] for r in gmin)
    one_universal = any(len(r[1]) == 1 and next(iter(r[1])) in universal for r in gmin)
    examples = []
    for bad, count in hist.most_common(4):
        examples.append(
            (
                count,
                tuple((names[a], names[b]) for a, b in sorted(bad)),
            )
        )
    recut = None
    target = None
    for gamma, bad, side, mells in gmin:
        if len(bad) == 1 and next(iter(bad)) in universal:
            target = side
            break
    if target is not None:
        diff = [i for i in range(n) if target[i] != intended_side[i]]
        comp = [i for i in range(n) if i not in diff]
        if len(comp) < len(diff):
            diff = comp
        recut = tuple(names[i] for i in diff)
    return {
        "L": L,
        "n": n,
        "maxcuts": len(maxcuts),
        "connB": len(records),
        "min_gamma": min_gamma,
        "gmin_count": len(gmin),
        "intended_survives": intended_survives,
        "one_universal": one_universal,
        "universal": tuple((names[a], names[b]) for a, b in sorted(universal)),
        "examples": examples,
        "intended_bad": tuple((names[a], names[b]) for a, b in sorted(intended)),
        "intended_gamma": sum(ell ** 2 for _e, ell in (struct_for_side(n, adj, intended_side)[1].items())),
        "recut_switch": recut,
    }


def scan_single_extra(L):
    n, E, names, intended, _universal, _intended_side = build_stretch(L)
    base = set(E)
    out = []
    for a in range(n):
        for b in range(a + 1, n):
            extra = edge(a, b)
            if extra in base:
                continue
            EE = sorted(base | {extra})
            if not is_triangle_free(n, EE):
                continue
            adj = adj_from_edges(n, EE)
            records = []
            for side in maxcut_all(n, adj):
                if not Bconn(n, adj, side):
                    continue
                st = struct_for_side(n, adj, side)
                if st is None:
                    continue
                M, ell, _T, _mu, _cyc = st
                gamma = sum(ell[f] ** 2 for f in M)
                bad = bad_edges_for_side(EE, side)
                records.append((gamma, bad, ell))
            if not records:
                continue
            min_gamma = min(r[0] for r in records)
            survivors = [r for r in records if r[0] == min_gamma and intended <= r[1]]
            if not survivors:
                continue
            ell = survivors[0][2]
            out.append(
                {
                    "extra": (names[a], names[b]),
                    "min_gamma": min_gamma,
                    "intended_lengths": tuple(
                        (names[u], names[v], ell[edge(u, v)])
                        for u, v in sorted(intended)
                    ),
                }
            )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-L", type=int, default=13)
    ap.add_argument("--single-extra-L", type=int, default=0)
    args = ap.parse_args()
    if args.single_extra_L:
        rows = scan_single_extra(args.single_extra_L)
        print("single-extra L", args.single_extra_L, "intended-survivors", len(rows))
        for row in rows:
            print(row)
        return
    for L in range(5, args.max_L + 1, 2):
        rec = scan_L(L)
        print("L", L, "n", rec["n"], "maxcuts", rec["maxcuts"], "connB", rec["connB"])
        if rec.get("connB", 0):
            print("  min_gamma", rec["min_gamma"], "gmin", rec["gmin_count"])
            print("  intended_survives", rec["intended_survives"], "one_universal", rec["one_universal"])
            print("  universal", rec["universal"])
            print("  intended_bad", rec["intended_bad"], "intended_gamma", rec["intended_gamma"])
            print("  recut_switch", rec["recut_switch"])
            print("  gmin bad examples", rec["examples"])
        print()


if __name__ == "__main__":
    main()
