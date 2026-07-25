#!/usr/bin/env python3
"""Saturate a four-dimensional normal-cone fan before evaluating BV alpha.

The first all-supersets audit exposed normal subdivision cells of lattice
index two.  Treating those cells with the unimodular formula is invalid.  This
module repairs the gap by inserting primitive lattice rays from the half-open
fundamental parallelepiped of every nonsaturated simplicial cell.  Each star
subdivision strictly lowers the affected determinants.  Once all cells have
index one, Berline--Vergne's simple valuation on normal cones permits summing
their exact unimodular values.
"""

from fractions import Fraction
from itertools import product
from math import gcd

import r5_codim4_bv_independent as bv
import r5_codim4_full_cone_alpha as geometry
import r5_codim4_normal_subdivision_alpha as normal
from r5_codim4_full_cone_alpha_v2 import pulling_tetrahedra_unimodular


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    assert divisor
    return tuple(value // divisor for value in vector)


def fundamental_ray(cell, rays):
    """Return a new primitive lattice ray inside a nonsaturated cell."""
    index = normal.cell_index(cell, rays)
    assert index > 1
    basis = tuple(rays[i] for i in cell)
    candidates = []
    for numerators in product(range(index), repeat=4):
        if not any(numerators):
            continue
        coordinates = []
        integral = True
        for row in range(4):
            numerator = sum(basis[column][row] * numerators[column]
                            for column in range(4))
            if numerator % index:
                integral = False
                break
            coordinates.append(numerator // index)
        if not integral:
            continue
        ray = primitive(tuple(coordinates))
        if ray in rays:
            continue
        support = sum(value > 0 for value in numerators)
        if support < 2:
            continue
        # Prefer an interior ray, then the ray producing the smallest largest
        # replacement determinant.  Either choice strictly lowers the index.
        replacements = []
        for local, numerator in enumerate(numerators):
            if numerator:
                replacement = tuple(
                    ray if i == local else basis[i] for i in range(4)
                )
                matrix = [[replacement[column][row] for column in range(4)]
                          for row in range(4)]
                replacements.append(abs(int(geometry.determinant(matrix))))
        assert replacements and max(replacements) < index
        candidates.append((-support, max(replacements), sum(replacements), ray))
    assert candidates, (cell, index)
    return min(candidates)[-1]


def saturated_direct_normal_alpha(normal_rays, feasible_lattice_gram):
    """Evaluate a pointed full normal cone using a saturated star fan."""
    rays = list(map(tuple, normal_rays))
    extreme, polar = normal.extreme_normal_indices(rays)
    extreme_generators, facets = normal.facets_of_generator_cone(extreme, rays)
    local_cells = pulling_tetrahedra_unimodular(extreme_generators, facets)
    cells = tuple(sorted(tuple(sorted(extreme[i] for i in cell))
                         for cell in local_cells))

    inserted_active = []
    for ray_index in range(len(rays)):
        if ray_index in extreme:
            continue
        cells, used = normal.star_insert(cells, ray_index, rays)
        if used:
            inserted_active.append(ray_index)

    inserted_saturation = []
    while True:
        bad = next((cell for cell in cells
                    if normal.cell_index(cell, rays) > 1), None)
        if bad is None:
            break
        ray = fundamental_ray(bad, rays)
        ray_index = len(rays)
        rays.append(ray)
        cells, used = normal.star_insert(cells, ray_index, rays)
        assert used
        inserted_saturation.append(ray_index)

    indices = tuple(normal.cell_index(cell, rays) for cell in cells)
    assert indices and set(indices) == {1}
    basis_normal_gram = bv.inverse(feasible_lattice_gram)
    cell_values = []
    for cell in cells:
        gram = normal.normal_metric_gram(cell, rays, basis_normal_gram)
        feasible_gram = bv.inverse(gram)
        cell_values.append((cell, geometry.alpha_generic(feasible_gram)))
    return {
        "alpha": sum((value for _, value in cell_values), Fraction(0)),
        "extreme_indices": extreme,
        "polar_rays": polar,
        "inserted_active_indices": tuple(inserted_active),
        "inserted_saturation_indices": tuple(inserted_saturation),
        "rays": tuple(rays),
        "cells": cells,
        "cell_indices": indices,
        "cell_values": tuple(cell_values),
    }


def main():
    # Reproduce the known closed cone, whose first triangulation is already
    # saturated, before the all-supersets checker imports this module.
    normals, _ = bv.rank5_hive_normals()
    basis_ids = (0, 1, 4, 5)
    active_ids = (0, 1, 2, 3, 4, 5)
    coordinates, gram = geometry.coordinates_in_basis(
        normals, basis_ids, active_ids
    )
    result = saturated_direct_normal_alpha(coordinates, gram)
    assert result["alpha"] == Fraction(17977, 604800)
    print("PASS")
    print(f"alpha={result['alpha']}")
    print(f"saturation_rays={result['inserted_saturation_indices']}")


if __name__ == "__main__":
    main()
