#!/usr/bin/env python3
"""Exact gates for the C72 persistent-hard-root sieve.

The arithmetic constructor is imported from C67 so that this audit uses the
same distinct-factor convention and hard/splitless definitions.  All claims
reported as exhaustive are checked at every integer cutoff through --limit.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from array import array
from collections import defaultdict
from pathlib import Path
from types import ModuleType


FIXED_GENERATED_DIVISORS = (3, 5, 9, 17, 27, 33)
HARD_RESIDUES_MOD_9 = {0, 2, 3, 6}


def load_c67() -> ModuleType:
    root = Path(__file__).resolve().parents[4]
    path = root / "problems/424/fanout/wave5/C67_weak_scb.py"
    spec = importlib.util.spec_from_file_location("c67_weak_scb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def up(n: int) -> int:
    return 2 * n - 1


def factor3_depth(root: int) -> int:
    residue = root % 9
    if residue in (0, 3):
        return 0
    if residue == 2:
        return 1
    if residue == 6:
        return 2
    raise AssertionError(("hard residue", root, residue))


def hole_type(n: int, data: dict) -> str:
    if n in data["splitless"]:
        return "splitless"
    if n in data["hard"]:
        return "hard"
    if n in data["seed3_roots"]:
        return "seed3"
    if n in data["holes"]:
        return "nonroot"
    return "generated"


def event_record(
    root: int,
    depth: int,
    parent: int,
    child: int,
    divisor: int,
    image: int,
    death: int,
    data: dict,
) -> dict:
    return {
        "root": root,
        "depth": depth,
        "parent": parent,
        "child": child,
        "divisor": divisor,
        "image": image,
        "image_type": hole_type(image, data),
        "image_pairs": [list(pair) for pair in data["pairs"][image]],
        "active_until_exclusive": death,
    }


def scan(limit: int) -> dict:
    if limit < 74:
        raise ValueError("--limit must be at least 74")

    c67 = load_c67()
    data = c67.build_arithmetic(limit)
    holes: set[int] = data["holes"]
    generated: set[int] = data["generated"]
    hard: set[int] = data["hard"]
    splitless: set[int] = data["splitless"]

    for divisor in FIXED_GENERATED_DIVISORS:
        if divisor not in generated or divisor % 2 == 0:
            raise AssertionError(("fixed divisor is not odd generated", divisor))

    active_delta = array("i", [0]) * (limit + 2)
    mature_delta = array("i", [0]) * (limit + 2)
    hard_prefix = array("I", [0]) * (limit + 1)
    splitless_prefix = array("I", [0]) * (limit + 1)

    fixed3_events: list[dict] = []
    selected_events: list[dict] = []
    first_survival: dict[int, dict] = {}
    first_nonsplitless: dict[int, dict] = {}
    fixed3_images: dict[int, int] = {}

    for root in sorted(hard):
        if root % 9 not in HARD_RESIDUES_MOD_9:
            raise AssertionError(("hard residue classification", root, root % 9))

        chain: list[int] = [root]
        parent = root
        while up(parent) <= limit and up(parent) in holes:
            parent = up(parent)
            chain.append(parent)
        death = up(parent) if up(parent) <= limit else limit + 1
        if death <= limit and death not in generated:
            raise AssertionError(("chain exit is not generated", root, death))

        active_delta[root] += 1
        if death <= limit:
            active_delta[death] -= 1

        # A hard root is reducible, and every proper chain descendant has its
        # distinct seed-2 split.  Thus the injective top map never reaches E.
        for node in chain:
            if node in splitless:
                raise AssertionError(("hard-chain node is splitless", root, node))

        depth3 = factor3_depth(root)
        parent3 = root
        for _ in range(depth3):
            parent3 = up(parent3)
        if parent3 % 9 not in (0, 3):
            raise AssertionError(("factor-3 parent residue", root, parent3))
        image3 = 2 * parent3 // 3
        gate3 = up(parent3)
        if not c67.allowed(image3) or 3 * image3 != gate3 + 1:
            raise AssertionError(("factor-3 arithmetic", root, parent3, image3))
        if gate3 <= limit and gate3 in holes:
            if image3 not in holes:
                raise AssertionError(("persistent factor-3 image", root, image3))
            if image3 in fixed3_images:
                raise AssertionError(
                    ("factor-3 injection", fixed3_images[image3], root, image3)
                )
            fixed3_images[image3] = root
            record = event_record(
                root, depth3, parent3, gate3, 3, image3, death, data
            )
            fixed3_events.append(record)
            mature_delta[gate3] += 1
            if death <= limit:
                mature_delta[death] -= 1

        selected: dict | None = None
        for depth, node in enumerate(chain[:-1] if death <= limit else chain):
            child = up(node)
            if child > limit or child not in holes:
                break
            for divisor in FIXED_GENERATED_DIVISORS:
                if node % divisor:
                    continue
                image = 2 * node // divisor
                if not c67.allowed(image) or image == divisor:
                    continue
                pair = tuple(sorted((divisor, image)))
                if pair not in data["pairs"][child]:
                    raise AssertionError(("missing admissible pair", child, pair))
                if image not in holes:
                    raise AssertionError(
                        ("fixed generated divisor did not force a hole", child, pair)
                    )
                record = event_record(
                    root, depth, node, child, divisor, image, death, data
                )
                prior = first_survival.get(divisor)
                if prior is None or (child, root, depth) < (
                    prior["child"],
                    prior["root"],
                    prior["depth"],
                ):
                    first_survival[divisor] = record
                if image not in splitless:
                    prior = first_nonsplitless.get(divisor)
                    if prior is None or (child, root, depth) < (
                        prior["child"],
                        prior["root"],
                        prior["depth"],
                    ):
                        first_nonsplitless[divisor] = record
                if selected is None:
                    selected = record
        if selected is not None:
            selected_events.append(selected)

    # Find the first collision for the deterministic union rule: least chain
    # depth, then the displayed fixed-divisor order.
    by_image: dict[int, list[dict]] = defaultdict(list)
    for record in selected_events:
        by_image[record["image"]].append(record)
    first_collision: dict | None = None
    for image, records in by_image.items():
        records.sort(key=lambda row: (row["child"], row["root"]))
        longest: dict | None = None
        for current in records:
            if (
                longest is not None
                and longest["active_until_exclusive"] > current["child"]
            ):
                candidate = {
                    "cutoff": current["child"],
                    "image": image,
                    "first": longest,
                    "second": current,
                }
                key = (candidate["cutoff"], image)
                if first_collision is None or key < (
                    first_collision["cutoff"],
                    first_collision["image"],
                ):
                    first_collision = candidate
            if longest is None or current["active_until_exclusive"] > longest[
                "active_until_exclusive"
            ]:
                longest = current

    checkpoints_requested = [
        74,
        186,
        318,
        539,
        1_000,
        5_000,
        10_000,
        100_000,
        1_000_000,
    ]
    checkpoints = {x for x in checkpoints_requested if x <= limit}
    checkpoint_rows: list[dict] = []
    active = 0
    mature = 0
    hard_count = 0
    splitless_count = 0
    first_shell_failure = None
    first_scalar_failure = None
    max_scalar_ratio = (0, 1, 0)
    for cutoff in range(2, limit + 1):
        active += active_delta[cutoff]
        mature += mature_delta[cutoff]
        hard_count += int(cutoff in hard)
        splitless_count += int(cutoff in splitless)
        hard_prefix[cutoff] = hard_count
        splitless_prefix[cutoff] = splitless_count

        root_parent_cutoff = (cutoff + 1) // 2
        hard_fresh_shell = hard_count - hard_prefix[root_parent_cutoff]
        if hard_fresh_shell > active and first_shell_failure is None:
            first_shell_failure = {
                "cutoff": cutoff,
                "hard_fresh_shell": hard_fresh_shell,
                "persistent_hard": active,
            }
        if mature > active:
            raise AssertionError(("mature exceeds active", cutoff, mature, active))

        splitless_upper_shell = (
            splitless_count - splitless_prefix[cutoff // 2]
        )
        if active > splitless_upper_shell and first_scalar_failure is None:
            first_scalar_failure = {
                "cutoff": cutoff,
                "persistent_hard": active,
                "splitless_upper_shell": splitless_upper_shell,
            }
        if (
            splitless_upper_shell
            and active * max_scalar_ratio[1]
            > max_scalar_ratio[0] * splitless_upper_shell
        ):
            max_scalar_ratio = (active, splitless_upper_shell, cutoff)

        if cutoff in checkpoints:
            checkpoint_rows.append(
                {
                    "cutoff": cutoff,
                    "hard": hard_count,
                    "persistent_hard": active,
                    "factor3_mature_persistent": mature,
                    "factor3_fresh_remainder": active - mature,
                    "hard_fresh_shell": hard_fresh_shell,
                    "splitless_upper_shell": splitless_upper_shell,
                }
            )

    expected_active = sum(
        data["top_of_root"][root] in holes for root in hard
    )
    if active != expected_active:
        raise AssertionError(("terminal active replay", active, expected_active))

    final_mature = [
        row
        for row in fixed3_events
        if row["child"] <= limit < row["active_until_exclusive"]
    ]
    final_image_types = defaultdict(int)
    for row in final_mature:
        final_image_types[row["image_type"]] += 1

    return {
        "limit": limit,
        "definitions_source": "problems/424/fanout/wave5/C67_weak_scb.py",
        "checked_every_cutoff": [2, limit],
        "hard_residues_mod_9": sorted(HARD_RESIDUES_MOD_9),
        "fresh_shell_lower_bound_first_failure": first_shell_failure,
        "scalar_AH_le_splitless_upper_shell_first_failure": first_scalar_failure,
        "max_scalar_ratio": {
            "numerator": max_scalar_ratio[0],
            "denominator": max_scalar_ratio[1],
            "cutoff": max_scalar_ratio[2],
        },
        "factor3_map": {
            "depth_by_hard_residue": {"0,3": 0, "2": 1, "6": 2},
            "globally_distinct_images_checked": len(fixed3_images),
            "active_mature_at_limit": len(final_mature),
            "active_image_types_at_limit": dict(sorted(final_image_types.items())),
        },
        "fixed_generated_divisors": list(FIXED_GENERATED_DIVISORS),
        "first_persistent_divisibility_witness": {
            str(key): first_survival[key] for key in FIXED_GENERATED_DIVISORS
        },
        "first_nonsplitless_fixed_divisor_image": {
            str(key): first_nonsplitless.get(key)
            for key in FIXED_GENERATED_DIVISORS
        },
        "first_collision_for_least_depth_then_divisor_map": first_collision,
        "checkpoints": checkpoint_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result["checkpoints"][-1], sort_keys=True))


if __name__ == "__main__":
    main()
