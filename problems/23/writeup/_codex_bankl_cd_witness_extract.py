"""Extract a cold exact witness for the current Bank-L CD bridge mismatch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _codex_bankl_lcb_skeleton as skel  # noqa: E402


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def graph_from_name(name: str) -> tuple[int, list[tuple[int, int]]]:
    if name.startswith("cen"):
        return skel.dec(name[3:])
    if name.startswith("C") and name.endswith("[1]"):
        L = int(name[1:-3])
        return skel.blowup([1] * L)
    raise ValueError(f"unsupported witness name: {name}")


def delta(edge_set: list[tuple[int, int]], verts: set[int]) -> list[tuple[int, int]]:
    return sorted(e for e in edge_set if (e[0] in verts) ^ (e[1] in verts))


def enrich(rec: dict[str, Any]) -> dict[str, Any]:
    n, edges = graph_from_name(rec["name"])
    side = [int(x) for x in rec["side"]]
    blue = sorted(norm_edge(e) for e in edges if side[e[0]] != side[e[1]])
    bad = sorted(norm_edge(e) for e in edges if side[e[0]] == side[e[1]])
    intervals = []
    for item in rec["intervals"]:
        verts = set(item["raw_vertices"])
        intervals.append(
            {
                **item,
                "raw_delta_B": delta(blue, verts),
                "raw_delta_M": delta(bad, verts),
            }
        )
    return {
        "schema": "bankl_cd_mismatch_witness_v1",
        "selection": "lexicographically smallest non-SAT record by (n,L,P_Q,name,row)",
        "name": rec["name"],
        "n": n,
        "edges": sorted(norm_edge(e) for e in edges),
        "side": rec["side"],
        "blue_edges": blue,
        "bad_edges": bad,
        "row_data": {
            k: rec[k]
            for k in (
                "f",
                "row",
                "L",
                "m",
                "p",
                "h",
                "d",
                "r",
                "P_Q",
                "rho_Q",
                "kappa",
                "sum_sigma0",
                "sum_25sigma0",
                "sum_nuK",
                "cd_margin",
                "raw_coarea_margin",
                "mu_margin_no_residual",
                "per_interval_fail_count",
                "per_interval_deficit_total",
                "status",
            )
        },
        "intervals": intervals,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_cd_gate_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cd_mismatch_witness_v1.json")
    args = ap.parse_args()

    best: tuple[tuple[Any, ...], dict[str, Any]] | None = None
    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("status") == "SAT":
                continue
            key = (rec["n"], rec["L"], rec["P_Q"], rec["name"], tuple(rec["row"]))
            if best is None or key < best[0]:
                best = (key, rec)
    if best is None:
        raise SystemExit("no mismatch witness found")

    witness = enrich(best[1])
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out),
        "name": witness["name"],
        "n": witness["n"],
        "row": witness["row_data"]["row"],
        "status": witness["row_data"]["status"],
        "cd_margin": witness["row_data"]["cd_margin"],
        "per_interval_fail_count": witness["row_data"]["per_interval_fail_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
