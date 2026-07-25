#!/usr/bin/env python3
"""Unimodular-triangulation search wrapper for full-cone BV alpha."""

from fractions import Fraction
from itertools import product

import r5_codim4_full_cone_alpha as core


def facet_fans(facet, facets):
    if len(facet) == 3:
        return ((tuple(sorted(facet)),),)
    facet_set = set(facet)
    edges = set()
    for other in facets:
        if other == facet:
            continue
        common = tuple(sorted(facet_set.intersection(other)))
        if len(common) == 2:
            edges.add(common)
    answers = []
    for apex in facet:
        triangles = tuple(sorted({
            tuple(sorted((apex,) + edge))
            for edge in edges if apex not in edge
        }))
        if len(triangles) == len(facet) - 2:
            answers.append(triangles)
    assert answers, facet
    return tuple(answers)


def determinant_index(tetrahedron, rays):
    matrix = [[rays[j][i] for j in tetrahedron] for i in range(4)]
    return abs(int(core.determinant(matrix)))


def pulling_tetrahedra_unimodular(rays, facets):
    best = None
    for apex in range(len(rays)):
        opposite = [facet for facet in facets if apex not in facet]
        fan_choices = [facet_fans(facet, facets) for facet in opposite]
        for choices in product(*fan_choices):
            tetrahedra = tuple(sorted({
                tuple(sorted((apex,) + triangle))
                for triangles in choices for triangle in triangles
            }))
            if not tetrahedra:
                continue
            indices = tuple(determinant_index(tetrahedron, rays) for tetrahedron in tetrahedra)
            score = (max(indices), sum(indices), len(tetrahedra), tetrahedra)
            if best is None or score < best[0]:
                best = (score, tetrahedra)
            if set(indices) == {1}:
                return tetrahedra
    assert best is not None
    return best[1]


core.pulling_tetrahedra = pulling_tetrahedra_unimodular


def main():
    normals, _ = core.bv.rank5_hive_normals()
    basis_ids = (0, 1, 4, 5)
    active_ids = (0, 1, 2, 3, 4, 5)
    coordinates, lattice_gram = core.coordinates_in_basis(normals, basis_ids, active_ids)
    result = core.full_cone_alpha(coordinates, lattice_gram)
    assert result["alpha"] == Fraction(17977, 604800)
    print("PASS")
    print(f"basis_ids={basis_ids} active_ids={active_ids}")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
