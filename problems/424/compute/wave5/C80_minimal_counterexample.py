#!/usr/bin/env python3
"""Exact obstruction to a blocker-local least-counterexample induction.

The source is the infinite forward closure of {2, 3, 21}.  Since every
allowed product output is larger than both of its distinct factors, its
prefix through a cutoff is computed exactly by ascending trial division.
No optimizer or floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from pathlib import Path


CUTOFF = 74
GENERATORS = {2, 3, 21}


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result: list[tuple[int, int]] = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def hard_shape(value: int) -> bool:
    pairs = admissible_pairs(value)
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def seed_root(value: int) -> int:
    while value % 2:
        value = (value + 1) // 2
    return value


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def closure_prefix(generators: set[int], cutoff: int) -> set[int]:
    members = {value for value in generators if value <= cutoff}
    for value in range(2, cutoff + 1):
        if not allowed(value) or value in members:
            continue
        if any(
            left in members and right in members
            for left, right in admissible_pairs(value)
        ):
            members.add(value)
    return members


def image_prefix(source: set[int], cutoff: int) -> set[int]:
    image = {2, 3}
    for value in range(4, cutoff + 1):
        if not allowed(value):
            continue
        if any(
            left in source and right in source
            for left, right in admissible_pairs(value)
        ):
            image.add(value)
    return image


def check_forward_closed(source: set[int], cutoff: int) -> None:
    if not {2, 3}.issubset(source):
        raise RuntimeError("source omits a seed")
    for value in range(4, cutoff + 1):
        for left, right in admissible_pairs(value):
            if left in source and right in source and value not in source:
                raise RuntimeError(
                    f"closure failure: {left}*{right}-1={value}"
                )


def hard_holes_and_boundaries(
    members: set[int], cutoff: int
) -> tuple[list[int], list[int]]:
    hard_holes = [
        value
        for value in range(2, cutoff + 1)
        if allowed(value) and hard_shape(value) and value not in members
    ]
    boundaries = [
        2 * parent - 1
        for parent in range(2, (cutoff + 1) // 2 + 1)
        if allowed(parent)
        and parent not in members
        and 2 * parent - 1 in members
    ]
    return hard_holes, boundaries


def shell_sets(members: set[int], cutoff: int) -> tuple[list[int], list[int]]:
    unhealed_hard: list[int] = []
    healed_nonhard: list[int] = []
    for root in range(2, cutoff + 1, 2):
        if not allowed(root) or root in members:
            continue
        healed = chain_top(root, cutoff) in members
        if hard_shape(root):
            if not healed:
                unhealed_hard.append(root)
        elif healed:
            healed_nonhard.append(root)
    return unhealed_hard, healed_nonhard


def blocker_reach(
    start: int, present: set[int], image: set[int], cutoff: int
) -> tuple[set[int], list[dict[str, object]]]:
    """Close under every absent factor on a missing image chain."""
    reached = {start}
    queue = deque([start])
    trace: list[dict[str, object]] = []
    while queue:
        root = queue.popleft()
        value = root
        while value <= cutoff and value not in image:
            for left, right in admissible_pairs(value):
                blockers = [parent for parent in (left, right) if parent not in present]
                trace.append(
                    {
                        "root": root,
                        "chain_value": value,
                        "pair": [left, right],
                        "missing_endpoints": blockers,
                    }
                )
                for blocker in blockers:
                    next_root = seed_root(blocker)
                    if next_root not in reached:
                        reached.add(next_root)
                        queue.append(next_root)
            value = 2 * value - 1
    return reached, trace


def maximum_matching(graph: dict[int, set[int]]) -> dict[int, int]:
    right_to_left: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in sorted(graph[left]):
            if right in seen:
                continue
            seen.add(right)
            if right not in right_to_left or augment(right_to_left[right], seen):
                right_to_left[right] = left
                return True
        return False

    for left in sorted(graph):
        augment(left, set())
    return {left: right for right, left in right_to_left.items()}


def audit() -> dict[str, object]:
    source = closure_prefix(GENERATORS, CUTOFF)
    check_forward_closed(source, CUTOFF)
    image = image_prefix(source, CUTOFF)
    check_forward_closed(image, CUTOFF)

    expected_source = {
        2, 3, 5, 9, 14, 17, 21, 26, 27, 33, 41, 44, 50, 51, 53,
        62, 65, 69,
    }
    expected_image = expected_source - {21}
    if source != expected_source:
        raise RuntimeError(f"unexpected source prefix: {sorted(source)}")
    if image != expected_image:
        raise RuntimeError(f"unexpected image prefix: {sorted(image)}")

    hard_73, boundary_73 = hard_holes_and_boundaries(image, 73)
    hard_74, boundary_74 = hard_holes_and_boundaries(image, 74)
    if (hard_73, boundary_73) != ([54], [41, 69]):
        raise RuntimeError("unexpected event lists at cutoff 73")
    if (hard_74, boundary_74) != ([54, 74], [41, 69]):
        raise RuntimeError("unexpected event lists at cutoff 74")

    unhealed_73, healed_73 = shell_sets(image, 73)
    unhealed_74, healed_74 = shell_sets(image, 74)
    if (unhealed_73, healed_73) != ([54], [6, 18]):
        raise RuntimeError("unexpected shell at cutoff 73")
    if (unhealed_74, healed_74) != ([54, 74], [6, 18]):
        raise RuntimeError("unexpected shell at cutoff 74")

    if len(boundary_74) - len(hard_74) != len(healed_74) - len(unhealed_74):
        raise RuntimeError("C78 shell identity failed")

    source_reaches: dict[int, set[int]] = {}
    image_reaches: dict[int, set[int]] = {}
    source_traces: dict[str, list[dict[str, object]]] = {}
    image_traces: dict[str, list[dict[str, object]]] = {}
    graph: dict[int, set[int]] = {}
    for hard in unhealed_74:
        source_reach, source_trace = blocker_reach(
            hard, source, image, CUTOFF
        )
        image_reach, image_trace = blocker_reach(
            hard, image, image, CUTOFF
        )
        source_reaches[hard] = source_reach
        image_reaches[hard] = image_reach
        source_traces[str(hard)] = source_trace
        image_traces[str(hard)] = image_trace
        graph[hard] = image_reach & set(healed_74)
    matching = maximum_matching(graph)
    expected_reaches = {54: {54, 6}, 74: {74, 8, 6}}
    if source_reaches != expected_reaches:
        raise RuntimeError(f"unexpected source-blocker closure: {source_reaches}")
    if image_reaches != expected_reaches:
        raise RuntimeError(f"unexpected image-hole closure: {image_reaches}")
    if graph != {54: {6}, 74: {6}} or len(matching) != 1:
        raise RuntimeError("expected the 2-to-1 local Hall obstruction")

    grounded = closure_prefix({2, 3}, CUTOFF)
    grounded_image = image_prefix(grounded, CUTOFF)
    expected_grounded = {
        2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69,
    }
    if grounded != expected_grounded or grounded_image != grounded:
        raise RuntimeError("unexpected canonical grounded prefix")
    grounded_hard, grounded_boundaries = hard_holes_and_boundaries(
        grounded, CUTOFF
    )
    grounded_unhealed, grounded_healed = shell_sets(grounded, CUTOFF)
    grounded_reaches = {
        hard: blocker_reach(hard, grounded, grounded, CUTOFF)[0]
        for hard in grounded_unhealed
    }
    if (grounded_hard, grounded_boundaries) != (hard_74, boundary_74):
        raise RuntimeError("grounded event lists differ from the image witness")
    if (grounded_unhealed, grounded_healed) != (unhealed_74, healed_74):
        raise RuntimeError("grounded shell differs from the image witness")
    if grounded_reaches != expected_reaches:
        raise RuntimeError("grounded blocker closure differs from the image witness")

    hard_shapes = [
        value
        for value in range(2, CUTOFF + 1)
        if allowed(value) and hard_shape(value)
    ]
    if hard_shapes != [54, 74]:
        raise RuntimeError(f"unexpected hard shapes: {hard_shapes}")
    if admissible_pairs(8) or hard_shape(8):
        raise RuntimeError("the excluded equal pair 3*3 was admitted")
    if admissible_pairs(54) != [(5, 11)]:
        raise RuntimeError("bad factor audit for 54")
    if admissible_pairs(74) != [(5, 15)]:
        raise RuntimeError("bad factor audit for 74")
    if 25 % 3 != 1:
        raise RuntimeError("the rejected 3*25 cofactor is not forbidden")
    for hard in hard_shapes:
        if hard % 6 not in (0, 2):
            raise RuntimeError(f"bad hard parity at {hard}")
        for left, right in admissible_pairs(hard):
            if left == right or not (left % 2 and right % 2):
                raise RuntimeError(f"parity/distinctness failure at {hard}")

    return {
        "schema_version": 1,
        "source_definition": "least forward-closed allowed set containing 2,3,21",
        "cutoff": CUTOFF,
        "source_prefix": sorted(source),
        "image_prefix": sorted(image),
        "unsupported_source_prefix": sorted(source - image),
        "least_step": {
            "at_73": {
                "hard_holes": hard_73,
                "boundary_children": boundary_73,
                "Q_minus_H": len(boundary_73) - len(hard_73),
                "unhealed_hard_roots": unhealed_73,
                "healed_nonhard_roots": healed_73,
            },
            "at_74": {
                "hard_holes": hard_74,
                "boundary_children": boundary_74,
                "Q_minus_H": len(boundary_74) - len(hard_74),
                "unhealed_hard_roots": unhealed_74,
                "healed_nonhard_roots": healed_74,
            },
        },
        "complete_source_blocker_reach": {
            str(hard): sorted(reach) for hard, reach in source_reaches.items()
        },
        "complete_image_hole_reach": {
            str(hard): sorted(reach) for hard, reach in image_reaches.items()
        },
        "reachable_healed_nonhard": {
            str(hard): sorted(graph[hard]) for hard in sorted(graph)
        },
        "local_matching": {
            "size": len(matching),
            "required": len(unhealed_74),
            "matching": {str(left): right for left, right in sorted(matching.items())},
        },
        "unreachable_reserve_root": 18,
        "source_blocker_trace": source_traces,
        "image_hole_trace": image_traces,
        "canonical_grounded_replay": {
            "source_definition": "least forward-closed allowed set containing 2,3",
            "source_equals_image_through_cutoff": True,
            "prefix": sorted(grounded),
            "hard_holes": grounded_hard,
            "boundary_children": grounded_boundaries,
            "unhealed_hard_roots": grounded_unhealed,
            "healed_nonhard_roots": grounded_healed,
            "complete_reach": {
                str(hard): sorted(reach)
                for hard, reach in grounded_reaches.items()
            },
        },
        "parity_and_distinct_factor_audit": {
            "hard_shapes": hard_shapes,
            "hard_residues_mod_6": {str(value): value % 6 for value in hard_shapes},
            "pairs_54": [list(pair) for pair in admissible_pairs(54)],
            "pairs_74": [list(pair) for pair in admissible_pairs(74)],
            "rejected_74_pair": [3, 25],
            "rejected_74_reason": "25 is 1 modulo 3",
            "pairs_8": [],
            "rejected_8_pair": [3, 3],
            "rejected_8_reason": "equal factors",
            "seed_2_equal_exception": "2*2-1=3 is excluded and 3 is inserted as a seed",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
