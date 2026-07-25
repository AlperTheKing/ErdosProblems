#!/usr/bin/env python3
"""Direct normal-cone BV alpha with exact coset-ray refinement.

This extends ``r5_codim4_normal_subdivision_alpha.py``: if retained active hive
normals do not already make every maximal cell saturated, a nonzero lattice
point of a cell's half-open fundamental parallelepiped is inserted as a star
subdivision ray.  The index strictly drops on the selected cell.  Refinement
continues until every maximal normal cell has determinant one.
"""

from fractions import Fraction
from itertools import product
from math import gcd

import r5_codim4_bv_independent as bv
import r5_codim4_full_cone_alpha as geometry
from r5_codim4_full_cone_alpha_v2 import pulling_tetrahedra_unimodular
import r5_codim4_normal_subdivision_alpha as core


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    assert divisor
    return tuple(value // divisor for value in vector)


def fundamental_refinement_ray(cell, rays):
    index = core.cell_index(cell, rays)
    assert index > 1
    candidates = set()
    for residues in product(range(index), repeat=4):
        if not any(residues):
            continue
        numerators = tuple(
            sum(residues[i] * rays[cell[i]][j] for i in range(4))
            for j in range(4)
        )
        if not all(value % index == 0 for value in numerators):
            continue
        vector = primitive(tuple(value // index for value in numerators))
        if vector in rays:
            continue
        coefficients = core.coordinates_in_cell(vector, cell, rays)
        if not all(value >= 0 for value in coefficients):
            continue
        support = tuple(i for i, value in enumerate(coefficients) if value > 0)
        children = tuple(coefficients[i] * index for i in support)
        if not children or not all(value.denominator == 1 for value in children):
            continue
        if max(children) >= index:
            continue
        score = (
            max(children), sum(children), len(support),
            sum(abs(value) for value in vector), vector,
        )
        candidates.add((score, vector))
    assert candidates, (cell, index, tuple(rays[i] for i in cell))
    return min(candidates)[1]


def direct_normal_alpha_refined(normal_rays, feasible_lattice_gram):
    active_count = len(normal_rays)
    rays = list(map(tuple, normal_rays))
    extreme, polar = core.extreme_normal_indices(tuple(rays))
    extreme_generators, facets = core.facets_of_generator_cone(extreme, tuple(rays))
    local_cells = pulling_tetrahedra_unimodular(extreme_generators, facets)
    cells = tuple(sorted(tuple(sorted(extreme[i] for i in cell)) for cell in local_cells))

    inserted_active = []
    for ray_index in range(active_count):
        if ray_index in extreme:
            continue
        cells, used = core.star_insert(cells, ray_index, tuple(rays))
        if used:
            inserted_active.append(ray_index)

    coset_rays = []
    for _ in range(100):
        bad = [(core.cell_index(cell, tuple(rays)), cell) for cell in cells]
        bad = [record for record in bad if record[0] > 1]
        if not bad:
            break
        _, cell = max(bad)
        vector = fundamental_refinement_ray(cell, tuple(rays))
        ray_index = len(rays)
        rays.append(vector)
        cells, used = core.star_insert(cells, ray_index, tuple(rays))
        assert used
        coset_rays.append((ray_index, vector))
    else:
        raise AssertionError("coset refinement did not terminate")

    indices = tuple(core.cell_index(cell, tuple(rays)) for cell in cells)
    assert all(index == 1 for index in indices)
    basis_normal_gram = bv.inverse(feasible_lattice_gram)
    cell_values = []
    for cell in cells:
        gram = core.normal_metric_gram(cell, tuple(rays), basis_normal_gram)
        alpha = geometry.alpha_generic(bv.inverse(gram))
        cell_values.append((cell, alpha))
    return {
        "alpha": sum((value for _, value in cell_values), Fraction(0)),
        "active_count": active_count,
        "extreme_indices": extreme,
        "inserted_active_indices": tuple(inserted_active),
        "coset_rays": tuple(coset_rays),
        "all_rays": tuple(rays),
        "cells": cells,
        "cell_indices": indices,
        "cell_values": tuple(cell_values),
    }


def main():
    normals, _ = bv.rank5_hive_normals()
    basis_ids = (0, 1, 4, 5)
    active_ids = (0, 1, 2, 3, 4, 5)
    coordinates, feasible_lattice_gram = geometry.coordinates_in_basis(
        normals, basis_ids, active_ids
    )
    result = direct_normal_alpha_refined(coordinates, feasible_lattice_gram)
    assert result["alpha"] == Fraction(17977, 604800)
    print("PASS")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
