"""Exact P_Q pressure cross-tab for Bank-L rows.

For every L>5 row Q, compute the bare-row packet data

    p = e_M(V(Q)), h = |delta_M(V(Q))|, d = |delta_B(V(Q))|, r=N-L,
    P_Q = 25(p-1) + 25(d+h)/2 - 2Lr,
    rho_Q = 25*(eta - B(V(Q))).

The script joins these data to the existing compact JSONL certificate records
so it can report the current certificate kind without rerunning switch search.
It asserts the exact identity -Delta_Q = rho_Q - P_Q.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

import _codex_bankl_lcb_skeleton as skel


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def delta(edge_set: set[tuple[int, int]], verts: set[int]) -> set[tuple[int, int]]:
    return {e for e in edge_set if (e[0] in verts) ^ (e[1] in verts)}


def row_key(name: str, n: int, f, row) -> str:
    return json.dumps({"name": name, "n": n, "f": list(f), "row": list(row)}, sort_keys=True)


def load_certs(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            out[row_key(rec["name"], rec["n"], rec["f"], rec["row"])].append(rec)
    return out


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def compute_row_packet(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...]) -> dict:
    W = set(row)
    L = len(W)
    blue = {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}
    bad = {norm_edge(e) for e in edges if side[e[0]] == side[e[1]]}
    p = sum(1 for e in bad if e[0] in W and e[1] in W)
    h = len(delta(bad, W))
    d = len(delta(blue, W))
    m = len(bad)
    r = n - L
    eta = F(n * n, 25) - m
    B = F(n * n - r * r, 25) - p - F(d + h, 2)
    rho = 25 * (eta - B)
    Pq = 25 * (p - 1) + F(25 * (d + h), 2) - 2 * L * r
    delta_q = 25 * m + L * L - 25 - n * n
    assert F(-delta_q) == rho - Pq, (n, row, p, h, d, r, Pq, rho, delta_q)
    return {"p": p, "h": h, "d": d, "r": r, "P_Q": Pq, "rho_Q": rho, "B_packet": B}


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], certs: dict[str, list[dict]], out, acc: Counter) -> None:
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    _comp_map, find = skel.kcomponents(n, cyc)
    by_comp: dict[int, list[tuple[int, int]]] = {}
    for g in M:
        by_comp.setdefault(find(g[0]), []).append(g)
    for f in M:
        for row in cyc[f]:
            L = len(set(row))
            if L <= 5:
                continue
            key = row_key(name, n, f, row)
            bucket = certs.get(key)
            if not bucket:
                acc["missing_cert"] += 1
                continue
            cert = bucket.pop(0)
            packet = compute_row_packet(n, edges, side, tuple(row))
            Pq = packet["P_Q"]
            sign = "pos" if Pq > 0 else "zero" if Pq == 0 else "neg"
            scope = cert["row_scope"]
            kind = cert["certificate_kind"]
            acc["rows"] += 1
            acc[f"sign:{sign}"] += 1
            acc[f"scope:{scope}:sign:{sign}"] += 1
            acc[f"kind:{kind}:sign:{sign}"] += 1
            acc[f"scope_kind:{scope}:{kind}:sign:{sign}"] += 1
            if Pq > 0:
                acc["positive_rows"] += 1
            rec = {
                "name": name,
                "n": n,
                "m": cert["m"],
                "f": list(f),
                "row": list(row),
                "L": L,
                "row_scope": scope,
                "certificate_kind": kind,
                "p": packet["p"],
                "h": packet["h"],
                "d": packet["d"],
                "r": packet["r"],
                "P_Q": frac_s(Pq),
                "rho_Q": frac_s(packet["rho_Q"]),
                "B_packet": frac_s(packet["B_packet"]),
                "minus_Delta_Q": cert["minus_Delta_Q"],
            }
            if Pq > 0:
                out.write(json.dumps(rec, sort_keys=True) + "\n")


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], certs: dict[str, list[dict]], out, acc: Counter, max_cuts: int | None) -> None:
    _adj, cuts = skel.gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        scan_side(name, n, edges, [int(x) for x in side], certs, out, acc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", default="tmp/bankl_lcb_certs_n11.jsonl")
    ap.add_argument("--positive-output", default="tmp/bankl_pq_positive_rows.jsonl")
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    args = ap.parse_args()

    certs = load_certs(Path(args.certs))
    acc: Counter = Counter()
    out_path = Path(args.positive_output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        for L in (7, 9, 11, 13, 15, 17, 19):
            n, edges = skel.blowup([1] * L)
            scan_side(f"C{L}[1]", n, edges, skel.cycle_blowup_side([1] * L), certs, out, acc)
        for L in range(8, 31, 2):
            n, edges, side, _bad = skel.build_two_lane(L)
            scan_side(f"two-lane-L{L}", n, edges, side, certs, out, acc)
        for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
            bad = skel.greedy_chords(Ll, k, gap)
            n, edges, side, _ = skel.build_k_lane(Ll, k, bad)
            scan_side(f"klane-L{Ll}k{k}", n, edges, side, certs, out, acc)
        named = [
            ("Grotzsch", skel.mycielski(5, skel.Cn(5))),
            ("M(C7)", skel.mycielski(7, skel.Cn(7))),
            ("C7|Grotzsch", skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            scan_gmins(name, n, edges, certs, out, acc, args.max_cuts)
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = skel.dec(g6)
                scan_gmins(f"cen{g6}", n, edges, certs, out, acc, args.max_cuts)

    leftover = sum(len(v) for v in certs.values())
    summary = {
        "rows": acc["rows"],
        "missing_cert": acc["missing_cert"],
        "leftover_cert_records": leftover,
        "positive_rows": acc["positive_rows"],
        "positive_output": str(out_path),
        "sign_counts": {k.removeprefix("sign:"): v for k, v in sorted(acc.items()) if k.startswith("sign:")},
        "scope_sign_counts": {k.removeprefix("scope:"): v for k, v in sorted(acc.items()) if k.startswith("scope:")},
        "kind_sign_counts": {k.removeprefix("kind:"): v for k, v in sorted(acc.items()) if k.startswith("kind:")},
    }
    print(json.dumps(summary, sort_keys=True))
    assert acc["missing_cert"] == 0
    assert leftover == 0
    print("PASS Bank-L P_Q cross-tab exact identity checked")


if __name__ == "__main__":
    main()