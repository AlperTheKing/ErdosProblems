"""Exact pointwise/expectation upper bound for R29's 2943 PHT instance."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
R29 = ROOT / "tmp" / "fanout" / "r29_gate" / "lead"
sys.path.insert(0, str(R29))

from r29_lead_gate import adjacency, build, shortest_rows  # noqa: E402


def row_pairs(row):
    for x in row:
        for y in row:
            yield (x, y)


def main():
    data = build()
    n = data["n"]
    start = data["selectorStart"]
    stop = data["selectorStop"]
    rigid_rows = data["rows"][:start] + data["rows"][stop:]
    selector_atoms = data["atoms"][start:stop]
    blue_adj = adjacency(n, data["blue"])

    rigid_pair_count = Counter()
    rigid_vertex_count = Counter()
    for row in rigid_rows:
        rigid_pair_count.update(row_pairs(row))
        rigid_vertex_count.update(row)

    pair_family_multiplicities = defaultdict(list)
    vertex_family_support = Counter()
    family_histogram = Counter()
    for atom in selector_atoms:
        family = shortest_rows(blue_adj, *atom)
        family_histogram[len(family)] += 1
        assert len(family) == 680
        pair_counts = Counter()
        family_vertices = set()
        for row in family:
            pair_counts.update(row_pairs(row))
            family_vertices.update(row)
        for pair, multiplicity in pair_counts.items():
            pair_family_multiplicities[pair].append(multiplicity)
        vertex_family_support.update(family_vertices)

    all_pairs = set(rigid_pair_count) | set(pair_family_multiplicities)
    expected_raw_units = Fraction(0)
    for pair in all_pairs:
        rigid = rigid_pair_count[pair]
        multiplicities = pair_family_multiplicities.get(pair, ())
        expected_count = Fraction(rigid) + sum(
            (Fraction(a, 680) for a in multiplicities), Fraction(0)
        )
        if rigid:
            expected_excess = expected_count - 1
        else:
            probability_zero = Fraction(1)
            for a in multiplicities:
                probability_zero *= Fraction(680 - a, 680)
            expected_excess = expected_count - 1 + probability_zero
        assert expected_excess >= 0
        expected_raw_units += 2 * expected_excess

    blue_degree = [len(blue_adj[v]) for v in range(n)]
    possible_hit_vertices = []
    hitneed_degree_bound = 0
    for v in range(n):
        max_row_count = rigid_vertex_count[v] + vertex_family_support[v]
        if 5 * max_row_count > n - blue_degree[v]:
            possible_hit_vertices.append({
                "v": v,
                "blueDegree": blue_degree[v],
                "maxRowCount": max_row_count,
            })
            hitneed_degree_bound += blue_degree[v]

    mean_upper = expected_raw_units + hitneed_degree_bound
    threshold = 30811 - 28
    residual = Fraction(threshold) - mean_upper
    payload = {
        "arithmetic": "Fraction/integer only",
        "omega": {
            "definition": "full Cartesian product of complete shortest-row families, each indexed row once",
            "rigidFamilies": len(rigid_rows),
            "selectorFamilies": len(selector_atoms),
            "selectorFamilySize": 680,
            "cardinality": "680^676",
        },
        "capacityConventions": {
            "collisionUpper": "two times raw ordered-pair excess, including diagonal pairs",
            "activeScope": "pointwise subset of raw collision owners",
            "hitNeedUpper": "blue degree; zero if 5*maxRowCount <= n-blueDegree",
            "rowMultiplicity": "literal row indices; CompleteShortestRowDB row lists are semantic-Nodup",
        },
        "familyHistogram": dict(sorted(family_histogram.items())),
        "expectedRawCollision": [
            expected_raw_units.numerator, expected_raw_units.denominator
        ],
        "possibleHitVertices": possible_hit_vertices,
        "hitNeedDegreeBound": hitneed_degree_bound,
        "meanScopedScoreUpper": [mean_upper.numerator, mean_upper.denominator],
        "phtThreshold": threshold,
        "certifiedResidual": [residual.numerator, residual.denominator],
        "phtCertified": residual >= 0,
        "r29SourceSha256": hashlib.sha256(
            (R29 / "r29_lead_gate.py").read_bytes()
        ).hexdigest(),
        "scriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return int(residual < 0)


if __name__ == "__main__":
    raise SystemExit(main())
