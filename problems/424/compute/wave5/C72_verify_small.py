#!/usr/bin/env python3
"""Independent small-range verifier for C72.

This file deliberately does not import C67.  It reconstructs admissible
factor pairs by trial division and the least generated set by ascending
recursion, then replays the C72 lemmas and displayed falsifiers.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


DIVISORS = (3, 5, 9, 17, 27, 33)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def up(n: int) -> int:
    return 2 * n - 1


def pairs(n: int) -> list[tuple[int, int]]:
    total = n + 1
    out = []
    a = 2
    while a * a < total:
        if total % a == 0:
            b = total // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def is_hard(n: int, pair_map: list[list[tuple[int, int]]]) -> bool:
    if n % 2 or not pair_map[n]:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def factor3_depth(root: int) -> int:
    residue = root % 9
    if residue in (0, 3):
        return 0
    if residue == 2:
        return 1
    if residue == 6:
        return 2
    raise AssertionError((root, residue))


def verify(limit: int) -> dict:
    if limit < 12_000:
        raise ValueError("--limit must be at least 12000")

    pair_map = [[] for _ in range(limit + 1)]
    generated = set()
    holes = set()
    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        pair_map[n] = pairs(n)
        if n in (2, 3) or any(
            a in generated and b in generated for a, b in pair_map[n]
        ):
            generated.add(n)
        else:
            holes.add(n)

    splitless = {n for n in holes if not pair_map[n]}
    hard = {n for n in holes if is_hard(n, pair_map)}
    if any(g not in generated for g in DIVISORS):
        raise AssertionError("fixed divisor is not generated")

    active_delta = [0] * (limit + 2)
    mature_delta = [0] * (limit + 2)
    fixed3_image_to_root = {}
    intervals = {}
    for root in sorted(hard):
        if root % 9 not in (0, 2, 3, 6):
            raise AssertionError(("hard residue", root, root % 9))
        chain = [root]
        while up(chain[-1]) <= limit and up(chain[-1]) in holes:
            chain.append(up(chain[-1]))
        death = up(chain[-1]) if up(chain[-1]) <= limit else limit + 1
        if death <= limit and death not in generated:
            raise AssertionError(("death", root, death))
        active_delta[root] += 1
        if death <= limit:
            active_delta[death] -= 1
        intervals[root] = (root, death, chain)

        if any(node in splitless for node in chain):
            raise AssertionError(("splitless chain node", root))

        depth = factor3_depth(root)
        parent = root
        for _ in range(depth):
            parent = up(parent)
        image = 2 * parent // 3
        gate = up(parent)
        if parent % 9 not in (0, 3) or not allowed(image):
            raise AssertionError(("factor3 arithmetic", root, parent, image))
        if gate <= limit and gate in holes:
            if image not in holes:
                raise AssertionError(("factor3 image", root, image))
            if image in fixed3_image_to_root:
                raise AssertionError(
                    ("factor3 collision", fixed3_image_to_root[image], root, image)
                )
            fixed3_image_to_root[image] = root
            mature_delta[gate] += 1
            if death <= limit:
                mature_delta[death] -= 1

    hard_prefix = [0] * (limit + 1)
    splitless_prefix = [0] * (limit + 1)
    active = 0
    mature = 0
    first_shell_failure = None
    for cutoff in range(2, limit + 1):
        active += active_delta[cutoff]
        mature += mature_delta[cutoff]
        hard_prefix[cutoff] = hard_prefix[cutoff - 1] + int(cutoff in hard)
        splitless_prefix[cutoff] = (
            splitless_prefix[cutoff - 1] + int(cutoff in splitless)
        )
        shell = hard_prefix[cutoff] - hard_prefix[(cutoff + 1) // 2]
        if shell > active and first_shell_failure is None:
            first_shell_failure = (cutoff, shell, active)
        if mature > active:
            raise AssertionError(("mature", cutoff, mature, active))

    # Replay the two explicit non-splitless images.
    for root, child, divisor, image, image_kind in (
        (174, 347, 3, 116, "seed3"),
        (1110, 2219, 5, 444, "hard"),
    ):
        if root not in hard or child not in holes or divisor * image != child + 1:
            raise AssertionError(("displayed divisor witness", root))
        actual = (
            "splitless"
            if image in splitless
            else "hard"
            if image in hard
            else "seed3"
        )
        if actual != image_kind:
            raise AssertionError(("displayed image type", image, actual, image_kind))

    # Independently reconstruct the deterministic union map and its first
    # overlapping collision interval.
    selected = []
    for root, (_, death, chain) in intervals.items():
        choice = None
        usable_chain = chain[:-1] if death <= limit else chain
        for depth, parent in enumerate(usable_chain):
            child = up(parent)
            if child > limit or child not in holes:
                break
            for divisor in DIVISORS:
                if parent % divisor:
                    continue
                image = 2 * parent // divisor
                if allowed(image) and image != divisor:
                    if tuple(sorted((divisor, image))) not in pair_map[child]:
                        raise AssertionError(("pair replay", child, divisor, image))
                    if image not in holes:
                        raise AssertionError(("hole replay", child, image))
                    choice = {
                        "root": root,
                        "start": child,
                        "death": death,
                        "depth": depth,
                        "divisor": divisor,
                        "image": image,
                    }
                    break
            if choice is not None:
                break
        if choice is not None:
            selected.append(choice)

    by_image = defaultdict(list)
    for row in selected:
        by_image[row["image"]].append(row)
    first_collision = None
    for image, rows in by_image.items():
        rows.sort(key=lambda row: (row["start"], row["root"]))
        longest = None
        for row in rows:
            if longest is not None and longest["death"] > row["start"]:
                candidate = {
                    "cutoff": row["start"],
                    "image": image,
                    "roots": [longest["root"], row["root"]],
                    "divisors": [longest["divisor"], row["divisor"]],
                }
                if first_collision is None or (
                    candidate["cutoff"], candidate["image"]
                ) < (first_collision["cutoff"], first_collision["image"]):
                    first_collision = candidate
            if longest is None or row["death"] > longest["death"]:
                longest = row

    expected_collision = {
        "cutoff": 2819,
        "image": 564,
        "roots": [846, 1410],
        "divisors": [3, 5],
    }
    if first_collision != expected_collision:
        raise AssertionError(("first collision", first_collision))

    checkpoint = 5_000
    active_at_checkpoint = sum(
        birth <= checkpoint < death for birth, death, _ in intervals.values()
    )
    mature_at_checkpoint = sum(
        root in fixed3_image_to_root.values()
        and up(
            next(
                node
                for depth, node in enumerate(intervals[root][2])
                if depth == factor3_depth(root)
            )
        )
        <= checkpoint
        < intervals[root][1]
        for root in hard
    )
    return {
        "limit": limit,
        "constructor": "independent trial division",
        "hard": len(hard),
        "splitless": len(splitless),
        "fixed3_distinct_images": len(fixed3_image_to_root),
        "fresh_shell_first_failure": first_shell_failure,
        "first_union_collision": first_collision,
        "checkpoint_5000": {
            "hard": hard_prefix[checkpoint],
            "persistent_hard": active_at_checkpoint,
            "factor3_mature_persistent": mature_at_checkpoint,
            "splitless_upper_shell": (
                splitless_prefix[checkpoint]
                - splitless_prefix[checkpoint // 2]
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=12_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
