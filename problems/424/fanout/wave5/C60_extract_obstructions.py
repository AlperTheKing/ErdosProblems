#!/usr/bin/env python3
"""Extract the minimal exact C60 recurrence/template obstructions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COMPUTE = ROOT / "problems" / "424" / "compute" / "wave5"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C56 = load_module("c60_obstruction_c56", COMPUTE / "C56_dual_cert.py")


def exact_slice(limit: int) -> dict:
    cert = C56.generate(limit, 1e-7)
    verified = C56.verify_one(cert)
    closures: dict[int, list[list]] = defaultdict(list)
    for name, value in cert["row"]:
        if name.startswith("closure_"):
            closures[int(name.split("_")[1])].append([name, -int(value)])
    return {
        "limit": limit,
        "verified": verified,
        "q21": [row for row in cert["row"] if row[0] == "q_ge_difference_21"],
        "closure188": closures.get(188, []),
        "multi_closure_outputs": {
            str(n): rows for n, rows in closures.items() if len(rows) > 1
        },
        "max_closure_weight": max(
            (-int(value) for name, value in cert["row"] if name.startswith("closure_")),
            default=0,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patterns", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    patterns = json.loads(args.patterns.read_text(encoding="utf-8"))
    slices = [exact_slice(limit) for limit in (328, 329, 634, 635, 1017)]
    feature_rows = patterns["lp_features"]
    multi = [row["limit"] for row in feature_rows if not row["one_closure_per_output"]]
    weights = Counter(row["max_closure_weight"] for row in feature_rows)
    payload = {
        "exact_slices": slices,
        "first_boundary_deletion": patterns["lp_recurrence"]["first_boundary_row_removal"],
        "first_selector_switch": patterns["lp_recurrence"]["first_closure_selector_switch"],
        "first_multi_selector_limit": min(multi) if multi else None,
        "multi_selector_cutoffs_through_2000": multi,
        "maximum_expanded_dual_backreach": patterns["lp_recurrence"][
            "maximum_observed_backreach"
        ],
        "maximum_closure_weight_through_2000": max(weights, default=0),
        "first_incremental_reroute": patterns["flow_summary"]["first_rerouting"],
        "longest_incremental_path": patterns["flow_summary"]["longest_path_first"],
        "maximum_incremental_reverse_edges": patterns["flow_summary"][
            "maximum_reverse_edges"
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
