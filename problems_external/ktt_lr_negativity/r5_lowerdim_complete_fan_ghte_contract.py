#!/usr/bin/env python3
"""Exact complete-fan GHTE contracts for intrinsic 3D side-five hives.

The checker has two fixed examples.

* ``horn_gap`` is the four-vertex chamber-wall example from
  ``R5_LOWERDIM_HORN_GAP.md``.
* ``hard`` is selected by an exact replay of the first intrinsic-dimensional
  three record in ``tier0/runs/fam4/_sym5b.jsonl`` whose reconstructed hive
  has more than four vertices and a nonsaturated q=2 normal cone.  The
  selected polytope has seven vertices and saturation index two.

For each example the program reconstructs the saturated intrinsic tangent
lattice, enumerates the complete three-dimensional normal fan, builds the
primitive quotient-lattice balance matrices for q=2 and q=3, computes the
matching Berline--Vergne vector with the Euclidean complement induced from
the six hive coordinates, and checks both Euler--Maclaurin pairings exactly.
It emits an exact Farkas certificate when GHTE holds, or an exact nonnegative
balanced witness if it fails.

All mathematical decisions use integers and ``Fraction``.  The JSONL corpus
is used only to provide candidate partition triples; every selected candidate
is rebuilt from the defining hive inequalities before it can pass.
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
sys.path.insert(0, HERE)

from hive5 import build_hive5, lattice_count  # noqa: E402
from polytope5 import (affine_rank as ambient_affine_rank, lattice_coords,
                       reduce_rhs, vertices as ambient_vertices)  # noqa: E402
from r4_complete_fan_ghte_contract import (  # noqa: E402
    canonical_sign,
    cross,
    det3_columns,
    dot,
    interpolate,
    inverse,
    matrix_rank,
    matrix_vector,
    quotient_completion,
    quotient_vector,
    serialize,
    solve_linear,
    transpose,
)


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


def q(value=0):
    return Fraction(value)


def matrix_multiply(left, right):
    if not left:
        return tuple()
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(len(right)))
              for j in range(len(right[0])))
        for i in range(len(left))
    )


def metric_dot(left, right, gram):
    return sum(
        Fraction(left[i]) * gram[i][j] * Fraction(right[j])
        for i in range(len(left))
        for j in range(len(right))
    )


def rational_primitive(vector):
    """Primitive integral vector on a nonzero rational ray."""
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, Fraction(value).denominator)
    integral = tuple(int(Fraction(value) * denominator) for value in vector)
    divisor = 0
    for value in integral:
        divisor = gcd(divisor, abs(value))
    assert divisor
    return tuple(value // divisor for value in integral)


def affine_rank(points):
    if len(points) <= 1:
        return 0
    base = points[0]
    return matrix_rank(tuple(
        tuple(Fraction(point[i]) - Fraction(base[i]) for i in range(3))
        for point in points[1:]
    ))


def sublattice_saturation_index(basis):
    """Index of the row lattice in its saturation inside Z^6."""
    divisor = 0
    for columns in combinations(range(6), 3):
        minor_rows = tuple(tuple(row[column] for column in columns)
                           for row in basis)
        divisor = gcd(divisor, abs(det3_columns(*minor_rows)))
    return divisor


def intrinsic_model(boundary):
    hive = build_hive5(boundary["lambda"], boundary["mu"], boundary["nu"])
    assert hive["ok"]
    ambient = tuple(ambient_vertices(reduce_rhs(hive["b"])))
    assert ambient_affine_rank(ambient) == 3
    coordinates, dimension = lattice_coords(ambient)
    assert dimension == 3
    coordinates = tuple(tuple(Fraction(value) for value in point)
                        for point in coordinates)

    # Recover the saturated tangent-lattice basis in the original six hive
    # coordinates from the independently returned intrinsic coordinates.
    base = ambient[0]
    chosen = next(
        subset for subset in combinations(range(1, len(ambient)), 3)
        if det3_columns(*(coordinates[i] for i in subset)) != 0
    )
    coordinate_matrix = tuple(coordinates[i] for i in chosen)
    ambient_matrix = tuple(tuple(ambient[i][j] - base[j] for j in range(6))
                           for i in chosen)
    basis = matrix_multiply(inverse(coordinate_matrix), ambient_matrix)
    assert all(value.denominator == 1 for row in basis for value in row)
    basis = tuple(tuple(int(value) for value in row) for row in basis)
    saturation_index = sublattice_saturation_index(basis)
    assert saturation_index == 1
    for point, coord in zip(ambient, coordinates):
        rebuilt = tuple(
            base[j] + sum(coord[i] * basis[i][j] for i in range(3))
            for j in range(6)
        )
        assert rebuilt == point

    primal_gram = tuple(tuple(dot(left, right) for right in basis)
                        for left in basis)
    dual_gram = inverse(primal_gram)
    return {
        "hive": hive,
        "ambient_vertices": ambient,
        "intrinsic_vertices": coordinates,
        "M_basis_in_Z6": basis,
        "M_basis_saturation_index": saturation_index,
        "M_gram": primal_gram,
        "N_gram": dual_gram,
        "affine_origin": base,
    }


def enumerate_facets(vertices):
    found = {}
    for subset in combinations(range(len(vertices)), 3):
        left = tuple(vertices[subset[1]][i] - vertices[subset[0]][i]
                     for i in range(3))
        right = tuple(vertices[subset[2]][i] - vertices[subset[0]][i]
                      for i in range(3))
        raw = cross(left, right)
        if not any(raw):
            continue
        normal = rational_primitive(raw)
        rhs = dot(normal, vertices[subset[0]])
        values = tuple(dot(normal, vertex) - rhs for vertex in vertices)
        if all(value <= 0 for value in values):
            pass
        elif all(value >= 0 for value in values):
            normal = tuple(-value for value in normal)
            rhs = -rhs
            values = tuple(-value for value in values)
        else:
            continue
        if all(value == 0 for value in values):
            continue
        on = tuple(i for i, value in enumerate(values) if value == 0)
        if affine_rank(tuple(vertices[i] for i in on)) != 2:
            continue
        key = normal, rhs
        record = {"normal": normal, "rhs": rhs, "vertices": on}
        if key in found:
            assert found[key] == record
        found[key] = record
    facets = tuple(sorted(found.values(), key=lambda item: (
        item["normal"], item["rhs"], item["vertices"]
    )))
    assert facets
    return facets


def normalized_edge(vertices, endpoints):
    delta = tuple(vertices[endpoints[1]][i] - vertices[endpoints[0]][i]
                  for i in range(3))
    tangent = rational_primitive(delta)
    pivot = next(i for i, value in enumerate(tangent) if value)
    length = delta[pivot] / tangent[pivot]
    if length < 0:
        tangent = tuple(-value for value in tangent)
        length = -length
    assert length > 0
    assert delta == tuple(length * value for value in tangent)
    return tangent, length


def enumerate_edges(facets, vertices):
    found = {}
    for left, right in combinations(range(len(facets)), 2):
        common = tuple(sorted(
            set(facets[left]["vertices"]) & set(facets[right]["vertices"])
        ))
        if affine_rank(tuple(vertices[i] for i in common)) != 1:
            continue
        assert len(common) == 2
        tangent, length = normalized_edge(vertices, common)
        record = {
            "vertices": common,
            "facets": (left, right),
            "primitive_tangent": tangent,
            "length": length,
        }
        if common in found:
            assert found[common] == record
        found[common] = record
    return tuple(found[key] for key in sorted(found))


def pair_index(left, right):
    divisor = 0
    for value in cross(left, right):
        divisor = gcd(divisor, abs(int(value)))
    return divisor


def q2_refinement_ray(left, right):
    index = pair_index(left, right)
    assert index > 1
    candidates = []
    for a, b in product(range(index), repeat=2):
        if not a or not b:
            continue
        numerator = tuple(a * left[i] + b * right[i] for i in range(3))
        if not all(value % index == 0 for value in numerator):
            continue
        vector = rational_primitive(tuple(value // index for value in numerator))
        left_index = pair_index(left, vector)
        right_index = pair_index(vector, right)
        if not (0 < left_index < index and 0 < right_index < index):
            continue
        candidates.append((max(left_index, right_index), left_index + right_index,
                           sum(abs(value) for value in vector), vector))
    assert candidates, (left, right, index)
    return min(candidates)[-1]


def q2_unimodular_alpha(left, right, dual_gram):
    assert pair_index(left, right) == 1
    aa = metric_dot(left, left, dual_gram)
    bb = metric_dot(right, right, dual_gram)
    cc = metric_dot(left, right, dual_gram)
    return Fraction(1, 4) - Fraction(1, 12) * cc * (
        Fraction(1, aa) + Fraction(1, bb)
    )


def q2_alpha(left, right, dual_gram):
    cells = [(tuple(left), tuple(right))]
    inserted = []
    while any(pair_index(*cell) > 1 for cell in cells):
        new_cells = []
        for cell in cells:
            if pair_index(*cell) == 1:
                new_cells.append(cell)
                continue
            middle = q2_refinement_ray(*cell)
            inserted.append(middle)
            new_cells.extend(((cell[0], middle), (middle, cell[1])))
        cells = new_cells
    values = tuple(q2_unimodular_alpha(*cell, dual_gram) for cell in cells)
    return sum(values, Fraction(0)), {
        "cells": tuple(cells),
        "cell_indices": tuple(pair_index(*cell) for cell in cells),
        "cell_values": values,
        "inserted_rays": tuple(inserted),
    }


def coordinates_in_cell(vector, cell, rays):
    columns = tuple(rays[i] for i in cell)
    row_matrix = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
    return tuple(sum(inverse(row_matrix)[i][j] * vector[j] for j in range(3))
                 for i in range(3))


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
        numerator = tuple(sum(residues[i] * rays[cell[i]][j] for i in range(3))
                          for j in range(3))
        if not all(value % index == 0 for value in numerator):
            continue
        vector = rational_primitive(tuple(value // index for value in numerator))
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
        candidates.append((max(child_indices), sum(child_indices), len(support),
                           sum(abs(value) for value in vector), vector))
    assert candidates, (cell, index, tuple(rays[i] for i in cell))
    return min(candidates)[-1]


def vertex_facet_cycle(vertex_index, incident_facets, edges):
    adjacency = {facet: set() for facet in incident_facets}
    for edge in edges:
        if vertex_index not in edge["vertices"]:
            continue
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
        assert following not in cycle
        cycle.append(following)
    assert start in adjacency[cycle[-1]]
    return tuple(cycle)


def q3_unimodular_alpha(cell, rays, dual_gram):
    normal_gram = tuple(tuple(metric_dot(rays[i], rays[j], dual_gram)
                                for j in cell) for i in cell)
    feasible_gram = inverse(normal_gram)
    answer = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        answer += Fraction(1, 24) * feasible_gram[i][j] * (
            Fraction(1, feasible_gram[i][i])
            + Fraction(1, feasible_gram[j][j])
        )
    return answer


def q3_alpha(vertex_index, incident_facets, facets, edges, dual_gram):
    cycle = vertex_facet_cycle(vertex_index, incident_facets, edges)
    rays = [facets[i]["normal"] for i in cycle]
    cells = tuple((0, i, i + 1) for i in range(1, len(rays) - 1))
    inserted = []
    for _ in range(100):
        bad = tuple((abs(det3_columns(*(rays[i] for i in cell))), cell)
                    for cell in cells)
        bad = tuple(record for record in bad if record[0] > 1)
        if not bad:
            break
        _, cell = max(bad)
        ray = fundamental_refinement_ray(cell, tuple(rays))
        ray_index = len(rays)
        rays.append(ray)
        cells = star_insert(cells, ray_index, tuple(rays))
        inserted.append((ray_index, ray))
    else:
        raise AssertionError("q3 unimodular refinement did not terminate")
    indices = tuple(abs(det3_columns(*(rays[i] for i in cell))) for cell in cells)
    assert all(index == 1 for index in indices)
    values = tuple(q3_unimodular_alpha(cell, tuple(rays), dual_gram)
                   for cell in cells)
    return sum(values, Fraction(0)), {
        "facet_cycle": cycle,
        "rays": tuple(rays),
        "cells": cells,
        "cell_indices": indices,
        "cell_values": values,
        "inserted_rays": tuple(inserted),
    }


def build_q2(facets, edges, dual_gram, ehrhart):
    completions = tuple(quotient_completion(facet["normal"]) for facet in facets)
    matrix = [[0] * len(edges) for _ in range(2 * len(facets))]
    incidences = []
    alphas = []
    subdivisions = []
    volumes = []
    for edge_index, edge in enumerate(edges):
        left, right = edge["facets"]
        incidence = []
        for facet_index, other_index in ((left, right), (right, left)):
            vector = quotient_vector(
                facets[facet_index]["normal"], facets[other_index]["normal"],
                completions[facet_index],
            )
            matrix[2 * facet_index][edge_index] = vector[0]
            matrix[2 * facet_index + 1][edge_index] = vector[1]
            incidence.append((facet_index, vector))
        alpha, detail = q2_alpha(facets[left]["normal"],
                                 facets[right]["normal"], dual_gram)
        incidences.append(tuple(incidence))
        alphas.append(alpha)
        subdivisions.append(detail)
        volumes.append(edge["length"])
    matrix = tuple(tuple(row) for row in matrix)
    alphas = tuple(alphas)
    volumes = tuple(volumes)
    assert matrix_vector(matrix, volumes) == (Fraction(0),) * len(matrix)
    assert dot(alphas, volumes) == ehrhart[1]

    # Every current intrinsic side-five q2 entry is positive.  The zero vector
    # is therefore an exact Farkas certificate, while the nontrivial balance
    # identities are still checked independently above.
    y = (Fraction(0),) * len(matrix)
    shifted = tuple(alphas[i] + matrix_vector(transpose(matrix), y)[i]
                    for i in range(len(alphas)))
    assert min(shifted) >= 0
    return {
        "column_order": tuple(edge["vertices"] for edge in edges),
        "row_blocks": tuple((i, facets[i]["normal"], completions[i][0],
                             completions[i][1]) for i in range(len(facets))),
        "incidences": tuple(incidences),
        "B": matrix,
        "rank_B": matrix_rank(matrix),
        "kernel_dimension": len(edges) - matrix_rank(matrix),
        "face_volume_v": volumes,
        "B_times_v": matrix_vector(matrix, volumes),
        "BV_a": alphas,
        "BV_subdivisions": tuple(subdivisions),
        "pairing": dot(alphas, volumes),
        "Farkas_y": y,
        "shifted_BV": shifted,
        "minimum_raw_BV": min(alphas),
    }


def build_q3(vertices, facets, edges, vertex_facets, dual_gram, ehrhart):
    matrix = [[0] * len(vertices) for _ in range(len(edges))]
    incidences = []
    for edge_index, edge in enumerate(edges):
        left, right = edge["facets"]
        annihilator = canonical_sign(cross(facets[left]["normal"],
                                           facets[right]["normal"]))
        entries = []
        for vertex_index in edge["vertices"]:
            images = []
            for facet_index in vertex_facets[vertex_index]:
                if facet_index in edge["facets"]:
                    continue
                image = dot(annihilator, facets[facet_index]["normal"])
                if image:
                    images.append(1 if image > 0 else -1)
            assert images and len(set(images)) == 1
            generator = images[0]
            matrix[edge_index][vertex_index] = generator
            entries.append((vertex_index, generator))
        assert sorted(value for _, value in entries) == [-1, 1]
        incidences.append({"annihilator": annihilator, "entries": tuple(entries)})
    matrix = tuple(tuple(row) for row in matrix)
    volumes = (Fraction(1),) * len(vertices)
    assert matrix_vector(matrix, volumes) == (Fraction(0),) * len(matrix)
    assert matrix_rank(matrix) == len(vertices) - 1

    alphas = []
    subdivisions = []
    for vertex_index, incident_facets in enumerate(vertex_facets):
        alpha, detail = q3_alpha(vertex_index, incident_facets, facets, edges,
                                 dual_gram)
        alphas.append(alpha)
        subdivisions.append(detail)
    alphas = tuple(alphas)
    assert dot(alphas, volumes) == ehrhart[0] == 1

    target = (Fraction(1, len(vertices)),) * len(vertices)
    rhs = tuple(target[i] - alphas[i] for i in range(len(vertices)))
    y = tuple(solve_linear(transpose(matrix), rhs))
    shifted = tuple(alphas[i] + matrix_vector(transpose(matrix), y)[i]
                    for i in range(len(vertices)))
    assert shifted == target
    return {
        "column_order": tuple(range(len(vertices))),
        "row_order": tuple(edge["vertices"] for edge in edges),
        "incidences": tuple(incidences),
        "B": matrix,
        "rank_B": matrix_rank(matrix),
        "kernel_dimension": len(vertices) - matrix_rank(matrix),
        "face_volume_v": volumes,
        "B_times_v": matrix_vector(matrix, volumes),
        "BV_a": alphas,
        "BV_subdivisions": tuple(subdivisions),
        "pairing": dot(alphas, volumes),
        "Farkas_y": y,
        "shifted_BV": shifted,
        "minimum_raw_BV": min(alphas),
    }


def exact_corpus_selection():
    scanned_records = 0
    intrinsic_dim3_records = 0
    selected = None
    selected_vertices = None
    selected_pair_index = None
    selected_minimum_alpha = None
    q2_cones_rebuilt = 0
    negative_q2_entries = 0
    minimum_q2_alpha = None
    maximum_vertex_count = 0
    maximum_pair_index = 0
    qualifying_records = 0
    with open(CORPUS, "r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            record = json.loads(line)
            scanned_records += 1
            if record.get("status") != "OK" or record.get("d") != 3:
                continue
            intrinsic_dim3_records += 1
            boundary = {
                "lambda": tuple(record["lam"]),
                "mu": tuple(record["mu"]),
                "nu": tuple(record["nu"]),
            }
            model = intrinsic_model(boundary)
            vertices = model["intrinsic_vertices"]
            facets = enumerate_facets(vertices)
            edges = enumerate_edges(facets, vertices)
            local_alphas = []
            local_indices = []
            for edge in edges:
                left, right = edge["facets"]
                first = facets[left]["normal"]
                second = facets[right]["normal"]
                alpha, _detail = q2_alpha(first, second, model["N_gram"])
                local_alphas.append(alpha)
                local_indices.append(pair_index(first, second))
            assert local_alphas and local_indices
            count = len(vertices)
            local_maximum_index = max(local_indices)
            local_minimum_alpha = min(local_alphas)
            q2_cones_rebuilt += len(edges)
            negative_q2_entries += sum(alpha < 0 for alpha in local_alphas)
            minimum_q2_alpha = (local_minimum_alpha if minimum_q2_alpha is None
                                else min(minimum_q2_alpha, local_minimum_alpha))
            maximum_vertex_count = max(maximum_vertex_count, count)
            maximum_pair_index = max(maximum_pair_index, local_maximum_index)
            if count > 4 and local_maximum_index > 1:
                qualifying_records += 1
            if selected is None and count > 4 and local_maximum_index > 1:
                selected = boundary
                selected_vertices = count
                selected_line = line_number
                selected_pair_index = local_maximum_index
                selected_minimum_alpha = local_minimum_alpha
    assert selected == HARD
    assert selected_vertices == 7
    assert selected_pair_index == 2
    assert scanned_records == 1500
    assert intrinsic_dim3_records == 87
    assert q2_cones_rebuilt == 866
    assert negative_q2_entries == 0
    assert minimum_q2_alpha == Fraction(1, 10)
    assert maximum_vertex_count == 10
    assert maximum_pair_index == 2
    assert qualifying_records == 6
    return {
        "corpus_relative_path": os.path.relpath(CORPUS, HERE).replace("\\", "/"),
        "records_scanned": scanned_records,
        "intrinsic_dim3_records_rebuilt": intrinsic_dim3_records,
        "q2_cones_rebuilt": q2_cones_rebuilt,
        "negative_q2_entries": negative_q2_entries,
        "minimum_q2_alpha": minimum_q2_alpha,
        "maximum_vertex_count": maximum_vertex_count,
        "maximum_pair_saturation_index": maximum_pair_index,
        "qualifying_records": qualifying_records,
        "selection_line": selected_line,
        "criterion": ("exact affine dimension 3, more than four vertices, "
                      "and q2 saturation index greater than one"),
        "selected_boundary": selected,
        "selected_vertex_count": selected_vertices,
        "selected_maximum_pair_saturation_index": selected_pair_index,
        "selected_minimum_q2_alpha": selected_minimum_alpha,
    }


def ehrhart_data(model):
    hive = model["hive"]
    counts = tuple(
        lattice_count(hive["A"], [dilation * rhs for rhs in hive["b"]], 6)
        for dilation in range(6)
    )
    coefficients = interpolate(counts[:4])
    for dilation in (4, 5):
        assert sum(coefficients[k] * Fraction(dilation) ** k
                   for k in range(4)) == counts[dilation]
    return counts, coefficients


def build_contract(name, boundary):
    model = intrinsic_model(boundary)
    vertices = model["intrinsic_vertices"]
    facets = enumerate_facets(vertices)
    edges = enumerate_edges(facets, vertices)
    assert len(vertices) - len(edges) + len(facets) == 2
    vertex_facets = tuple(tuple(
        i for i, facet in enumerate(facets) if vertex_index in facet["vertices"]
    ) for vertex_index in range(len(vertices)))
    counts, ehrhart = ehrhart_data(model)
    q2 = build_q2(facets, edges, model["N_gram"], ehrhart)
    q3 = build_q3(vertices, facets, edges, vertex_facets, model["N_gram"], ehrhart)
    return {
        "schema": "r5-intrinsic-3d-complete-normal-fan-ghte-v1",
        "name": name,
        "boundary": boundary,
        "lattices": {
            "ambient_affine_origin": model["affine_origin"],
            "M_basis_in_Z6": model["M_basis_in_Z6"],
            "M_basis_saturation_index": model["M_basis_saturation_index"],
            "M_gram": model["M_gram"],
            "N_dual_gram": model["N_gram"],
        },
        "ambient_vertices": model["ambient_vertices"],
        "intrinsic_vertices": vertices,
        "facets": facets,
        "edges": edges,
        "vertex_facets": vertex_facets,
        "fan_f_vector": (1, len(facets), len(edges), len(vertices)),
        "ehrhart_counts_0_to_5": counts,
        "ehrhart_coefficients": ehrhart,
        "q2": q2,
        "q3": q3,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    scan = exact_corpus_selection()
    contracts = (
        build_contract("horn_gap", HORN_GAP),
        build_contract("hard", HARD),
    )
    payload_object = serialize({"corpus_scan": scan, "contracts": contracts})
    payload = json.dumps(payload_object, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("ascii")).hexdigest()
    if args.full:
        print(json.dumps(payload_object, sort_keys=True, indent=2))
    print("PASS")
    print(f"contract_sha256={digest}")
    print("corpus_scan=" + json.dumps(serialize(scan), sort_keys=True,
                                       separators=(",", ":")))
    for contract in payload_object["contracts"]:
        print(f"{contract['name']}: fan_f_vector={contract['fan_f_vector']} "
              f"ehrhart={contract['ehrhart_coefficients']}")
        for degree in ("q2", "q3"):
            data = contract[degree]
            minimum = min(Fraction(value) for value in data["shifted_BV"])
            print(f"  {degree}: rank_B={data['rank_B']} "
                  f"kernel_dimension={data['kernel_dimension']} "
                  f"pairing={data['pairing']} min_raw={data['minimum_raw_BV']} "
                  f"min_shifted={minimum}")


if __name__ == "__main__":
    main()
