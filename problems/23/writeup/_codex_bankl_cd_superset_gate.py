"""Gate aggregate CD using all valid supersets of each raw 3-interval.

The earlier CD gate used the v2 approximation to Comp([i,i+2]).  This script
keeps the same raw sigma_i^0, but for each interval maximizes nu_K over all
proper vertex supersets containing the raw 3-vertex interval that are connected
after switching and terminal-shadow valid.  It tests the aggregate inequality

    25 * sum_i sigma_i^0 <= sum_i max_S nu_K(S)

on records emitted by _codex_bankl_cd_gate.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _codex_bankl_lcb_skeleton as skel  # noqa: E402


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


@lru_cache(maxsize=None)
def graph_from_name(name: str) -> tuple[int, tuple[tuple[int, int], ...]]:
    if name.startswith("cen"):
        n, edges = skel.dec(name[3:])
        return n, tuple(norm_edge(e) for e in edges)
    if name.startswith("C") and name.endswith("[1]"):
        L = int(name[1:-3])
        n, edges = skel.blowup([1] * L)
        return n, tuple(norm_edge(e) for e in edges)
    m = re.fullmatch(r"two-lane-L(\d+)", name)
    if m:
        n, edges, _side, _bad = skel.build_two_lane(int(m.group(1)))
        return n, tuple(norm_edge(e) for e in edges)
    m = re.fullmatch(r"klane-L(\d+)k(\d+)", name)
    if m:
        Ll, k = int(m.group(1)), int(m.group(2))
        # Match the small direct stress cases from _codex_bankl_cd_gate.py.
        gap_by = {(12, 4): 6, (14, 4): 8, (16, 5): 8, (20, 6): 10}
        bad = skel.greedy_chords(Ll, k, gap_by[(Ll, k)])
        n, edges, _side, _ = skel.build_k_lane(Ll, k, bad)
        return n, tuple(norm_edge(e) for e in edges)
    if name == "Grotzsch":
        n, edges = skel.mycielski(5, skel.Cn(5))
        return n, tuple(norm_edge(e) for e in edges)
    if name == "M(C7)":
        n, edges = skel.mycielski(7, skel.Cn(7))
        return n, tuple(norm_edge(e) for e in edges)
    if name == "C7|Grotzsch":
        n, edges = skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)
        return n, tuple(norm_edge(e) for e in edges)
    raise ValueError(f"unsupported name: {name}")


def all_supersets(seed: set[int], universe: set[int]):
    rest = sorted(universe - seed)
    for k in range(len(rest) + 1):
        for add in combinations(rest, k):
            s = set(seed)
            s.update(add)
            if s and s != universe:
                yield s


def best_interval_nuK(n: int, edges: list[tuple[int, int]], side: list[int], st, row: tuple[int, ...], i: int) -> dict[str, Any]:
    adj = skel.adj_from_edges(n, edges)
    base_gamma = skel.gamma_data(n, adj, side)
    if base_gamma is None:
        raise ValueError("missing base gamma")
    blue_edges = {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}
    bad_edges = {norm_edge(e) for e in edges if side[e[0]] == side[e[1]]}
    old_bad_len = {norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}
    universe = set(range(n))
    seed = set(row[i : i + 3])
    checked = connected = terminal = valid_count = 0
    best = None
    for s in all_supersets(seed, universe):
        checked += 1
        side2 = skel.switched(side, s)
        conn = skel.Bconn(n, adj, side2)
        if conn:
            connected += 1
        mask = sum(1 << v for v in s)
        term = skel.terminal_shadow_details(n, adj, side, st, mask)
        if term is not None:
            terminal += 1
        if not (conn and term is not None):
            continue
        rec = skel.switch_record(n, blue_edges, bad_edges, old_bad_len, s, ("superset", i))
        if rec["nuK"] is None:
            continue
        valid_count += 1
        cand = {
            "verts": sorted(s),
            "size": len(s),
            "sigma": rec["sigma"],
            "nu": str(rec["nu"]),
            "K_S": rec["K_S"],
            "nuK": str(rec["nuK"]),
            "dB": rec["dB"],
            "dM": rec["dM"],
        }
        if best is None or int(cand["nuK"]) > int(best["nuK"]) or (
            int(cand["nuK"]) == int(best["nuK"]) and (cand["size"], cand["verts"]) < (best["size"], best["verts"])
        ):
            best = cand
    return {
        "i": i,
        "seed": sorted(seed),
        "checked": checked,
        "connected_count": connected,
        "terminal_count": terminal,
        "valid_count": valid_count,
        "best": best,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_cd_gate_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cd_superset_gate_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_cd_superset_gate_v1_summary.json")
    ap.add_argument("--limit-rows", type=int, default=None)
    ap.add_argument("--include-sat", action="store_true")
    args = ap.parse_args()

    counts: Counter[str] = Counter()
    first_fail = None
    with Path(args.input).open("r", encoding="utf-8") as fh, Path(args.output).open("w", encoding="utf-8", newline="\n") as out:
        for line in fh:
            if not line.strip():
                continue
            src = json.loads(line)
            if src.get("status") == "SAT" and not args.include_sat:
                continue
            n0, edge_tuple = graph_from_name(src["name"])
            edges = list(edge_tuple)
            if n0 != src["n"]:
                raise AssertionError((src["name"], n0, src["n"]))
            side = [int(x) for x in src["side"]]
            adj = skel.adj_from_edges(n0, edges)
            st = skel.struct_for_side(n0, adj, side)
            if st is None:
                raise AssertionError(("st", src["name"]))
            row = tuple(src["row"])
            intervals = []
            sum_best = 0
            for raw_interval in src["intervals"]:
                i = raw_interval["i"]
                b = best_interval_nuK(n0, edges, side, st, row, i)
                best = b["best"]
                nuK = 0 if best is None else int(best["nuK"])
                sum_best += nuK
                intervals.append({**b, "target_25sigma0": raw_interval["twentyfive_sigma0"], "raw_sigma0": raw_interval["sigma0"]})
            target = int(src["sum_25sigma0"])
            margin = sum_best - target
            status = "SAT" if margin >= 0 else "FAIL"
            rec = {
                "schema": "bankl_cd_superset_gate_v1",
                "name": src["name"],
                "n": src["n"],
                "side": src["side"],
                "f": src["f"],
                "row": src["row"],
                "L": src["L"],
                "P_Q": src["P_Q"],
                "rho_Q": src["rho_Q"],
                "sum_25sigma0": target,
                "sum_best_nuK": sum_best,
                "margin": margin,
                "status": status,
                "intervals": intervals,
            }
            counts["rows"] += 1
            counts[f"status:{status}"] += 1
            counts[f"L:{src['L']}"] += 1
            if status != "SAT":
                counts["fail"] += 1
                first_fail = first_fail or rec
            out.write(json.dumps(rec, sort_keys=True) + "\n")
            if args.limit_rows is not None and counts["rows"] >= args.limit_rows:
                break

    summary = {
        "input": args.input,
        "output": args.output,
        "rows": counts["rows"],
        "fail": counts["fail"],
        "statuses": {k.removeprefix("status:"): v for k, v in sorted(counts.items()) if k.startswith("status:")},
        "by_L": {k.removeprefix("L:"): v for k, v in sorted(counts.items()) if k.startswith("L:")},
        "first_fail": first_fail,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("output", "rows", "fail", "statuses", "by_L")}, sort_keys=True))
    print("PASS Bank-L CD all-superset aggregate gate" if counts["fail"] == 0 else "FAIL Bank-L CD all-superset aggregate gate")


if __name__ == "__main__":
    main()
