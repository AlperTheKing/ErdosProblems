#!/usr/bin/env python3
"""Sanity-check the q=2 subdivision convention in the r5 dim-3 contract.

This is intentionally a narrow diagnostic.  It compares the contract's
normal-cone subdivision value with a direct local Euler--Maclaurin evaluation
of the polar feasible cone in the saturated quotient lattice and inherited
metric.
"""

from fractions import Fraction
import sympy as sp

import r4_complete_fan_ghte_independent_audit as direct
import r5_lowerdim_complete_fan_ghte_contract as contract


def correct_q2_alpha(left, right, dual_gram):
    completion, rank = direct.subspace_completion((left, right), 3)
    assert rank == 2
    inverse = completion.inv()
    plane_basis = completion[:, :2]
    left_coordinates = tuple(int(value) for value in
                             (inverse * sp.Matrix(left))[:2, 0])
    right_coordinates = tuple(int(value) for value in
                              (inverse * sp.Matrix(right))[:2, 0])
    normal_metric = plane_basis.T * sp.Matrix(dual_gram) * plane_basis
    feasible_metric = normal_metric.inv()

    def feasible_ray(normal, other):
        ray = direct.primitive((normal[1], -normal[0]))
        if direct.dot(other, ray) > 0:
            ray = tuple(-value for value in ray)
        assert direct.dot(normal, ray) == 0 and direct.dot(other, ray) < 0
        return ray

    rays = (feasible_ray(left_coordinates, right_coordinates),
            feasible_ray(right_coordinates, left_coordinates))
    return direct.mu_constant_simplicial(rays, feasible_metric)


def check(name, boundary):
    model = contract.intrinsic_model(boundary)
    vertices = model["intrinsic_vertices"]
    facets = contract.enumerate_facets(vertices)
    edges = contract.enumerate_edges(facets, vertices)
    old_values = []
    correct_values = []
    mismatches = []
    for index, edge in enumerate(edges):
        left = facets[edge["facets"][0]]["normal"]
        right = facets[edge["facets"][1]]["normal"]
        old, _ = contract.q2_alpha(left, right, model["N_gram"])
        correct = correct_q2_alpha(left, right, model["N_gram"])
        old_values.append(old)
        correct_values.append(correct)
        if old != correct:
            mismatches.append({
                "edge": index,
                "saturation_index": contract.pair_index(left, right),
                "contract_alpha": old,
                "direct_alpha": correct,
                "length": edge["length"],
                "left": left,
                "right": right,
            })
    old_pairing = sum(old_values[i] * Fraction(edges[i]["length"])
                      for i in range(len(edges)))
    correct_pairing = sum(correct_values[i] * Fraction(edges[i]["length"])
                          for i in range(len(edges)))
    return mismatches, old_pairing, correct_pairing


def main():
    any_mismatch = False
    for name, boundary in (("horn_gap", contract.HORN_GAP),
                           ("hard", contract.HARD)):
        mismatches, old_pairing, correct_pairing = check(name, boundary)
        any_mismatch |= bool(mismatches)
        print(f"{name}: mismatches={len(mismatches)} "
              f"contract_pairing={old_pairing} direct_pairing={correct_pairing}")
        for mismatch in mismatches:
            print("  " + repr(mismatch))
    print("MISMATCH_FOUND" if any_mismatch else "PASS")


if __name__ == "__main__":
    main()
