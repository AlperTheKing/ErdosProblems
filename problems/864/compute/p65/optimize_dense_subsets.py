#!/usr/bin/env python3
"""Exact conditioned-subset optimization for all dense P53 ruler universes."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SEARCH = ROOT / "problems/864/compute/p65/search_hole_restricted_folds.py"
OPTIMIZER = ROOT / "problems/864/compute/p65/optimize_parent_subsets.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "problems/864/compute/p65/dense_subset_optimization.json",
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    search = load(SEARCH, "p65_search_for_dense")
    opt = load(OPTIMIZER, "p65_optimizer_for_dense")
    started = time.perf_counter()
    rows = []
    universe_rows = []
    for index, listed in enumerate(search.load_dense_rulers()):
        for orientation, base in (
            ("listed", listed),
            ("reflected", tuple(listed[-1] - x for x in reversed(listed))),
        ):
            p, width = len(base), base[-1]
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = max(-1, baseline - width - 2)
            start_index = len(rows)
            for gamma in range(max_gamma + 1):
                for b in (1, 2):
                    row = opt.solve_universe(base, gamma, b, args.seconds, args.workers)
                    row.update({
                        "universe_index": index, "orientation": orientation,
                        "universe_p": p, "universe_width": width,
                    })
                    rows.append(row)
            local = rows[start_index:]
            optimized = [r for r in local if r["status"] == "OPTIMAL"]
            universe_rows.append({
                "universe_index": index, "orientation": orientation,
                "p": p, "width": width, "cases": len(local),
                "optimized_cases": len(optimized),
                "maximum_objective": max(
                    (int(r["objective_C_S_minus_2p"]) for r in optimized),
                    default=None,
                ),
            })

    accepted = {
        "OPTIMAL", "INFEASIBLE", "SKIP_MONOTONE_UPPER_BOUND",
        "SKIP_NO_POSITIVE_DELTA_SUBSET",
    }
    unresolved = [r for r in rows if r["status"] not in accepted]
    optimized = [r for r in rows if r["status"] == "OPTIMAL"]
    falsifiers = [r for r in optimized if int(r["objective_C_S_minus_2p"]) >= -2]
    top = sorted(
        optimized,
        key=lambda r: (
            int(r["objective_C_S_minus_2p"]), int(r["C_S"]),
            -int(r["p"]), -int(r["h"]),
        ),
        reverse=True,
    )[:20]
    output = {
        "schema_version": 1, "arithmetic": "exact integer CP-SAT",
        "domain": (
            "all subsets retaining the top endpoint of each listed P53 dense "
            "ruler and its reflection, every positive-defect translation, b=1,2"
        ),
        "universes": universe_rows, "rows": rows,
        "status_counts": dict(sorted(Counter(str(r["status"]) for r in rows).items())),
        "unresolved_count": len(unresolved), "unresolved": unresolved,
        "falsifier_count": len(falsifiers), "falsifiers": falsifiers,
        "maximum_objective": max(
            (int(r["objective_C_S_minus_2p"]) for r in optimized), default=None
        ),
        "top_twenty": top,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "universes": len(universe_rows), "cases": len(rows),
        "status_counts": output["status_counts"],
        "unresolved_count": output["unresolved_count"],
        "falsifier_count": output["falsifier_count"],
        "maximum_objective": output["maximum_objective"],
        "elapsed_seconds": output["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
