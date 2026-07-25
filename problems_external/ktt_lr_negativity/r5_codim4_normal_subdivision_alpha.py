#!/usr/bin/env python3
"""Canonical direct-normal-cone BV alpha by saturated subdivision.

Berline--Vergne Corollary 24 says the dual-normal-cone functional is a simple
valuation: for a subdivision of a full-dimensional normal cone, its value is
the sum over full-dimensional cells only.  This checker therefore works in
the normal cone (not by inclusion--exclusion in the polar feasible cone).

The active primitive hive normals are expressed in a saturated normal-lattice
basis.  We triangulate the cone on its extreme rays, star-insert every retained
active non-extreme ray, verify each final 4-cell has lattice index one, and sum
the independently derived unimodular BV constants of the dual feasible cells.
"""

from fractions import Fraction

import r5_codim4_bv_independent as bv
import r5_codim4_full_cone_alpha as geometry
from r5_codim4_full_cone_alpha_v2 import pulling_tetrahedra_unimodular


def polar_rays(normal_rays):
    return geometry.feasible_extreme_rays(normal_rays)


def extreme_normal_indices(normal_rays):
    polar = polar_rays(normal_rays)
    answer = []
    for i, normal in enumerate(normal_rays):
        zero_rays = [ray for ray in polar if geometry.dot(normal, ray) == 0]
        if geometry.rank(zero_rays) == 3:
            answer.append(i)
    return tuple(answer), polar


def facets_of_generator_cone(generator_indices, normal_rays):
    generators = tuple(normal_rays[i] for i in generator_indices)
    polar = polar_rays(generators)
    facets = set()
    for covector in polar:
        facet = tuple(
            local for local, generator in enumerate(generators)
            if geometry.dot(generator, covector) == 0
        )
        if len(facet) >= 3 and geometry.rank([generators[i] for i in facet]) == 3:
            facets.add(facet)
    return generators, tuple(sorted(facets))


def coordinates_in_cell(vector, cell, rays):
    # Solve V*c=vector through the Gram matrix; V is a nonsingular Z-basis
    # over Q, not necessarily unimodular.
    basis = tuple(rays[i] for i in cell)
    gram = tuple(
        tuple(geometry.dot(left, right) for right in basis) for left in basis
    )
    inverse_gram = bv.inverse(gram)
    products = tuple(geometry.dot(left, vector) for left in basis)
    return tuple(
        sum(inverse_gram[i][j] * products[j] for j in range(4))
        for i in range(4)
    )


def star_insert(cells, ray_index, rays):
    vector = rays[ray_index]
    new_cells = set()
    used = False
    for cell in cells:
        coefficients = coordinates_in_cell(vector, cell, rays)
        if not all(value >= 0 for value in coefficients):
            new_cells.add(cell)
            continue
        support = [i for i, value in enumerate(coefficients) if value > 0]
        if len(support) == 1 and cell[support[0]] == ray_index:
            new_cells.add(cell)
            continue
        used = True
        for local in support:
            replacement = tuple(sorted(
                [ray_index] + [cell[i] for i in range(4) if i != local]
            ))
            if len(set(replacement)) == 4 and geometry.rank([rays[i] for i in replacement]) == 4:
                new_cells.add(replacement)
    return tuple(sorted(new_cells)), used


def cell_index(cell, rays):
    matrix = [[rays[j][i] for j in cell] for i in range(4)]
    return abs(int(geometry.determinant(matrix)))


def normal_metric_gram(cell, rays, basis_normal_gram):
    return tuple(
        tuple(
            sum(
                rays[i][a] * basis_normal_gram[a][b] * rays[j][b]
                for a in range(4) for b in range(4)
            )
            for j in cell
        )
        for i in cell
    )


def direct_normal_alpha(normal_rays, feasible_lattice_gram):
    normal_rays = tuple(map(tuple, normal_rays))
    extreme, polar = extreme_normal_indices(normal_rays)
    extreme_generators, facets = facets_of_generator_cone(extreme, normal_rays)
    local_cells = pulling_tetrahedra_unimodular(extreme_generators, facets)
    cells = tuple(sorted(tuple(sorted(extreme[i] for i in cell)) for cell in local_cells))

    inserted = []
    for ray_index in range(len(normal_rays)):
        if ray_index in extreme:
            continue
        cells, used = star_insert(cells, ray_index, normal_rays)
        if used:
            inserted.append(ray_index)

    indices = tuple(cell_index(cell, normal_rays) for cell in cells)
    assert all(index == 1 for index in indices), (cells, indices)
    basis_normal_gram = bv.inverse(feasible_lattice_gram)
    cell_values = []
    for cell in cells:
        gram = normal_metric_gram(cell, normal_rays, basis_normal_gram)
        feasible_gram = bv.inverse(gram)
        alpha = geometry.alpha_generic(feasible_gram)
        cell_values.append((cell, alpha))
    return {
        "alpha": sum((value for _, value in cell_values), Fraction(0)),
        "extreme_indices": extreme,
        "polar_rays": polar,
        "inserted_indices": tuple(inserted),
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
    result = direct_normal_alpha(coordinates, feasible_lattice_gram)
    assert result["alpha"] == Fraction(17977, 604800)
    expected_values = sorted((
        Fraction(3587, 120960), Fraction(39, 3200), Fraction(-349, 28800)
    ))
    assert sorted(value for _, value in result["cell_values"]) == expected_values
    print("PASS")
    print(f"basis_ids={basis_ids} active_ids={active_ids}")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
