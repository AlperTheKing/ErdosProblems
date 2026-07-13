"""Exact uniform-product upper bound for PHT on reconstructed R29.

Every nonpersistent owner in a lock arm is assigned to its unique traffic
leaf. Such an owner can be active only if a selected local selector row
touches that leaf's lock region. For each owner we bound scoped collision by
the smaller of unconditional expected raw collision and deterministic maximum
raw collision times the exact trigger probability. Unmapped owners retain
their full expected raw collision. HitNeed is bounded by blue degree only at
vertices where the deterministic row-count/slack test cannot force it to zero.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R29 = ROOT / "tmp" / "fanout" / "r29_gate" / "lead"
sys.path.insert(0, str(R29))

from r29_lead_gate import adjacency, build, canonical_bytes, shortest_rows


DEN = 680


def frac_payload(value: Fraction):
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "floor": value.numerator // value.denominator,
    }


def main() -> int:
    data = build()
    start, stop = data["selectorStart"], data["selectorStop"]
    rigid_rows = data["rows"][:start] + data["rows"][stop:]
    fixed_pairs = Counter()
    fixed_row_count = Counter()
    for row in rigid_rows:
        fixed_row_count.update(row)
        fixed_pairs.update((x, y) for x in row for y in row)

    pair_stats = {}
    family_presence = Counter()
    trigger_absence_numerator = {leaf: 1 for leaf in range(3, 55)}
    trigger_family_count = Counter()
    local_rows = 0
    arm_leaf = {leaf: leaf for leaf in range(3, 55)}
    next_arm_vertex = 56
    for leaf in range(3, 55):
        for _ in range(26):
            arm_leaf[next_arm_vertex] = leaf
            arm_leaf[next_arm_vertex + 1] = leaf
            next_arm_vertex += 2
    assert next_arm_vertex == 2760
    adj = adjacency(data["n"], data["blue"])
    selector_atoms = data["atoms"][start:stop]
    family_sizes = Counter()
    for atom in selector_atoms:
        family = shortest_rows(adj, *atom)
        assert len(family) == DEN
        family_sizes[len(family)] += 1
        row_pair_occurrences = Counter()
        vertices = set()
        family_triggers = Counter()
        for row in family:
            vertices.update(row)
            row_pair_occurrences.update((x, y) for x in row for y in row)
            if 55 not in row:
                local_rows += 1
                xds = [v for v in row if v in data["dXToLeaf"]]
                assert len(xds) == 1
                for leaf in {arm_leaf[v] for v in row if v in arm_leaf}:
                    family_triggers[leaf] += 1
        for leaf, count in family_triggers.items():
            trigger_absence_numerator[leaf] *= DEN - count
            trigger_family_count[leaf] += 1
        family_presence.update(vertices)
        for pair, count in row_pair_occurrences.items():
            if pair in pair_stats:
                stat = pair_stats[pair]
                stat[0] += count
                stat[1] += 1
                stat[2] *= DEN - count
            else:
                pair_stats[pair] = [count, 1, DEN - count]

    assert family_sizes == Counter({680: 676})
    assert local_rows == 676 * 4

    all_pairs = fixed_pairs.keys() | pair_stats.keys()
    expected_raw_excess = Fraction(0)
    expected_raw_by_owner = Counter()
    maximum_raw_by_owner = Counter()
    nonzero_random_pairs = 0
    for pair in all_pairs:
        fixed = fixed_pairs.get(pair, 0)
        total_count, families, absence_product = pair_stats.get(
            pair, (0, 0, 1)
        )
        mean = Fraction(total_count, DEN)
        if fixed:
            excess = fixed - 1 + mean
        elif families == 1:
            excess = Fraction(0)
        else:
            excess = mean - 1 + Fraction(
                absence_product, DEN ** families
            )
        assert excess >= 0
        if excess:
            nonzero_random_pairs += 1
            expected_raw_excess += excess
            expected_raw_by_owner[pair[0]] += 2 * excess
        maximum_count = fixed + families
        if maximum_count >= 2:
            maximum_raw_by_owner[pair[0]] += 2 * (maximum_count - 1)
    expected_raw_collision = 2 * expected_raw_excess

    # Check the fixed traffic collision block used by the reconstruction.
    for leaf in range(3, 55):
        fixed_leaf = 2 * sum(
            count - 1
            for (x, _), count in fixed_pairs.items()
            if x == leaf and count >= 2
        )
        assert fixed_leaf == 200
    expected_local_rows = Fraction(676 * 4, DEN)
    trigger_probability = {
        leaf: 1 - Fraction(
            trigger_absence_numerator[leaf],
            DEN ** trigger_family_count[leaf],
        )
        for leaf in range(3, 55)
    }
    assert min(trigger_family_count.values()) > 0
    expected_scoped_collision_upper = Fraction(0)
    mapped_owner_bound = Fraction(0)
    unmapped_owner_bound = Fraction(0)
    for owner in range(data["n"]):
        raw = expected_raw_by_owner[owner]
        if owner in arm_leaf:
            leaf = arm_leaf[owner]
            bound = min(
                raw,
                maximum_raw_by_owner[owner] * trigger_probability[leaf],
            )
            mapped_owner_bound += bound
        else:
            bound = raw
            unmapped_owner_bound += bound
        expected_scoped_collision_upper += bound

    blue_degree = Counter()
    for x, y in data["blue"]:
        blue_degree[x] += 1
        blue_degree[y] += 1
    problematic = {}
    hitneed_upper = 0
    for vertex in range(data["n"]):
        max_rows = fixed_row_count[vertex] + family_presence[vertex]
        if 5 * max_rows + blue_degree[vertex] > data["n"]:
            problematic[vertex] = {
                "maxRows": max_rows,
                "blueDegree": blue_degree[vertex],
            }
            hitneed_upper += blue_degree[vertex]

    expected_score_upper = expected_scoped_collision_upper + hitneed_upper
    threshold = Fraction(30811 - 28)
    residual_lower = threshold - expected_score_upper
    selector_q_raw = (
        expected_raw_by_owner[2760] + expected_raw_by_owner[2761]
    )
    conditional_collision_upper = (
        expected_scoped_collision_upper - selector_q_raw
    )
    # The three hubs contribute one HitNeed each.  At the anchor, the four
    # cable edges are permanent and each local row can expose at most two
    # additional incident lock edges.
    conditional_hitneed_upper = 3 + 4 + 2 * expected_local_rows
    conditional_score_upper = (
        conditional_collision_upper + conditional_hitneed_upper
    )
    conditional_residual = threshold - conditional_score_upper
    payload = {
        "arithmetic": "Fraction exact",
        "instanceSha256": hashlib.sha256(canonical_bytes(data)).hexdigest(),
        "selectorFamilies": 676,
        "rowsPerSelector": DEN,
        "localRowsPerSelector": 4,
        "productCardinality": str(DEN ** 676),
        "nonzeroExpectedCollisionPairs": nonzero_random_pairs,
        "expectedRawCollision": frac_payload(expected_raw_collision),
        "expectedLocalRows": frac_payload(expected_local_rows),
        "triggerFamilyCountHistogram": dict(
            Counter(trigger_family_count.values())
        ),
        "mappedOwnerCollisionUpper": frac_payload(mapped_owner_bound),
        "unmappedOwnerCollisionUpper": frac_payload(unmapped_owner_bound),
        "topUnmappedRawOwners": [
            {
                "owner": owner,
                "expectedRaw": frac_payload(value),
                "maximumRaw": maximum_raw_by_owner[owner],
            }
            for owner, value in sorted(
                (
                    (owner, expected_raw_by_owner[owner])
                    for owner in range(data["n"])
                    if owner not in arm_leaf and expected_raw_by_owner[owner]
                ),
                key=lambda item: item[1],
                reverse=True,
            )[:20]
        ],
        "expectedScopedCollisionUpper": frac_payload(
            expected_scoped_collision_upper
        ),
        "problematicHitNeedVertices": problematic,
        "hitNeedUpper": hitneed_upper,
        "expectedScoreUpper": frac_payload(expected_score_upper),
        "selectorQRawCollisionRemovedConditionally": frac_payload(
            selector_q_raw
        ),
        "conditionalHitNeedUpper": frac_payload(
            conditional_hitneed_upper
        ),
        "conditionalScoreUpper": frac_payload(conditional_score_upper),
        "phtThreshold": 30783,
        "residualLower": frac_payload(residual_lower),
        "conditionalResidualLower": frac_payload(conditional_residual),
        "phtCertifiedByUpperBound": residual_lower >= 0,
        "phtCertifiedConditional": conditional_residual >= 0,
        "conditionalPremises": [
            "q_L and q_R are never ActiveOwner for any selector tuple",
            "anchor activeDegree <= 4 + 2 * number of local rows",
        ],
        "boundPremise": (
            "a lock-arm owner can be active only if a local row touches its "
            "unique traffic-leaf region"
        ),
    }
    payload["scriptSha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
