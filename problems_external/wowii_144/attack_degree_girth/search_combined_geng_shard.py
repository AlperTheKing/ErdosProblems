#!/usr/bin/env python3
"""Search a deterministic nauty shard for a W144-COMB counterexample."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("order", type=int)
    parser.add_argument("residue", type=int)
    parser.add_argument("modulus", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    command = [str(GENG), "-Ctfq", str(args.order), f"{args.residue}/{args.modulus}"]
    run = subprocess.Popen(command, stdout=subprocess.PIPE)
    assert run.stdout is not None
    result = {"order": args.order, "residue": args.residue, "modulus": args.modulus,
              "generated": 0, "retained": 0, "residuals": 0, "minimum_slack": None,
              "first_minimum": None, "first_failure": None}
    for line in run.stdout:
        code = line.strip()
        if not code:
            continue
        result["generated"] += 1
        graph = nx.from_graph6_bytes(code)
        g = girth(graph)
        beta = cycle_rank(graph)
        if g is None or g < 5 or beta < 2:
            continue
        result["retained"] += 1
        n = len(graph)
        eta, center = center_depth(graph)
        delta = max(dict(graph.degree()).values())
        diameter = nx.diameter(graph)
        terms = [delta - 1, diameter - g // 2, n - g - beta + 1]
        slack = max(terms) - eta
        if eta >= delta and eta > diameter - g // 2:
            result["residuals"] += 1
        item = {"graph6": code.decode(), "n": n, "m": graph.number_of_edges(),
                "girth": g, "beta": beta, "diameter": diameter,
                "maximum_degree": delta, "eta": eta, "center": sorted(center),
                "terms": terms, "slack": slack, "edges": sorted(map(list, graph.edges()))}
        if result["minimum_slack"] is None or slack < result["minimum_slack"]:
            result["minimum_slack"] = slack
            result["first_minimum"] = item
        if slack < 0:
            result["first_failure"] = item
            break
    if run.poll() is None:
        run.terminate()
    elif run.returncode != 0:
        raise RuntimeError("geng failed")
    output = args.output or HERE / f"combined_geng_n{args.order}_{args.residue}_of_{args.modulus}.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
