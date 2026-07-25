#!/usr/bin/env python3
"""Targeted realization gate for one nonunit side-five hive circuit.

The fixed primitive circuit is the A5-normal relation

    n0 - 2*n2 - n3 + 2*n4 = 0.

Its support functional is
`(mu_4-mu_5)-(nu_4-nu_5)`.  This script searches only the existing
finite `wave4_pop.json` dim-6 corpus for the two triangulations with a common
three-ray link, then verifies the interpolated wall over GMP rationals.  It is
a falsification gate for the proposed unit-crepant-wall lemma, not a KTT
census.
"""

from collections import defaultdict
from fractions import Fraction
from math import gcd, lcm
import json
import sys

import cdd.gmp as cg

sys.path.insert(0, "problems_external/ktt_lr_negativity/r5_certificate")
from hive5 import NORMALS5, build_hive5  # noqa: E402


# This bottom-boundary circuit occurs as four simultaneous global facets in
# 116 members of the fixed corpus; the first raw circuit tested did not.
TARGET_INDICES = (11, 15, 16, 17)
TARGET = tuple(NORMALS5[i] for i in TARGET_INDICES)
COEFFICIENTS = (1, -2, -1, 2)
POSITIVE = frozenset((TARGET[0], TARGET[3]))
NEGATIVE = frozenset((TARGET[1], TARGET[2]))


def parse(text):
    parts = tuple(int(value) for value in text.split(","))
    return parts + (0,) * (5 - len(parts))


def primitive(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, Fraction(value).denominator)
    integers = tuple(int(Fraction(value) * denominator) for value in vector)
    divisor = gcd(0, *(abs(value) for value in integers))
    assert divisor
    return tuple(value // divisor for value in integers), divisor


def exact_fan(boundary, allow_wall=False):
    hive = build_hive5(*boundary)
    if not hive["ok"]:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(rhs)] + [Fraction(-x) for x in row]
         for row, rhs in zip(hive["A"], hive["b"])],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if matrix.lin_set:
        return None
    facets = []
    supports = {}
    for row in matrix.array:
        normal, divisor = primitive(tuple(-value for value in row[1:]))
        support = Fraction(row[0], divisor)
        if normal in supports:
            return None
        facets.append(normal)
        supports[normal] = support
    if not set(TARGET).issubset(supports):
        return None

    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    if not generators.array or any(row[0] != 1 for row in generators.array):
        return None
    vertices = tuple(tuple(Fraction(x) for x in row[1:])
                     for row in generators.array)
    tight_sets = []
    for vertex in vertices:
        tight = tuple(sorted(
            normal for normal, row in zip(facets, matrix.array)
            if Fraction(row[0])
            + sum(Fraction(row[j + 1]) * vertex[j] for j in range(6)) == 0
        ))
        if not allow_wall and len(tight) != 6:
            return None
        if allow_wall and len(tight) not in (6, 7):
            return None
        tight_sets.append(tight)
    omega = sum(coefficient * supports[normal]
                for coefficient, normal in zip(COEFFICIENTS, TARGET))
    expected = ((boundary[1][3] - boundary[1][4])
                - (boundary[2][3] - boundary[2][4]))
    assert omega == expected
    return {
        "boundary": boundary,
        "facets": tuple(sorted(facets)),
        "supports": supports,
        "omega": omega,
        "tight_sets": tuple(sorted(tight_sets)),
        "vertices": vertices,
    }


def flip_links(fan):
    """Return common links carrying either circuit triangulation."""
    by_link = defaultdict(set)
    target = frozenset(TARGET)
    for tight in fan["tight_sets"]:
        tight = frozenset(tight)
        circuit_part = tight & target
        if len(circuit_part) != 3:
            continue
        link = tight - target
        if len(link) == 3:
            by_link[tuple(sorted(link))].add(circuit_part)
    output = []
    left_triples = frozenset((target - frozenset((ray,)) for ray in POSITIVE))
    right_triples = frozenset((target - frozenset((ray,)) for ray in NEGATIVE))
    for link, triples in by_link.items():
        frozen = frozenset(triples)
        if frozen == left_triples:
            output.append((link, "positive_omissions"))
        elif frozen == right_triples:
            output.append((link, "negative_omissions"))
    return tuple(output)


def interpolate_wall(left, right, link):
    assert left["omega"] * right["omega"] < 0
    t = -left["omega"] / (right["omega"] - left["omega"])
    denominator = t.denominator
    boundary = tuple(tuple(int(denominator * ((1 - t) * x + t * y))
                           for x, y in zip(left_part, right_part))
                     for left_part, right_part in zip(left["boundary"], right["boundary"]))
    wall = exact_fan(boundary, allow_wall=True)
    if wall is None or wall["omega"] != 0 or wall["facets"] != left["facets"]:
        return None
    target_wall = frozenset(TARGET) | frozenset(link)
    nonsimple = [frozenset(tight) for tight in wall["tight_sets"] if len(tight) == 7]
    if nonsimple != [target_wall]:
        return None
    return {"t": t, "scale": denominator, "boundary": boundary,
            "wall_tight_sets": wall["tight_sets"]}


def main():
    records = json.load(open(
        "problems_external/ktt_lr_negativity/purged_region/wave4_pop.json",
        encoding="utf-8",
    ))
    records = [record for record in records
               if record.get("d_ambient") == 6 and record.get("dim") == 6]
    groups = defaultdict(lambda: {"positive_omissions": [], "negative_omissions": []})
    accepted = 0
    for index, record in enumerate(records):
        boundary = tuple(parse(record[key]) for key in ("lam", "mu", "nu"))
        fan = exact_fan(boundary)
        if fan is None or fan["omega"] == 0:
            continue
        accepted += 1
        for link, orientation in flip_links(fan):
            key = fan["facets"], link
            opposite = ("negative_omissions" if orientation == "positive_omissions"
                        else "positive_omissions")
            for candidate in groups[key][opposite]:
                if candidate["omega"] * fan["omega"] >= 0:
                    continue
                wall = interpolate_wall(candidate, fan, link)
                if wall is None:
                    continue
                print("PASS")
                print("records", len(records), "accepted", accepted, "index", index)
                print("target", TARGET)
                print("coefficients", COEFFICIENTS)
                print("left", candidate["boundary"], candidate["omega"], opposite)
                print("right", fan["boundary"], fan["omega"], orientation)
                print("link", link)
                print("wall", wall)
                return 0
            groups[key][orientation].append(fan)
    print("NO_REALIZATION", len(records), accepted, len(groups))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
