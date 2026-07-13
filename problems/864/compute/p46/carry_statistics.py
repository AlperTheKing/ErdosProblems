#!/usr/bin/env python3
"""Exact signed carry statistics and falsification search for Problem 864."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable, Iterator

Profile = dict[str, object]


def reflected_ruler(row: dict[str, object]) -> tuple[tuple[int, ...], int] | None:
    values = sorted(int(x) for x in row["A"])
    k = len(values)
    sigma = int(row.get("exceptional_sum") or 0)
    multiplicity = int(row.get("exceptional_multiplicity") or 0)
    if k % 2 or multiplicity != k // 2 or sigma <= 0:
        return None
    value_set = set(values)
    if any(sigma - x not in value_set for x in values):
        return None
    lower = [x for x in values if 2 * x < sigma]
    if len(lower) != k // 2:
        return None
    top = max(lower)
    z = tuple(sorted(top - x for x in lower))
    gap = sigma - 2 * top
    return (z, gap) if gap > 0 else None


def sum_support(values: tuple[int, ...]) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise AssertionError((values, "not integer Sidon", total))
            out[total] = {
                "pair": [left, right],
                "ordered_multiplicity": 1 if left == right else 2,
            }
    return out


def difference_support(values: tuple[int, ...]) -> dict[int, dict[str, object]]:
    pairs: dict[int, list[list[int]]] = defaultdict(list)
    for left in values:
        for right in values:
            pairs[left - right].append([left, right])
    out: dict[int, dict[str, object]] = {}
    for difference, labels in pairs.items():
        if difference and len(labels) != 1:
            raise AssertionError((values, "difference collision", difference, labels))
        out[difference] = {
            "pairs": labels,
            "ordered_multiplicity": len(labels),
        }
    return out


def groups_mod_h(support: dict[int, dict[str, object]], h: int) -> dict[int, list[int]]:
    out: dict[int, list[int]] = defaultdict(list)
    for value in support:
        out[value % h].append(value)
    for residue, literal_values in out.items():
        literal_values.sort()
        if len(literal_values) > 2:
            raise AssertionError((h, residue, literal_values))
    return dict(out)


def multiplicity_histogram(groups: dict[int, list[int]]) -> dict[str, int]:
    return {
        str(m): count for m, count in sorted(Counter(map(len, groups.values())).items())
    }


def collision_structure(
    groups: dict[int, list[int]],
    support: dict[int, dict[str, object]],
    overlap: set[int],
    target: int,
    h: int,
    difference_side: bool,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for residue, literal_values in sorted(groups.items()):
        if len(literal_values) != 2:
            continue
        overlap_residue = (target - residue) % h if difference_side else residue
        row: dict[str, object] = {
            "residue": residue,
            "overlap_sum_residue": overlap_residue,
            "literal_values": literal_values,
            "ordered_multiplicities": [
                int(support[x]["ordered_multiplicity"]) for x in literal_values
            ],
            "in_overlap": overlap_residue in overlap,
        }
        label = "ordered_pair_labels" if difference_side else "unordered_pair_labels"
        key = "pairs" if difference_side else "pair"
        row[label] = [support[x][key] for x in literal_values]
        out.append(row)
    return out


def exact_profile(
    values_input: Iterable[int],
    b: int,
    source_id: str,
    kind: str,
    details: bool,
) -> Profile:
    values = tuple(sorted(values_input))
    if len(values) < 2 or len(set(values)) != len(values) or values[0] < 0:
        raise AssertionError((source_id, "invalid B", values))
    if b not in (1, 2):
        raise AssertionError((source_id, "invalid b", b))
    h = values[-1] + 1
    p = len(values)
    target = (-b) % h
    sums = sum_support(values)
    differences = difference_support(values)
    sum_size = p * (p + 1) // 2
    difference_size = p * (p - 1) + 1
    if len(sums) != sum_size or len(differences) != difference_size:
        raise AssertionError((source_id, "integer support size"))
    if sum(int(x["ordered_multiplicity"]) for x in sums.values()) != p * p:
        raise AssertionError((source_id, "ordered sum mass"))
    if sum(int(x["ordered_multiplicity"]) for x in differences.values()) != p * p:
        raise AssertionError((source_id, "ordered difference mass"))
    if any(-b - s in differences for s in sums):
        raise AssertionError((source_id, "-b in 3B-B"))

    sum_groups = groups_mod_h(sums, h)
    difference_groups = groups_mod_h(differences, h)
    translated_difference_residues = {(target - r) % h for r in difference_groups}
    overlap = set(sum_groups) & translated_difference_residues

    support_layers: Counter[int] = Counter()
    ordered_layers: Counter[int] = Counter()
    residue_rows: dict[int, dict[str, int | str | bool]] = {}
    for residue in sorted(overlap):
        difference_residue = (target - residue) % h
        local_support: Counter[int] = Counter()
        local_ordered: Counter[int] = Counter()
        for s in sum_groups[residue]:
            sw = int(sums[s]["ordered_multiplicity"])
            for d in difference_groups[difference_residue]:
                dw = int(differences[d]["ordered_multiplicity"])
                numerator = s + d + b
                if numerator % h:
                    raise AssertionError((source_id, "nonintegral carry", s, d))
                layer = numerator // h
                if layer not in (1, 2):
                    raise AssertionError((source_id, "unexpected carry", layer))
                local_support[layer] += 1
                local_ordered[layer] += sw * dw
                support_layers[layer] += 1
                ordered_layers[layer] += sw * dw
        layer_set = set(local_support)
        if layer_set == {1}:
            layer_type = "carry1_only"
        elif layer_set == {2}:
            layer_type = "carry2_only"
        elif layer_set == {1, 2}:
            layer_type = "both"
        else:
            raise AssertionError((source_id, residue, local_support))
        sum_collision = len(sum_groups[residue]) == 2
        difference_collision = len(difference_groups[difference_residue]) == 2
        if sum_collision and difference_collision:
            raise AssertionError((source_id, "simultaneous overlap collision", residue))
        residue_rows[residue] = {
            "support1": local_support[1],
            "support2": local_support[2],
            "ordered1": local_ordered[1],
            "ordered2": local_ordered[2],
            "type": layer_type,
            "sum_collision": sum_collision,
            "difference_collision": difference_collision,
        }

    only1 = sum(row["type"] == "carry1_only" for row in residue_rows.values())
    only2 = sum(row["type"] == "carry2_only" for row in residue_rows.values())
    both = sum(row["type"] == "both" for row in residue_rows.values())
    sum_collision_overlap = sum(bool(row["sum_collision"]) for row in residue_rows.values())
    difference_collision_overlap = sum(
        bool(row["difference_collision"]) for row in residue_rows.values()
    )
    neither_collision_overlap = len(overlap) - sum_collision_overlap - difference_collision_overlap
    sum_collisions = sum_size - len(sum_groups)
    difference_collisions = difference_size - len(difference_groups)
    baseline = sum_size + difference_size
    delta = baseline - h
    union_holes = h - len(set(sum_groups) | translated_difference_residues)
    raw_overlap = len(sum_groups) + len(difference_groups) - h

    if support_layers[1] != only1 + both or support_layers[2] != only2 + both:
        raise AssertionError((source_id, "exclusive/both identity"))
    if both != sum_collision_overlap + difference_collision_overlap:
        raise AssertionError((source_id, "both/collision identity"))
    if delta != len(overlap) + sum_collisions + difference_collisions - union_holes:
        raise AssertionError((source_id, "delta identity"))
    outside_collisions = (
        sum_collisions + difference_collisions - sum_collision_overlap - difference_collision_overlap
    )
    if delta != support_layers[1] + support_layers[2] + outside_collisions - union_holes:
        raise AssertionError((source_id, "support-pair delta identity"))

    moments: dict[str, dict[str, int]] = {
        "support_by_residue_power": {},
        "ordered_by_residue_power": {},
        "support_by_cut_coordinate_power": {},
        "ordered_by_cut_coordinate_power": {},
    }
    for power in range(3):
        sr = wr = sc = wc = 0
        for residue, row in residue_rows.items():
            support_signed = int(row["support1"]) - int(row["support2"])
            ordered_signed = int(row["ordered1"]) - int(row["ordered2"])
            cut_coordinate = 2 * residue - (h - b)
            sr += residue**power * support_signed
            wr += residue**power * ordered_signed
            sc += cut_coordinate**power * support_signed
            wc += cut_coordinate**power * ordered_signed
        moments["support_by_residue_power"][str(power)] = sr
        moments["ordered_by_residue_power"][str(power)] = wr
        moments["support_by_cut_coordinate_power"][str(power)] = sc
        moments["ordered_by_cut_coordinate_power"][str(power)] = wc

    out: Profile = {
        "source_id": source_id,
        "kind": kind,
        "B": list(values),
        "b": b,
        "p": p,
        "h": h,
        "min_B": values[0],
        "width_B": values[-1] - values[0],
        "gap": 2 * values[0] + b,
        "max_E": b + 2 * (h - 1),
        "baseline": baseline,
        "delta": delta,
        "sum_support_integer": sum_size,
        "difference_support_integer": difference_size,
        "sum_support_mod_h": len(sum_groups),
        "difference_support_mod_h": len(difference_groups),
        "sum_collision_residues": sum_collisions,
        "difference_collision_residues": difference_collisions,
        "sum_modular_multiplicity_histogram": multiplicity_histogram(sum_groups),
        "difference_modular_multiplicity_histogram": multiplicity_histogram(difference_groups),
        "raw_pigeonhole_overlap": raw_overlap,
        "actual_overlap": len(overlap),
        "union_holes": union_holes,
        "carry1_only_residues": only1,
        "carry2_only_residues": only2,
        "both_residues": both,
        "neither_collision_overlap_residues": neither_collision_overlap,
        "sum_collision_overlap_residues": sum_collision_overlap,
        "difference_collision_overlap_residues": difference_collision_overlap,
        "simultaneous_collision_overlap_residues": 0,
        "sum_collision_outside_overlap_residues": sum_collisions - sum_collision_overlap,
        "difference_collision_outside_overlap_residues": (
            difference_collisions - difference_collision_overlap
        ),
        "support_carry_counts": {"1": support_layers[1], "2": support_layers[2]},
        "ordered_representation_carry_counts": {
            "1": ordered_layers[1], "2": ordered_layers[2]
        },
        "natural_signed_moments": moments,
        "identity_checks": {
            "support_carry1_equals_only1_plus_both": True,
            "support_carry2_equals_only2_plus_both": True,
            "both_equals_overlap_sum_plus_difference_collisions": True,
            "no_simultaneous_overlap_collision": True,
            "delta_equals_overlap_plus_collisions_minus_union_holes": True,
            "delta_equals_support_pairs_plus_outside_collisions_minus_union_holes": True,
        },
    }
    if details:
        out["sum_collision_structure"] = collision_structure(
            sum_groups, sums, overlap, target, h, False
        )
        out["difference_collision_structure"] = collision_structure(
            difference_groups, differences, overlap, target, h, True
        )
    return out


def legacy_projection(row: Profile) -> dict[str, object]:
    p, h = int(row["p"]), int(row["h"])
    return {
        "p": p,
        "gap": row["gap"],
        "width": row["width_B"],
        "max_E": row["max_E"],
        "coefficient_num": row["max_E"],
        "coefficient_den": p * p,
        "slot_order": h,
        "modular_threshold_slack_twice": -2 * int(row["delta"]),
        "sum_support_mod_h": row["sum_support_mod_h"],
        "difference_support_mod_h": row["difference_support_mod_h"],
        "baseline_support": row["baseline"],
        "forced_overlap": row["raw_pigeonhole_overlap"],
        "actual_overlap": row["actual_overlap"],
        "carry1_only_residues": row["carry1_only_residues"],
        "carry2_only_residues": row["carry2_only_residues"],
        "both_positive_layers_residues": row["both_residues"],
        "literal_pair_counts_by_layer": {
            key: value
            for key, value in row["support_carry_counts"].items()
            if value
        },
    }


def load_p20(samples_path: Path, p44_path: Path) -> tuple[list[Profile], dict[str, int]]:
    p44 = json.loads(p44_path.read_text(encoding="utf-8"))
    legacy = {row["sample_id"]: row for row in p44["reports"]}
    reports: list[Profile] = []
    with samples_path.open(encoding="utf-8") as source:
        for line in source:
            sample = json.loads(line)
            reflected = reflected_ruler(sample)
            if reflected is None:
                continue
            z, gap = reflected
            b = 1 if gap % 2 else 2
            gamma = (gap - b) // 2
            row = exact_profile(
                (gamma + x for x in z), b, str(sample["sample_id"]),
                str(sample.get("kind") or "p20"), True,
            )
            old = legacy.get(sample["sample_id"])
            if old is None:
                raise AssertionError((sample["sample_id"], "missing P44 row"))
            mismatches = {
                key: (old.get(key), value)
                for key, value in legacy_projection(row).items()
                if old.get(key) != value
            }
            if mismatches:
                raise AssertionError((sample["sample_id"], mismatches))
            reports.append(row)
    if len(reports) != int(p44["fully_reflected_count"]):
        raise AssertionError((len(reports), p44["fully_reflected_count"]))
    reports.sort(key=lambda row: (
        Fraction(int(row["max_E"]), int(row["p"]) ** 2),
        int(row["p"]), str(row["source_id"]),
    ))
    return reports, {
        "p44_reports_checked": len(reports),
        "legacy_fields_checked_per_report": len(legacy_projection(reports[0])),
        "legacy_field_mismatches": 0,
    }


def sidon_rulers(width: int) -> Iterator[tuple[int, ...]]:
    chosen = [0]
    used: set[int] = set()

    def new_differences(value: int) -> tuple[int, ...] | None:
        differences = tuple(value - old for old in chosen)
        if len(set(differences)) < len(differences) or any(d in used for d in differences):
            return None
        return differences

    def recurse(next_value: int) -> Iterator[tuple[int, ...]]:
        endpoint = new_differences(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(next_value, width):
            differences = new_differences(value)
            if differences is None:
                continue
            chosen.append(value)
            used.update(differences)
            yield from recurse(value + 1)
            used.difference_update(differences)
            chosen.pop()

    yield from recurse(1)


def forbidden_three_minus_one(values: tuple[int, ...]) -> set[int]:
    sums, differences = sum_support(values), difference_support(values)
    return {s + d for s in sums for d in differences}


def enumerate_positive_delta(max_width: int) -> tuple[list[Profile], dict[str, object]]:
    reports: list[Profile] = []
    by_width: list[dict[str, int]] = []
    total_rulers = total_candidates = 0
    for width in range(1, max_width + 1):
        ruler_count = candidate_count = hole_count = 0
        for ruler in sidon_rulers(width):
            ruler_count += 1
            total_rulers += 1
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = forbidden_three_minus_one(ruler)
            z = tuple(sorted(width - x for x in ruler))
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    candidate_count += 1
                    total_candidates += 1
                    center = 2 * width + 2 * gamma + b
                    if center in forbidden:
                        continue
                    source_id = (
                        f"enum-W{width}-F{'_'.join(map(str, ruler))}-b{b}-g{gamma}"
                    )
                    row = exact_profile(
                        (gamma + x for x in z), b, source_id,
                        "exhaustive-positive-delta", False,
                    )
                    if int(row["delta"]) <= 0:
                        raise AssertionError((source_id, row["delta"]))
                    reports.append(row)
                    hole_count += 1
        by_width.append({
            "width": width,
            "sidon_rulers": ruler_count,
            "positive_delta_candidates": candidate_count,
            "admissible_holes": hole_count,
        })
    return reports, {
        "domain": (
            "all (B,b), b in {1,2}, delta>0, endpoint-normalized ruler "
            f"width max(B)-min(B) <= {max_width}"
        ),
        "max_width": max_width,
        "sidon_rulers": total_rulers,
        "positive_delta_candidates": total_candidates,
        "admissible_holes": len(reports),
        "admissible_holes_by_p": {
            str(p): count
            for p, count in sorted(Counter(int(row["p"]) for row in reports).items())
        },
        "by_width": by_width,
    }


def profile_key(row: Profile) -> tuple[object, ...]:
    return (
        int(row["p"]), int(row["h"]), int(row["b"]),
        tuple(int(x) for x in row["B"]), str(row["source_id"]),
    )


def deduplicate(reports: list[Profile]) -> list[Profile]:
    unique: dict[tuple[tuple[int, ...], int], Profile] = {}
    for row in reports:
        key = (tuple(int(x) for x in row["B"]), int(row["b"]))
        if key not in unique or profile_key(row) < profile_key(unique[key]):
            unique[key] = row
    return sorted(unique.values(), key=profile_key)


def profiles_sha256(reports: list[Profile]) -> str:
    digest = hashlib.sha256()
    for row in reports:
        payload = [
            row["source_id"], row["B"], row["b"], row["p"], row["h"],
            row["delta"], row["actual_overlap"], row["union_holes"],
            row["sum_collision_residues"], row["difference_collision_residues"],
            row["carry1_only_residues"], row["carry2_only_residues"],
            row["both_residues"], row["support_carry_counts"],
            row["ordered_representation_carry_counts"], row["natural_signed_moments"],
        ]
        digest.update(json.dumps(payload, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def witness(row: Profile) -> dict[str, object]:
    support = row["support_carry_counts"]
    ordered = row["ordered_representation_carry_counts"]
    moments = row["natural_signed_moments"]
    keys = (
        "source_id", "kind", "p", "h", "b", "B", "delta", "actual_overlap",
        "sum_collision_residues", "difference_collision_residues", "union_holes",
        "carry1_only_residues", "carry2_only_residues", "both_residues",
    )
    out = {key: row[key] for key in keys}
    out.update({
        "support_carry1": support["1"],
        "support_carry2": support["2"],
        "ordered_carry1": ordered["1"],
        "ordered_carry2": ordered["2"],
        "support_signed_moment0": moments["support_by_residue_power"]["0"],
        "ordered_signed_moment0": moments["ordered_by_residue_power"]["0"],
    })
    return out


def metrics(row: Profile) -> dict[str, int]:
    support = row["support_carry_counts"]
    ordered = row["ordered_representation_carry_counts"]
    moments = row["natural_signed_moments"]
    cs = int(row["sum_collision_residues"])
    cd = int(row["difference_collision_residues"])
    return {
        "delta": int(row["delta"]),
        "actual_overlap": int(row["actual_overlap"]),
        "sum_collision_residues": cs,
        "difference_collision_residues": cd,
        "total_collision_residues": cs + cd,
        "union_holes": int(row["union_holes"]),
        "carry1_only_residues": int(row["carry1_only_residues"]),
        "carry2_only_residues": int(row["carry2_only_residues"]),
        "both_residues": int(row["both_residues"]),
        "exclusive_residues": int(row["carry1_only_residues"])
        + int(row["carry2_only_residues"]),
        "support_carry1": int(support["1"]),
        "support_carry2": int(support["2"]),
        "support_carry_total": int(support["1"]) + int(support["2"]),
        "support_signed_moment0": int(moments["support_by_residue_power"]["0"]),
        "ordered_carry1": int(ordered["1"]),
        "ordered_carry2": int(ordered["2"]),
        "ordered_carry_total": int(ordered["1"]) + int(ordered["2"]),
        "ordered_signed_moment0": int(moments["ordered_by_residue_power"]["0"]),
        "support_signed_residue_moment1": int(moments["support_by_residue_power"]["1"]),
        "support_signed_residue_moment2": int(moments["support_by_residue_power"]["2"]),
        "ordered_signed_residue_moment1": int(moments["ordered_by_residue_power"]["1"]),
        "ordered_signed_residue_moment2": int(moments["ordered_by_residue_power"]["2"]),
        "support_signed_cut_moment0": int(moments["support_by_cut_coordinate_power"]["0"]),
        "support_signed_cut_moment1": int(moments["support_by_cut_coordinate_power"]["1"]),
        "support_signed_cut_moment2": int(moments["support_by_cut_coordinate_power"]["2"]),
        "ordered_signed_cut_moment0": int(moments["ordered_by_cut_coordinate_power"]["0"]),
        "ordered_signed_cut_moment1": int(moments["ordered_by_cut_coordinate_power"]["1"]),
        "ordered_signed_cut_moment2": int(moments["ordered_by_cut_coordinate_power"]["2"]),
    }


def inequality_tests(reports: list[Profile]) -> dict[str, object]:
    positive = [row for row in reports if int(row["delta"]) > 0]
    tests: list[tuple[str, str, Callable[[Profile], int], Callable[[Profile], int]]] = [
        ("delta_le_overlap", "delta <= |I|",
         lambda r: int(r["delta"]), lambda r: int(r["actual_overlap"])),
        ("delta_le_support_carry_total", "delta <= U1+U2",
         lambda r: int(r["delta"]),
         lambda r: sum(int(x) for x in r["support_carry_counts"].values())),
        ("delta_le_carry1_support", "delta <= U1",
         lambda r: int(r["delta"]), lambda r: int(r["support_carry_counts"]["1"])),
        ("delta_le_exclusive_residues", "delta <= only1+only2",
         lambda r: int(r["delta"]),
         lambda r: int(r["carry1_only_residues"]) + int(r["carry2_only_residues"])),
        ("delta_le_abs_support_signed_moment0", "delta <= |U1-U2|",
         lambda r: int(r["delta"]),
         lambda r: abs(int(r["natural_signed_moments"]["support_by_residue_power"]["0"]))),
        ("delta_le_both_plus_abs_support_signed_moment0", "delta <= both+|U1-U2|",
         lambda r: int(r["delta"]),
         lambda r: int(r["both_residues"])
         + abs(int(r["natural_signed_moments"]["support_by_residue_power"]["0"]))),
        ("p_delta_le_abs_ordered_signed_moment0", "p*delta <= |W1-W2|",
         lambda r: int(r["p"]) * int(r["delta"]),
         lambda r: abs(int(r["natural_signed_moments"]["ordered_by_residue_power"]["0"]))),
        ("delta_le_total_collisions", "delta <= C_S+C_D",
         lambda r: int(r["delta"]),
         lambda r: int(r["sum_collision_residues"]) + int(r["difference_collision_residues"])),
        ("collisions_le_union_holes", "C_S+C_D <= H_0 (equiv. delta <= |I|)",
         lambda r: int(r["sum_collision_residues"]) + int(r["difference_collision_residues"]),
         lambda r: int(r["union_holes"])),
        ("overlap_square_le_p_cubed", "|I|^2 <= p^3",
         lambda r: int(r["actual_overlap"]) ** 2, lambda r: int(r["p"]) ** 3),
        ("support_signed_square_le_p_cubed", "|U1-U2|^2 <= p^3",
         lambda r: int(r["natural_signed_moments"]["support_by_residue_power"]["0"]) ** 2,
         lambda r: int(r["p"]) ** 3),
        ("collision_square_le_p_cubed", "(C_S+C_D)^2 <= p^3",
         lambda r: (int(r["sum_collision_residues"])
                    + int(r["difference_collision_residues"])) ** 2,
         lambda r: int(r["p"]) ** 3),
    ]
    out: dict[str, object] = {}
    for name, statement, lhs, rhs in tests:
        failure_count = 0
        smallest: Profile | None = None
        smallest_key: tuple[object, ...] | None = None
        worst: Profile | None = None
        worst_rank: tuple[object, ...] | None = None
        worst_violation = 0
        for row in positive:
            left = lhs(row)
            right = rhs(row)
            key = profile_key(row)
            violation = left - right
            if violation > 0:
                failure_count += 1
                if smallest_key is None or key < smallest_key:
                    smallest = row
                    smallest_key = key
            rank = (violation, key)
            if worst_rank is None or rank > worst_rank:
                worst = row
                worst_rank = rank
                worst_violation = violation
        assert worst is not None
        out[name] = {
            "statement": statement,
            "tested_positive_delta_profiles": len(positive),
            "failure_count": failure_count,
            "smallest_falsifier": witness(smallest) if smallest else None,
            "maximum_violation_lhs_minus_rhs": worst_violation,
            "maximum_violation_witness": witness(worst),
        }
    return out

def exact_extrema(reports: list[Profile]) -> dict[str, object]:
    positive = [row for row in reports if int(row["delta"]) > 0]
    scalar_names = list(metrics(positive[0]))
    scalar_state: dict[str, dict[str, object]] = {
        name: {
            "minimum": None, "minimum_row": None, "minimum_rank": None,
            "maximum": None, "maximum_row": None, "maximum_rank": None,
        }
        for name in scalar_names
    }
    ratio_functions: dict[str, Callable[[Profile], Fraction]] = {
        "delta_over_p2": lambda r: Fraction(int(r["delta"]), int(r["p"]) ** 2),
        "overlap_over_p2": lambda r: Fraction(int(r["actual_overlap"]), int(r["p"]) ** 2),
        "collisions_over_p2": lambda r: Fraction(
            int(r["sum_collision_residues"]) + int(r["difference_collision_residues"]),
            int(r["p"]) ** 2),
        "abs_support_signed0_over_p2": lambda r: Fraction(
            abs(int(r["natural_signed_moments"]["support_by_residue_power"]["0"])),
            int(r["p"]) ** 2),
        "overlap_square_over_p3": lambda r: Fraction(
            int(r["actual_overlap"]) ** 2, int(r["p"]) ** 3),
    }
    ratio_state: dict[str, dict[str, object]] = {
        name: {
            "minimum": None, "minimum_row": None, "minimum_rank": None,
            "maximum": None, "maximum_row": None, "maximum_rank": None,
        }
        for name in ratio_functions
    }
    for row in positive:
        key = profile_key(row)
        values = metrics(row)
        for name, value in values.items():
            state = scalar_state[name]
            low_rank = (value, key)
            high_rank = (value, key)
            if state["minimum_rank"] is None or low_rank < state["minimum_rank"]:
                state["minimum"] = value
                state["minimum_row"] = row
                state["minimum_rank"] = low_rank
            if state["maximum_rank"] is None or high_rank > state["maximum_rank"]:
                state["maximum"] = value
                state["maximum_row"] = row
                state["maximum_rank"] = high_rank
        for name, function in ratio_functions.items():
            value = function(row)
            state = ratio_state[name]
            rank = (value, key)
            if state["minimum_rank"] is None or rank < state["minimum_rank"]:
                state["minimum"] = value
                state["minimum_row"] = row
                state["minimum_rank"] = rank
            if state["maximum_rank"] is None or rank > state["maximum_rank"]:
                state["maximum"] = value
                state["maximum_row"] = row
                state["maximum_rank"] = rank
    scalar = {
        name: {
            "minimum": state["minimum"],
            "minimum_witness": witness(state["minimum_row"]),
            "maximum": state["maximum"],
            "maximum_witness": witness(state["maximum_row"]),
        }
        for name, state in scalar_state.items()
    }
    ratios = {
        name: {
            "minimum": str(state["minimum"]),
            "minimum_witness": witness(state["minimum_row"]),
            "maximum": str(state["maximum"]),
            "maximum_witness": witness(state["maximum_row"]),
        }
        for name, state in ratio_state.items()
    }
    return {"positive_delta_profiles": len(positive), "scalar": scalar, "ratios": ratios}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples", type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--p44", type=Path,
        default=Path("problems/864/compute/p44/carry_layer_profiles.json"),
    )
    parser.add_argument("--max-width", type=int, default=24)
    parser.add_argument("--store-enumerated-reports", action="store_true")
    parser.add_argument(
        "--output", type=Path,
        default=Path("problems/864/compute/p46/carry_statistics.json"),
    )
    args = parser.parse_args()
    if args.max_width < 1:
        parser.error("--max-width must be positive")

    p20, cross_check = load_p20(args.samples, args.p44)
    enumerated, enumeration_summary = enumerate_positive_delta(args.max_width)
    combined = deduplicate(p20 + enumerated)
    enumeration_output = {
        **enumeration_summary,
        "reports_sha256": profiles_sha256(enumerated),
        "reports_stored": args.store_enumerated_reports,
    }
    if args.store_enumerated_reports:
        enumeration_output["reports"] = enumerated
    output = {
        "schema_version": 1,
        "arithmetic": "integer",
        "definitions": {
            "support_carry_counts": "one per distinct literal (s,d) support-label pair",
            "ordered_representation_carry_counts": (
                "weight r_{B+B}(s)r_{B-B}(d), using ordered pair representations"
            ),
            "signed_moments": (
                "carry-1 minus carry-2 local mass against residue^j and "
                "(2*residue-(h-b))^j, j=0,1,2"
            ),
            "delta": "(3p^2-p+2)/2-h",
            "union_holes": "h-|((B+B) mod h) union (-b-(B-B) mod h)|",
        },
        "cross_check": cross_check,
        "p20": {"fully_reflected_profiles": len(p20), "reports": p20},
        "enumeration": enumeration_output,
        "combined_unique_profiles": len(combined),
        "exact_extrema": exact_extrema(combined),
        "inequality_tests": inequality_tests(combined),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "p44_cross_check": cross_check,
        "enumeration": {k: v for k, v in enumeration_summary.items() if k != "by_width"},
        "combined_unique_profiles": len(combined),
        "inequality_failures": {
            name: row["failure_count"] for name, row in output["inequality_tests"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()









