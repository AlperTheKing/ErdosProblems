"""Attachment profiles for positive-pressure Bank-L rows.

This scans gamma-min connected-B census cuts and records how off-row vertices
attach by blue edges to a P_Q>0 row packet.  The main pressure-cover case is
usually p=1,h=0, where pressure is entirely boundary pressure

    P_Q = 25 d / 2 - 2 L r.

The attachment multiset exposes the triangle-free combinatorics behind d.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pq_crosstab as pq


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def blue_edges(edges: list[tuple[int, int]], side: list[int]) -> set[tuple[int, int]]:
    return {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}


def attachment_record(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...]) -> dict:
    W = set(row)
    B = blue_edges(edges, side)
    outer_degs = []
    outer_masks = []
    row_bdy_degs = {v: 0 for v in W}
    row_index = {v: i for i, v in enumerate(row)}
    for u in range(n):
        if u in W:
            continue
        hit = []
        for v in W:
            if norm_edge((u, v)) in B:
                hit.append(row_index[v])
                row_bdy_degs[v] += 1
        outer_degs.append(len(hit))
        outer_masks.append(tuple(sorted(hit)))
    return {
        "outer_degs": tuple(sorted(outer_degs, reverse=True)),
        "outer_masks": tuple(sorted(outer_masks)),
        "row_bdy_degs": tuple(row_bdy_degs[v] for v in row),
        "row_bdy_degs_sorted": tuple(sorted(row_bdy_degs.values(), reverse=True)),
    }


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
            L = len(set(row))
            if L <= 5:
                continue
            packet = pq.compute_row_packet(n, edges, side, row)
            if packet["P_Q"] <= 0:
                continue
            att = attachment_record(n, edges, side, row)
            kind = "main" if packet["p"] == 1 and packet["h"] == 0 else "residue"
            sig = (
                kind,
                L,
                packet["r"],
                packet["p"],
                packet["h"],
                packet["d"],
                pq.frac_s(packet["P_Q"]),
                att["outer_degs"],
                att["outer_masks"],
                att["row_bdy_degs_sorted"],
            )
            acc[sig] += 1
            if sig not in examples:
                examples[sig] = {
                    "name": name,
                    "n": n,
                    "f": list(f),
                    "row": list(row),
                    "P_Q": pq.frac_s(packet["P_Q"]),
                    "rho_Q": pq.frac_s(packet["rho_Q"]),
                    "outer_degs": list(att["outer_degs"]),
                    "outer_masks": [list(x) for x in att["outer_masks"]],
                    "row_bdy_degs": list(att["row_bdy_degs"]),
                    "row_bdy_degs_sorted": list(att["row_bdy_degs_sorted"]),
                }


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
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--summary-output", default="tmp/bankl_pq_attachment_profile.json")
    args = ap.parse_args()

    acc: Counter = Counter()
    examples: dict = {}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = skel.dec(g6)
            scan_gmins(f"cen{g6}", n, edges, acc, examples, args.max_cuts)

    top = []
    by_kind = Counter()
    by_outer_degs = Counter()
    for sig, count in acc.items():
        kind, L, r, p, h, d, Pq, outer_degs, outer_masks, row_bdy = sig
        by_kind[kind] += count
        by_outer_degs[(kind, L, r, d, outer_degs)] += count
        if len(top) < args.top:
            pass
    for sig, count in acc.most_common(args.top):
        kind, L, r, p, h, d, Pq, outer_degs, outer_masks, row_bdy = sig
        top.append({
            "count": count,
            "kind": kind,
            "L": L,
            "r": r,
            "p": p,
            "h": h,
            "d": d,
            "P_Q": Pq,
            "outer_degs": list(outer_degs),
            "outer_masks": [list(x) for x in outer_masks],
            "row_bdy_degs_sorted": list(row_bdy),
            "example": examples[sig],
        })

    summary = {
        "rows": sum(acc.values()),
        "unique_attachment_signatures": len(acc),
        "by_kind": dict(sorted(by_kind.items())),
        "top_attachment_signatures": top,
        "top_outer_degree_signatures": [
            {
                "count": count,
                "kind": sig[0],
                "L": sig[1],
                "r": sig[2],
                "d": sig[3],
                "outer_degs": list(sig[4]),
            }
            for sig, count in by_outer_degs.most_common(args.top)
        ],
    }
    out = Path(args.summary_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": summary["rows"],
        "unique_attachment_signatures": summary["unique_attachment_signatures"],
        "by_kind": summary["by_kind"],
        "summary_output": str(out),
    }, sort_keys=True))
    print("TOP_ATTACHMENT_SIGNATURES")
    for item in top:
        print(json.dumps({k: item[k] for k in ("count", "kind", "L", "r", "p", "h", "d", "P_Q", "outer_degs", "row_bdy_degs_sorted")}, sort_keys=True))


if __name__ == "__main__":
    main()
