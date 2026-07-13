"""Exact DFS search for residue-indistinguishable signed-ruler lift twins.

The candidate has the same p, G, W, and indexed residues modulo m as a valid
witness.  It must remain an integer Sidon ruler but acquire a forbidden
difference/shifted-sum equality.  A found twin is a literal falsifier to any
single-modulus criterion that sees only those residue histograms and their
aggregate collision (wrap) counts.
"""

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path


HERE = Path(__file__).resolve().parent
AUDIT = runpy.run_path(str(HERE / "residue_phase_audit.py"))
WITNESSES = AUDIT["WITNESSES"]
normalize = AUDIT["normalize"]
is_sidon = AUDIT["is_sidon"]
cross_collisions = AUDIT["cross_collisions"]
same_profile = AUDIT["same_profile"]
modulus_profile = AUDIT["modulus_profile"]


def choices_for(z: list[int], modulus: int) -> list[list[int]]:
    width = z[-1]
    choices: list[list[int]] = []
    for i, value in enumerate(z):
        if i == 0 or i == len(z) - 1:
            choices.append([value])
            continue
        residue = value % modulus
        choices.append(list(range(residue, width + 1, modulus)))
    return choices


def estimated_box(choices: list[list[int]]) -> int:
    out = 1
    for options in choices:
        out *= len(options)
        if out > 10**12:
            return 10**12
    return out


def search_one(z: list[int], gap: int, modulus: int, max_nodes: int) -> dict[str, object]:
    options = choices_for(z, modulus)
    p = len(z)
    nodes = 0
    selected: list[int] = []
    pair_sums: set[int] = set()
    answer: list[int] | None = None

    def dfs(index: int) -> None:
        nonlocal nodes, answer
        if answer is not None or nodes >= max_nodes:
            return
        nodes += 1
        if index == p:
            if selected == z:
                return
            collisions = cross_collisions(selected, gap)
            if collisions:
                answer = selected.copy()
            return

        lower = selected[-1] + 1 if selected else 0
        upper = z[-1] - (p - 1 - index)
        for value in options[index]:
            if value < lower or value > upper:
                continue
            new_sums = [value + old for old in selected] + [2 * value]
            if len(new_sums) != len(set(new_sums)):
                continue
            if any(total in pair_sums for total in new_sums):
                continue
            selected.append(value)
            pair_sums.update(new_sums)
            dfs(index + 1)
            for total in new_sums:
                pair_sums.remove(total)
            selected.pop()
            if answer is not None or nodes >= max_nodes:
                return

    dfs(0)
    record: dict[str, object] = {
        "m": modulus,
        "estimated_box": estimated_box(options),
        "nodes": nodes,
        "exhausted": nodes < max_nodes,
    }
    if answer is not None:
        assert is_sidon(answer)
        assert same_profile(z, answer, gap, modulus)
        original_profile = modulus_profile(z, gap, modulus)
        lifted_profile = modulus_profile(answer, gap, modulus)
        for key in ("z_hist", "d_hist", "s_hist", "cross", "d_internal", "s_internal"):
            assert original_profile[key] == lifted_profile[key]
        record.update(
            {
                "found": True,
                "lifted_z": answer,
                "cross_collisions": cross_collisions(answer, gap),
                "profile": original_profile,
            }
        )
    else:
        record["found"] = False
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
            options = choices_for(z, modulus)
            box = estimated_box(options)
            if box > 1:
                candidates.append((box, modulus))
        candidates.sort()
        result = None
        attempts = []
        for _, modulus in candidates:
            record = search_one(z, gap, modulus, args.max_nodes)
            attempts.append({key: record[key] for key in ("m", "estimated_box", "nodes", "exhausted", "found")})
            if record["found"]:
                result = record
                break
        print(
            json.dumps(
                {
                    "p": p,
                    "theta": theta,
                    "z": z,
                    "gap": gap,
                    "attempts": attempts,
                    "twin": result,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
