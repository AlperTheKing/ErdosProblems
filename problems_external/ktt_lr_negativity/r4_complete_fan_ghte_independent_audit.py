#!/usr/bin/env python3
"""Zero-trust audit of the side-four complete-fan GHTE contract.

This file deliberately does not import ``r4_complete_fan_ghte_contract`` or
any project hive/polytope/BV module.  It independently

* derives the 18 hive inequalities from the three rhombus families;
* reconstructs the complete face lattice with exact arithmetic;
* builds q=2 quotient-lattice balancing blocks in independently chosen bases;
* evaluates q=2 BV constants, treating index two in a saturated basis;
* computes vertex BV constants directly on feasible tangent cones by the
  local Euler--Maclaurin recursion (no subdivision of the normal cone);
* builds the q=3 graph balancing matrix and an exact Farkas certificate; and
* checks the Ehrhart values both by hive lattice enumeration and the LR rule.

All arithmetic affecting a verdict is integral, Fraction, or SymPy Rational.
"""

from __future__ import annotations

from collections import Counter, deque
from functools import lru_cache
from fractions import Fraction
from itertools import combinations, product
from math import ceil, floor, gcd
import hashlib
import json

import sympy as sp


RANK = 4
LAMBDA = (12, 8, 4, 0)
MU = (12, 8, 4, 0)
NU = (18, 14, 10, 6)
INTERIOR = ((1, 1), (1, 2), (2, 1))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def content_gcd(values):
    answer = 0
    for value in values:
        answer = gcd(answer, abs(int(value)))
    return answer


