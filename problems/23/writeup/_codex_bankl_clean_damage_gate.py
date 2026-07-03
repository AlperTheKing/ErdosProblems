"""Exact damage gate for clean positive-pressure Bank-L rows.

For a clean row packet W=V(Q) with p=1 and h=0, SH' gives an extension
damage bound <= d/2.  Bank-L needs the sharper allowance

    damage <= 2 L r / 25

when the off-row graph R is recolored optimally.  Since damage is integral,
the exact finite gate checks

    min_optimal_boundary_damage <= floor(2 L r / 25)

for every census P_Q>0 row with p=1,h=0.
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


def min_opt_damage(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...]) -> dict:
    W = set(row)
    R = [v for v in range(n) if v not in W]
    idx = {v: i for i, v in enumerate(R)}
    inside = [(u, v) for u, v in edges if u in idx and v in idx]
    boundary_blue = [(u, v) for u, v in edges if side[u] != side[v] and ((u in W) ^ (v in W))]

    best_inside = None
    best_damage = None
    best_masks = 0
    for mask in range(1 << len(R)):
        def col(x: int) -> int:
            if x in W:
                return side[x]
            return (mask >> idx[x]) & 1

        mono_inside = sum(1 for u, v in inside if col(u) == col(v))
        if best_inside is not None and mono_inside > best_inside:
            continue
        damage = sum(1 for u, v in boundary_blue if col(u) == col(v))
        # Global flip on R preserves the inside bad count and complements blue
        # boundary damage because h=0 in this gate.
        damage = min(damage, len(boundary_blue) - damage)
        if best_inside is None or mono_inside < best_inside:
            best_inside = mono_inside
            best_damage = damage
            best_masks = 1
        elif mono_inside == best_inside:
            best_masks += 1
            if damage < best_damage:
                best_damage = damage
    return {
        "r": len(R),
        "beta_R": best_inside,
        "min_damage": best_damage,
        "optimal_colorings": best_masks,
        "d": len(boundary_blue),
    }


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], acc: Counter, failures: list[dict]) -> None:
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
            if packet["p"] != 1 or packet["h"] != 0:
                acc["nonclean_positive"] += 1
                continue
            acc["clean_positive"] += 1
            dmg = min_opt_damage(n, edges, side, row)
            allowance_floor = (2 * L * packet["r"]) // 25
            acc[f"shape:L{L}:r{packet['r']}:d{packet['d']}:allow{allowance_floor}:damage{dmg['min_damage']}"] += 1
            if dmg["min_damage"] <= allowance_floor:
                acc["pass"] += 1
            else:
                acc["fail"] += 1
                if len(failures) < 20:
                    failures.append({
                        "name": name,
                        "n": n,
                        "f": list(f),
                        "row": list(row),
                        "L": L,
                        "p": packet["p"],
                        "h": packet["h"],
                        "d": packet["d"],
                        "r": packet["r"],
                        "P_Q": pq.frac_s(packet["P_Q"]),
                        "rho_Q": pq.frac_s(packet["rho_Q"]),
                        "allowance_floor": allowance_floor,
                        **dmg,
                    })


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], acc: Counter, failures: list[dict], max_cuts: int | None) -> None:
    _adj, cuts = skel.gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side0 in cuts:
        scan_side(name, n, edges, [int(x) for x in side0], acc, failures)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--failure-output", default="tmp/bankl_clean_damage_failures.json")
    args = ap.parse_args()

    acc: Counter = Counter()
    failures: list[dict] = []
    for nn in range(args.min_n, args.max_n + 1):
        before_clean = acc["clean_positive"]
        before_fail = acc["fail"]
        for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = skel.dec(g6)
            scan_gmins(f"cen{g6}", n, edges, acc, failures, args.max_cuts)
        print(json.dumps({
            "N": nn,
            "clean_positive_added": acc["clean_positive"] - before_clean,
            "fail_added": acc["fail"] - before_fail,
            "clean_positive_total": acc["clean_positive"],
            "fail_total": acc["fail"],
        }, sort_keys=True), flush=True)

    out = Path(args.failure_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(failures, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shape_counts = {k: v for k, v in sorted(acc.items()) if k.startswith("shape:")}
    summary = {
        "clean_positive": acc["clean_positive"],
        "nonclean_positive": acc["nonclean_positive"],
        "pass": acc["pass"],
        "fail": acc["fail"],
        "shape_counts": shape_counts,
        "failure_output": str(out),
    }
    print(json.dumps(summary, sort_keys=True))
    print("PASS clean damage gate" if acc["fail"] == 0 else "FAIL clean damage gate")


if __name__ == "__main__":
    main()
