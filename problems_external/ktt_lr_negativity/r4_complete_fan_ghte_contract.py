#!/usr/bin/env python3
"""Exact complete-normal-fan GHTE foundation contract for one rank-4 hive.

The program reconstructs the hive from the three rhombus families, enumerates
its complete face lattice, builds quotient-lattice balancing matrices for
q=2 and q=3, computes normalized face volumes and Berline--Vergne weights,
and emits exact Farkas primal certificates.

All decisions use integers or Fraction.  The default output is a compact
summary; ``--full`` prints the entire canonical JSON contract.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd
import argparse
import hashlib
import json


RANK = 4
LAM = (12, 8, 4, 0)
MU = (12, 8, 4, 0)
NU = (18, 14, 10, 6)
INTERIOR = ((1, 1), (1, 2), (2, 1))


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def det3_columns(a, b, c):
    return dot(a, cross(b, c))


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    if not divisor:
        raise ValueError("zero vector is not primitive")
    return tuple(int(value) // divisor for value in vector)


def canonical_sign(vector):
    vector = primitive(vector)
    first = next(value for value in vector if value)
    return vector if first > 0 else tuple(-value for value in vector)


def matrix_rank(rows):
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


def affine_rank(points):
    if len(points) <= 1:
        return 0
    base = points[0]
    return matrix_rank([[x - y for x, y in zip(point, base)] for point in points[1:]])


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


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def solve_square(rows, rhs):
    inv = inverse(rows)
    return matvec(inv, rhs)


def solve_linear(rows, rhs):
    """One exact solution, with all nonpivot variables set to zero."""
    if not rows:
        assert not rhs
        return []
    columns = len(rows[0])
    work = [
        [Fraction(value) for value in row] + [Fraction(rhs[i])]
        for i, row in enumerate(rows)
    ]
    pivot_columns = []
    row = 0
    for column in range(columns):
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
        pivot_columns.append(column)
        row += 1
        if row == len(work):
            break
    for i in range(row, len(work)):
        assert any(work[i][j] for j in range(columns)) or not work[i][columns]
    solution = [Fraction(0)] * columns
    for i, column in enumerate(pivot_columns):
        solution[column] = work[i][columns]
    assert all(dot(r, solution) == b for r, b in zip(rows, rhs))
    return solution


def boundary_values():
    boundary = {}
    total = 0
    for y in range(RANK + 1):
        boundary[(0, y)] = total
        if y < RANK:
            total += LAM[y]
    total = sum(LAM)
    for x in range(RANK + 1):
        boundary[(x, RANK - x)] = total
        if x < RANK:
            total += MU[x]
    total = 0
    for x in range(RANK + 1):
        boundary[(x, 0)] = total
        if x < RANK:
            total += NU[x]
    boundary[(0, 0)] = 0
    return boundary


def rhombus_rows():
    boundary = boundary_values()
    coordinate = {point: i for i, point in enumerate(INTERIOR)}
    rows = []

    def add(tag, plus, minus):
        normal = [0, 0, 0]
        constant = 0
        for point in plus:
            if point in coordinate:
                normal[coordinate[point]] -= 1
            else:
                constant -= boundary[point]
        for point in minus:
            if point in coordinate:
                normal[coordinate[point]] += 1
            else:
                constant += boundary[point]
        rows.append({"tag": tag, "normal": tuple(normal), "rhs": -constant})

    for x in range(RANK + 1):
        for y in range(RANK + 1):
            if x + y <= RANK - 2:
                add(f"A({x},{y})", ((x + 1, y), (x, y + 1)),
                    ((x, y), (x + 1, y + 1)))
            if y >= 1 and x + y <= RANK - 1:
                add(f"B({x},{y})", ((x, y), (x + 1, y)),
                    ((x, y + 1), (x + 1, y - 1)))
            if x >= 1 and x + y <= RANK - 1:
                add(f"C({x},{y})", ((x, y), (x, y + 1)),
                    ((x + 1, y), (x - 1, y + 1)))
    assert len(rows) == 18
    return rows


def solve_vertex(normals, rhs):
    rows = tuple(tuple(Fraction(value) for value in row) for row in normals)
    if det3_columns(rows[0], rows[1], rows[2]) == 0:
        return None
    # solve rows*x=rhs, while inverse expects the displayed row matrix
    return solve_square(rows, tuple(Fraction(value) for value in rhs))


def enumerate_vertices(rows):
    found = set()
    for subset in combinations(range(len(rows)), 3):
        normals = [rows[i]["normal"] for i in subset]
        vertex = solve_vertex(normals, [rows[i]["rhs"] for i in subset])
        if vertex is None:
            continue
        if all(dot(row["normal"], vertex) <= row["rhs"] for row in rows):
            found.add(tuple(vertex))
    return tuple(sorted(found))


def reduce_rows(rows):
    offsets = {}
    tags = {}
    for row in rows:
        normal = primitive(row["normal"])
        divisor = next(abs(x) for x in row["normal"] if x) // next(
            abs(x) for x in normal if x
        )
        assert row["rhs"] % divisor == 0
        rhs = row["rhs"] // divisor
        if normal not in offsets or rhs < offsets[normal]:
            offsets[normal] = rhs
            tags[normal] = [row["tag"]]
        elif rhs == offsets[normal]:
            tags[normal].append(row["tag"])
    return tuple((normal, offsets[normal], tuple(sorted(tags[normal])))
                 for normal in sorted(offsets))


def enumerate_facets(reduced, vertices):
    facets = []
    for normal, rhs, tags in reduced:
        on = tuple(i for i, vertex in enumerate(vertices) if dot(normal, vertex) == rhs)
        if affine_rank([vertices[i] for i in on]) == 2:
            facets.append({"normal": normal, "rhs": rhs, "vertices": on, "tags": tags})
    facets.sort(key=lambda facet: (facet["normal"], facet["rhs"], facet["vertices"]))
    return tuple(facets)


def enumerate_edges(facets, vertices):
    edges = {}
    for left, right in combinations(range(len(facets)), 2):
        common = tuple(sorted(set(facets[left]["vertices"]) & set(facets[right]["vertices"])))
        if affine_rank([vertices[i] for i in common]) != 1:
            continue
        endpoints = max(combinations(common, 2), key=lambda pair: sum(
            (vertices[pair[0]][k] - vertices[pair[1]][k]) ** 2 for k in range(3)
        ))
        endpoints = tuple(sorted(endpoints))
        if endpoints in edges:
            assert edges[endpoints]["facets"] == (left, right)
        edges[endpoints] = {"vertices": endpoints, "facets": (left, right)}
    ordered = []
    for endpoints in sorted(edges):
        edge = edges[endpoints]
        delta = tuple(vertices[endpoints[1]][k] - vertices[endpoints[0]][k] for k in range(3))
        assert all(value.denominator == 1 for value in delta)
        length = 0
        for value in delta:
            length = gcd(length, abs(int(value)))
        assert length > 0
        tangent = tuple(int(value) // length for value in delta)
        ordered.append({**edge, "length": length, "oriented_tangent": tangent})
    return tuple(ordered)


def integer_vectors_l1(radius):
    return tuple(sorted(
        (vector for vector in product(range(-radius, radius + 1), repeat=3)
         if sum(abs(value) for value in vector) <= radius),
        key=lambda vector: (sum(abs(value) for value in vector), vector),
    ))


def quotient_completion(normal):
    """Canonical positive SL(3,Z) completion [normal,q1,q2]."""
    for radius in range(1, 8):
        vectors = integer_vectors_l1(radius)
        candidates = []
        for first in vectors:
            for second in vectors:
                if det3_columns(normal, first, second) == 1:
                    candidates.append((
                        max(sum(abs(x) for x in first), sum(abs(x) for x in second)),
                        sum(abs(x) for x in first) + sum(abs(x) for x in second),
                        first, second,
                    ))
        if candidates:
            _, _, first, second = min(candidates)
            columns = (normal, first, second)
            row_matrix = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
            inv = inverse(row_matrix)
            assert all(value.denominator == 1 for row in inv for value in row)
            return first, second, inv
    raise AssertionError(f"no SL completion for {normal}")


def quotient_vector(normal, other, completion):
    first, second, inv = completion
    coordinates = matvec(inv, other)
    quotient = tuple(int(value) for value in coordinates[1:])
    divisor = gcd(abs(quotient[0]), abs(quotient[1]))
    assert divisor
    primitive_quotient = tuple(value // divisor for value in quotient)
    # Cross product realizes the same primitive quotient ray in the tangent
    # lattice.  This independently checks saturation of the quotient vector.
    tangent_from_quotient = tuple(
        primitive_quotient[0] * value1 + primitive_quotient[1] * value2
        for value1, value2 in zip(cross(normal, first), cross(normal, second))
    )
    assert primitive(tangent_from_quotient) == primitive(cross(normal, other))
    return primitive_quotient


def pair_saturation_index(left, right):
    minors = cross(left, right)
    divisor = 0
    for value in minors:
        divisor = gcd(divisor, abs(value))
    return divisor


def bv_alpha_q2(left, right):
    index = pair_saturation_index(left, right)
    assert index in (1, 2)
    aa = dot(left, left)
    bb = dot(right, right)
    cc = dot(left, right)
    return Fraction(1, 4) - Fraction(cc, 12 * index) * (
        Fraction(1, aa) + Fraction(1, bb)
    )


def gram(rays):
    return tuple(tuple(dot(left, right) for right in rays) for left in rays)


def bv_alpha_unimodular_normal_cell(rays):
    assert abs(det3_columns(*rays)) == 1
    feasible_gram = inverse(gram(rays))
    answer = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        answer += Fraction(1, 24) * feasible_gram[i][j] * (
            Fraction(1, feasible_gram[i][i]) + Fraction(1, feasible_gram[j][j])
        )
    return answer


def coordinates_in_cell(vector, cell, rays):
    columns = tuple(rays[i] for i in cell)
    row_matrix = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
    return matvec(inverse(row_matrix), vector)


def star_insert(cells, ray_index, rays):
    output = set()
    used = False
    for cell in cells:
        coordinates = coordinates_in_cell(rays[ray_index], cell, rays)
        if all(value >= 0 for value in coordinates):
            support = tuple(i for i, value in enumerate(coordinates) if value > 0)
            if support:
                used = True
                for position in support:
                    child = list(cell)
                    child[position] = ray_index
                    child = tuple(sorted(child))
                    assert abs(det3_columns(*(rays[i] for i in child))) > 0
                    output.add(child)
                continue
        output.add(tuple(cell))
    assert used
    return tuple(sorted(output))


def fundamental_refinement_ray(cell, rays):
    index = abs(det3_columns(*(rays[i] for i in cell)))
    assert index > 1
    candidates = []
    for residues in product(range(index), repeat=3):
        if not any(residues):
            continue
        numerator = tuple(sum(residues[i] * rays[cell[i]][j] for i in range(3)) for j in range(3))
        if not all(value % index == 0 for value in numerator):
            continue
        vector = primitive(tuple(value // index for value in numerator))
        if vector in rays:
            continue
        coordinates = coordinates_in_cell(vector, cell, rays)
        if not all(value >= 0 for value in coordinates):
            continue
        support = tuple(i for i, value in enumerate(coordinates) if value > 0)
        child_indices = []
        for position in support:
            child = [rays[i] for i in cell]
            child[position] = vector
            child_indices.append(abs(det3_columns(*child)))
        if not child_indices or max(child_indices) >= index:
            continue
        candidates.append((
            max(child_indices), sum(child_indices), len(support),
            sum(abs(value) for value in vector), vector,
        ))
    assert candidates, (cell, index, tuple(rays[i] for i in cell))
    return min(candidates)[-1]


def vertex_facet_cycle(vertex_index, incident_facets, edges):
    adjacency = {facet: set() for facet in incident_facets}
    for edge in edges:
        if vertex_index in edge["vertices"]:
            left, right = edge["facets"]
            if left in adjacency and right in adjacency:
                adjacency[left].add(right)
                adjacency[right].add(left)
    assert all(len(neighbors) == 2 for neighbors in adjacency.values()), adjacency
    start = min(incident_facets)
    second = min(adjacency[start])
    cycle = [start, second]
    while len(cycle) < len(incident_facets):
        previous, current = cycle[-2], cycle[-1]
        following = next(value for value in adjacency[current] if value != previous)
        assert following not in cycle or (following == start and len(cycle) == len(incident_facets))
        cycle.append(following)
    assert start in adjacency[cycle[-1]]
    return tuple(cycle)


def bv_alpha_vertex(vertex_index, incident_facets, facets, edges):
    cycle = vertex_facet_cycle(vertex_index, incident_facets, edges)
    rays = [facets[i]["normal"] for i in cycle]
    cells = tuple((0, i, i + 1) for i in range(1, len(rays) - 1))
    inserted = []
    for _ in range(100):
        bad = [(abs(det3_columns(*(rays[i] for i in cell))), cell) for cell in cells]
        bad = [record for record in bad if record[0] > 1]
        if not bad:
            break
        _, cell = max(bad)
        ray = fundamental_refinement_ray(cell, tuple(rays))
        ray_index = len(rays)
        rays.append(ray)
        cells = star_insert(cells, ray_index, tuple(rays))
        inserted.append((ray_index, ray))
    else:
        raise AssertionError("unimodular refinement did not terminate")
    indices = tuple(abs(det3_columns(*(rays[i] for i in cell))) for cell in cells)
    assert all(index == 1 for index in indices)
    values = tuple(bv_alpha_unimodular_normal_cell(tuple(rays[i] for i in cell)) for cell in cells)
    return sum(values, Fraction(0)), {
        "facet_cycle": cycle,
        "rays": tuple(rays),
        "cells": cells,
        "cell_values": values,
        "inserted_rays": tuple(inserted),
    }


def lattice_count(rows, vertices, dilation):
    if dilation == 0:
        return 1
    lower = [min(int(vertex[k]) for vertex in vertices) * dilation for k in range(3)]
    upper = [max(int(vertex[k]) for vertex in vertices) * dilation for k in range(3)]
    total = 0
    for point in product(*(range(lower[k], upper[k] + 1) for k in range(3))):
        if all(dot(row["normal"], point) <= dilation * row["rhs"] for row in rows):
            total += 1
    return total


def polynomial_multiply(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i + j] += x * y
    return result


def interpolate(values):
    result = [Fraction(0)] * len(values)
    for i, value in enumerate(values):
        numerator = [Fraction(1)]
        denominator = Fraction(1)
        for j in range(len(values)):
            if i == j:
                continue
            numerator = polynomial_multiply(numerator, [Fraction(-j), Fraction(1)])
            denominator *= i - j
        for degree, coefficient in enumerate(numerator):
            result[degree] += Fraction(value) * coefficient / denominator
    return tuple(result)


def matrix_vector(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix):
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def fraction_string(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def serialize(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def build_contract():
    rows = rhombus_rows()
    vertices = enumerate_vertices(rows)
    assert len(vertices) == 11 and affine_rank(vertices) == 3
    assert all(value.denominator == 1 for vertex in vertices for value in vertex)
    reduced = reduce_rows(rows)
    facets = enumerate_facets(reduced, vertices)
    edges = enumerate_edges(facets, vertices)
    assert len(facets) == 12 and len(edges) == 21
    assert len(vertices) - len(edges) + len(facets) == 2

    vertex_facets = tuple(tuple(
        i for i, facet in enumerate(facets) if vertex_index in facet["vertices"]
    ) for vertex_index in range(len(vertices)))
    vertex_edges = tuple(tuple(
        i for i, edge in enumerate(edges) if vertex_index in edge["vertices"]
    ) for vertex_index in range(len(vertices)))

    # q=2: rays/facets are the (q-1)-cones and edges are the q-cones.
    completions = tuple(quotient_completion(facet["normal"]) for facet in facets)
    b2 = [[0] * len(edges) for _ in range(2 * len(facets))]
    q2_incidences = []
    a2 = []
    w2 = []
    for edge_index, edge in enumerate(edges):
        left, right = edge["facets"]
        incidence = []
        for facet_index, other_index in ((left, right), (right, left)):
            vector = quotient_vector(
                facets[facet_index]["normal"], facets[other_index]["normal"],
                completions[facet_index],
            )
            b2[2 * facet_index][edge_index] = vector[0]
            b2[2 * facet_index + 1][edge_index] = vector[1]
            incidence.append((facet_index, vector))
        q2_incidences.append(tuple(incidence))
        a2.append(bv_alpha_q2(facets[left]["normal"], facets[right]["normal"]))
        w2.append(Fraction(edge["length"]))
    b2 = tuple(tuple(row) for row in b2)
    a2 = tuple(a2)
    w2 = tuple(w2)
    assert matrix_vector(b2, w2) == (Fraction(0),) * len(b2)

    counts = tuple(lattice_count(rows, vertices, dilation) for dilation in range(6))
    ehrhart = interpolate(counts[:4])
    assert ehrhart == (Fraction(1), Fraction(7), Fraction(18), Fraction(24))
    assert all(sum(ehrhart[k] * Fraction(n) ** k for k in range(4)) == counts[n]
               for n in (4, 5))
    assert dot(a2, w2) == ehrhart[1]
    y2 = (Fraction(0),) * len(b2)
    shifted2 = tuple(x + y for x, y in zip(a2, matrix_vector(transpose(b2), y2)))
    assert shifted2 == a2 and min(shifted2) > 0

    # q=3: edge cones are the (q-1)-cones and vertex cones are q-cones.
    b3 = [[0] * len(vertices) for _ in range(len(edges))]
    q3_incidences = []
    for edge_index, edge in enumerate(edges):
        left, right = edge["facets"]
        annihilator = canonical_sign(cross(facets[left]["normal"], facets[right]["normal"]))
        entries = []
        for vertex_index in edge["vertices"]:
            images = []
            for facet_index in vertex_facets[vertex_index]:
                if facet_index not in edge["facets"]:
                    image = dot(annihilator, facets[facet_index]["normal"])
                    if image:
                        images.append(1 if image > 0 else -1)
            assert images and len(set(images)) == 1
            generator = images[0]
            b3[edge_index][vertex_index] = generator
            entries.append((vertex_index, generator))
        assert sorted(value for _, value in entries) == [-1, 1]
        q3_incidences.append({"annihilator": annihilator, "entries": tuple(entries)})
    b3 = tuple(tuple(row) for row in b3)
    w3 = (Fraction(1),) * len(vertices)
    assert matrix_vector(b3, w3) == (Fraction(0),) * len(edges)
    assert matrix_rank(b3) == len(vertices) - 1

    a3 = []
    vertex_subdivisions = []
    for vertex_index, incident_facets in enumerate(vertex_facets):
        alpha, detail = bv_alpha_vertex(vertex_index, incident_facets, facets, edges)
        a3.append(alpha)
        vertex_subdivisions.append(detail)
    a3 = tuple(a3)
    assert dot(a3, w3) == ehrhart[0] == 1

    target3 = (Fraction(1, len(vertices)),) * len(vertices)
    rhs3 = tuple(target3[i] - a3[i] for i in range(len(vertices)))
    y3 = tuple(solve_linear(transpose(b3), rhs3))
    shifted3 = tuple(x + y for x, y in zip(a3, matrix_vector(transpose(b3), y3)))
    assert shifted3 == target3 and min(shifted3) > 0

    contract = {
        "schema": "r4-complete-normal-fan-ghte-v1",
        "boundary": {"lambda": LAM, "mu": MU, "nu": NU},
        "lattices": {"M_basis": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                     "N_dual_basis": ((1, 0, 0), (0, 1, 0), (0, 0, 1))},
        "raw_rhombus_rows": tuple((row["tag"], row["normal"], row["rhs"]) for row in rows),
        "vertices": vertices,
        "facets": facets,
        "edges": edges,
        "vertex_facets": vertex_facets,
        "vertex_edges": vertex_edges,
        "fan_f_vector": (1, len(facets), len(edges), len(vertices)),
        "ehrhart_counts_0_to_5": counts,
        "ehrhart_coefficients": ehrhart,
        "q2": {
            "column_order": tuple(edge["vertices"] for edge in edges),
            "row_blocks": tuple((i, facets[i]["normal"], completions[i][0], completions[i][1])
                                for i in range(len(facets))),
            "incidences": tuple(q2_incidences),
            "B": b2,
            "rank_B": matrix_rank(b2),
            "kernel_dimension": len(edges) - matrix_rank(b2),
            "face_volume_w": w2,
            "B_times_w": matrix_vector(b2, w2),
            "BV_a": a2,
            "pairing": dot(a2, w2),
            "Farkas_y": y2,
            "shifted_BV": shifted2,
        },
        "q3": {
            "column_order": tuple(range(len(vertices))),
            "row_order": tuple(edge["vertices"] for edge in edges),
            "incidences": tuple(q3_incidences),
            "B": b3,
            "rank_B": matrix_rank(b3),
            "kernel_dimension": len(vertices) - matrix_rank(b3),
            "face_volume_w": w3,
            "B_times_w": matrix_vector(b3, w3),
            "BV_a": a3,
            "vertex_subdivisions": tuple(vertex_subdivisions),
            "pairing": dot(a3, w3),
            "Farkas_y": y3,
            "shifted_BV": shifted3,
        },
    }
    return contract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    contract = serialize(build_contract())
    payload = json.dumps(contract, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("ascii")).hexdigest()
    if args.full:
        print(json.dumps(contract, sort_keys=True, indent=2))
    print("PASS")
    print(f"contract_sha256={digest}")
    print(f"fan_f_vector={contract['fan_f_vector']}")
    print(f"ehrhart_counts_0_to_5={contract['ehrhart_counts_0_to_5']}")
    print(f"ehrhart_coefficients={contract['ehrhart_coefficients']}")
    for q in ("q2", "q3"):
        data = contract[q]
        print(f"{q}: rank_B={data['rank_B']} kernel_dimension={data['kernel_dimension']} "
              f"pairing={data['pairing']} min_shifted={min(Fraction(x) for x in data['shifted_BV'])}")


if __name__ == "__main__":
    main()
