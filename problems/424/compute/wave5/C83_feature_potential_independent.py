#!/usr/bin/env python3
"""Independent exact replay of the C83 X=186 feature-Hall obstruction.

This verifier uses only the Python standard library and does not import either
C83 synthesis program.  It reconstructs the grounded set, its one-step image,
the shell sets, obstruction ranks, and the full local feature partition.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


X = 186
EXPECTED_SOURCE = {
    2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69,
    77, 80, 81, 84, 87, 98, 99, 101, 105, 122, 125, 129, 131, 134,
    137, 149, 152, 153, 158, 159, 161, 164, 167, 173,
}
EXPECTED_HARD = {54, 74, 114, 144, 174, 186}
EXPECTED_HEALED = {6, 18, 20, 32, 38, 66}


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs(n: int) -> tuple[tuple[int, int], ...]:
    out = []
    for a in range(2, math.isqrt(n + 1) + 1):
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if a < b and allowed(a) and allowed(b):
                out.append((a, b))
    return tuple(out)


VALUES = tuple(n for n in range(2, X + 1) if allowed(n))
PAIRS = {n: pairs(n) for n in VALUES}


def closure() -> set[int]:
    result = {2, 3}
    for n in VALUES:
        if any(a in result and b in result for a, b in PAIRS[n]):
            result.add(n)
    return result


def image(source: set[int]) -> set[int]:
    result = {2, 3}
    for n in VALUES:
        if any(a in source and b in source for a, b in PAIRS[n]):
            result.add(n)
    return result


def hard_shape(n: int) -> bool:
    if n % 2 or not PAIRS[n]:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def top(root: int) -> int:
    n = root
    while 2 * n - 1 <= X:
        n = 2 * n - 1
    return n


def ranks(generated: set[int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for n in VALUES:
        if n in generated:
            continue
        if not PAIRS[n]:
            result[n] = 0
            continue
        minima = []
        for a, b in PAIRS[n]:
            blockers = [result[z] for z in (a, b) if z not in generated]
            require(blockers, ("grounded pair for hole", n, a, b))
            minima.append(min(blockers))
        result[n] = 1 + max(minima)
    return result


def scale(outer: int, inner: int) -> int:
    return (outer // inner).bit_length() - 1


def endpoint_feature(z: int, n: int, generated: set[int], rank: dict[int, int]) -> tuple:
    state = ("G",) if z in generated else ("H", rank[z])
    return state + (z % 6, scale(n, z))


def feature(n: int, side: str, generated: set[int], rank: dict[int, int]) -> tuple:
    kind = "hard" if side == "H" else ("splitless" if not PAIRS[n] else "seed3")
    factor_rows = []
    for a, b in PAIRS[n]:
        factor_rows.append(tuple(sorted((
            endpoint_feature(a, n, generated, rank),
            endpoint_feature(b, n, generated, rank),
        ))))
    return (
        kind,
        n % 18,
        rank[n],
        scale(X, n),
        len(PAIRS[n]),
        tuple(sorted(factor_rows)),
    )


def main() -> None:
    generated = closure()
    supported = image(generated)
    require(generated == EXPECTED_SOURCE, "grounded-prefix mismatch")
    require(supported == generated, "grounded image is not fixed")

    hard_roots = {
        n for n in VALUES
        if n % 2 == 0 and n not in generated and hard_shape(n) and top(n) not in generated
    }
    target_roots = {
        n for n in VALUES
        if n % 2 == 0 and n not in generated and not hard_shape(n) and top(n) > n
    }
    unhealed = {n for n in hard_roots if top(n) not in supported}
    healed = {n for n in target_roots if n not in supported and top(n) in supported}
    require(hard_roots == EXPECTED_HARD == unhealed, "hard-shell mismatch")
    require(healed == EXPECTED_HEALED, "healed-shell mismatch")

    rank = ranks(generated)
    hard_classes: dict[tuple, list[int]] = defaultdict(list)
    target_classes: dict[tuple, list[int]] = defaultdict(list)
    for n in hard_roots:
        hard_classes[feature(n, "H", generated, rank)].append(n)
    for n in target_roots:
        target_classes[feature(n, "N", generated, rank)].append(n)

    require(len(hard_classes) == 6, "hard classes are not six singletons")
    require(all(len(c) == 1 for c in hard_classes.values()), "non-singleton hard class")
    f48 = feature(48, "N", generated, rank)
    f66 = feature(66, "N", generated, rank)
    require(f48 == f66, "48/66 feature collision missing")
    require(sorted(target_classes[f48]) == [48, 66], "collision class mismatch")
    require(66 in healed and 48 not in healed, "collision does not mix shell states")

    # Because every hard root is unhealed in this image, a sound static block
    # can use only a target class wholly contained in the healed set.
    usable = [members for members in target_classes.values() if set(members) <= healed]
    target_capacity = sum(len(members) for members in usable)
    hard_demand = sum(len(members) for members in hard_classes.values())
    require(target_capacity == 5, ("target capacity", target_capacity))
    require(hard_demand == 6, ("hard demand", hard_demand))
    require(hard_demand > target_capacity, "no Hall deficit")

    result = {
        "cutoff": X,
        "grounded_size": len(generated),
        "hard_roots": sorted(unhealed),
        "healed_nonhard_roots": sorted(healed),
        "collision_class": sorted(target_classes[f48]),
        "hard_demand": hard_demand,
        "sound_target_capacity_upper_bound": target_capacity,
        "feature_hall_deficit": hard_demand - target_capacity,
        "independent_standard_library_verification": True,
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps(result, indent=2))
    print("canonical_sha256", hashlib.sha256(encoded).hexdigest().upper())


if __name__ == "__main__":
    main()
