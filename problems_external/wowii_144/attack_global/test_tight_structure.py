#!/usr/bin/env python3
"""Classify exact-equality W144-VE instances by cyclomatic number."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
from test_steiner_vertex_fast import GENG, audit_one, parse_graph6


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    instance_mu: Counter[int] = Counter()
    graph_mu: Counter[int] = Counter()
    by_n: dict[str, dict] = {}
    examples: dict[int, dict] = {}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        graph6s = proc.stdout.split()
        tight_graphs = tight_instances = tested = 0
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers) as executor:
            for result in executor.map(audit_one, graph6s, chunksize=16):
                if result is None:
                    continue
                tested += 1
                tight = [r for r in result["records"] if r["slack"] == 0]
                if not tight:
                    continue
                tight_graphs += 1
                tight_instances += len(tight)
                order, adjacency = parse_graph6(result["graph6"])
                edges = sum(mask.bit_count() for mask in adjacency) // 2
                mu = edges - order + 1
                graph_mu[mu] += 1
                instance_mu[mu] += len(tight)
                examples.setdefault(mu, tight[0])
        by_n[str(n)] = {"generated": len(graph6s), "tested": tested,
                        "tight_graphs": tight_graphs,
                        "tight_instances": tight_instances}
        print(n, by_n[str(n)], flush=True)
    answer = {
        "by_n": by_n,
        "tight_graphs_by_cyclomatic": dict(sorted(graph_mu.items())),
        "tight_instances_by_cyclomatic": dict(sorted(instance_mu.items())),
        "first_example_by_cyclomatic": examples,
    }
    print(json.dumps(answer, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
