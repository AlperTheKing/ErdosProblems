"""Lossless D22-reduced degree-4 multiplier SDP for the Gamma_11 arc bound.

This implements the registered R10 direct-route experiment at fixed c = 25:

    nu_S(x) has nonnegative coefficients and degree 4,
    sum_S nu_S(x) = 25 (sum_i x_i)^4,
    (sum_i x_i)^6 - sum_S nu_S(x) q_S(x) is SOS after x_i = y_i^2.

The cut family consists of all 56 cyclic-interval cuts of Z/11Z, including
the empty interval and intervals of lengths 1,...,5.  Complementary cuts are
identified by putting vertex 0 on the zero side.

The reduction is exact and uses only permutation/orbit identifications:

* one nonnegative scalar for each D22 orbit of
  (arc cut, degree-4 multiplier monomial);
* one PSD matrix for each D22 orbit of target parity masks;
* entries of a representative PSD matrix are identified exactly along the
  stabilizer orbits of unordered basis pairs;
* one normalization equation per degree-4 monomial orbit and one target
  coefficient equation per degree-6 monomial orbit.

Any unrestricted feasible certificate can be averaged over D22, so this
invariant model is lossless.  Conversely, every reduced solution expands by
permutations into the standard Q4 certificate data layout.  The optional
pickle export is deliberately marked NUMERICAL_ONLY: acceptance still
requires rational reconstruction followed by the independent exact Q4 gate.

Examples
--------
Build and audit the reduced cone without solving:

    python CODEX_R10_g11_d22_sdp.py

Solve with Clarabel and export a numerical warm start:

    python CODEX_R10_g11_d22_sdp.py --solve --solver CLARABEL
"""

from __future__ import annotations

import argparse
import pickle
import sys
import time
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import cvxpy as cp
import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
ROUND7 = HERE.parent / "round7"
sys.path.insert(0, str(ROUND7))

from Q4_graphs import all_cuts, gamma_graph  # noqa: E402
from Q4_sos import monomials, multinom, parity_blocks  # noqa: E402


N = 11
D = 4
DT = 6
C_FIXED = 25
GroupElement = tuple[int, int]  # (sign, translation): i -> sign*i + translation
Exponent = tuple[int, ...]


def group_elements() -> tuple[GroupElement, ...]:
    """The 22 affine permutations of the dihedral group on Z/11Z."""
    return tuple((sign, shift) for sign in (1, -1) for shift in range(N))


GROUP = group_elements()


def vertex_image(vertex: int, element: GroupElement) -> int:
    sign, shift = element
    return (sign * vertex + shift) % N


def exponent_image(exponent: Exponent, element: GroupElement) -> Exponent:
    out = [0] * N
    for vertex, power in enumerate(exponent):
        out[vertex_image(vertex, element)] = power
    return tuple(out)


def side_from_mask(mask: int) -> frozenset[int]:
    """Decode the canonical Q4 cut mask (vertex 0 is always on side zero)."""
    return frozenset(vertex for vertex in range(1, N) if (mask >> (vertex - 1)) & 1)


def canonical_mask(side: Iterable[int]) -> int:
    """Canonicalize a cut modulo complementation and return its Q4 mask."""
    side = frozenset(side)
    if 0 in side:
        side = frozenset(range(N)) - side
    return sum(1 << (vertex - 1) for vertex in side)


def cyclic_interval_cuts(edges: list[tuple[int, int]]) -> list[tuple[int, frozenset[int]]]:
    """Return exactly the 56 cuts represented by intervals of lengths 0,...,5."""
    all_by_mask = {mask: (mask, mono) for mask, mono in all_cuts(N, edges)}
    masks = {canonical_mask(())}
    for length in range(1, 6):
        for start in range(N):
            interval = {(start + offset) % N for offset in range(length)}
            masks.add(canonical_mask(interval))
    assert len(masks) == 56, f"expected 56 interval cuts, got {len(masks)}"
    return [all_by_mask[mask] for mask in sorted(masks)]


