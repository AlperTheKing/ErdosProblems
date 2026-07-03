"""Extract a cold witness from the all-superset aggregate CD gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from _codex_bankl_cd_superset_gate import graph_from_name, norm_edge  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_cd_superset_gate_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cd_superset_fail_witness_v1.json")
    args = ap.parse_args()

    best = None
    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("status") != "FAIL":
                continue
            key = (rec["n"], rec["L"], rec["P_Q"], rec["margin"], rec["name"], tuple(rec["row"]))
            if best is None or key < best[0]:
                best = (key, rec)
    if best is None:
        raise SystemExit("no all-superset failure found")

    rec = best[1]
    n, edge_tuple = graph_from_name(rec["name"])
    edges = sorted(norm_edge(e) for e in edge_tuple)
    side = [int(x) for x in rec["side"]]
    blue = [e for e in edges if side[e[0]] != side[e[1]]]
    bad = [e for e in edges if side[e[0]] == side[e[1]]]
    out = {
        "schema": "bankl_cd_superset_fail_witness_v1",
        "selection": "lexicographically smallest FAIL by (n,L,P_Q,margin,name,row)",
        "name": rec["name"],
        "n": n,
        "edges": edges,
        "side": rec["side"],
        "blue_edges": blue,
        "bad_edges": bad,
        "record": rec,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": args.output,
        "name": rec["name"],
        "n": n,
        "row": rec["row"],
        "L": rec["L"],
        "P_Q": rec["P_Q"],
        "sum_25sigma0": rec["sum_25sigma0"],
        "sum_best_nuK": rec["sum_best_nuK"],
        "margin": rec["margin"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
