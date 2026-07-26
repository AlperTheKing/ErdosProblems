"""Audit the exact induced-C5 face forced on the R10 D22 SDP.

The input pickle is numerical only.  This audit does not round it.  It proves
the rank of the parity-zero evaluation space with exact SymPy arithmetic and
measures how far the floating Gram matrix and multipliers lie from the face
that every exact c=25 certificate must satisfy.
"""

from __future__ import annotations

import importlib.util
import pickle
import sys
from pathlib import Path

import numpy as np
import sympy as sy


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
NUMERIC_PATH = HERE / "CODEX_R10_g11_d22_numeric.pkl"
ROUND7 = HERE.parent / "round7"
sys.path.insert(0, str(ROUND7))

from Q4_graphs import induced_C5s  # noqa: E402


def load_builder():
    spec = importlib.util.spec_from_file_location("codex_r10_d22_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load D22 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def support_inside(exponent: tuple[int, ...], vertices: set[int]) -> bool:
    return all(power == 0 or vertex in vertices for vertex, power in enumerate(exponent))


def main() -> None:
    builder = load_builder()
    model = builder.build_model()
    with NUMERIC_PATH.open("rb") as handle:
        numeric = pickle.load(handle)
    if numeric.get("NUMERICAL_ONLY") is not True:
        raise AssertionError("input must be marked NUMERICAL_ONLY")

    cycles = induced_C5s(11, model.edges)
    if len(cycles) != 33:
        raise AssertionError(f"expected 33 induced C5s, got {len(cycles)}")

    arc_minima = []
    tight_cut_counts = []
    for cycle in cycles:
        vertices = set(cycle)
        q_values = [
            sum(
                model.edges[edge_index][0] in vertices
                and model.edges[edge_index][1] in vertices
                for edge_index in monochromatic_edges
            )
            for _mask, monochromatic_edges in model.cuts
        ]
        arc_minima.append(min(q_values))
        tight_cut_counts.append(sum(value == min(q_values) for value in q_values))
    if set(arc_minima) != {1}:
        raise AssertionError(f"not every induced C5 is tight: minima={arc_minima}")
    print(
        f"C5_TIGHTNESS_OK cycles={len(cycles)} arc_minimum=1 "
        f"tight_cut_count_range={min(tight_cut_counts)}..{max(tight_cut_counts)}"
    )

    # Recover one numerical value per multiplier orbit and verify exact tying.
    nu_values = np.full(int(model.multiplier_variable.size), np.nan)
    maximum_tie_error = 0.0
    for cut_index in range(len(model.cuts)):
        for monomial_index, monomial in enumerate(model.multiplier_monomials):
            orbit_id = int(model.multiplier_orbit_ids[cut_index, monomial_index])
            value = float(numeric["nu"].get((cut_index, monomial), 0.0))
            if np.isnan(nu_values[orbit_id]):
                nu_values[orbit_id] = value
            else:
                maximum_tie_error = max(
                    maximum_tie_error, abs(nu_values[orbit_id] - value)
                )

    forced_zero_orbits: set[int] = set()
    for cycle in cycles:
        vertices = set(cycle)
        supported_monomials = [
            monomial_index
            for monomial_index, monomial in enumerate(model.multiplier_monomials)
            if support_inside(monomial, vertices)
        ]
        for cut_index, (_mask, monochromatic_edges) in enumerate(model.cuts):
            q_value = sum(
                model.edges[edge_index][0] in vertices
                and model.edges[edge_index][1] in vertices
                for edge_index in monochromatic_edges
            )
            if q_value <= 1:
                continue
            forced_zero_orbits.update(
                int(model.multiplier_orbit_ids[cut_index, monomial_index])
                for monomial_index in supported_monomials
            )
    forced_maximum = max(abs(nu_values[index]) for index in forced_zero_orbits)
    print(
        f"MULTIPLIER_FACE forced_zero_orbits={len(forced_zero_orbits)}/"
        f"{len(nu_values)} max_abs_forced={forced_maximum:.12e} "
        f"orbit_tie_error={maximum_tie_error:.3e}"
    )

    qblock_by_parity = {
        tuple(power & 1 for power in basis[0]): (basis, np.asarray(matrix, dtype=float))
        for basis, matrix in numeric["Q"]
    }
    parity_zero_orbit = next(
        orbit for orbit in model.gram_orbits if sum(orbit.parity_rep) == 0
    )
    basis, matrix = qblock_by_parity[parity_zero_orbit.parity_rep]
    evaluation_vectors = []
    for cycle in cycles:
        vertices = set(cycle)
        evaluation_vectors.append(
            [int(support_inside(exponent, vertices)) for exponent in basis]
        )
    evaluation = sy.Matrix(evaluation_vectors)
    exact_rank = evaluation.rank()
    if exact_rank != 33:
        raise AssertionError(f"expected exact evaluation rank 33, got {exact_rank}")

    evaluation_float = np.asarray(evaluation_vectors, dtype=float)
    kernel_product = matrix @ evaluation_float.T
    eigenvalues = np.linalg.eigvalsh((matrix + matrix.T) / 2)
    print(
        f"CENTRAL_FACE exact_kernel_rank={exact_rank} block_order={len(basis)} "
        f"max_abs_QK={np.max(np.abs(kernel_product)):.12e} "
        f"inf_norm_QK={np.linalg.norm(kernel_product, ord=np.inf):.12e}"
    )
    print(
        "CENTRAL_SPECTRUM "
        f"min_eigenvalue={eigenvalues[0]:.12e} "
        f"nullity_at_1e-5={int(np.count_nonzero(eigenvalues < 1e-5))} "
        f"forced_nullity_lower_bound={exact_rank}"
    )
    print("FACE_AUDIT_CONCLUSION: raw numerical iterate must not be rationally rounded")


if __name__ == "__main__":
    main()