def action_table(objects: list[Exponent]) -> tuple[np.ndarray, dict[Exponent, int]]:
    """Return the D22 action table on a permutation-closed exponent list."""
    index = {item: i for i, item in enumerate(objects)}
    table = np.empty((len(GROUP), len(objects)), dtype=np.int32)
    for gi, element in enumerate(GROUP):
        for i, item in enumerate(objects):
            table[gi, i] = index[exponent_image(item, element)]
    return table, index


def orbit_ids(action: np.ndarray) -> tuple[np.ndarray, list[int], list[list[int]]]:
    """Orbit IDs and canonical representatives for a finite group action table."""
    count = action.shape[1]
    ids = np.full(count, -1, dtype=np.int32)
    representatives: list[int] = []
    members: list[list[int]] = []
    for seed in range(count):
        if ids[seed] >= 0:
            continue
        orbit = sorted(set(int(action[gi, seed]) for gi in range(action.shape[0])))
        oid = len(representatives)
        representatives.append(min(orbit))
        members.append(orbit)
        for item in orbit:
            if ids[item] not in (-1, oid):
                raise AssertionError("overlapping group orbits")
            ids[item] = oid
    assert np.all(ids >= 0)
    return ids, representatives, members


def cut_action_table(cuts: list[tuple[int, frozenset[int]]]) -> np.ndarray:
    index = {mask: i for i, (mask, _mono) in enumerate(cuts)}
    table = np.empty((len(GROUP), len(cuts)), dtype=np.int32)
    for gi, element in enumerate(GROUP):
        for cut_index, (mask, _mono) in enumerate(cuts):
            image = {vertex_image(vertex, element) for vertex in side_from_mask(mask)}
            image_mask = canonical_mask(image)
            if image_mask not in index:
                raise AssertionError("cyclic-interval cut family is not D22-closed")
            table[gi, cut_index] = index[image_mask]
    return table


def pair_orbit_ids(cut_action: np.ndarray, monomial_action: np.ndarray) -> tuple[np.ndarray, int]:
    """D22 orbit ID for every (cut, multiplier monomial) pair."""
    number_cuts = cut_action.shape[1]
    number_monomials = monomial_action.shape[1]
    ids = np.full((number_cuts, number_monomials), -1, dtype=np.int32)
    number_orbits = 0
    for cut_index in range(number_cuts):
        for monomial_index in range(number_monomials):
            if ids[cut_index, monomial_index] >= 0:
                continue
            orbit = {
                (
                    int(cut_action[gi, cut_index]),
                    int(monomial_action[gi, monomial_index]),
                )
                for gi in range(len(GROUP))
            }
            for image_cut, image_monomial in orbit:
                old = int(ids[image_cut, image_monomial])
                if old not in (-1, number_orbits):
                    raise AssertionError("overlapping pair orbits")
                ids[image_cut, image_monomial] = number_orbits
            number_orbits += 1
    assert np.all(ids >= 0)
    return ids, number_orbits


def parity(exponent: Exponent) -> Exponent:
    return tuple(power & 1 for power in exponent)


def image_permutation(
    basis: list[Exponent], target_basis: list[Exponent], element: GroupElement
) -> np.ndarray:
    """Map representative basis indices to target-basis indices."""
    target_index = {item: i for i, item in enumerate(target_basis)}
    return np.array(
        [target_index[exponent_image(item, element)] for item in basis],
        dtype=np.int32,
    )


def unordered_entry_orbits(
    basis: list[Exponent], stabilizer: list[GroupElement]
) -> tuple[np.ndarray, int]:
    """Tie symmetric matrix entries along stabilizer orbits."""
    size = len(basis)
    basis_index = {item: i for i, item in enumerate(basis)}
    permutations = []
    for element in stabilizer:
        permutations.append(
            np.array(
                [basis_index[exponent_image(item, element)] for item in basis],
                dtype=np.int32,
            )
        )
    ids = np.full((size, size), -1, dtype=np.int32)
    number_orbits = 0
    for i in range(size):
        for j in range(i, size):
            if ids[i, j] >= 0:
                continue
            orbit = {
                tuple(sorted((int(permutation[i]), int(permutation[j]))))
                for permutation in permutations
            }
            for row, column in orbit:
                old = int(ids[row, column])
                if old not in (-1, number_orbits):
                    raise AssertionError("overlapping Gram-entry orbits")
                ids[row, column] = ids[column, row] = number_orbits
            number_orbits += 1
    assert np.all(ids >= 0)
    return ids, number_orbits


