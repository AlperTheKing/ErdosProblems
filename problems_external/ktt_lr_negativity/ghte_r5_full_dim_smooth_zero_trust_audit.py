#!/usr/bin/env python3
"""Zero-trust audit of one smooth full-dimensional side-five hive fan.

This checker deliberately does not import ``hive5.py`` or
``ghte_r5_full_dim_smooth_audit.py``.  It reconstructs the thirty rhombus
inequalities from triangular-grid coordinates, asks exact cddlib for the
polytope, and derives the complete simplicial normal fan from tight facets.

The primary gate is q=5.  The Todd curve class is computed independently by
toric fixed-point localization.  Its equality to a nonnegative combination
of invariant curves is then verified by exact intersection pairings with all
ray divisors.  The primitive quotient balancing matrix and the actual edge
length vector are also reconstructed and checked exactly.

Scope: one finite GHTE validation gate.  A PASS is not evidence for the full
King--Tollu--Toumazet conjecture.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import itertools
import json
from math import gcd, lcm
from pathlib import Path

import cdd.gmp as cg
import numpy as np
from scipy.optimize import linprog
from sympy import Matrix


RANK = 5
DIM = 6
TRIPLE = (
    (16, 13, 10, 4, 1),
    (13, 9, 4, 1, 0),
    (27, 22, 13, 5, 4),
)
SLOTS = ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1))


def primitive(vector):
    vector = tuple(int(value) for value in vector)
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    if divisor == 0:
        raise ValueError("zero vector is not primitive")
    return tuple(value // divisor for value in vector)


def fraction_json(value):
    value = Fraction(value)
    return [value.numerator, value.denominator]


def boundary_values(lam, mu, nu):
    """Return the three boundary paths in the fixed triangular convention."""
    if sum(lam) + sum(mu) != sum(nu):
        raise ValueError("weight mismatch")
    partial = lambda part, k: sum(part[:k])
    values = {(0, y): partial(lam, y) for y in range(RANK + 1)}
    values.update({
        (x, RANK - x): sum(lam) + partial(mu, x)
        for x in range(RANK + 1)
    })
    values.update({(x, 0): partial(nu, x) for x in range(RANK + 1)})
    values[(0, 0)] = 0
    return values


def rhombi():
    """Generate all three orientations as (obtuse, acute, label)."""
    output = []
    for x in range(RANK + 1):
        for y in range(RANK + 1):
            if x + y <= RANK - 2:
                output.append((
                    ((x + 1, y), (x, y + 1)),
                    ((x, y), (x + 1, y + 1)),
                    ("A", x, y),
                ))
            if y >= 1 and x + y <= RANK - 1:
                output.append((
                    ((x, y), (x + 1, y)),
                    ((x, y + 1), (x + 1, y - 1)),
                    ("B", x, y),
                ))
            if x >= 1 and x + y <= RANK - 1:
                output.append((
                    ((x, y), (x, y + 1)),
                    ((x + 1, y), (x - 1, y + 1)),
                    ("C", x, y),
                ))
    return output


def hive_inequalities():
    """Derive A h <= b directly from obtuse-sum >= acute-sum."""
    slot_index = {slot: index for index, slot in enumerate(SLOTS)}
    boundary = boundary_values(*TRIPLE)
    rows = []
    boundary_only = []
    for obtuse, acute, label in rhombi():
        coefficients = [0] * DIM
        rhs = 0
        # acute - obtuse <= 0; move known boundary coordinates to the RHS.
        for sign, vertices in ((1, acute), (-1, obtuse)):
            for vertex in vertices:
                if vertex in slot_index:
                    coefficients[slot_index[vertex]] += sign
                else:
                    rhs -= sign * boundary[vertex]
        if any(coefficients):
            rows.append((tuple(coefficients), int(rhs), label))
        else:
            boundary_only.append((int(rhs), label))
    if len(rows) != 30 or len(rhombi()) != 30:
        raise AssertionError((len(rows), len(rhombi())))
    if any(rhs < 0 for rhs, _ in boundary_only):
        raise AssertionError("violated boundary-only rhombus")
    return rows


def normalize_cdd_inequality(row):
    """Normalize c0+c.x>=0 to primitive outward a.x<=h."""
    values = [Fraction(value) for value in row]
    scale = 1
    for value in values:
        scale = lcm(scale, value.denominator)
    integers = [int(value * scale) for value in values]
    divisor = 0
    for value in integers[1:]:
        divisor = gcd(divisor, abs(value))
    if divisor == 0:
        raise ValueError("constant inequality")
    normal = tuple(-value // divisor for value in integers[1:])
    support = Fraction(integers[0], divisor)
    return normal, support


def exact_polytope_and_fan():
    rows = hive_inequalities()
    hrep = cg.matrix_from_array(
        [[Fraction(rhs)] + [Fraction(-value) for value in normal]
         for normal, rhs, _ in rows],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(hrep)
    if hrep.lin_set:
        raise AssertionError("unexpected affine equations")
    facets = sorted(normalize_cdd_inequality(row) for row in hrep.array)
    if len(set(facets)) != len(facets):
        raise AssertionError("duplicate canonical facets")

    polyhedron = cg.polyhedron_from_matrix(hrep)
    generators = cg.copy_generators(polyhedron)
    vertices = []
    for row in generators.array:
        if Fraction(row[0]) != 1:
            raise AssertionError("polyhedron is unbounded")
        vertices.append(tuple(Fraction(value) for value in row[1:]))
    vertices = tuple(sorted(set(vertices)))
    if not vertices:
        raise AssertionError("empty polytope")

    ray_vectors = tuple(normal for normal, _ in facets)
    supports = tuple(support for _, support in facets)
    maximal = []
    vertex_for_cone = {}
    for vertex in vertices:
        tight = tuple(
            index for index, (normal, support) in enumerate(facets)
            if sum(Fraction(a) * x for a, x in zip(normal, vertex)) == support
        )
        if len(tight) != DIM:
            raise AssertionError(("not simple", vertex, tight))
        determinant = int(Matrix.hstack(
            *(Matrix(ray_vectors[index]) for index in tight)
        ).det())
        if abs(determinant) != 1:
            raise AssertionError(("not smooth", vertex, tight, determinant))
        maximal.append(tight)
        vertex_for_cone[tight] = vertex
    maximal = tuple(sorted(set(maximal)))
    if len(maximal) != len(vertices):
        raise AssertionError("two vertices have the same normal cone")

    cones = {}
    for q in range(DIM + 1):
        cones[q] = tuple(sorted({
            tuple(subset)
            for maximal_cone in maximal
            for subset in itertools.combinations(maximal_cone, q)
        }))

    # Full affine dimension makes the intrinsic tangent lattice exactly Z^6.
    base = Matrix(vertices[0])
    differences = Matrix.hstack(*(Matrix(vertex) - base for vertex in vertices[1:]))
    if differences.rank() != DIM:
        raise AssertionError("not full-dimensional")

    return {
        "rows": rows,
        "facets": tuple(facets),
        "rays": ray_vectors,
        "supports": supports,
        "vertices": vertices,
        "maximal": maximal,
        "vertex_for_cone": vertex_for_cone,
        "cones": cones,
    }


def quotient_basis(fan, tau):
    """Use a containing smooth maximal cone to obtain N/N_tau coordinates."""
    maximal = next(cone for cone in fan["maximal"] if set(tau) <= set(cone))
    complement = tuple(index for index in maximal if index not in tau)
    ordered = tuple(tau) + complement
    basis = Matrix.hstack(*(Matrix(fan["rays"][index]) for index in ordered))
    determinant = int(basis.det())
    if abs(determinant) != 1:
        raise AssertionError((tau, determinant))
    inverse = basis.inv()
    if any(Fraction(value).denominator != 1 for value in inverse):
        raise AssertionError("nonintegral quotient chart")
    return inverse, len(tau)


def balance_matrix(fan, q):
    """Build B_q from primitive image rays in each quotient lattice."""
    if q == 0:
        return Matrix.zeros(0, 1), fan["cones"][0], {}
    columns = fan["cones"][q]
    column_index = {cone: index for index, cone in enumerate(columns)}
    rows = []
    quotient_payload = {}
    quotient_dimension = DIM - q + 1
    for tau in fan["cones"][q - 1]:
        inverse, offset = quotient_basis(fan, tau)
        local_rows = [[0] * len(columns) for _ in range(quotient_dimension)]
        local_payload = {}
        for sigma in columns:
            if not set(tau) < set(sigma):
                continue
            extra = next(index for index in sigma if index not in tau)
            coordinates = tuple(
                int(value) for value in (inverse * Matrix(fan["rays"][extra]))[offset:, :]
            )
            if primitive(coordinates) != coordinates:
                raise AssertionError(("nonprimitive quotient ray", tau, sigma, coordinates))
            local_payload[sigma] = coordinates
            for coordinate, value in enumerate(coordinates):
                local_rows[coordinate][column_index[sigma]] = value
        rows.extend(local_rows)
        quotient_payload[tau] = local_payload
    return Matrix(rows), columns, quotient_payload


def primitive_kernel_direction(normals):
    kernel = Matrix(normals).nullspace()
    if len(kernel) != 1:
        raise AssertionError("expected a rank-five wall")
    vector = kernel[0]
    scale = 1
    for value in vector:
        scale = lcm(scale, int(value.q))
    return primitive(tuple(int(value * scale) for value in vector))


def edge_lengths(fan):
    lengths = []
    endpoint_payload = {}
    for sigma in fan["cones"][5]:
        containing = tuple(cone for cone in fan["maximal"] if set(sigma) < set(cone))
        if len(containing) != 2:
            raise AssertionError(("bad complete-fan wall", sigma, containing))
        endpoints = tuple(fan["vertex_for_cone"][cone] for cone in containing)
        direction = primitive_kernel_direction([fan["rays"][index] for index in sigma])
        difference = tuple(endpoints[1][i] - endpoints[0][i] for i in range(DIM))
        ratios = [Fraction(delta, step) for delta, step in zip(difference, direction) if step]
        if not ratios or any(value != ratios[0] for value in ratios):
            raise AssertionError((sigma, endpoints, direction))
        length = abs(ratios[0])
        if length <= 0:
            raise AssertionError("zero edge")
        lengths.append(length)
        endpoint_payload[sigma] = (endpoints, direction, length)
    return Matrix(lengths), endpoint_payload


TODD_TERMS = {
    0: Fraction(1),
    1: Fraction(1, 2),
    2: Fraction(1, 12),
    4: Fraction(-1, 720),
    6: Fraction(1, 30240),
}


def todd_homogeneous(degree, values):
    polynomial = [Fraction(1)] + [Fraction(0)] * degree
    for value in values:
        updated = [Fraction(0)] * (degree + 1)
        for old_degree, old_coefficient in enumerate(polynomial):
            if old_coefficient == 0:
                continue
            for add_degree, bernoulli_coefficient in TODD_TERMS.items():
                if old_degree + add_degree <= degree:
                    updated[old_degree + add_degree] += (
                        old_coefficient * bernoulli_coefficient * value ** add_degree
                    )
        polynomial = updated
    return polynomial[degree]


def localization_charts(fan, probe):
    charts = {}
    for maximal in fan["maximal"]:
        basis = Matrix.hstack(*(Matrix(fan["rays"][index]) for index in maximal))
        coordinates = basis.inv() * Matrix(probe)
        values = {index: Fraction(coordinates[position])
                  for position, index in enumerate(maximal)}
        if any(value == 0 for value in values.values()):
            raise ValueError("nongeneric localization probe")
        charts[maximal] = values
    return charts


def localize_monomial(fan, charts, factors):
    """Integrate a degree-six divisor monomial by fixed-point localization."""
    required = set(factors)
    total = Fraction(0)
    for maximal, values in charts.items():
        if not required <= set(maximal):
            continue
        numerator = Fraction(1)
        for index in factors:
            numerator *= values[index]
        denominator = Fraction(1)
        for index in maximal:
            denominator *= values[index]
        total += numerator / denominator
    return total


def localize_todd_pairing(fan, charts, cone, q):
    """Integrate x_cone * td_q, where dim(cone)=6-q."""
    required = set(cone)
    total = Fraction(0)
    for maximal, values in charts.items():
        if not required <= set(maximal):
            continue
        numerator = Fraction(1)
        for index in cone:
            numerator *= values[index]
        numerator *= todd_homogeneous(q, tuple(values.values()))
        denominator = Fraction(1)
        for index in maximal:
            denominator *= values[index]
        total += numerator / denominator
    return total


def effective_certificate(fan, q):
    probes = (
        (1, 7, 31, 127, 511, 2053),
        (3, 11, 47, 191, 769, 3079),
    )
    charts = [localization_charts(fan, probe) for probe in probes]
    test_cones = fan["cones"][DIM - q]
    orbit_cones = fan["cones"][q]

    targets = []
    intersections = []
    for chart in charts:
        targets.append(Matrix([
            localize_todd_pairing(fan, chart, cone, q)
            for cone in test_cones
        ]))
        intersections.append(Matrix([
            [localize_monomial(fan, chart, test_cone + orbit_cone)
             for orbit_cone in orbit_cones]
            for test_cone in test_cones
        ]))
    if targets[0] != targets[1] or intersections[0] != intersections[1]:
        raise AssertionError("localization result depends on the generic probe")
    target = targets[0]
    intersection = intersections[0]

    # A floating-point LP is used only to identify a candidate basic support.
    # Every value in the returned certificate is recomputed and checked over Q.
    float_matrix = np.array(intersection.tolist(), dtype=float)
    float_target = np.array(target, dtype=float).reshape(-1)
    result = linprog(
        np.zeros(len(orbit_cones)),
        A_eq=float_matrix,
        b_eq=float_target,
        bounds=[(0, None)] * len(orbit_cones),
        method="highs",
        options={"dual_feasibility_tolerance": 1e-9,
                 "primal_feasibility_tolerance": 1e-9},
    )
    if not result.success:
        raise AssertionError(("no numerical effective certificate", result.message))
    support = [index for index, value in enumerate(result.x) if value > 1e-9]
    candidate_matrix = intersection[:, support]
    solution_set = Matrix.gauss_jordan_solve(candidate_matrix, target)
    solution = solution_set[0]
    parameters = solution_set[1]
    if parameters.rows:
        substitutions = {symbol: 0 for symbol in parameters}
        solution = solution.subs(substitutions)
    certificate = [Fraction(0)] * len(orbit_cones)
    for index, value in zip(support, solution):
        certificate[index] = Fraction(value)
    certificate_vector = Matrix(certificate)
    if intersection * certificate_vector != target:
        raise AssertionError("candidate certificate fails exact equality")
    if any(value < 0 for value in certificate):
        raise AssertionError(("candidate certificate is not effective", certificate))

    return {
        "target": target,
        "intersection": intersection,
        "certificate": certificate_vector,
        "certificate_support": tuple(
            (orbit_cones[index], certificate[index])
            for index in range(len(orbit_cones)) if certificate[index]
        ),
        "rank": intersection.rank(),
        "test_cones": test_cones,
        "orbit_cones": orbit_cones,
    }


def stable_hash(payload):
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    fan = exact_polytope_and_fan()
    all_certificates = {}
    balance_summaries = {}
    for q in range(DIM + 1):
        certificate_q = effective_certificate(fan, q)
        balance_q, cones_q, _ = balance_matrix(fan, q)
        if certificate_q["intersection"] * balance_q.T != Matrix.zeros(
                certificate_q["intersection"].rows, balance_q.rows):
            raise AssertionError(("Chow quotient does not annihilate balancing", q))
        if balance_q.rank() + certificate_q["rank"] != len(cones_q):
            raise AssertionError(("balancing rows do not give all Chow relations", q))
        all_certificates[q] = certificate_q
        balance_summaries[q] = (balance_q.rows, balance_q.cols, balance_q.rank())

    balance, q5_cones, quotient_payload = balance_matrix(fan, 5)
    lengths, edge_payload = edge_lengths(fan)
    if balance * lengths != Matrix.zeros(balance.rows, 1):
        raise AssertionError("actual edge-length vector is not balanced")

    certificate = all_certificates[5]
    linear_from_supports = sum(
        fan["supports"][index] * certificate["target"][index]
        for index in range(len(fan["rays"]))
    )
    linear_from_edges = (lengths.T * certificate["certificate"])[0]
    if linear_from_supports != linear_from_edges:
        raise AssertionError("Todd divisor pairing disagrees with edge cycle")

    payload = {
        "scope": "one finite side-five GHTE validation gate; not a proof of general KTT",
        "triple": [list(part) for part in TRIPLE],
        "rhombi": len(rhombi()),
        "facets": len(fan["facets"]),
        "vertex_count": len(fan["vertices"]),
        "cone_counts": {str(q): len(fan["cones"][q]) for q in range(DIM + 1)},
        "full_dimensional": True,
        "intrinsic_lattice": "Z^6 (ambient full dimension; saturated)",
        "smooth": True,
        "rays": [list(ray) for ray in fan["rays"]],
        "supports": [fraction_json(value) for value in fan["supports"]],
        "vertex_coordinates": [
            [fraction_json(value) for value in vertex] for vertex in fan["vertices"]
        ],
        "maximal_cones": [list(cone) for cone in fan["maximal"]],
        "all_q": {
            str(q): {
                "orbit_cones": len(fan["cones"][q]),
                "chow_rank": all_certificates[q]["rank"],
                "balance_shape": list(balance_summaries[q][:2]),
                "balance_rank": balance_summaries[q][2],
                "effective_support_size": len(all_certificates[q]["certificate_support"]),
                "effective_min": fraction_json(min(all_certificates[q]["certificate"])),
                "effective_cycle": [
                    {"cone": list(cone), "coefficient": fraction_json(value)}
                    for cone, value in all_certificates[q]["certificate_support"]
                ],
            }
            for q in range(DIM + 1)
        },
        "q5": {
            "cones": len(q5_cones),
            "balance_shape": [balance.rows, balance.cols],
            "balance_rank": balance.rank(),
            "edge_lengths_positive": all(value > 0 for value in lengths),
            "edge_balance_zero": True,
            "todd_pairing_rank": certificate["rank"],
            "effective_support_size": len(certificate["certificate_support"]),
            "effective_min": fraction_json(min(certificate["certificate"])),
            "target": [fraction_json(value) for value in certificate["target"]],
            "linear_coefficient": fraction_json(linear_from_edges),
            "chow_annihilates_balance": True,
            "rank_complement": certificate["rank"] + balance.rank() == len(q5_cones),
            "cone_order": [list(cone) for cone in q5_cones],
            "balance_matrix": [[int(value) for value in balance.row(row)]
                               for row in range(balance.rows)],
            "edge_lengths": [fraction_json(value) for value in lengths],
            "primitive_quotient_vectors": [
                {
                    "tau": list(tau),
                    "incidences": [
                        {"sigma": list(sigma), "vector": list(vector)}
                        for sigma, vector in sorted(incidences.items())
                    ],
                }
                for tau, incidences in sorted(quotient_payload.items())
            ],
            "effective_cycle": [
                {"cone": list(cone), "coefficient": fraction_json(value)}
                for cone, value in certificate["certificate_support"]
            ],
        },
    }
    payload["payload_sha256"] = stable_hash(payload)
    output = Path(__file__).with_name("ghte_r5_full_dim_smooth_zero_trust_payload.json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("PASS: independent side-five smooth complete-fan q=5 audit")
    print("facets=%d vertices=%d cones=%s" % (
        len(fan["facets"]), len(fan["vertices"]), payload["cone_counts"]
    ))
    print("B5=%dx%d rank=%d edge_balance=0" % (
        balance.rows, balance.cols, balance.rank()
    ))
    print("td5_pairing_rank=%d effective_support=%d min=%s" % (
        certificate["rank"], len(certificate["certificate_support"]),
        min(certificate["certificate"]),
    ))
    print("all_q_chow_ranks=%s all_q_effective=PASS" % (
        tuple(all_certificates[q]["rank"] for q in range(DIM + 1)),
    ))
    print("linear_coefficient=%s" % linear_from_edges)
    print("payload_sha256=%s" % payload["payload_sha256"])


if __name__ == "__main__":
    main()
