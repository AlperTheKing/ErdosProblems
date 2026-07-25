#!/usr/bin/env python3
"""Zero-trust audit of the intrinsic-dimensional-three side-five GHTE gate.

This program deliberately does not import the checker being audited or any of
its r4 linear-algebra helpers.  It uses only the authoritative side-five hive
inequalities and exact ambient vertex engine.  The intrinsic H-description is
recovered by restricting all thirty hive inequalities to the saturated
direction lattice.  Facets therefore do not come from the audited script's
supporting-triple enumeration.

For q=2, quotient rays are embedded independently as primitive cross-product
images.  For q=3, the balance matrix is an independently oriented graph
incidence matrix.  Vertex BV values are recomputed for every cyclic fan
triangulation and all results must agree after exact unimodular refinement.
All decisions use integers or Fraction.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm
import argparse
import hashlib
import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_certificate"))

from hive5 import build_hive5  # noqa: E402
from polytope5 import (affine_rank as ambient_affine_rank, lattice_coords,
                       reduce_rhs, vertices as ambient_vertices)  # noqa: E402


HORN_GAP = {
    "lambda": (4, 3, 3, 1, 0),
    "mu": (4, 2, 1, 1, 0),
    "nu": (6, 5, 4, 2, 2),
}
HARD = {
    "lambda": (27, 6),
    "mu": (20, 8, 4, 1),
    "nu": (40, 14, 5, 4, 3),
}
CORPUS = os.path.join(HERE, "tier0", "runs", "fam4", "_sym5b.jsonl")


def dot(left, right):
    return sum(Fraction(x) * Fraction(y) for x, y in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def det3_rows(a, b, c):
    return dot(a, cross(b, c))


def rank(rows):
    if not rows:
        return 0
    work = [[Fraction(value) for value in row] for row in rows]
    row = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(row, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        scale = work[row][column]
        work[row] = [value / scale for value in work[row]]
        for i in range(len(work)):
            if i != row and work[i][column]:
                scale = work[i][column]
                work[i] = [x - scale * y for x, y in zip(work[i], work[row])]
        row += 1
        if row == len(work):
            break
    return row


def inverse(matrix):
    size = len(matrix)
    work = [
        [Fraction(matrix[i][j]) for j in range(size)]
        + [Fraction(i == j) for j in range(size)]
        for i in range(size)
    ]
    for column in range(size):
        pivot = next(i for i in range(column, size) if work[i][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for i in range(size):
            if i == column:
                continue
            scale = work[i][column]
            if scale:
                work[i] = [x - scale * y for x, y in zip(work[i], work[column])]
    return tuple(tuple(row[size:]) for row in work)


def matmul(left, right):
    return tuple(tuple(
        sum(Fraction(left[i][k]) * Fraction(right[k][j])
            for k in range(len(right)))
        for j in range(len(right[0]))) for i in range(len(left)))


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix):
    return tuple(tuple(row[j] for row in matrix) for j in range(len(matrix[0])))


def solve_linear(rows, rhs):
    """Return one exact solution, setting free coordinates to zero."""
    work = [
        [Fraction(value) for value in row] + [Fraction(rhs[i])]
        for i, row in enumerate(rows)
    ]
    ncols = len(rows[0])
    pivots = []
    row = 0
    for column in range(ncols):
        pivot = next((i for i in range(row, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        scale = work[row][column]
        work[row] = [value / scale for value in work[row]]
        for i in range(len(work)):
            if i != row and work[i][column]:
                scale = work[i][column]
                work[i] = [x - scale * y for x, y in zip(work[i], work[row])]
        pivots.append(column)
        row += 1
        if row == len(work):
            break
    for i in range(row, len(work)):
        assert any(work[i][j] for j in range(ncols)) or work[i][ncols] == 0
    answer = [Fraction(0)] * ncols
    for i, column in enumerate(pivots):
        answer[column] = work[i][ncols]
    assert matvec(rows, answer) == tuple(Fraction(value) for value in rhs)
    return tuple(answer)


def affine_rank3(points):
    if len(points) <= 1:
        return 0
    base = points[0]
    return rank(tuple(tuple(point[i] - base[i] for i in range(3))
                      for point in points[1:]))


def primitive_integer(vector):
    divisor = 0
    for value in vector:
        assert Fraction(value).denominator == 1
        divisor = gcd(divisor, abs(int(value)))
    assert divisor
    return tuple(int(value) // divisor for value in vector)


def primitive_rational_ray(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, Fraction(value).denominator)
    integral = tuple(int(Fraction(value) * denominator) for value in vector)
    return primitive_integer(integral)


def saturation_index(basis):
    divisor = 0
    for cols in combinations(range(6), 3):
        minor = tuple(tuple(basis[i][j] for j in cols) for i in range(3))
        divisor = gcd(divisor, abs(int(det3_rows(*minor))))
    return divisor


def metric_dot(left, right, gram):
    return sum(Fraction(left[i]) * gram[i][j] * Fraction(right[j])
               for i in range(3) for j in range(3))


def recover_intrinsic(boundary):
    hive = build_hive5(boundary["lambda"], boundary["mu"], boundary["nu"])
    assert hive["ok"]
    ambient = tuple(ambient_vertices(reduce_rhs(hive["b"])))
    assert ambient_affine_rank(ambient) == 3
    raw_coordinates, dimension = lattice_coords(ambient)
    assert dimension == 3
    coordinates = tuple(tuple(Fraction(value) for value in point)
                        for point in raw_coordinates)
    assert coordinates[0] == (0, 0, 0)

    chosen = next(indices for indices in combinations(range(1, len(ambient)), 3)
                  if det3_rows(*(coordinates[i] for i in indices)) != 0)
    coordinate_rows = tuple(coordinates[i] for i in chosen)
    ambient_differences = tuple(
        tuple(ambient[i][j] - ambient[0][j] for j in range(6)) for i in chosen
    )
    basis_q = matmul(inverse(coordinate_rows), ambient_differences)
    assert all(value.denominator == 1 for row in basis_q for value in row)
    basis = tuple(tuple(int(value) for value in row) for row in basis_q)
    assert saturation_index(basis) == 1
    for point, coordinate in zip(ambient, coordinates):
        rebuilt = tuple(ambient[0][j] + sum(
            coordinate[i] * basis[i][j] for i in range(3)
        ) for j in range(6))
        assert rebuilt == point

    primal_gram = tuple(tuple(dot(left, right) for right in basis)
                        for left in basis)
    dual_gram = inverse(primal_gram)

    # Restrict every original hive inequality to x = origin + z*basis.
    reduced = {}
    for row, rhs0 in zip(hive["A"], hive["b"]):
        normal = tuple(sum(row[j] * basis[i][j] for j in range(6))
                       for i in range(3))
        rhs = Fraction(rhs0) - dot(row, ambient[0])
        if not any(normal):
            assert rhs >= 0
            continue
        divisor = 0
        for value in normal:
            divisor = gcd(divisor, abs(value))
        normal = tuple(value // divisor for value in normal)
        rhs /= divisor
        if normal not in reduced or rhs < reduced[normal]:
            reduced[normal] = rhs

    inequalities = tuple((normal, reduced[normal]) for normal in sorted(reduced))
    for point in coordinates:
        assert all(dot(normal, point) <= rhs for normal, rhs in inequalities)

    facets = []
    for normal, rhs in inequalities:
        on = tuple(i for i, point in enumerate(coordinates)
                   if dot(normal, point) == rhs)
        if affine_rank3(tuple(coordinates[i] for i in on)) == 2:
            facets.append({"normal": normal, "rhs": rhs, "vertices": on})
    facets = tuple(facets)

    edge_map = {}
    for left, right in combinations(range(len(facets)), 2):
        common = tuple(sorted(set(facets[left]["vertices"])
                              & set(facets[right]["vertices"])))
        if affine_rank3(tuple(coordinates[i] for i in common)) != 1:
            continue
        assert len(common) == 2
        delta = tuple(coordinates[common[1]][i] - coordinates[common[0]][i]
                      for i in range(3))
        denominator = 1
        for value in delta:
            denominator = lcm(denominator, value.denominator)
        integral = tuple(int(value * denominator) for value in delta)
        divisor = 0
        for value in integral:
            divisor = gcd(divisor, abs(value))
        tangent = tuple(value // divisor for value in integral)
        length = Fraction(divisor, denominator)
        record = {"vertices": common, "facets": (left, right),
                  "primitive_tangent": tangent, "length": length}
        assert common not in edge_map
        edge_map[common] = record
    edges = tuple(edge_map[key] for key in sorted(edge_map))
    assert len(coordinates) - len(edges) + len(facets) == 2
    vertex_facets = tuple(tuple(i for i, facet in enumerate(facets)
                                if v in facet["vertices"])
                          for v in range(len(coordinates)))
    return {
        "boundary": boundary,
        "hive": hive,
        "ambient_vertices": ambient,
        "vertices": coordinates,
        "origin": ambient[0],
        "basis": basis,
        "primal_gram": primal_gram,
        "dual_gram": dual_gram,
        "inequalities": inequalities,
        "facets": facets,
        "edges": edges,
        "vertex_facets": vertex_facets,
    }


def pair_index(left, right):
    divisor = 0
    for value in cross(left, right):
        divisor = gcd(divisor, abs(int(value)))
    return divisor


def q2_unimodular_alpha(left, right, dual_gram):
    assert pair_index(left, right) == 1
    aa = metric_dot(left, left, dual_gram)
    bb = metric_dot(right, right, dual_gram)
    cc = metric_dot(left, right, dual_gram)
    return Fraction(1, 4) - Fraction(1, 12) * cc * (
        Fraction(1, aa) + Fraction(1, bb)
    )


def q2_alpha(left, right, dual_gram):
    index = pair_index(left, right)
    if index == 1:
        return q2_unimodular_alpha(left, right, dual_gram), None
    candidates = []
    for a, b in product(range(1, index), repeat=2):
        numerator = tuple(a * left[i] + b * right[i] for i in range(3))
        if not all(value % index == 0 for value in numerator):
            continue
        ray = primitive_integer(tuple(value // index for value in numerator))
        li, ri = pair_index(left, ray), pair_index(ray, right)
        if 0 < li < index and 0 < ri < index:
            candidates.append((max(li, ri), li + ri, tuple(-x for x in ray), ray))
    assert candidates, (left, right, index)
    middle = min(candidates)[-1]
    assert pair_index(left, middle) == pair_index(middle, right) == 1
    value = (q2_unimodular_alpha(left, middle, dual_gram)
             + q2_unimodular_alpha(middle, right, dual_gram))

    # Independent closed formula for an index-two cone.
    if index == 2:
        aa = metric_dot(left, left, dual_gram)
        bb = metric_dot(right, right, dual_gram)
        cc = metric_dot(left, right, dual_gram)
        closed = Fraction(1, 4) - Fraction(1, 12 * index) * cc * (
            Fraction(1, aa) + Fraction(1, bb)
        )
        assert value == closed
    return value, middle


def q2_contract(model):
    facets, edges = model["facets"], model["edges"]
    matrix = [[0] * len(edges) for _ in range(3 * len(facets))]
    alphas, lengths, insertions, indices = [], [], [], []
    for e, edge in enumerate(edges):
        left, right = edge["facets"]
        for facet_index, other_index in ((left, right), (right, left)):
            image = primitive_integer(cross(facets[facet_index]["normal"],
                                            facets[other_index]["normal"]))
            for k in range(3):
                matrix[3 * facet_index + k][e] = image[k]
        alpha, middle = q2_alpha(facets[left]["normal"],
                                 facets[right]["normal"], model["dual_gram"])
        alphas.append(alpha)
        lengths.append(edge["length"])
        insertions.append(middle)
        indices.append(pair_index(facets[left]["normal"],
                                  facets[right]["normal"]))
    matrix = tuple(tuple(row) for row in matrix)
    alphas, lengths = tuple(alphas), tuple(lengths)
    balance = matvec(matrix, lengths)
    assert balance == (Fraction(0),) * len(matrix)
    return {
        "B_cross_embedding": matrix,
        "rank_B": rank(matrix),
        "kernel_dimension": len(edges) - rank(matrix),
        "face_volume_v": lengths,
        "B_times_v": balance,
        "BV_a": alphas,
        "pair_indices": tuple(indices),
        "inserted_rays": tuple(insertions),
        "pairing": dot(alphas, lengths),
        "Farkas_y": (Fraction(0),) * len(matrix),
        "shifted_BV": alphas,
    }


def coordinates_in_normal_cell(vector, rays):
    row_matrix = tuple(tuple(rays[j][i] for j in range(3)) for i in range(3))
    return matvec(inverse(row_matrix), vector)


def refinement_ray(rays):
    index = abs(int(det3_rows(*rays)))
    assert index > 1
    candidates = []
    for residues in product(range(index), repeat=3):
        if not any(residues):
            continue
        numerator = tuple(sum(residues[i] * rays[i][j] for i in range(3))
                          for j in range(3))
        if not all(value % index == 0 for value in numerator):
            continue
        ray = primitive_integer(tuple(value // index for value in numerator))
        coordinates = coordinates_in_normal_cell(ray, rays)
        if not all(value >= 0 for value in coordinates):
            continue
        support = tuple(i for i, value in enumerate(coordinates) if value > 0)
        children = []
        for position in support:
            child = list(rays)
            child[position] = ray
            children.append(abs(int(det3_rows(*child))))
        if children and max(children) < index:
            # Prefer a different tie-break from the audited checker.
            candidates.append((max(children), sum(children),
                               -sum(abs(x) for x in ray), tuple(-x for x in ray), ray))
    assert candidates, (rays, index)
    return min(candidates)[-1]


def q3_unimodular_alpha(rays, primal_gram, dual_gram):
    assert abs(det3_rows(*rays)) == 1
    normal_gram = tuple(tuple(metric_dot(rays[i], rays[j], dual_gram)
                              for j in range(3)) for i in range(3))
    from_normal = inverse(normal_gram)

    # Independently form the primal dual basis to the three normal rows.
    inv_rows = inverse(tuple(tuple(Fraction(x) for x in ray) for ray in rays))
    columns = tuple(tuple(inv_rows[j][i] for j in range(3)) for i in range(3))
    direct = tuple(tuple(metric_dot(columns[i], columns[j], primal_gram)
                         for j in range(3)) for i in range(3))
    assert direct == from_normal
    answer = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        answer += Fraction(1, 24) * direct[i][j] * (
            Fraction(1, direct[i][i]) + Fraction(1, direct[j][j])
        )
    return answer


def refine_q3_cell(rays, primal_gram, dual_gram):
    index = abs(int(det3_rows(*rays)))
    if index == 1:
        return q3_unimodular_alpha(rays, primal_gram, dual_gram), (rays,)
    ray = refinement_ray(rays)
    coordinates = coordinates_in_normal_cell(ray, rays)
    support = tuple(i for i, value in enumerate(coordinates) if value > 0)
    total = Fraction(0)
    leaves = []
    for position in support:
        child = list(rays)
        child[position] = ray
        value, child_leaves = refine_q3_cell(tuple(child), primal_gram, dual_gram)
        total += value
        leaves.extend(child_leaves)
    return total, tuple(leaves)


def facet_cycle(vertex, model):
    incident = model["vertex_facets"][vertex]
    adjacency = {facet: set() for facet in incident}
    for edge in model["edges"]:
        if vertex not in edge["vertices"]:
            continue
        left, right = edge["facets"]
        adjacency[left].add(right)
        adjacency[right].add(left)
    assert all(len(neighbors) == 2 for neighbors in adjacency.values())
    start = max(incident)
    second = max(adjacency[start])
    cycle = [start, second]
    while len(cycle) < len(incident):
        previous, current = cycle[-2], cycle[-1]
        following = next(x for x in adjacency[current] if x != previous)
        assert following not in cycle
        cycle.append(following)
    assert start in adjacency[cycle[-1]]
    return tuple(cycle)


def q3_vertex_alpha(vertex, model):
    cycle = facet_cycle(vertex, model)
    values, leaf_counts = [], []
    for anchor in range(len(cycle)):
        order = cycle[anchor:] + cycle[:anchor]
        total = Fraction(0)
        leaves = []
        for i in range(1, len(order) - 1):
            rays = tuple(model["facets"][j]["normal"]
                         for j in (order[0], order[i], order[i + 1]))
            value, local_leaves = refine_q3_cell(
                rays, model["primal_gram"], model["dual_gram"]
            )
            total += value
            leaves.extend(local_leaves)
        assert all(abs(det3_rows(*leaf)) == 1 for leaf in leaves)
        values.append(total)
        leaf_counts.append(len(leaves))
    assert len(set(values)) == 1, (vertex, cycle, values)
    return values[0], cycle, tuple(leaf_counts)


def q3_contract(model):
    vertices, edges = model["vertices"], model["edges"]
    matrix = [[0] * len(vertices) for _ in range(len(edges))]
    for e, edge in enumerate(edges):
        left, right = edge["vertices"]
        matrix[e][left] = -1
        matrix[e][right] = 1
    matrix = tuple(tuple(row) for row in matrix)
    volumes = (Fraction(1),) * len(vertices)
    assert matvec(matrix, volumes) == (Fraction(0),) * len(edges)
    alphas, cycles, triangulation_leaf_counts = [], [], []
    for vertex in range(len(vertices)):
        alpha, cycle, counts = q3_vertex_alpha(vertex, model)
        alphas.append(alpha)
        cycles.append(cycle)
        triangulation_leaf_counts.append(counts)
    alphas = tuple(alphas)
    target = (Fraction(1, len(vertices)),) * len(vertices)
    rhs = tuple(target[i] - alphas[i] for i in range(len(vertices)))
    y = solve_linear(transpose(matrix), rhs)
    shifted = tuple(alphas[i] + matvec(transpose(matrix), y)[i]
                    for i in range(len(vertices)))
    assert shifted == target
    return {
        "B_graph_incidence": matrix,
        "rank_B": rank(matrix),
        "kernel_dimension": len(vertices) - rank(matrix),
        "face_volume_v": volumes,
        "B_times_v": matvec(matrix, volumes),
        "facet_cycles": tuple(cycles),
        "triangulation_leaf_counts": tuple(triangulation_leaf_counts),
        "BV_a": alphas,
        "pairing": sum(alphas, Fraction(0)),
        "Farkas_y": y,
        "shifted_BV": shifted,
    }


def floor_fraction(value):
    return value.numerator // value.denominator


def ceil_fraction(value):
    return -floor_fraction(-value)


def intrinsic_lattice_count(model, dilation):
    if dilation == 0:
        return 1
    vertices = model["vertices"]
    bounds = []
    for i in range(3):
        bounds.append((ceil_fraction(dilation * min(v[i] for v in vertices)),
                       floor_fraction(dilation * max(v[i] for v in vertices))))
    total = 0
    for point in product(*(range(lo, hi + 1) for lo, hi in bounds)):
        if all(dot(normal, point) <= dilation * rhs
               for normal, rhs in model["inequalities"]):
            total += 1
    return total


def ehrhart(model):
    counts = tuple(intrinsic_lattice_count(model, n) for n in range(6))
    vandermonde = tuple(tuple(Fraction(n) ** k for k in range(4))
                        for n in range(4))
    coefficients = matvec(inverse(vandermonde), counts[:4])
    for n in (4, 5):
        assert sum(coefficients[k] * n ** k for k in range(4)) == counts[n]
    return counts, coefficients


def build_contract(name, boundary):
    model = recover_intrinsic(boundary)
    q2 = q2_contract(model)
    q3 = q3_contract(model)
    counts, coefficients = ehrhart(model)
    assert q2["pairing"] == coefficients[1]
    assert q3["pairing"] == coefficients[0] == 1
    if name == "hard":
        assert model["basis"] == ((1, 0, 0, 0, 0, 0),
                                   (0, 0, 0, 1, 0, 0),
                                   (0, 0, 0, 0, 0, 1))
        assert tuple(model["vertices"]) == (
            (Fraction(0), Fraction(0), Fraction(0)),
            (Fraction(1), Fraction(-1), Fraction(-1)),
            (Fraction(1), Fraction(-1), Fraction(0)),
            (Fraction(3, 2), Fraction(-3, 2), Fraction(-1, 2)),
            (Fraction(2), Fraction(-1), Fraction(-1)),
            (Fraction(2), Fraction(-1), Fraction(0)),
            (Fraction(3), Fraction(0), Fraction(0)),
        )
    return {
        "name": name,
        "boundary": boundary,
        "ambient_vertices": model["ambient_vertices"],
        "intrinsic_vertices": model["vertices"],
        "M_basis_in_Z6": model["basis"],
        "M_gram": model["primal_gram"],
        "N_gram": model["dual_gram"],
        "facets": model["facets"],
        "edges": model["edges"],
        "fan_f_vector": (1, len(model["facets"]), len(model["edges"]),
                         len(model["vertices"])),
        "ehrhart_counts_0_to_5": counts,
        "ehrhart_coefficients": coefficients,
        "q2": q2,
        "q3": q3,
    }


def parse_fraction(value):
    return Fraction(value)


def corpus_audit():
    records_scanned = 0
    dim3 = 0
    cone_count = 0
    negative = 0
    minimum = None
    maximum_vertices = 0
    maximum_index = 0
    qualifying = 0
    balance_failures = 0
    pairing_failures = 0
    first_qualifying = None
    summaries = []
    with open(CORPUS, "r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            record = json.loads(line)
            records_scanned += 1
            if record.get("status") != "OK" or record.get("d") != 3:
                continue
            dim3 += 1
            boundary = {"lambda": tuple(record["lam"]),
                        "mu": tuple(record["mu"]),
                        "nu": tuple(record["nu"])}
            model = recover_intrinsic(boundary)
            q2 = q2_contract(model)
            alphas = q2["BV_a"]
            indices = q2["pair_indices"]
            cone_count += len(alphas)
            negative += sum(value < 0 for value in alphas)
            minimum = min(alphas) if minimum is None else min(minimum, *alphas)
            maximum_vertices = max(maximum_vertices, len(model["vertices"]))
            maximum_index = max(maximum_index, *indices)
            if any(q2["B_times_v"]):
                balance_failures += 1
            expected_a1 = parse_fraction(record["coeffs_low_to_high"][1])
            if q2["pairing"] != expected_a1:
                pairing_failures += 1
            is_qualifying = len(model["vertices"]) > 4 and max(indices) > 1
            if is_qualifying:
                qualifying += 1
                if first_qualifying is None:
                    first_qualifying = (line_number, boundary)
            summaries.append({
                "line": line_number,
                "boundary": boundary,
                "fan_f_vector": (1, len(model["facets"]), len(model["edges"]),
                                 len(model["vertices"])),
                "q2_rank": q2["rank_B"],
                "q2_kernel_dimension": q2["kernel_dimension"],
                "q2_pair_indices": indices,
                "q2_BV_a": alphas,
                "q2_pairing": q2["pairing"],
                "record_a1": expected_a1,
            })
    assert records_scanned == 1500
    assert dim3 == 87
    assert cone_count == 866
    assert negative == 0
    assert minimum == Fraction(1, 10)
    assert maximum_vertices == 10
    assert maximum_index == 2
    assert qualifying == 6
    assert balance_failures == pairing_failures == 0
    assert first_qualifying == (2, HARD)
    return {
        "records_scanned": records_scanned,
        "intrinsic_dim3_records_rebuilt": dim3,
        "q2_cones_rebuilt": cone_count,
        "negative_q2_entries": negative,
        "minimum_q2_alpha": minimum,
        "maximum_vertex_count": maximum_vertices,
        "maximum_pair_saturation_index": maximum_index,
        "qualifying_records": qualifying,
        "balance_failures": balance_failures,
        "pairing_failures_against_recorded_exact_polynomial": pairing_failures,
        "first_qualifying_line_and_boundary": first_qualifying,
        "per_record": tuple(summaries),
    }


def serialize(value):
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else str(value)
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    contracts = (build_contract("horn_gap", HORN_GAP),
                 build_contract("hard", HARD))
    corpus = corpus_audit()
    payload = serialize({"schema": "r5-lowerdim-ghte-zero-trust-v1",
                         "contracts": contracts, "corpus": corpus})
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("ascii")).hexdigest()
    if args.full:
        print(json.dumps(payload, sort_keys=True, indent=2))
    print("PASS")
    print("audit_sha256=" + digest)
    print("corpus=" + json.dumps({key: serialize(value) for key, value in corpus.items()
                                  if key != "per_record"}, sort_keys=True,
                                 separators=(",", ":")))
    for contract in contracts:
        print(f"{contract['name']}: fan={contract['fan_f_vector']} "
              f"ehrhart={contract['ehrhart_coefficients']}")
        for degree in ("q2", "q3"):
            data = contract[degree]
            print(f"  {degree}: rank={data['rank_B']} "
                  f"ker={data['kernel_dimension']} pairing={data['pairing']} "
                  f"min_raw={min(data['BV_a'])} min_shifted={min(data['shifted_BV'])}")


if __name__ == "__main__":
    main()