def primitive(vector):
    divisor = content_gcd(vector)
    assert divisor
    return tuple(int(value) // divisor for value in vector)


def det_columns(*columns):
    return int(sp.Matrix.hstack(*(sp.Matrix(column) for column in columns)).det())


def rank_vectors(vectors):
    if not vectors:
        return 0
    return sp.Matrix(vectors).rank()


def affine_rank(points):
    if len(points) < 2:
        return 0
    base = points[0]
    return rank_vectors([[x - y for x, y in zip(point, base)] for point in points[1:]])


def to_fraction(value):
    value = sp.Rational(value)
    return Fraction(int(value.p), int(value.q))


def boundary_values():
    """Use boundary edge differences; no project boundary convention is read."""
    boundary = {(0, 0): 0}
    running = 0
    for y in range(RANK + 1):
        boundary[(0, y)] = running
        if y < RANK:
            running += LAMBDA[y]
    running = sum(LAMBDA)
    for x in range(RANK + 1):
        boundary[(x, RANK - x)] = running
        if x < RANK:
            running += MU[x]
    running = 0
    for x in range(RANK + 1):
        boundary[(x, 0)] = running
        if x < RANK:
            running += NU[x]
    return boundary


def hive_rows():
    boundary = boundary_values()
    coordinate = {point: index for index, point in enumerate(INTERIOR)}
    rows = []

    def add(tag, obtuse, acute):
        # obtuse sum >= acute sum, written normal . h <= rhs.
        normal = [0, 0, 0]
        constant = 0
        for point in obtuse:
            if point in coordinate:
                normal[coordinate[point]] -= 1
            else:
                constant -= boundary[point]
        for point in acute:
            if point in coordinate:
                normal[coordinate[point]] += 1
            else:
                constant += boundary[point]
        rows.append((tag, tuple(normal), -constant))

    for x, y in product(range(RANK + 1), repeat=2):
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
    return tuple(rows)


def solve_three(normals, rhs):
    matrix = sp.Matrix(normals)
    if matrix.det() == 0:
        return None
    solution = matrix.inv() * sp.Matrix(rhs)
    return tuple(to_fraction(value) for value in solution)


def enumerate_vertices(rows):
    vertices = set()
    for chosen in combinations(rows, 3):
        point = solve_three([row[1] for row in chosen], [row[2] for row in chosen])
        if point is not None and all(dot(normal, point) <= rhs for _, normal, rhs in rows):
            vertices.add(point)
    return tuple(sorted(vertices))


def irredundant_facets(rows, vertices):
    # Collapse parallel duplicates only after primitive normalization.
    offsets = {}
    tags = {}
    for tag, normal, rhs in rows:
        divisor = content_gcd(normal)
        normal = tuple(value // divisor for value in normal)
        assert rhs % divisor == 0
        rhs //= divisor
        if normal not in offsets or rhs < offsets[normal]:
            offsets[normal] = rhs
            tags[normal] = [tag]
        elif rhs == offsets[normal]:
            tags[normal].append(tag)
    facets = []
    for normal, rhs in offsets.items():
        incident = tuple(i for i, vertex in enumerate(vertices) if dot(normal, vertex) == rhs)
        if affine_rank([vertices[i] for i in incident]) == 2:
            facets.append((normal, rhs, incident, tuple(sorted(tags[normal]))))
    return tuple(sorted(facets))


def enumerate_edges(facets, vertices):
    edges = []
    seen = set()
    for i, j in combinations(range(len(facets)), 2):
        common = tuple(sorted(set(facets[i][2]) & set(facets[j][2])))
        if affine_rank([vertices[k] for k in common]) != 1:
            continue
        endpoints = max(combinations(common, 2), key=lambda pair: sum(
            (vertices[pair[0]][k] - vertices[pair[1]][k]) ** 2 for k in range(3)
        ))
        endpoints = tuple(sorted(endpoints))
        assert endpoints not in seen
        seen.add(endpoints)
        delta = tuple(vertices[endpoints[1]][k] - vertices[endpoints[0]][k] for k in range(3))
        assert all(value.denominator == 1 for value in delta)
        length = content_gcd(int(value) for value in delta)
        tangent = tuple(int(value) // length for value in delta)
        edges.append((endpoints, (i, j), length, tangent))
    return tuple(sorted(edges))


def matrix_rank(rows):
    return sp.Matrix(rows).rank()


def completion(normal):
    """Choose a quotient basis in an order different from the target code."""
    candidates = sorted(product(range(-2, 3), repeat=3), reverse=True)
    candidates = [item for item in candidates if item != (0, 0, 0)]
    for second in candidates:
        for third in candidates:
            determinant = det_columns(normal, second, third)
            if abs(determinant) == 1:
                if determinant < 0:
                    second, third = third, second
                matrix = sp.Matrix.hstack(sp.Matrix(normal), sp.Matrix(second), sp.Matrix(third))
                assert matrix.det() == 1
                return second, third, matrix.inv()
    raise AssertionError(f"no unimodular completion for {normal}")


def quotient_ray(normal, other, inverse_completion):
    coordinates = inverse_completion * sp.Matrix(other)
    quotient = (int(coordinates[1]), int(coordinates[2]))
    divisor = content_gcd(quotient)
    assert divisor
    return tuple(value // divisor for value in quotient)


def q2_alpha(outward_u, outward_v):
    index = content_gcd(cross(outward_u, outward_v))
    if index == 1:
        aa, bb, cc = dot(outward_u, outward_u), dot(outward_v, outward_v), dot(outward_u, outward_v)
        return Fraction(1, 4) - Fraction(cc, 12) * (Fraction(1, aa) + Fraction(1, bb))
    assert index == 2
    # Work in the saturated basis s,t.  This intentionally does not use an
    # ambient-determinant division in the index-two formula.
    assert all((x + y) % 2 == 0 and (x - y) % 2 == 0
               for x, y in zip(outward_u, outward_v))
    s = tuple((x + y) // 2 for x, y in zip(outward_u, outward_v))
    t = tuple((x - y) // 2 for x, y in zip(outward_u, outward_v))
    assert dot(s, t) == 0 and content_gcd(cross(s, t)) == 1
    aa, bb = dot(s, s), dot(t, t)
    return Fraction(aa + 2 * bb, 6 * (aa + bb))


def build_q2(facets, edges):
    blocks = [completion(facet[0]) for facet in facets]
    matrix = [[0] * len(edges) for _ in range(2 * len(facets))]
    alphas, lengths, indices = [], [], []
    for column, edge in enumerate(edges):
        left, right = edge[1]
        for facet_index, other_index in ((left, right), (right, left)):
            vector = quotient_ray(facets[facet_index][0], facets[other_index][0],
                                  blocks[facet_index][2])
            matrix[2 * facet_index][column] = vector[0]
            matrix[2 * facet_index + 1][column] = vector[1]
        u, v = facets[left][0], facets[right][0]
        indices.append(content_gcd(cross(u, v)))
        alphas.append(q2_alpha(u, v))
        lengths.append(Fraction(edge[2]))
    balance = tuple(sum(Fraction(row[j]) * lengths[j] for j in range(len(edges)))
                    for row in matrix)
    return tuple(tuple(row) for row in matrix), tuple(alphas), tuple(lengths), tuple(indices), balance


def lattice_count(rows, vertices, dilation):
    if dilation == 0:
        return 1
    low = [dilation * min(int(vertex[i]) for vertex in vertices) for i in range(3)]
    high = [dilation * max(int(vertex[i]) for vertex in vertices) for i in range(3)]
    answer = 0
    for point in product(*(range(low[i], high[i] + 1) for i in range(3))):
        if all(dot(normal, point) <= dilation * rhs for _, normal, rhs in rows):
            answer += 1
    return answer


def interpolate(values):
    x = sp.symbols("x")
    polynomial = sp.interpolate([(i, value) for i, value in enumerate(values)], x).expand()
    return tuple(to_fraction(polynomial.coeff(x, degree)) for degree in range(len(values)))


def compositions(total, parts, bounds):
    if parts == 1:
        if total <= bounds[0]:
            yield (total,)
        return
    for first in range(min(total, bounds[0]) + 1):
        for rest in compositions(total - first, parts - 1, bounds[1:]):
            yield (first,) + rest


def lr_tableau_count(scale):
    """Independent LR-rule count, with one weakly increasing word per row."""
    lam = tuple(scale * value for value in LAMBDA)
    nu = tuple(scale * value for value in NU)
    content = tuple(scale * value for value in MU)
    intervals = tuple((lam[row] + 1, nu[row]) for row in range(4))
    lengths = tuple(end - start + 1 for start, end in intervals)
    assert lengths == (6 * scale,) * 4
    row_options = tuple(compositions(6 * scale, 4, content))

    @lru_cache(maxsize=None)
    def recurse(row, remaining, seen, previous_entries):
        if row == 4:
            return int(all(value == 0 for value in remaining))
        answer = 0
        start, end = intervals[row]
        for counts in row_options:
            if any(counts[i] > remaining[i] for i in range(4)):
                continue
            trial = list(seen)
            valid = True
            # LR word reads each weakly increasing row from right to left.
            for symbol in range(3, -1, -1):
                trial[symbol] += counts[symbol]
                if any(trial[i] < trial[i + 1] for i in range(3)):
                    valid = False
                    break
            if not valid:
                continue
            entries = tuple(symbol + 1 for symbol in range(4) for _ in range(counts[symbol]))
            if previous_entries:
                above_start, above_end = intervals[row - 1]
                overlap_start, overlap_end = max(start, above_start), min(end, above_end)
                for column in range(overlap_start, overlap_end + 1):
                    if previous_entries[column - above_start] >= entries[column - start]:
                        valid = False
                        break
            if not valid:
                continue
            new_remaining = tuple(remaining[i] - counts[i] for i in range(4))
            answer += recurse(row + 1, new_remaining, tuple(trial), entries)
        return answer

    return recurse(0, content, (0, 0, 0, 0), ())


def subspace_completion(face_generators, ambient_dimension):
    """A unimodular basis whose first columns span the saturated face lattice."""
    k = rank_vectors(face_generators)
    assert k == len(face_generators) and 0 < k < ambient_dimension
    if k == 1:
        saturated = [primitive(face_generators[0])]
    elif (ambient_dimension, k) == (3, 2):
        normal = primitive(cross(face_generators[0], face_generators[1]))
        vectors = sorted(product(range(-3, 4), repeat=3))
        vectors = [value for value in vectors if value != (0, 0, 0) and dot(normal, value) == 0]
        saturated = None
        for left, right in combinations(vectors, 2):
            if cross(left, right) in (normal, tuple(-x for x in normal)):
                saturated = [left, right]
                break
        assert saturated is not None
    else:
        raise AssertionError((ambient_dimension, k))
    vectors = sorted(product(range(-3, 4), repeat=ambient_dimension), reverse=True)
    vectors = [value for value in vectors if value != (0,) * ambient_dimension]
    need = ambient_dimension - k
    for complement in combinations(vectors, need):
        columns = saturated + list(complement)
        determinant = det_columns(*columns) if ambient_dimension == 3 else int(
            sp.Matrix.hstack(*(sp.Matrix(column) for column in columns)).det())
        if abs(determinant) == 1:
            if determinant < 0:
                columns[-1] = tuple(-x for x in columns[-1])
            matrix = sp.Matrix.hstack(*(sp.Matrix(column) for column in columns))
            assert matrix.det() == 1
            return matrix, k
    raise AssertionError("unimodular subspace completion failed")


def face_multiplicity(generators, ambient_dimension):
    k = len(generators)
    matrix = sp.Matrix.hstack(*(sp.Matrix(generator) for generator in generators))
    minors = []
    for rows in combinations(range(ambient_dimension), k):
        minors.append(abs(int(matrix.extract(rows, range(k)).det())))
    return content_gcd(minors)


def fundamental_points(generators):
    dimension = len(generators)
    matrix = sp.Matrix.hstack(*(sp.Matrix(generator) for generator in generators))
    inverse = matrix.inv()
    corners = []
    for mask in product((0, 1), repeat=dimension):
        corners.append(tuple(sum(mask[j] * generators[j][i] for j in range(dimension))
                             for i in range(dimension)))
    lows = [floor(min(corner[i] for corner in corners)) for i in range(dimension)]
    highs = [ceil(max(corner[i] for corner in corners)) for i in range(dimension)]
    answer = []
    for point in product(*(range(lows[i], highs[i] + 1) for i in range(dimension))):
        coordinates = inverse * sp.Matrix(point)
        if all(0 <= value < 1 for value in coordinates):
            answer.append(point)
    assert len(answer) == abs(int(matrix.det()))
    return tuple(answer)


def quotient_data(face_generators, other_generators, gram, covector):
    dimension = gram.rows
    completion_matrix, k = subspace_completion(face_generators, dimension)
    inverse = completion_matrix.inv()
    quotient_generators = []
    for generator in other_generators:
        coordinates = inverse * sp.Matrix(generator)
        quotient_generators.append(tuple(sp.Rational(value) for value in coordinates[k:, 0]))
    transformed_gram = completion_matrix.T * gram * completion_matrix
    aa = transformed_gram[:k, :k]
    bb = transformed_gram[:k, k:]
    dd = transformed_gram[k:, k:]
    quotient_gram = sp.simplify(dd - bb.T * aa.inv() * bb)
    transformed_covector = completion_matrix.T * covector
    face_covector = transformed_covector[:k, 0]
    raw_quotient_covector = transformed_covector[k:, 0]
    quotient_covector = sp.simplify(raw_quotient_covector - bb.T * aa.inv() * face_covector)
    return tuple(quotient_generators), quotient_gram, sp.Matrix(quotient_covector)


def mu_expression(generators, gram, covector, variable):
    """BV mu of a full-dimensional simplicial feasible cone along t*covector."""
    dimension = len(generators)
    assert gram.rows == dimension and len(generators) == dimension
    vectors = tuple(sp.Matrix(generator) for generator in generators)
    pairings = tuple(sp.simplify(covector.dot(vector)) for vector in vectors)
    if any(value == 0 for value in pairings):
        raise ZeroDivisionError("nongeneric covector")
    points = fundamental_points(generators)
    numerator = sum(sp.exp(variable * covector.dot(sp.Matrix(point))) for point in points)
    discrete = numerator / sp.prod(1 - sp.exp(variable * value) for value in pairings)
    determinant = abs(int(sp.Matrix.hstack(*vectors).det()))
    integral = (-1) ** dimension * determinant / sp.prod(variable * value for value in pairings)
    expression = discrete - integral
    for size in range(1, dimension):
        for face_indices in combinations(range(dimension), size):
            other_indices = tuple(i for i in range(dimension) if i not in face_indices)
            face = tuple(generators[i] for i in face_indices)
            others = tuple(generators[i] for i in other_indices)
            multiplicity = face_multiplicity(face, dimension)
            face_integral = ((-1) ** size * multiplicity /
                             sp.prod(variable * pairings[i] for i in face_indices))
            q_generators, q_gram, q_covector = quotient_data(face, others, gram, covector)
            expression -= mu_expression(q_generators, q_gram, q_covector, variable) * face_integral
    return expression


def multiply_laurent(left, right, low, high):
    answer = {}
    for exponent_left, coefficient_left in left.items():
        for exponent_right, coefficient_right in right.items():
            exponent = exponent_left + exponent_right
            if low <= exponent <= high:
                answer[exponent] = answer.get(exponent, sp.Rational(0)) + coefficient_left * coefficient_right
    return {exponent: sp.simplify(coefficient) for exponent, coefficient in answer.items()
            if coefficient != 0}


def geometric_laurent(pairing, high):
    """Series of 1/(1-exp(pairing*t)), from t^-1 through t^high."""
    pairing = sp.Rational(pairing)
    answer = {-1: -1 / pairing, 0: sp.Rational(1, 2)}
    for exponent in range(1, high + 1):
        coefficient = -sp.bernoulli(exponent + 1) * pairing ** exponent / sp.factorial(exponent + 1)
        if coefficient:
            answer[exponent] = coefficient
    return answer


def mu_laurent(generators, gram, covector, maximum_order):
    """Exact truncated local Euler--Maclaurin recursion.

    The output is the Taylor series of mu through ``maximum_order``.  During
    the calculation all Laurent coefficients down to minus the dimension are
    retained and are required to cancel identically.
    """
    dimension = len(generators)
    vectors = tuple(sp.Matrix(generator) for generator in generators)
    pairings = tuple(sp.simplify(covector.dot(vector)) for vector in vectors)
    if any(value == 0 for value in pairings):
        raise ZeroDivisionError("nongeneric covector")

    denominator = {0: sp.Rational(1)}
    # A high positive term from one factor can combine with the t^-1 terms of
    # all remaining factors.  Retain that headroom until the product is done.
    factor_high = maximum_order + dimension - 1
    product_high = maximum_order + dimension
    for index, pairing in enumerate(pairings):
        denominator = multiply_laurent(
            denominator, geometric_laurent(pairing, factor_high),
            -(index + 1), product_high,
        )
    denominator = {exponent: coefficient for exponent, coefficient in denominator.items()
                   if exponent <= maximum_order}
    points = fundamental_points(generators)
    numerator = {}
    for exponent in range(maximum_order + dimension + 1):
        numerator[exponent] = sum(
            covector.dot(sp.Matrix(point)) ** exponent for point in points
        ) / sp.factorial(exponent)
    result = multiply_laurent(denominator, numerator, -dimension, maximum_order)

    determinant = abs(int(sp.Matrix.hstack(*vectors).det()))
    integral_coefficient = ((-1) ** dimension * determinant /
                            sp.prod(pairings))
    result[-dimension] = result.get(-dimension, sp.Rational(0)) - integral_coefficient

    for size in range(1, dimension):
        for face_indices in combinations(range(dimension), size):
            other_indices = tuple(i for i in range(dimension) if i not in face_indices)
            face = tuple(generators[i] for i in face_indices)
            others = tuple(generators[i] for i in other_indices)
            multiplicity = face_multiplicity(face, dimension)
            face_integral_coefficient = ((-1) ** size * multiplicity /
                                         sp.prod(pairings[i] for i in face_indices))
            q_generators, q_gram, q_covector = quotient_data(face, others, gram, covector)
            transverse = mu_laurent(
                q_generators, q_gram, q_covector, maximum_order + size
            )
            for exponent, coefficient in transverse.items():
                shifted = exponent - size
                if -dimension <= shifted <= maximum_order:
                    result[shifted] = (result.get(shifted, sp.Rational(0))
                                       - coefficient * face_integral_coefficient)

    result = {exponent: sp.simplify(coefficient) for exponent, coefficient in result.items()}
    assert all(result.get(exponent, 0) == 0 for exponent in range(-dimension, 0)), result
    return {exponent: result.get(exponent, sp.Rational(0))
            for exponent in range(maximum_order + 1)}


def mu_constant_simplicial(generators, gram=None):
    dimension = len(generators)
    gram = sp.eye(dimension) if gram is None else sp.Matrix(gram)
    covectors = [
        tuple(2 ** i + 3 ** (dimension - i) for i in range(dimension)),
        tuple(5 ** i + 2 * 7 ** (dimension - i) for i in range(dimension)),
        tuple(11 ** i + 13 ** (dimension - i) for i in range(dimension)),
    ]
    for candidate in covectors:
        try:
            value = mu_laurent(generators, gram, sp.Matrix(candidate), 0)[0]
            if value.is_Rational:
                return to_fraction(value)
        except (ZeroDivisionError, ValueError):
            continue
    raise AssertionError(f"could not regularize cone {generators}")


def intrinsic_two_cone_mu(left, right):
    completion_matrix, k = subspace_completion((left, right), 3)
    assert k == 2
    basis = completion_matrix[:, :2]
    inverse = completion_matrix.inv()
    generators = []
    for vector in (left, right):
        coordinates = inverse * sp.Matrix(vector)
        assert coordinates[2] == 0
        generators.append(tuple(sp.Rational(value) for value in coordinates[:2, 0]))
    gram = basis.T * basis
    return mu_constant_simplicial(tuple(generators), gram)


def tangent_cycle(vertex_index, vertices, facets, edges):
    incident_edges = [index for index, edge in enumerate(edges) if vertex_index in edge[0]]
    rays = {}
    edge_facets = {}
    for edge_index in incident_edges:
        edge = edges[edge_index]
        other = edge[0][0] if edge[0][1] == vertex_index else edge[0][1]
        delta = tuple(vertices[other][i] - vertices[vertex_index][i] for i in range(3))
        assert all(value.denominator == 1 for value in delta)
        rays[edge_index] = primitive(tuple(int(value) for value in delta))
        edge_facets[edge_index] = set(edge[1])
    adjacency = {edge_index: set() for edge_index in incident_edges}
    for left, right in combinations(incident_edges, 2):
        if edge_facets[left] & edge_facets[right]:
            adjacency[left].add(right)
            adjacency[right].add(left)
    assert all(len(neighbors) == 2 for neighbors in adjacency.values())
    start = min(incident_edges)
    cycle = [start, min(adjacency[start])]
    while len(cycle) < len(incident_edges):
        previous, current = cycle[-2], cycle[-1]
        following = next(value for value in adjacency[current] if value != previous)
        assert following not in cycle
        cycle.append(following)
    assert start in adjacency[cycle[-1]]
    return tuple(rays[index] for index in cycle)


def vertex_alpha(tangent_rays):
    if len(tangent_rays) == 3:
        return mu_constant_simplicial(tangent_rays), None
    assert len(tangent_rays) == 4
    r0, r1, r2, r3 = tangent_rays
    first = (mu_constant_simplicial((r0, r1, r2))
             + mu_constant_simplicial((r0, r2, r3))
             - intrinsic_two_cone_mu(r0, r2))
    second = (mu_constant_simplicial((r1, r2, r3))
              + mu_constant_simplicial((r1, r3, r0))
              - intrinsic_two_cone_mu(r1, r3))
    assert first == second
    return first, second


def build_q3(vertices, facets, edges):
    matrix = [[0] * len(vertices) for _ in edges]
    for row, edge in enumerate(edges):
        tail, head = edge[0]
        matrix[row][tail] = -1
        matrix[row][head] = 1
        # Geometric quotient audit: all non-edge facet rays at the endpoints
        # map to opposite signs under the primitive edge tangent covector.
        tangent = primitive(tuple(int(vertices[head][i] - vertices[tail][i]) for i in range(3)))
        endpoint_signs = []
        for vertex_index in (tail, head):
            values = []
            for facet_index, facet in enumerate(facets):
                if vertex_index in facet[2] and facet_index not in edge[1]:
                    value = dot(tangent, facet[0])
                    if value:
                        values.append(1 if value > 0 else -1)
            assert values and len(set(values)) == 1
            endpoint_signs.append(values[0])
        assert endpoint_signs[0] == -endpoint_signs[1]
    alphas = []
    tangent_rays = []
    for vertex_index in range(len(vertices)):
        cycle = tangent_cycle(vertex_index, vertices, facets, edges)
        alpha, second = vertex_alpha(cycle)
        alphas.append(alpha)
        tangent_rays.append(cycle)
        if second is not None:
            assert alpha == second
    return tuple(tuple(row) for row in matrix), tuple(alphas), tuple(tangent_rays)


def graph_farkas_certificate(matrix, alphas):
    vertices = len(alphas)
    target = (Fraction(1, vertices),) * vertices
    rhs = tuple(target[i] - alphas[i] for i in range(vertices))
    assert sum(rhs, Fraction(0)) == 0
    adjacency = {i: [] for i in range(vertices)}
    for edge_index, row in enumerate(matrix):
        tail = row.index(-1)
        head = row.index(1)
        adjacency[tail].append((head, edge_index))
        adjacency[head].append((tail, edge_index))
    parent = {0: None}
    parent_edge = {}
    order = [0]
    queue = deque([0])
    while queue:
        vertex = queue.popleft()
        for neighbor, edge_index in adjacency[vertex]:
            if neighbor not in parent:
                parent[neighbor] = vertex
                parent_edge[neighbor] = edge_index
                order.append(neighbor)
                queue.append(neighbor)
    assert len(parent) == vertices
    subtree = list(rhs)
    y = [Fraction(0)] * len(matrix)
    for child in reversed(order[1:]):
        edge_index = parent_edge[child]
        row = matrix[edge_index]
        # Sum divergence on the child subtree is +y if child is the head,
        # and -y if child is the tail.
        y[edge_index] = subtree[child] if row[child] == 1 else -subtree[child]
        subtree[parent[child]] += subtree[child]
    shifted = tuple(alphas[column] + sum(Fraction(matrix[row][column]) * y[row]
                                         for row in range(len(matrix)))
                    for column in range(vertices))
    assert shifted == target
    return tuple(y), shifted


def serialize(value):
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def main():
    rows = hive_rows()
    vertices = enumerate_vertices(rows)
    facets = irredundant_facets(rows, vertices)
    edges = enumerate_edges(facets, vertices)
    assert len(vertices) == 11 and len(edges) == 21 and len(facets) == 12
    assert len(vertices) - len(edges) + len(facets) == 2
    assert all(value.denominator == 1 for vertex in vertices for value in vertex)

    counts = tuple(lattice_count(rows, vertices, dilation) for dilation in range(6))
    coefficients = interpolate(counts[:4])
    assert coefficients == (Fraction(1), Fraction(7), Fraction(18), Fraction(24))
    assert all(sum(coefficients[k] * n ** k for k in range(4)) == counts[n] for n in (4, 5))
    # One LR-rule evaluation is enough to audit the boundary convention.  The
    # five dilation values themselves are independently enumerated in the hive
    # lattice above; running the tableau recursion through scale five would add
    # no new geometric check and is needlessly expensive.
    lr_count_at_one = lr_tableau_count(1)
    assert lr_count_at_one == counts[1] == 50

    b2, a2, w2, indices2, balance2 = build_q2(facets, edges)
    rank2 = matrix_rank(b2)
    assert rank2 == 20 and len(edges) - rank2 == 1
    assert balance2 == (Fraction(0),) * len(balance2)
    pairing2 = sum(a2[i] * w2[i] for i in range(len(edges)))
    assert pairing2 == coefficients[1] == 7
    assert min(a2) == Fraction(1, 9)
    assert Counter(indices2) == Counter({1: 18, 2: 3})
    assert {a2[i] for i, index in enumerate(indices2) if index == 2} == {Fraction(5, 18)}

    b3, a3, tangent_rays = build_q3(vertices, facets, edges)
    rank3 = matrix_rank(b3)
    assert rank3 == 10 and len(vertices) - rank3 == 1
    assert all(sum(row) == 0 for row in b3)
    assert sum(a3, Fraction(0)) == coefficients[0] == 1
    y3, shifted3 = graph_farkas_certificate(b3, a3)
    assert shifted3 == (Fraction(1, 11),) * 11

    det2_index = vertices.index((Fraction(26), Fraction(32), Fraction(38)))
    det2_rays = tuple(sorted(tangent_rays[det2_index]))
    assert det2_rays == ((0, 1, 1), (1, 0, 1), (1, 1, 0))
    assert abs(det_columns(*det2_rays)) == 2

    # Direct recursion must reproduce the closed formula on every unimodular
    # simplicial tangent cone encountered in either triangulation.
    for rays in tangent_rays:
        if len(rays) == 3 and abs(det_columns(*rays)) == 1:
            matrix = sp.Matrix.hstack(*(sp.Matrix(ray) for ray in rays))
            feasible_gram = matrix.T * matrix
            closed = Fraction(1, 8)
            for i, j in combinations(range(3), 2):
                gij = int(feasible_gram[i, j])
                gii = int(feasible_gram[i, i])
                gjj = int(feasible_gram[j, j])
                closed += Fraction(gij, 24) * (Fraction(1, gii) + Fraction(1, gjj))
            assert mu_constant_simplicial(rays) == closed

    payload = serialize({
        "schema": "r4-complete-fan-ghte-independent-audit-v1",
        "boundary": {"lambda": LAMBDA, "mu": MU, "nu": NU},
        "face_lattice": {
            "f_vector": (1, len(facets), len(edges), len(vertices)),
            "vertices": vertices,
            "facets": facets,
            "edges": edges,
        },
        "ehrhart": {"counts_0_to_5": counts, "lr_rule_count_at_one": lr_count_at_one,
                     "coefficients": coefficients},
        "q2": {"rank": rank2, "kernel_dimension": len(edges) - rank2,
                "index_histogram": dict(sorted(Counter(indices2).items())),
                "alphas": a2, "lengths": w2, "balance": balance2,
                "pairing": pairing2, "minimum_alpha": min(a2)},
        "q3": {"rank": rank3, "kernel_dimension": len(vertices) - rank3,
                "alphas": a3, "pairing": sum(a3, Fraction(0)),
                "farkas_y": y3, "shifted": shifted3},
        "det2_vertex": {"vertex": vertices[det2_index], "tangent_rays": det2_rays,
                        "tangent_determinant": abs(det_columns(*det2_rays)),
                        "direct_BV_alpha": a3[det2_index]},
    })
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    digest = hashlib.sha256(encoded).hexdigest()
    print("PASS")
    print(f"audit_sha256={digest}")
    print(f"fan_f_vector={payload['face_lattice']['f_vector']}")
    print(f"ehrhart_counts_0_to_5={payload['ehrhart']['counts_0_to_5']}")
    print(f"lr_rule_count_at_one={payload['ehrhart']['lr_rule_count_at_one']}")
    print(f"ehrhart_coefficients={payload['ehrhart']['coefficients']}")
    print(f"q2: rank={rank2} kernel=1 index_histogram={dict(Counter(indices2))} "
          f"pairing={pairing2} min_alpha={min(a2)}")
    print(f"q3: rank={rank3} kernel=1 pairing={sum(a3, Fraction(0))} "
          f"min_shifted={min(shifted3)}")
    print(f"q3_BV_alphas={tuple(str(value) for value in a3)}")
    print(f"det2_vertex_alpha={a3[det2_index]}")


if __name__ == "__main__":
    main()
