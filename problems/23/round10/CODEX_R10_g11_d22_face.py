"""D22-reduced induced-C5 face model for the Gamma_11 R10 frontier.

This is a separate scaffold over CODEX_R10_g11_d22_sdp.py.  It does not alter
the original fixed-c feasibility constructor.  The graph, degree, cut family,
and target remain exactly:

    Gamma_11, multiplier degree 4 (d=2), c=25,
    all 56 cyclic-interval cuts.

Every induced C5 support U is tight for the arc bound.  Consequently:

F1. If q_S(1_U) > 1, then nu_S(1_U)=0.  Coefficientwise nonnegativity forces
    every coefficient of nu_S whose monomial support is contained in U to be
    zero.

F2. T(1_U)=0.  Positive semidefiniteness forces every parity-block evaluation
    vector v_B(1_U) into the Gram kernel.

The scaffold transports all F2 vectors from all parity blocks to each D22
representative, computes an exact rational row basis and exact rational
orthogonal projector, imposes Q K^T = 0, and maximizes a common margin on the
non-scalar kernel complements.  One-dimensional Gram blocks retain only their
existing nonnegativity constraints, matching the conservative convention in
round7/Q4_face.py: a scalar block may legitimately vanish without refuting
attainment.

Default execution is build-only.  A later authorized run may pass --solve.
Any floating result remains steering evidence until rational reconstruction
and independent exact verification.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np
import sympy as sy


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROUND7 = HERE.parent / "round7"
sys.path.insert(0, str(ROUND7))

from Q4_graphs import induced_C5s  # noqa: E402


def load_builder():
    spec = importlib.util.spec_from_file_location("codex_r10_d22_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the D22 constructor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def support_inside(exponent: tuple[int, ...], vertices: set[int]) -> bool:
    return all(power == 0 or vertex in vertices for vertex, power in enumerate(exponent))


def exact_row_basis(rows: list[tuple[int, ...]], width: int) -> list[list[Fraction]]:
    """Return an exact rational RREF basis for the span of integer rows."""
    unique = sorted(set(rows))
    if not unique:
        return []
    matrix = sy.Matrix(unique)
    reduced, _pivots = matrix.rref()
    basis = []
    for row in range(reduced.rows):
        values = [
            Fraction(int(value.p), int(value.q))
            for value in reduced.row(row)
        ]
        if any(values):
            basis.append(values)
    if any(len(row) != width for row in basis):
        raise AssertionError("kernel row width mismatch")
    return basis


def exact_projector(kernel: list[list[Fraction]], order: int) -> list[list[Fraction]]:
    """Orthogonal projector onto the complement of the exact kernel rowspace."""
    if not kernel:
        return [
            [Fraction(int(i == j), 1) for j in range(order)]
            for i in range(order)
        ]
    K = sy.Matrix(
        [[sy.Rational(value.numerator, value.denominator) for value in row] for row in kernel]
    )
    gram = K * K.T
    if gram.det() == 0:
        raise AssertionError("kernel basis is not independent")
    projector = sy.eye(order) - K.T * gram.inv() * K
    return [
        [
            Fraction(int(projector[i, j].p), int(projector[i, j].q))
            for j in range(order)
        ]
        for i in range(order)
    ]


@dataclass
class FaceOrbitData:
    kernel: list[list[Fraction]]
    projector: list[list[Fraction]]


@dataclass
class FaceModel:
    base: object
    cycles: list[tuple[int, ...]]
    forced_zero_multiplier_orbits: list[int]
    orbit_data: list[FaceOrbitData]
    margin: cp.Variable
    problem: cp.Problem


def transported_evaluation_rows(builder, orbit, cycles) -> list[tuple[int, ...]]:
    """All nonzero C5 evaluation vectors transported to a representative block."""
    rows: list[tuple[int, ...]] = []
    for parity_member in orbit.parity_members:
        element = orbit.image_elements[parity_member]
        acted_basis = [
            builder.exponent_image(exponent, element)
            for exponent in orbit.basis
        ]
        for cycle in cycles:
            vertices = set(cycle)
            row = tuple(
                int(support_inside(exponent, vertices))
                for exponent in acted_basis
            )
            if any(row):
                rows.append(row)
    return rows


def forced_multiplier_zeros(base, cycles) -> list[int]:
    forced: set[int] = set()
    for cycle in cycles:
        vertices = set(cycle)
        supported_monomials = [
            index
            for index, monomial in enumerate(base.multiplier_monomials)
            if support_inside(monomial, vertices)
        ]
        for cut_index, (_mask, monochromatic_edges) in enumerate(base.cuts):
            q_value = sum(
                base.edges[edge_index][0] in vertices
                and base.edges[edge_index][1] in vertices
                for edge_index in monochromatic_edges
            )
            if q_value <= 1:
                continue
            forced.update(
                int(base.multiplier_orbit_ids[cut_index, monomial_index])
                for monomial_index in supported_monomials
            )
    return sorted(forced)


def build_face_model() -> FaceModel:
    builder = load_builder()
    base = builder.build_model()
    if len(base.cuts) != 56 or len(base.edges) != 22:
        raise AssertionError("base model is not the fixed Gamma_11 56-cut model")
    cycles = induced_C5s(11, base.edges)
    if len(cycles) != 33:
        raise AssertionError(f"expected 33 induced C5s, got {len(cycles)}")

    # Exact tightness audit for every cycle and every arc cut.
    for cycle in cycles:
        vertices = set(cycle)
        q_values = [
            sum(
                base.edges[edge_index][0] in vertices
                and base.edges[edge_index][1] in vertices
                for edge_index in monochromatic_edges
            )
            for _mask, monochromatic_edges in base.cuts
        ]
        if min(q_values) != 1:
            raise AssertionError(f"induced C5 is not arc-tight: {cycle}")

    forced_zeros = forced_multiplier_zeros(base, cycles)
    constraints = list(base.problem.constraints)
    if forced_zeros:
        constraints.append(base.multiplier_variable[np.asarray(forced_zeros)] == 0)

    margin = cp.Variable(name="face_margin")
    orbit_data: list[FaceOrbitData] = []
    kernel_ranks = []
    complement_orders = []
    maximum_projector_error = 0.0

    for orbit in base.gram_orbits:
        rows = transported_evaluation_rows(builder, orbit, cycles)
        kernel = exact_row_basis(rows, len(orbit.basis))
        projector = exact_projector(kernel, len(orbit.basis))
        orbit_data.append(FaceOrbitData(kernel=kernel, projector=projector))
        kernel_ranks.append(len(kernel))
        complement_order = len(orbit.basis) - len(kernel)
        complement_orders.append(complement_order)

        if kernel:
            kernel_float = np.asarray(
                [[float(value) for value in row] for row in kernel],
                dtype=float,
            )
            constraints.append(orbit.matrix @ kernel_float.T == 0)
        projector_float = np.asarray(
            [[float(value) for value in row] for row in projector],
            dtype=float,
        )

        # Build-only audits of the exact projector after float conversion.
        symmetry_error = float(np.max(np.abs(projector_float - projector_float.T)))
        idempotence_error = float(
            np.max(np.abs(projector_float @ projector_float - projector_float))
        )
        kernel_error = (
            float(np.max(np.abs(projector_float @ kernel_float.T)))
            if kernel
            else 0.0
        )
        maximum_projector_error = max(
            maximum_projector_error,
            symmetry_error,
            idempotence_error,
            kernel_error,
        )

        # As in Q4_face.py, scalar blocks do not constrain the common margin.
        if len(orbit.basis) > 1 and complement_order > 0:
            constraints.append(orbit.matrix - margin * projector_float >> 0)

    if maximum_projector_error > 1e-9:
        raise AssertionError(
            f"rational projector float audit failed: {maximum_projector_error}"
        )
    problem = cp.Problem(cp.Maximize(margin), constraints)
    if not problem.is_dcp():
        raise AssertionError("face-restricted model is not DCP")

    print(
        f"FACE_BUILD graph=Gamma_11 c=25 d=2 cuts={len(base.cuts)} "
        f"cycles={len(cycles)}"
    )
    print(
        f"FACE_F1 forced_zero_multiplier_orbits={len(forced_zeros)}/"
        f"{base.multiplier_variable.size}"
    )
    print(
        f"FACE_F2 representative_blocks={len(base.gram_orbits)} "
        f"kernel_rank_total={sum(kernel_ranks)} "
        f"central_kernel_rank={kernel_ranks[0]} "
        f"complement_order_total={sum(complement_orders)}"
    )
    print(
        f"FACE_PROJECTOR_AUDIT maximum_float_error={maximum_projector_error:.3e} "
        f"margin_psd_blocks={sum(len(orbit.basis) > 1 and complement > 0 for orbit, complement in zip(base.gram_orbits, complement_orders))}"
    )

    return FaceModel(
        base=base,
        cycles=cycles,
        forced_zero_multiplier_orbits=forced_zeros,
        orbit_data=orbit_data,
        margin=margin,
        problem=problem,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--solver", choices=("CLARABEL", "SCS"), default="CLARABEL")
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument("--max-iter", type=int, default=500)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = time.perf_counter()
    face = build_face_model()
    print(f"FACE_BUILD_SECONDS={time.perf_counter() - start:.3f}")
    if not args.solve:
        print("FACE_BUILD_ONLY: no numerical or exact feasibility claim")
        return

    options: dict[str, object] = {
        "solver": args.solver,
        "verbose": args.verbose,
    }
    if args.solver == "CLARABEL":
        options.update(
            tol_gap_abs=args.tol,
            tol_gap_rel=args.tol,
            tol_feas=args.tol,
            max_iter=args.max_iter,
        )
    else:
        options.update(
            eps_abs=args.tol,
            eps_rel=args.tol,
            max_iters=args.max_iter,
        )
    solve_start = time.perf_counter()
    face.problem.solve(**options)
    print(
        f"FACE_SOLVE status={face.problem.status} margin={face.margin.value} "
        f"seconds={time.perf_counter() - solve_start:.3f}"
    )
    print("FLOATING_ONLY: rational reconstruction and independent exact gate required")


if __name__ == "__main__":
    main()
