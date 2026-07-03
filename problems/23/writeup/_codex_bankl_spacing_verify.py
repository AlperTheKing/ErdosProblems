"""Exact gate for the Bank-L row-neighbor spacing lemma.

For every positive-pressure clean row (P_Q > 0, p=1, h=0), verify that each
off-row vertex has at most two blue neighbors on the row, and if it has two
then the row positions differ by exactly two.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pq_crosstab as pq


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def blue_edges(edges: list[tuple[int, int]], side: list[int]) -> set[tuple[int, int]]:
    return {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}


def verify_row(
    name: str,
    n: int,
    edges: list[tuple[int, int]],
    side: list[int],
    f,
    row: tuple[int, ...],
    acc: Counter,
    examples: dict,
) -> None:
    packet = pq.compute_row_packet(n, edges, side, row)
    if packet["P_Q"] <= 0:
        return
    if not (packet["p"] == 1 and packet["h"] == 0):
        acc["positive_nonclean_rows"] += 1
        examples.setdefault("positive_nonclean", {
            "name": name,
            "n": n,
            "f": list(f),
            "row": list(row),
            "packet": {k: pq.frac_s(v) if k in ("P_Q", "rho_Q", "B_packet") else v for k, v in packet.items()},
        })
        return

    B = blue_edges(edges, side)
    W = set(row)
    row_index = {v: i for i, v in enumerate(row)}
    deg_counts: Counter = Counter()
    mask_counts: Counter = Counter()
    row_bdy = [0] * len(row)
    for x in range(n):
        if x in W:
            continue
        hits = tuple(i for i, v in enumerate(row) if norm_edge((x, v)) in B)
        deg_counts[len(hits)] += 1
        mask_counts[hits] += 1
        for i in hits:
            row_bdy[i] += 1
        if len(hits) > 2:
            acc["fail"] += 1
            examples.setdefault("too_many_hits", {
                "name": name,
                "n": n,
                "f": list(f),
                "row": list(row),
                "vertex": x,
                "hits": list(hits),
                "packet_d": packet["d"],
            })
        if len(hits) == 2 and hits[1] - hits[0] != 2:
            acc["fail"] += 1
            examples.setdefault("bad_spacing", {
                "name": name,
                "n": n,
                "f": list(f),
                "row": list(row),
                "vertex": x,
                "hits": list(hits),
                "packet_d": packet["d"],
            })

    if sum(row_bdy) != packet["d"]:
        acc["fail"] += 1
        examples.setdefault("boundary_mismatch", {
            "name": name,
            "n": n,
            "f": list(f),
            "row": list(row),
            "sum_row_bdy": sum(row_bdy),
            "packet_d": packet["d"],
        })

    acc["clean_positive_rows"] += 1
    acc[f"L:{len(row)}"] += 1
    acc[f"r:{packet['r']}"] += 1
    acc[f"d:{packet['d']}"] += 1
    acc[f"outer_deg_sig:{tuple(sorted(deg_counts.items()))}"] += 1
    for mask, c in mask_counts.items():
        if mask:
            acc[f"mask:{mask}"] += c


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], acc: Counter, examples: dict) -> None:
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    for f in M:
        for row0 in cyc[f]:
            row = tuple(row0)
            if len(set(row)) <= 5:
                continue
            verify_row(name, n, edges, side, f, row, acc, examples)


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], acc: Counter, examples: dict, max_cuts: int | None) -> None:
    _adj, cuts = skel.gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side0 in cuts:
        scan_side(name, n, edges, [int(x) for x in side0], acc, examples)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--output", default="tmp/bankl_spacing_verify_v1.json")
    args = ap.parse_args()

    acc: Counter = Counter()
    examples: dict = {}

    for L in (7, 9, 11, 13, 15, 17, 19):
        n, edges = skel.blowup([1] * L)
        scan_side(f"C{L}[1]", n, edges, skel.cycle_blowup_side([1] * L), acc, examples)
    for L in range(8, 31, 2):
        n, edges, side, _bad = skel.build_two_lane(L)
        scan_side(f"two-lane-L{L}", n, edges, side, acc, examples)
    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = skel.greedy_chords(Ll, k, gap)
        n, edges, side, _ = skel.build_k_lane(Ll, k, bad)
        scan_side(f"klane-L{Ll}k{k}", n, edges, side, acc, examples)
    named = [
        ("Grotzsch", skel.mycielski(5, skel.Cn(5))),
        ("M(C7)", skel.mycielski(7, skel.Cn(7))),
        ("C7|Grotzsch", skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)),
    ]
    for name, (n, edges) in named:
        scan_gmins(name, n, edges, acc, examples, args.max_cuts)
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = skel.dec(g6)
            scan_gmins(f"cen{g6}", n, edges, acc, examples, args.max_cuts)

    summary = {
        "clean_positive_rows": acc["clean_positive_rows"],
        "positive_nonclean_rows": acc["positive_nonclean_rows"],
        "fail": acc["fail"],
        "by_L": {k.removeprefix("L:"): v for k, v in sorted(acc.items()) if k.startswith("L:")},
        "by_r": {k.removeprefix("r:"): v for k, v in sorted(acc.items()) if k.startswith("r:")},
        "by_d": {k.removeprefix("d:"): v for k, v in sorted(acc.items()) if k.startswith("d:")},
        "outer_degree_signatures": {k.removeprefix("outer_deg_sig:"): v for k, v in sorted(acc.items()) if k.startswith("outer_deg_sig:")},
        "mask_counts": {k.removeprefix("mask:"): v for k, v in sorted(acc.items()) if k.startswith("mask:")},
        "examples": examples,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out),
        "clean_positive_rows": summary["clean_positive_rows"],
        "positive_nonclean_rows": summary["positive_nonclean_rows"],
        "fail": summary["fail"],
        "by_L": summary["by_L"],
    }, sort_keys=True))
    if summary["fail"] == 0:
        print("PASS Bank-L clean-row row-neighbor spacing")
    else:
        print("FAIL Bank-L clean-row row-neighbor spacing")


if __name__ == "__main__":
    main()
