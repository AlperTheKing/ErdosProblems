#!/usr/bin/env python3
"""Exact bitset search for seven-mark Sidon extensions of lifted P88."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106s = load(
    "p106_kclique_audit",
    ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py",
)
p106m = load(
    "p106_kclique_mutation",
    ROOT / "problems/864/compute/p106/scan_source_mutations.py",
)


def compatibility_graph(base, candidates):
    differences = {
        right - left
        for i, left in enumerate(base)
        for right in base[i + 1 :]
    }
    fixed_sums = {
        left + right
        for i, left in enumerate(base)
        for right in base[i:]
    }
    adjacency = [0] * len(candidates)
    compatible_pairs = 0
    for i, left in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            right = candidates[j]
            if right - left in differences or left + right in fixed_sums:
                continue
            adjacency[i] |= 1 << j
            adjacency[j] |= 1 << i
            compatible_pairs += 1
    return adjacency, compatible_pairs


def additions_are_sidon(additions):
    sums = set()
    for i, left in enumerate(additions):
        for right in additions[i:]:
            total = left + right
            if total in sums:
                return False
            sums.add(total)
    return True


def search(base, h, candidates, target, time_limit):
    adjacency, compatible_pairs = compatibility_graph(base, candidates)
    deadline = time.monotonic() + time_limit if time_limit else None
    nodes = complete_cliques = internally_sidon_cliques = 0
    witness = None

    def visit(chosen, available, need):
        nonlocal nodes, complete_cliques, internally_sidon_cliques, witness
        nodes += 1
        if deadline is not None and nodes % 65536 == 0 and time.monotonic() > deadline:
            raise TimeoutError
        if available.bit_count() < need:
            return False
        if need == 0:
            complete_cliques += 1
            additions = tuple(candidates[index] for index in chosen)
            if not additions_are_sidon(additions):
                return False
            internally_sidon_cliques += 1
            values = tuple(sorted(base + additions))
            assert p106m.is_sidon(values)
            row = p106s.audit(values, h, 1)
            if row["RM97_failure"]:
                p = len(values)
                witness = {
                    "B": values,
                    "additions": additions,
                    "p": p,
                    "h": h,
                    "b": 1,
                    "delta": (3 * p * p - p + 2) // 2 - h,
                    "sha256": hashlib.sha256(
                        ",".join(map(str, values)).encode("ascii")
                    ).hexdigest(),
                    **row,
                }
                return True
            return False

        remaining = available
        while remaining.bit_count() >= need:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            if visit(chosen + (vertex,), remaining & adjacency[vertex], need - 1):
                return True
        return False

    started = time.monotonic()
    status = "EXHAUSTED"
    try:
        visit((), (1 << len(candidates)) - 1, target)
    except TimeoutError:
        status = "TIME_LIMIT"
    if witness is not None:
        status = "WITNESS"
    return {
        "status": status,
        "candidate_count": len(candidates),
        "compatible_pairs": compatible_pairs,
        "target_additions": target,
        "search_nodes": nodes,
        "complete_pairwise_compatible_cliques": complete_cliques,
        "internally_sidon_cliques": internally_sidon_cliques,
        "wall_time_seconds": time.monotonic() - started,
        "positive_defect_RM97_witness": witness,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=7)
    parser.add_argument("--time-limit", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(
        (ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text()
    )
    parent = data["full_P88_q2_lift"]
    base, h = tuple(parent["B"]), int(parent["h"])
    candidates = tuple(p106m.individually_admissible_insertions(base))
    result = {
        "schema_version": 1,
        "arithmetic": "exact bitset clique enumeration plus exact Sidon and RM97 audits",
        "base_p": len(base),
        "h": h,
        **search(base, h, candidates, args.target, args.time_limit),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = dict(result)
    witness = summary["positive_defect_RM97_witness"]
    if witness is not None:
        summary["positive_defect_RM97_witness"] = {
            key: value for key, value in witness.items() if key != "B"
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
