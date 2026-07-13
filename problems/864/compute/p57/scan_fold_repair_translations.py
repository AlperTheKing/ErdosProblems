#!/usr/bin/env python3
"""Exact translation scan for the reflected fold-repair candidates."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "problems/864/compute/p20/results/samples.jsonl"
P45 = ROOT / "problems/864/compute/p45/audit_signed_carry_identity.py"
OUTPUT = ROOT / "problems/864/compute/p57/fold_repair_translation_scan.json"


def load_p45():
    spec = importlib.util.spec_from_file_location("p45_for_p57", P45)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P45 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bitset(values: set[int]) -> int:
    out = 0
    for value in values:
        out |= 1 << value
    return out


def ruler_data(values: tuple[int, ...]) -> dict[str, object]:
    gamma = min(values)
    z = tuple(value - gamma for value in values)
    p = len(z)
    width = z[-1]
    sums: dict[int, int] = {}
    for i, left in enumerate(z):
        for right in z[i:]:
            total = left + right
            if total in sums:
                raise AssertionError("input ruler is not integer Sidon")
            sums[total] = 1 if left == right else 2
    differences = {right - left for i, left in enumerate(z) for right in z[i + 1 :]}
    if len(differences) != p * (p - 1) // 2:
        raise AssertionError("input ruler repeats a positive difference")
    return {
        "Z": z,
        "p": p,
        "width": width,
        "sums": sums,
        "sum_bits": bitset(set(sums)),
        "difference_bits": bitset(differences),
    }


def scan_ruler(row: dict[str, object]) -> dict[str, object]:
    z = row["Z"]
    p = int(row["p"])
    width = int(row["width"])
    sums = row["sums"]
    sum_bits = int(row["sum_bits"])
    difference_bits = int(row["difference_bits"])
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = baseline - width - 2
    best = None
    best_scale = None
    admissible = 0
    if max_gamma < 0:
        return {"p": p, "width": width, "translations": 0, "best": None}

    for gamma in range(max_gamma + 1):
        h = gamma + width + 1
        folded = sum_bits & (sum_bits >> h)
        sum_collisions = folded.bit_count()
        difference_collisions = 0
        cursor = folded
        while cursor:
            low_bit = cursor & -cursor
            low_sum = low_bit.bit_length() - 1
            difference_collisions += int(sums[low_sum]) * int(sums[low_sum + h])
            cursor ^= low_bit
        if not (sum_collisions <= difference_collisions <= 4 * sum_collisions):
            raise AssertionError("P45 energy bounds failed")

        delta = baseline - h
        for b in (1, 2):
            gap = 2 * gamma + b
            if difference_bits & (sum_bits << gap):
                continue
            admissible += 1
            total_collisions = sum_collisions + difference_collisions
            score = delta - 5 * total_collisions - 4 * p
            candidate = {
                "p": p,
                "width": width,
                "gamma": gamma,
                "b": b,
                "h": h,
                "delta": delta,
                "sum_collisions": sum_collisions,
                "difference_collisions": difference_collisions,
                "score_delta_minus_5C_minus_4p": score,
                "Z": list(z),
            }
            key = (score, delta, -total_collisions, -gamma, -b)
            if best is None or key > best[0]:
                best = (key, candidate)
            excess = max(delta - 5 * total_collisions, 0)
            scale_key = (excess * excess, p**3)
            if (
                best_scale is None
                or scale_key[0] * best_scale[0][1]
                > best_scale[0][0] * scale_key[1]
            ):
                scaled = dict(candidate)
                scaled["positive_excess"] = excess
                scaled["excess_squared"] = excess * excess
                scaled["p_cubed"] = p**3
                best_scale = (scale_key, scaled)
    return {
        "p": p,
        "width": width,
        "translations": admissible,
        "best": None if best is None else best[1],
        "best_scale": None if best_scale is None else best_scale[1],
    }


def main() -> None:
    p45 = load_p45()
    rulers: dict[tuple[int, ...], dict[str, object]] = {}
    with SOURCE.open(encoding="utf-8") as stream:
        for line in stream:
            source_row = json.loads(line)
            parameters = p45.reflected_parameters(source_row)
            if parameters is None:
                continue
            values, _, _ = parameters
            data = ruler_data(tuple(values))
            rulers.setdefault(tuple(data["Z"]), data)

    reports = [scan_ruler(row) for row in rulers.values()]
    nonempty = [row for row in reports if row["best"] is not None]
    if not nonempty:
        raise AssertionError("no admissible translations found")
    winner = max(
        (row["best"] for row in nonempty),
        key=lambda row: (
            row["score_delta_minus_5C_minus_4p"], row["delta"], -row["p"]
        ),
    )
    scale_winner = max(
        (row["best_scale"] for row in nonempty),
        key=lambda row: Fraction(row["excess_squared"], row["p_cubed"]),
    )
    assertion = winner["score_delta_minus_5C_minus_4p"] <= 0
    scale_assertion = scale_winner["excess_squared"] <= 4 * scale_winner["p_cubed"]
    result = {
        "arithmetic": "exact integers",
        "source_rulers": len(rulers),
        "admissible_translations": sum(int(row["translations"]) for row in reports),
        "candidate": "delta <= 5*(C_S+C_D)+4*p",
        "failure_count": sum(
            int(row["best"] is not None and row["best"]["score_delta_minus_5C_minus_4p"] > 0)
            for row in reports
        ),
        "maximum_score": winner,
        "assertion_passed": assertion,
        "scale_candidate": "max(delta-5*(C_S+C_D),0)^2 <= 4*p^3",
        "scale_maximum": scale_winner,
        "scale_assertion_passed": scale_assertion,
        "reports": reports,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: result[key] for key in result if key != "reports"}, indent=2))
    if not scale_assertion:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
