#!/usr/bin/env python3
"""Exact C94 census for persistent hard roots and healed splitless roots.

The script deliberately imports only the accepted arithmetic constructor from
C67.  For a seed-2 root r, its literal chain is

    r, 2r-1, 4r-3, ... .

A hard root is persistent at cutoff X when every literal chain member through
X is a hole.  A structural splitless root is healed when some literal chain
member through X is generated.  All acceptance arithmetic is integral.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
C67_PATH = ROOT / "problems/424/fanout/wave5/C67_weak_scb.py"


def load_c67():
    spec = importlib.util.spec_from_file_location("c67_weak_scb", C67_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {C67_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_top(root: int, limit: int) -> tuple[int, int]:
    value = root
    depth = 0
    while 2 * value - 1 <= limit:
        value = 2 * value - 1
        depth += 1
    return value, depth


def literal_chain(root: int, limit: int) -> list[int]:
    out = []
    value = root
    while value <= limit:
        out.append(value)
        value = 2 * value - 1
    return out


def first_generated_on_chain(root: int, limit: int, generated: set[int]) -> tuple[int | None, int | None]:
    value = root
    depth = 0
    while value <= limit:
        if value in generated:
            return value, depth
        value = 2 * value - 1
        depth += 1
    return None, None


def first_generating_pair(value: int, pairs: dict[int, list[tuple[int, int]]], generated: set[int]) -> tuple[int, int]:
    for a, b in pairs[value]:
        if a in generated and b in generated:
            return a, b
    raise RuntimeError(("generated value has no generating pair", value))


def prime_factors(value: int, spf) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    while value > 1:
        p = int(spf[value])
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        out.append((p, exponent))
    return out


def splitless_type(root: int, spf) -> str:
    factors = prime_factors(root + 1, spf)
    if root + 1 == 9:
        return "square_3"
    if len(factors) == 1 and factors[0][1] == 2 and factors[0][0] % 3 == 2:
        return "square_p2mod3"
    v3 = next((e for p, e in factors if p == 3), 0)
    if any(p % 3 == 2 for p, _ in factors):
        raise RuntimeError(("unclassified splitless root", root, factors))
    if v3 == 0:
        return "semigroup_1mod3"
    if v3 == 1:
        return "three_times_semigroup"
    raise RuntimeError(("unexpected splitless 3-adic exponent", root, factors))


def audit(limit: int) -> dict:
    if limit < 2:
        raise ValueError("limit must be at least 2")
    c67 = load_c67()
    data = c67.build_arithmetic(limit)
    generated: set[int] = data["generated"]
    holes: set[int] = data["holes"]
    hard: set[int] = data["hard"]
    splitless: set[int] = data["splitless"]
    spf = c67.smallest_prime_factors(limit + 1)

    persistent_hard: list[int] = []
    hard_deaths: list[tuple[int, int, int]] = []
    healed_splitless: list[tuple[int, int, int]] = []
    persistent_splitless: list[int] = []
    splitless_types = Counter()
    healed_types = Counter()
    death_depths = Counter()
    death_min_factors = Counter()
    depth_one_min_factors = Counter()

    for root in sorted(hard):
        top, _ = literal_top(root, limit)
        death, depth = first_generated_on_chain(root, limit, generated)
        if top in holes:
            if death is not None:
                raise RuntimeError(("persistent hard root has a death", root, death))
            persistent_hard.append(root)
        else:
            if death is None or depth is None:
                raise RuntimeError(("dead hard root has no death", root, top))
            hard_deaths.append((root, death, depth))

    for root in sorted(splitless):
        kind = splitless_type(root, spf)
        splitless_types[kind] += 1
        death, depth = first_generated_on_chain(root, limit, generated)
        if death is None:
            persistent_splitless.append(root)
        else:
            if depth is None or depth < 1:
                raise RuntimeError(("splitless root healed at invalid depth", root, death, depth))
            healed_splitless.append((root, death, depth))
            healed_types[kind] += 1
            death_depths[depth] += 1
            a, _ = first_generating_pair(death, data["pairs"], generated)
            death_min_factors[a] += 1
            if depth == 1:
                depth_one_min_factors[a] += 1

    A_H = len(persistent_hard)
    D = len(healed_splitless)
    if A_H != sum(1 for root in hard if data["terminal_of_root"][root] == data["top_of_root"][root]):
        raise RuntimeError("persistent-hard cross-check failed")
    if len(splitless) != D + len(persistent_splitless):
        raise RuntimeError("splitless partition failed")

    hard_birth = Counter(hard)
    hard_death = Counter(death for _, death, _ in hard_deaths)
    splitless_death = Counter(death for _, death, _ in healed_splitless)
    active_hard = 0
    healed_bank = 0
    active_hard_history = [0] * (limit + 1)
    last_three_quarter_failure = None
    maximum_three_quarter_deficit = {"value": -(10**18), "X": 0, "A_H": 0, "D": 0}
    minimum_ratio = None
    for x in range(2, limit + 1):
        active_hard += hard_birth[x]
        active_hard -= hard_death[x]
        healed_bank += splitless_death[x]
        active_hard_history[x] = active_hard
        deficit = 3 * active_hard - 4 * healed_bank
        if deficit > maximum_three_quarter_deficit["value"]:
            maximum_three_quarter_deficit = {
                "value": deficit,
                "X": x,
                "A_H": active_hard,
                "D": healed_bank,
            }
        if deficit > 0:
            last_three_quarter_failure = {
                "X": x,
                "A_H": active_hard,
                "D": healed_bank,
                "deficit": deficit,
            }
        if active_hard and healed_bank:
            candidate = (healed_bank, active_hard, x)
            if minimum_ratio is None or candidate[0] * minimum_ratio[1] < minimum_ratio[0] * candidate[1]:
                minimum_ratio = candidate
    if active_hard != A_H or healed_bank != D:
        raise RuntimeError(("event sweep endpoint mismatch", active_hard, A_H, healed_bank, D))

    active_hard = 0
    healed_bank = 0
    maximum_additive_quarter_defect = None
    maximum_weighted_quarter_defect = None
    quarter_scale_samples = []
    sample_points = {10**power for power in range(1, 10) if 10**power <= limit}
    for x in range(2, limit + 1):
        active_hard += hard_birth[x]
        active_hard -= hard_death[x]
        healed_bank += splitless_death[x]
        quarter_hard = active_hard_history[x // 4]
        additive_defect = active_hard - healed_bank - quarter_hard
        weighted_defect = 7 * quarter_hard - 2 * healed_bank
        additive_record = {
            "value": additive_defect,
            "X": x,
            "A_H": active_hard,
            "D": healed_bank,
            "A_H_floor_X_over_4": quarter_hard,
        }
        weighted_record = {
            "value": weighted_defect,
            "X": x,
            "A_H": active_hard,
            "D": healed_bank,
            "A_H_floor_X_over_4": quarter_hard,
        }
        if (maximum_additive_quarter_defect is None or
                additive_defect > maximum_additive_quarter_defect["value"]):
            maximum_additive_quarter_defect = additive_record
        if (maximum_weighted_quarter_defect is None or
                weighted_defect > maximum_weighted_quarter_defect["value"]):
            maximum_weighted_quarter_defect = weighted_record
        if x in sample_points:
            quarter_scale_samples.append({
                "X": x,
                "A_H": active_hard,
                "D": healed_bank,
                "A_H_floor_X_over_4": quarter_hard,
                "additive_defect": additive_defect,
                "weighted_defect": weighted_defect,
            })

    maximum_persistent_splitless_depth = max(
        (literal_top(root, limit)[1] for root in persistent_splitless),
        default=-1,
    )
    deepest_persistent_splitless = [
        root
        for root in persistent_splitless
        if literal_top(root, limit)[1] == maximum_persistent_splitless_depth
    ]

    local_shadow_probe = None
    if limit >= 186:
        source_chain = literal_chain(74, 186)
        shadow_chain = literal_chain(8, 186)
        if data["pairs"][74] != [(5, 15)] or data["pairs"][15] != [(2, 8)]:
            raise RuntimeError("C94 local-shadow factorization probe changed")
        if 5 not in generated or 2 not in generated or 15 not in holes or 8 not in splitless:
            raise RuntimeError("C94 local-shadow state probe changed")
        if any(value not in holes for value in source_chain + shadow_chain):
            raise RuntimeError("C94 local-shadow persistence probe changed")
        hard_at_46 = [root for root in hard if root <= 46 and literal_top(root, 46)[0] in holes]
        if hard_at_46:
            raise RuntimeError(("unexpected persistent hard root through 46", hard_at_46))
        local_shadow_probe = {
            "cutoff": 186,
            "source": 74,
            "source_chain": source_chain,
            "factor_descent": [74, 15, 8],
            "complete_splitless_shadow": [8],
            "shadow_chain": shadow_chain,
            "shadow_healed_by_cutoff": False,
            "A_H_floor_cutoff_over_4": 0,
        }

    return {
        "limit": limit,
        "definitions": {
            "A_H": "hard roots whose literal seed-2 chain through X consists entirely of holes",
            "D": "structural splitless roots whose literal seed-2 chain has a generated member at most X",
        },
        "counts": {
            "generated": len(generated),
            "holes": len(holes),
            "hard": len(hard),
            "A_H": A_H,
            "splitless": len(splitless),
            "D": D,
            "persistent_splitless": len(persistent_splitless),
        },
        "ratios": {
            "D_over_A_H": {"numerator": D, "denominator": A_H},
            "four_D_minus_three_A_H": 4 * D - 3 * A_H,
            "D_minus_A_H": D - A_H,
        },
        "all_cutoff_three_quarter_gate": {
            "last_failure": last_three_quarter_failure,
            "maximum_deficit": maximum_three_quarter_deficit,
            "minimum_positive_D_over_A_H": None if minimum_ratio is None else {
                "numerator": minimum_ratio[0],
                "denominator": minimum_ratio[1],
                "X": minimum_ratio[2],
            },
        },
        "quarter_scale_gates": {
            "maximum_additive_defect": maximum_additive_quarter_defect,
            "maximum_weighted_defect": maximum_weighted_quarter_defect,
            "power_of_ten_samples": quarter_scale_samples,
            "local_shadow_probe": local_shadow_probe,
        },
        "splitless_types": dict(sorted(splitless_types.items())),
        "healed_splitless_types": dict(sorted(healed_types.items())),
        "healing_depths": {str(k): v for k, v in sorted(death_depths.items())},
        "persistent_hard_residue_mod_9": {
            str(k): v for k, v in sorted(Counter(r % 9 for r in persistent_hard).items())
        },
        "healed_splitless_residue_mod_9": {
            str(k): v for k, v in sorted(Counter(r % 9 for r, _, _ in healed_splitless).items())
        },
        "first_death_min_factor_histogram": {
            str(k): v for k, v in death_min_factors.most_common(40)
        },
        "depth_one_min_factor_histogram": {
            str(k): v for k, v in depth_one_min_factors.most_common(40)
        },
        "samples": {
            "persistent_hard_first": persistent_hard[:30],
            "healed_splitless_first": [
                {"root": r, "death": death, "depth": depth}
                for r, death, depth in healed_splitless[:30]
            ],
            "persistent_splitless_first": persistent_splitless[:30],
            "maximum_persistent_splitless_depth": maximum_persistent_splitless_depth,
            "deepest_persistent_splitless_roots": deepest_persistent_splitless[:30],
            "first_deepest_persistent_splitless_chain": (
                []
                if not deepest_persistent_splitless
                else literal_chain(deepest_persistent_splitless[0], limit)
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.limit)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