@dataclass
class GramOrbit:
    parity_rep: Exponent
    parity_members: list[Exponent]
    image_elements: dict[Exponent, GroupElement]
    basis: list[Exponent]
    stabilizer: list[GroupElement]
    entry_ids: np.ndarray
    variable: cp.Variable
    matrix: cp.Expression
    coefficient_map: sp.csr_matrix


@dataclass
class ReducedModel:
    edges: list[tuple[int, int]]
    cuts: list[tuple[int, frozenset[int]]]
    multiplier_monomials: list[Exponent]
    target_monomials: list[Exponent]
    multiplier_orbit_ids: np.ndarray
    multiplier_variable: cp.Variable
    multiplier_normalization: sp.csr_matrix
    multiplier_target: sp.csr_matrix
    gram_orbits: list[GramOrbit]
    parity_blocks_by_mask: dict[Exponent, list[Exponent]]
    target_representatives: list[int]
    problem: cp.Problem


def build_model() -> ReducedModel:
    n, edges = gamma_graph(N)
    assert n == N
    edge_set = {tuple(sorted(edge)) for edge in edges}
    for element in GROUP:
        image_edges = {
            tuple(sorted((vertex_image(u, element), vertex_image(v, element))))
            for u, v in edges
        }
        assert image_edges == edge_set, "D22 element is not a Gamma_11 automorphism"

    cuts = cyclic_interval_cuts(edges)
    cut_action = cut_action_table(cuts)

    multiplier_monomials = monomials(N, D)
    target_monomials = monomials(N, DT)
    multiplier_action, multiplier_index = action_table(multiplier_monomials)
    target_action, target_index = action_table(target_monomials)

    multiplier_ids, number_multiplier_orbits = pair_orbit_ids(cut_action, multiplier_action)
    multiplier_variable = cp.Variable(number_multiplier_orbits, nonneg=True, name="nu_orbit")

    multiplier_monomial_orbit_ids, multiplier_reps, _ = orbit_ids(multiplier_action)
    target_orbit_ids, target_reps, target_members = orbit_ids(target_action)
    del multiplier_monomial_orbit_ids, target_orbit_ids

    # One normalization equation per degree-4 monomial orbit.
    norm_rows: list[int] = []
    norm_cols: list[int] = []
    norm_values: list[int] = []
    norm_rhs = []
    for row, monomial_index in enumerate(multiplier_reps):
        for cut_index in range(len(cuts)):
            norm_rows.append(row)
            norm_cols.append(int(multiplier_ids[cut_index, monomial_index]))
            norm_values.append(1)
        norm_rhs.append(C_FIXED * multinom(multiplier_monomials[monomial_index]))
    normalization = sp.csr_matrix(
        (norm_values, (norm_rows, norm_cols)),
        shape=(len(multiplier_reps), number_multiplier_orbits),
        dtype=float,
    )

    # Multiplier contribution to one target coefficient per degree-6 orbit.
    target_rep_to_row = {target_monomials[index]: row for row, index in enumerate(target_reps)}
    target_rows: list[int] = []
    target_cols: list[int] = []
    target_values: list[int] = []
    for row, target_monomial_index in enumerate(target_reps):
        alpha = target_monomials[target_monomial_index]
        counts: Counter[int] = Counter()
        for cut_index, (_mask, monochromatic_edges) in enumerate(cuts):
            for edge_index in monochromatic_edges:
                u, v = edges[edge_index]
                if alpha[u] == 0 or alpha[v] == 0:
                    continue
                beta = list(alpha)
                beta[u] -= 1
                beta[v] -= 1
                monomial_index = multiplier_index[tuple(beta)]
                counts[int(multiplier_ids[cut_index, monomial_index])] += 1
        for orbit_id, value in counts.items():
            target_rows.append(row)
            target_cols.append(orbit_id)
            target_values.append(value)
    multiplier_target = sp.csr_matrix(
        (target_values, (target_rows, target_cols)),
        shape=(len(target_reps), number_multiplier_orbits),
        dtype=float,
    )

    # Target parity blocks and their D22 orbits.
    blocks = parity_blocks(N, DT)
    parity_blocks_by_mask = {parity(block[0]): block for block in blocks}
    parity_masks = sorted(parity_blocks_by_mask)
    parity_index = {mask: i for i, mask in enumerate(parity_masks)}
    parity_action = np.empty((len(GROUP), len(parity_masks)), dtype=np.int32)
    for gi, element in enumerate(GROUP):
        for pi, mask in enumerate(parity_masks):
            parity_action[gi, pi] = parity_index[exponent_image(mask, element)]
    _parity_ids, parity_reps, parity_members_by_id = orbit_ids(parity_action)

    constraints: list[cp.Constraint] = [
        normalization @ multiplier_variable == np.asarray(norm_rhs, dtype=float)
    ]
    gram_orbits: list[GramOrbit] = []
    gram_expression: cp.Expression | int = 0

    for parity_orbit_id, parity_rep_index in enumerate(parity_reps):
        parity_rep = parity_masks[parity_rep_index]
        parity_members = [parity_masks[index] for index in parity_members_by_id[parity_orbit_id]]
        basis = parity_blocks_by_mask[parity_rep]
        stabilizer = [
            element for element in GROUP if exponent_image(parity_rep, element) == parity_rep
        ]
        image_elements: dict[Exponent, GroupElement] = {}
        for member in parity_members:
            image_elements[member] = next(
                element for element in GROUP if exponent_image(parity_rep, element) == member
            )

        entry_ids, number_entry_orbits = unordered_entry_orbits(basis, stabilizer)
        variable = cp.Variable(number_entry_orbits, name=f"Qorbit_{parity_orbit_id}")
        size = len(basis)
        assignment = sp.csr_matrix(
            (
                np.ones(size * size),
                (
                    np.arange(size * size),
                    entry_ids.reshape(-1),
                ),
            ),
            shape=(size * size, number_entry_orbits),
        )
        matrix = cp.reshape(assignment @ variable, (size, size), order="C")
        if size == 1:
            constraints.append(matrix[0, 0] >= 0)
        else:
            constraints.append(matrix >> 0)

        gram_counts: Counter[tuple[int, int]] = Counter()
        for member in parity_members:
            element = image_elements[member]
            acted_basis = [exponent_image(item, element) for item in basis]
            assert set(acted_basis) == set(parity_blocks_by_mask[member])
            for i, left in enumerate(acted_basis):
                for j, right in enumerate(acted_basis):
                    alpha = tuple((a + b) // 2 for a, b in zip(left, right))
                    row = target_rep_to_row.get(alpha)
                    if row is not None:
                        gram_counts[(row, int(entry_ids[i, j]))] += 1
        gram_rows = [key[0] for key in gram_counts]
        gram_cols = [key[1] for key in gram_counts]
        gram_values = [gram_counts[key] for key in gram_counts]
        coefficient_map = sp.csr_matrix(
            (gram_values, (gram_rows, gram_cols)),
            shape=(len(target_reps), number_entry_orbits),
            dtype=float,
        )
        gram_expression = gram_expression + coefficient_map @ variable
        gram_orbits.append(
            GramOrbit(
                parity_rep=parity_rep,
                parity_members=parity_members,
                image_elements=image_elements,
                basis=basis,
                stabilizer=stabilizer,
                entry_ids=entry_ids,
                variable=variable,
                matrix=matrix,
                coefficient_map=coefficient_map,
            )
        )

    target_rhs = np.asarray(
        [multinom(target_monomials[index]) for index in target_reps],
        dtype=float,
    )
    constraints.append(multiplier_target @ multiplier_variable + gram_expression == target_rhs)
    problem = cp.Problem(cp.Minimize(0), constraints)

    # Structural checks: the reduced equations must account for every full orbit.
    assert sum(len(orbit) for orbit in target_members) == len(target_monomials)
    assert sum(len(orbit.parity_members) for orbit in gram_orbits) == len(blocks)
    assert len(target_index) == len(target_monomials)

    return ReducedModel(
        edges=edges,
        cuts=cuts,
        multiplier_monomials=multiplier_monomials,
        target_monomials=target_monomials,
        multiplier_orbit_ids=multiplier_ids,
        multiplier_variable=multiplier_variable,
        multiplier_normalization=normalization,
        multiplier_target=multiplier_target,
        gram_orbits=gram_orbits,
        parity_blocks_by_mask=parity_blocks_by_mask,
        target_representatives=target_reps,
        problem=problem,
    )


def print_model_summary(model: ReducedModel, build_seconds: float) -> None:
    parity_summary = Counter(
        (sum(orbit.parity_rep), len(orbit.basis), len(orbit.parity_members))
        for orbit in model.gram_orbits
    )
    gram_scalars = sum(int(orbit.variable.size) for orbit in model.gram_orbits)
    psd_orders = Counter(len(orbit.basis) for orbit in model.gram_orbits)
    print(f"build_seconds={build_seconds:.3f}")
    print(
        f"graph=Gamma_11 vertices={N} edges={len(model.edges)} "
        f"group_order={len(GROUP)} cuts={len(model.cuts)}"
    )
    print(
        f"degree4_monomials={len(model.multiplier_monomials)} "
        f"multiplier_orbit_scalars={model.multiplier_variable.size} "
        f"normalization_orbit_equations={model.multiplier_normalization.shape[0]}"
    )
    print(
        f"degree6_monomials={len(model.target_monomials)} "
        f"target_orbit_equations={len(model.target_representatives)} "
        f"parity_block_orbits={len(model.gram_orbits)} "
        f"gram_orbit_scalars={gram_scalars}"
    )
    print(f"representative_psd_orders={dict(sorted(psd_orders.items(), reverse=True))}")
    print(f"parity_orbit_types={dict(sorted(parity_summary.items()))}")
    print(
        f"normalization_nnz={model.multiplier_normalization.nnz} "
        f"multiplier_target_nnz={model.multiplier_target.nnz} "
        f"gram_target_nnz={sum(orbit.coefficient_map.nnz for orbit in model.gram_orbits)}"
    )


def solve_model(
    model: ReducedModel, solver: str, tolerance: float, max_iterations: int, verbose: bool
) -> float:
    solver = solver.upper()
    installed = set(cp.installed_solvers())
    if solver not in installed:
        raise RuntimeError(f"solver {solver} is not installed; installed={sorted(installed)}")
    options: dict[str, object] = {"solver": solver, "verbose": verbose}
    if solver == "CLARABEL":
        options.update(
            tol_gap_abs=tolerance,
            tol_gap_rel=tolerance,
            tol_feas=tolerance,
            max_iter=max_iterations,
        )
    elif solver == "SCS":
        options.update(
            eps_abs=tolerance,
            eps_rel=tolerance,
            max_iters=max_iterations,
            acceleration_lookback=20,
        )
    start = time.perf_counter()
    model.problem.solve(**options)
    return time.perf_counter() - start


def numerical_diagnostics(model: ReducedModel) -> dict[str, float]:
    nu = np.asarray(model.multiplier_variable.value, dtype=float)
    if nu.ndim != 1 or not np.all(np.isfinite(nu)):
        raise RuntimeError("solver returned no finite multiplier vector")
    norm_rows = model.multiplier_normalization @ nu
    norm_rhs = []
    # The representative order is recoverable from the row values of the exact RHS.
    # Use the CVXPY constraint residual for a solver-independent primary metric.
    norm_residual = float(np.max(np.abs(model.problem.constraints[0].violation())))
    del norm_rows, norm_rhs
    target_residual = float(np.max(np.abs(model.problem.constraints[-1].violation())))
    minimum_nu = float(np.min(nu))
    minimum_eigenvalue = float("inf")
    maximum_stabilizer_error = 0.0
    for orbit in model.gram_orbits:
        matrix = np.asarray(orbit.matrix.value, dtype=float)
        if matrix.shape == (1, 1):
            eigenvalue = float(matrix[0, 0])
        else:
            eigenvalue = float(np.linalg.eigvalsh((matrix + matrix.T) / 2).min())
        minimum_eigenvalue = min(minimum_eigenvalue, eigenvalue)
        basis_index = {item: i for i, item in enumerate(orbit.basis)}
        for element in orbit.stabilizer:
            permutation = [
                basis_index[exponent_image(item, element)] for item in orbit.basis
            ]
            error = float(
                np.max(
                    np.abs(
                        matrix[np.ix_(permutation, permutation)]
                        - matrix
                    )
                )
            )
            maximum_stabilizer_error = max(maximum_stabilizer_error, error)
    return {
        "normalization_max_abs_residual": norm_residual,
        "target_max_abs_residual": target_residual,
        "minimum_multiplier": minimum_nu,
        "minimum_representative_gram_eigenvalue": minimum_eigenvalue,
        "maximum_stabilizer_error": maximum_stabilizer_error,
    }


def expand_numeric(model: ReducedModel, output_path: Path, diagnostics: dict[str, float]) -> None:
    """Expand a reduced floating solution into the standard Q4 pickle layout."""
    nu_orbit = np.asarray(model.multiplier_variable.value, dtype=float)
    nu = {}
    for cut_index in range(len(model.cuts)):
        for monomial_index, monomial in enumerate(model.multiplier_monomials):
            value = float(nu_orbit[model.multiplier_orbit_ids[cut_index, monomial_index]])
            if value != 0.0:
                nu[(cut_index, monomial)] = value

    orbit_by_member: dict[Exponent, GramOrbit] = {}
    for orbit in model.gram_orbits:
        for member in orbit.parity_members:
            orbit_by_member[member] = orbit

    full_qblocks = []
    for block in parity_blocks(N, DT):
        mask = parity(block[0])
        orbit = orbit_by_member[mask]
        representative_matrix = np.asarray(orbit.matrix.value, dtype=float)
        element = orbit.image_elements[mask]
        permutation = image_permutation(orbit.basis, block, element)
        matrix = np.zeros_like(representative_matrix)
        matrix[np.ix_(permutation, permutation)] = representative_matrix
        full_qblocks.append((block, matrix.tolist()))

    payload = {
        "format": "Q4-certificate-layout-numerical-v1",
        "NUMERICAL_ONLY": True,
        "m": 11,
        "d": 2,
        "c": Fraction(25, 1),
        "n": N,
        "E": model.edges,
        "cuts": model.cuts,
        "nu": nu,
        "Q": full_qblocks,
        "reduction": {
            "group": GROUP,
            "multiplier_orbit_scalars": int(model.multiplier_variable.size),
            "gram_orbit_scalars": sum(int(orbit.variable.size) for orbit in model.gram_orbits),
            "parity_block_orbits": len(model.gram_orbits),
        },
        "diagnostics": diagnostics,
        "next_exact_step": (
            "Solve the reduced rational coefficient system on the numerical PSD face, "
            "expand orbit copies, convert every scalar to Fraction, and run Q4_verify.verify "
            "with d=2 before any theorem claim."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve", action="store_true", help="solve the fixed-c feasibility SDP")
    parser.add_argument("--solver", default="CLARABEL", choices=("CLARABEL", "SCS", "SDPA"))
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "CODEX_R10_g11_d22_numeric.pkl",
        help="numerical Q4-layout warm-start pickle",
    )
    parser.add_argument("--no-export", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_start = time.perf_counter()
    model = build_model()
    print_model_summary(model, time.perf_counter() - build_start)
    if not args.solve:
        print("BUILD_ONLY: no numerical feasibility claim")
        return

    print(
        f"SOLVE_START solver={args.solver} tol={args.tol:.3e} "
        f"max_iter={args.max_iter}",
        flush=True,
    )
    solve_seconds = solve_model(
        model,
        solver=args.solver,
        tolerance=args.tol,
        max_iterations=args.max_iter,
        verbose=args.verbose,
    )
    print(
        f"SOLVE_DONE status={model.problem.status} "
        f"solve_seconds={solve_seconds:.3f}",
        flush=True,
    )
    if model.problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        print("NO_EXPORT: floating solve did not return a feasible-status iterate")
        return
    diagnostics = numerical_diagnostics(model)
    for key, value in diagnostics.items():
        print(f"{key}={value:.12e}")
    if args.no_export:
        print("NO_EXPORT: requested by --no-export")
        return
    expand_numeric(model, args.output, diagnostics)
    print(f"NUMERICAL_ONLY_EXPORT={args.output.resolve()}")


if __name__ == "__main__":
    main()
