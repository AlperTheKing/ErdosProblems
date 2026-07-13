"""Verify P59's smallest block-count barycenter-coupling falsifier."""

from __future__ import annotations

import argparse
import json
from itertools import combinations, combinations_with_replacement
from pathlib import Path


HERE = Path(__file__).resolve().parent
Z = (0, 7, 9, 12, 20, 26, 30, 58)
GAP = 15
LEFT_SUM = 37
RIGHT_SUM = 39
LEFT_SET = (0, 7, 9, 12, 20, 26)
RIGHT_SET = (0, 7, 9, 12, 20, 30)
SEARCH_COUNTS = {
    "max_width": 58,
    "endpoint_sidon_rulers_scanned": 2_005_269,
    "admissible_gaps_on_rulers_with_static_violations": 1_234_661,
}


def pair_sums(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def positive_differences(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(b - a for a, b in combinations(values, 2))


def triple_class(values: tuple[int, ...], total: int) -> dict[str, object]:
    triples = tuple(
        triple
        for triple in combinations_with_replacement(values, 3)
        if sum(triple) == total
    )
    balanced = tuple(triple for triple in triples if len(set(triple)) in (1, 3))
    support = tuple(sorted({value for triple in balanced for value in triple}))
    epsilon = int(total % 3 == 0 and total // 3 in values)
    blocks = (len(support) + 2 * epsilon) // 3
    if 3 * sum(support) != total * len(support):
        raise AssertionError((total, support, "barycenter"))
    if len(support) % 3 != epsilon:
        raise AssertionError((total, support, epsilon, "residue"))
    return {
        "sum": total,
        "representations": triples,
        "balanced_representations": balanced,
        "B": support,
        "b": len(support),
        "epsilon": epsilon,
        "balanced_blocks": blocks,
        "barycenter_identity": {
            "left": 3 * sum(support),
            "right": total * len(support),
        },
    }


def epsilon(values: tuple[int, ...], total: int) -> int:
    return int(total % 3 == 0 and total // 3 in values)


def feasible_subsets(
    values: tuple[int, ...], cutoff: int, total: int
) -> tuple[tuple[int, ...], ...]:
    low = tuple(value for value in values if value <= cutoff)
    result: list[tuple[int, ...]] = []
    for size in range(1, len(low) + 1):
        for subset in combinations(low, size):
            if subset[-1] > total or 3 * sum(subset) != total * size:
                continue
            eps = epsilon(values, total)
            if size % 3 != eps:
                continue
            if eps and total // 3 not in subset:
                continue
            result.append(subset)
    return tuple(result)


def capacity_column(
    values: tuple[int, ...], cutoff: int, total: int, chosen: tuple[int, ...]
) -> dict[str, object]:
    triples = triple_class(values, total)["representations"]
    if not triples:
        raise AssertionError((total, "not a represented target"))
    feasible = feasible_subsets(values, cutoff, total)
    beta = max(map(len, feasible), default=0)
    if chosen not in feasible or len(chosen) != beta:
        raise AssertionError((total, chosen, beta, "not a capacity maximizer"))
    eps = epsilon(values, total)
    return {
        "sum": total,
        "represented_by": triples,
        "A": chosen,
        "beta": beta,
        "epsilon": eps,
        "block_count_parameter": (beta + 2 * eps) // 3,
        "barycenter_identity": {
            "left": 3 * sum(chosen),
            "right": total * len(chosen),
        },
        "feasible_subsets": len(feasible),
        "maximizers": sum(len(subset) == beta for subset in feasible),
    }


def verify() -> dict[str, object]:
    width = Z[-1]
    cutoff = width - GAP
    sums = pair_sums(Z)
    differences = positive_differences(Z)
    if len(sums) != len(set(sums)) or len(sums) != len(Z) * (len(Z) + 1) // 2:
        raise AssertionError("not Sidon by unordered pair sums")
    if len(differences) != len(set(differences)):
        raise AssertionError("not Sidon by positive differences")
    cross = sorted(set(differences).intersection(GAP + total for total in sums))
    if cross:
        raise AssertionError((cross, "invalid overlap pair"))
    if max(LEFT_SUM, RIGHT_SUM) > cutoff:
        raise AssertionError((cutoff, "columns above cutoff"))

    left = capacity_column(Z, cutoff, LEFT_SUM, LEFT_SET)
    right = capacity_column(Z, cutoff, RIGHT_SUM, RIGHT_SET)
    intersection = sorted(set(left["A"]).intersection(right["A"]))
    proposed_bound = int(left["block_count_parameter"]) + int(
        right["block_count_parameter"]
    )
    if len(intersection) <= proposed_bound:
        raise AssertionError((intersection, proposed_bound, "not a falsifier"))

    actual_left = triple_class(Z, 39)
    actual_right = triple_class(Z, 42)
    actual_intersection = sorted(
        set(actual_left["B"]).intersection(actual_right["B"])
    )
    actual_bound = int(actual_left["balanced_blocks"]) + int(
        actual_right["balanced_blocks"]
    )
    if len(actual_intersection) <= actual_bound:
        raise AssertionError((actual_intersection, actual_bound, "actual columns"))

    return {
        "claim_falsified": (
            "for distinct low sums x,y, maximizing P51 witnesses A_x,A_y "
            "satisfy |A_x intersect A_y| <= (beta_x+2 epsilon_x)/3 + "
            "(beta_y+2 epsilon_y)/3"
        ),
        "minimality_order": ["p", "W", "Z lexicographic", "G", "x", "y"],
        "minimality_reason_p": (
            "the endpoint W is absent from every low B_x; on at most six marks, "
            "the feasible sizes 1,3,4,6 cannot violate the block-count bound "
            "for distinct barycenters"
        ),
        "exhaustive_search": SEARCH_COUNTS,
        "search_program": "search_intersection_falsifier.cpp",
        "p": len(Z),
        "Z": Z,
        "W": width,
        "G": GAP,
        "K": cutoff,
        "pair_sums": sorted(sums),
        "pair_sum_count": len(set(sums)),
        "positive_differences": sorted(differences),
        "positive_difference_count": len(set(differences)),
        "cross_intersection": cross,
        "left_capacity_column": left,
        "right_capacity_column": right,
        "A_intersection": intersection,
        "intersection_size": len(intersection),
        "proposed_bound": proposed_bound,
        "failure_margin": len(intersection) - proposed_bound,
        "actual_partitioned_failure": {
            "left_column": actual_left,
            "right_column": actual_right,
            "intersection": actual_intersection,
            "intersection_size": len(actual_intersection),
            "block_bound": actual_bound,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=HERE / "smallest_falsifier.json"
    )
    args = parser.parse_args()
    certificate = verify()
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="ascii")
    print(
        "verified p={p} W={W} G={G} K={K}; intersection={intersection_size} "
        "bound={proposed_bound} margin={failure_margin}".format(**certificate)
    )


if __name__ == "__main__":
    main()
