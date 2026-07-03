"""Probe all interval supersets for a Bank-L CD mismatch witness."""

from __future__ import annotations

import argparse
import json
import sys
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


def all_supersets(seed: set[int], universe: set[int]):
    rest = sorted(universe - seed)
    for k in range(len(rest) + 1):
        for add in combinations(rest, k):
            s = set(seed)
            s.update(add)
            if s and s != universe:
                yield s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness", default="tmp/bankl_cd_mismatch_witness_v1.json")
    ap.add_argument("--output", default="tmp/bankl_cd_superset_probe_v1.json")
    args = ap.parse_args()

    wit = json.loads(Path(args.witness).read_text(encoding="utf-8"))
    n = wit["n"]
    edges = [tuple(e) for e in wit["edges"]]
    side = [int(x) for x in wit["side"]]
    row = tuple(wit["row_data"]["row"])
    adj = skel.adj_from_edges(n, edges)
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        raise SystemExit("witness side has no valid structure")
    base_gamma = skel.gamma_data(n, adj, side)
    if base_gamma is None:
        raise SystemExit("base gamma unavailable")
    blue_edges = {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}
    bad_edges = {norm_edge(e) for e in edges if side[e[0]] == side[e[1]]}
    old_bad_len = {norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}
    universe = set(range(n))

    interval_results: list[dict[str, Any]] = []
    for i in range(len(row) - 2):
        seed = set(row[i : i + 3])
        valid = []
        connected = 0
        terminal = 0
        total = 0
        for s in all_supersets(seed, universe):
            total += 1
            side2 = skel.switched(side, s)
            conn = skel.Bconn(n, adj, side2)
            mask = sum(1 << v for v in s)
            term = skel.terminal_shadow_details(n, adj, side, st, mask)
            if conn:
                connected += 1
            if term is not None:
                terminal += 1
            if not (conn and term is not None):
                continue
            rec = skel.switch_record(n, blue_edges, bad_edges, old_bad_len, s, ("superset", i))
            if rec["nuK"] is None:
                continue
            valid.append(
                {
                    "verts": sorted(s),
                    "size": len(s),
                    "sigma": rec["sigma"],
                    "nu": str(rec["nu"]),
                    "K_S": rec["K_S"],
                    "nuK": str(rec["nuK"]),
                    "dB": rec["dB"],
                    "dM": rec["dM"],
                    "new_lengths": rec["new_lengths"],
                }
            )
        valid_sorted = sorted(valid, key=lambda r: (-int(r["nuK"]), r["size"], r["verts"]))
        interval_results.append(
            {
                "i": i,
                "seed": sorted(seed),
                "target_25sigma0": next(x for x in wit["intervals"] if x["i"] == i)["twentyfive_sigma0"],
                "total_supersets": total,
                "connected_count": connected,
                "terminal_count": terminal,
                "valid_count": len(valid),
                "max_valid": valid_sorted[0] if valid_sorted else None,
                "valid_top5": valid_sorted[:5],
            }
        )

    out = {
        "schema": "bankl_cd_superset_probe_v1",
        "witness": args.witness,
        "name": wit["name"],
        "n": n,
        "row": list(row),
        "intervals": interval_results,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": args.output,
        "intervals": [
            {
                "i": r["i"],
                "target": r["target_25sigma0"],
                "valid_count": r["valid_count"],
                "max_nuK": None if r["max_valid"] is None else r["max_valid"]["nuK"],
                "max_verts": None if r["max_valid"] is None else r["max_valid"]["verts"],
            }
            for r in interval_results
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
