"""Exact search for twins preserving only residue histograms (not point labels)."""

from __future__ import annotations

import argparse
import json
import runpy
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
AUDIT = runpy.run_path(str(HERE / "residue_phase_audit.py"))
WITNESSES = AUDIT["WITNESSES"]
normalize = AUDIT["normalize"]
is_sidon = AUDIT["is_sidon"]
cross_collisions = AUDIT["cross_collisions"]
label_families = AUDIT["label_families"]
residue_counter = AUDIT["residue_counter"]
modulus_profile = AUDIT["modulus_profile"]


def grouped_options(z: list[int], modulus: int) -> tuple[list[tuple[int, list[tuple[int, ...]]]], int]:
    width = z[-1]
    required = Counter(x % modulus for x in z)
    groups = []
    box = 1
    for residue, count in sorted(required.items()):
        values = list(range(residue, width + 1, modulus))
        if len(values) < count:
            return [], 0
        choices = list(combinations(values, count))
        groups.append((residue, choices))
        box *= comb(len(values), count)
    return groups, box


def search_one(z: list[int], gap: int, modulus: int, max_nodes: int) -> dict[str, object]:
    groups, box = grouped_options(z, modulus)
    nodes = 0
    answer = None
    original_d, original_s = label_families(z, gap)
    original_d_hist = residue_counter(original_d, modulus)
    original_s_hist = residue_counter(original_s, modulus)
    for group_choice in product(*(choices for _, choices in groups)):
        nodes += 1
        if nodes > max_nodes:
            break
        candidate = sorted(value for choice in group_choice for value in choice)
        if candidate == z or candidate[0] != 0 or candidate[-1] != z[-1]:
            continue
        if not is_sidon(candidate):
            continue
        candidate_d, candidate_s = label_families(candidate, gap)
        if residue_counter(candidate_d, modulus) != original_d_hist:
            continue
        if residue_counter(candidate_s, modulus) != original_s_hist:
            continue
        collisions = cross_collisions(candidate, gap)
        if collisions:
            answer = candidate
            break
    record: dict[str, object] = {
        "m": modulus,
        "estimated_box": box,
        "nodes": min(nodes, max_nodes),
        "exhausted": nodes <= max_nodes,
        "found": answer is not None,
    }
    if answer is not None:
        original_profile = modulus_profile(z, gap, modulus)
        twin_profile = modulus_profile(answer, gap, modulus)
        for key in ("z_hist", "d_hist", "s_hist", "cross", "d_internal", "s_internal"):
            assert original_profile[key] == twin_profile[key]
        record.update(
            {
                "lifted_z": answer,
                "cross_collisions": cross_collisions(answer, gap),
                "profile": original_profile,
            }
        )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, action="append")
    parser.add_argument("--max-nodes", type=int, default=2_000_000)
    args = parser.parse_args()
    wanted = set(args.p or [p for p, _, _ in WITNESSES])
    for p, theta, lower in WITNESSES:
        if p not in wanted:
            continue
        z, gap = normalize(theta, lower)
        candidates = []
        for modulus in range(p, p * p + 1):
            _, box = grouped_options(z, modulus)
            if box > 1:
                candidates.append((box, modulus))
        candidates.sort()
        attempts = []
        twin = None
        for _, modulus in candidates:
            record = search_one(z, gap, modulus, args.max_nodes)
            attempts.append({key: record[key] for key in ("m", "estimated_box", "nodes", "exhausted", "found")})
            if record["found"]:
                twin = record
                break
        print(json.dumps({"p": p, "theta": theta, "z": z, "gap": gap, "attempts": attempts, "twin": twin}, sort_keys=True))


if __name__ == "__main__":
    main()
