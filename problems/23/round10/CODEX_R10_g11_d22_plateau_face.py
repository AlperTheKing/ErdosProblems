"""Sparse relative-interior model on the exact Gamma_11 plateau face.

This keeps the registered certificate fixed:

    c = 25, multiplier degree 4, all 56 cyclic-interval cuts,
    and the lossless D22-invariant coefficient system.

Two independently generated exact face artifacts are pinned by SHA-256:

* the q<=50 equality collector artifact supplies the original normalization
  and target coefficient maps;
* the symbolic complete-C5-blowup artifact supplies a sparser integer basis H
  for the same Gram face and exact evaluation-kernel bases.

For a representative Gram block Q, let the rows of U span the forced kernel.
The sparse equations Hq=0 are exactly QU^T=0 inside the invariant entry
coordinates.  Choose pivot columns P of U and free columns C.  Since U[:,P]
is nonsingular, QU^T=0 and symmetry imply

    Q = B Q[C,C] B^T

for a rational full-column-rank B with B[C,:]=I.  Hence Q is PSD if and only
if its principal submatrix Q[C,C] is PSD.  The model therefore replaces the
singular ambient PSD cones by these exact quotient cones and maximizes a
common relative-interior margin.

Any solver output is numerical steering evidence only.  It is not a
certificate until rational reconstruction, expanded exact Q4 verification,
and an independent exact replay all pass.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import cvxpy as cp
import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_DATA_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
BLOWUP_DATA_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DEFAULT_OUTPUT = HERE / "CODEX_R10_g11_d22_plateau_numeric.npz"

EXPECTED_BASE_SHA256 = (
    "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE"
)
EXPECTED_EQUALITY_DATA_SHA256 = (
    "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F"
)
EXPECTED_BLOWUP_DATA_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIME = 2_000_003


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def csr_from_archive(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"],
            archive[f"{name}_indices"],
            archive[f"{name}_indptr"],
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    difference = (left.tocsr() - right.tocsr()).tocsr()
    difference.eliminate_zeros()
    return difference.nnz == 0


def first_pair_representatives(ids: np.ndarray) -> np.ndarray:
    representatives: list[tuple[int, int] | None] = [None] * (
        int(ids.max()) + 1
    )
    for first in range(ids.shape[0]):
        for second in range(ids.shape[1]):
            orbit_id = int(ids[first, second])
            if representatives[orbit_id] is None:
                representatives[orbit_id] = (first, second)
    assert all(item is not None for item in representatives)
    return np.asarray(representatives, dtype=np.int32)


def first_entry_representatives(base) -> np.ndarray:
    output = []
    for orbit_index, orbit in enumerate(base.gram_orbits):
        qdim = int(orbit.variable.size)
        representatives: list[tuple[int, int] | None] = [None] * qdim
        for row in range(orbit.entry_ids.shape[0]):
            for column in range(row, orbit.entry_ids.shape[1]):
                entry_id = int(orbit.entry_ids[row, column])
                if representatives[entry_id] is None:
                    representatives[entry_id] = (row, column)
        assert all(item is not None for item in representatives)
        output.extend(
            (orbit_index, item[0], item[1])
            for item in representatives
            if item is not None
        )
    return np.asarray(output, dtype=np.int32)


def independent_pivot_columns_mod_prime(
    rows: list[tuple[int, ...]], width: int, prime: int = PRIME
) -> list[int]:
    """Return a column pivot set certified by a nonzero minor modulo prime."""
    echelon: dict[int, dict[int, int]] = {}
    for source in rows:
        if len(source) != width:
            raise AssertionError("kernel row has the wrong width")
        row = {
            column: int(value) % prime
            for column, value in enumerate(source)
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            base = echelon.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                echelon[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return sorted(echelon)


def parse_kernel_rows(
    blowup_archive, base, expected_dimensions: np.ndarray
) -> tuple[list[list[tuple[int, ...]]], list[list[int]]]:
    grouped: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for encoded in blowup_archive["kernel_rows_json"]:
        block_index, row = json.loads(str(encoded))
        grouped[int(block_index)].append(tuple(int(value) for value in row))

    rows_by_block: list[list[tuple[int, ...]]] = []
    free_by_block: list[list[int]] = []
    for block_index, orbit in enumerate(base.gram_orbits):
        rows = grouped.get(block_index, [])
        expected = int(expected_dimensions[block_index])
        if len(rows) != expected:
            raise AssertionError(
                f"kernel dimension mismatch in block {block_index}: "
                f"{len(rows)} != {expected}"
            )
        pivots = independent_pivot_columns_mod_prime(rows, len(orbit.basis))
        if len(pivots) != expected:
            raise AssertionError(
                f"kernel rows lose rank modulo {PRIME} in block {block_index}"
            )
        pivot_set = set(pivots)
        free = [
            index for index in range(len(orbit.basis)) if index not in pivot_set
        ]
        rows_by_block.append(rows)
        free_by_block.append(free)
    if sum(len(rows) for rows in rows_by_block) != 402:
        raise AssertionError("expected total evaluation-kernel rank 402")
    return rows_by_block, free_by_block


@dataclass
class PlateauModel:
    builder: object
    base: object
    equality_archive: object
    blowup_archive: object
    forced: np.ndarray
    live: np.ndarray
    gram_vector: cp.Expression
    gram_face: sp.csr_matrix
    kernel_rows: list[list[tuple[int, ...]]]
    free_coordinates: list[list[int]]
    margin: cp.Variable
    problem: cp.Problem


def build_model() -> PlateauModel:
    hashes = {
        "base": sha256(BASE_PATH),
        "equality": sha256(EQUALITY_DATA_PATH),
        "blowup": sha256(BLOWUP_DATA_PATH),
    }
    expected_hashes = {
        "base": EXPECTED_BASE_SHA256,
        "equality": EXPECTED_EQUALITY_DATA_SHA256,
        "blowup": EXPECTED_BLOWUP_DATA_SHA256,
    }
    if hashes != expected_hashes:
        raise AssertionError(f"pinned SHA-256 mismatch: {hashes}")

    builder = load_module("codex_r10_plateau_base", BASE_PATH)
    base = builder.build_model()
    equality = np.load(EQUALITY_DATA_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_DATA_PATH, allow_pickle=False)

    if int(equality["format_version"][0]) != 1:
        raise AssertionError("unsupported equality-face data version")
    if int(equality["q_max"][0]) != 50:
        raise AssertionError("equality-face artifact is not the q<=50 artifact")
    if equality["equality_representatives"].shape != (439, 11):
        raise AssertionError("unexpected equality representative table")

    forced = equality["forced_multiplier_orbits"].astype(np.int32)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    if len(forced) != 2085 or len(live) != 526:
        raise AssertionError("unexpected multiplier face dimensions")
    if not np.array_equal(forced, blowup["forced_multiplier_orbits"]):
        raise AssertionError("finite and symbolic F1 forced sets differ")
    if not np.array_equal(live, blowup["live_multiplier_orbits"]):
        raise AssertionError("finite and symbolic F1 live sets differ")
    if sorted(map(int, np.concatenate((forced, live)))) != list(range(2611)):
        raise AssertionError("forced/live multiplier IDs do not partition 0..2610")

    cut_masks = np.asarray(
        [mask for mask, _monochromatic in base.cuts], dtype=np.int32
    )
    if not np.array_equal(cut_masks, blowup["cut_masks"]):
        raise AssertionError("cut ordering mismatch")
    if not np.array_equal(
        np.asarray(base.multiplier_monomials, dtype=np.int8),
        blowup["multiplier_monomials"],
    ):
        raise AssertionError("multiplier monomial ordering mismatch")
    if not np.array_equal(
        first_pair_representatives(base.multiplier_orbit_ids),
        blowup["multiplier_pair_representatives"],
    ):
        raise AssertionError("multiplier pair-orbit ordering mismatch")

    offsets = equality["gram_offsets"].astype(np.int32)
    qdims = equality["gram_qdims"].astype(np.int32)
    masks = equality["gram_rep_masks"].astype(np.int8)
    if not np.array_equal(offsets, blowup["gram_offsets"]):
        raise AssertionError("Gram offsets differ between artifacts")
    if not np.array_equal(qdims, blowup["gram_qdims"]):
        raise AssertionError("Gram dimensions differ between artifacts")
    if not np.array_equal(masks, blowup["gram_rep_masks"]):
        raise AssertionError("Gram representative masks differ between artifacts")
    if not np.array_equal(
        first_entry_representatives(base),
        blowup["gram_entry_representatives"],
    ):
        raise AssertionError("Gram entry-orbit ordering mismatch")

    running = 0
    for block_index, orbit in enumerate(base.gram_orbits):
        if int(offsets[block_index]) != running:
            raise AssertionError("Gram offset mismatch against base constructor")
        if int(qdims[block_index]) != int(orbit.variable.size):
            raise AssertionError("Gram q-dimension mismatch against base constructor")
        if not np.array_equal(
            masks[block_index], np.asarray(orbit.parity_rep, dtype=np.int8)
        ):
            raise AssertionError("Gram parity representative mismatch")
        running += int(orbit.variable.size)
    if running != 8647:
        raise AssertionError(f"expected 8647 Gram scalars, got {running}")

    normalization_live = csr_from_archive(equality, "normalization_live")
    target_nu_live = csr_from_archive(equality, "target_nu_live")
    target_gram = csr_from_archive(equality, "target_gram")
    if not sparse_equal(
        normalization_live, base.multiplier_normalization[:, live]
    ):
        raise AssertionError("normalization map differs from base constructor")
    if not sparse_equal(target_nu_live, base.multiplier_target[:, live]):
        raise AssertionError("multiplier target map differs from base constructor")
    base_target_gram = sp.hstack(
        [orbit.coefficient_map for orbit in base.gram_orbits], format="csr"
    )
    if not sparse_equal(target_gram, base_target_gram):
        raise AssertionError("Gram target map differs from base constructor")

    gram_face = csr_from_archive(blowup, "gram_face").astype(np.float64)
    if gram_face.shape != (6129, 8647) or gram_face.nnz != 71973:
        raise AssertionError(
            f"unexpected symbolic H shape/nnz: {gram_face.shape}/{gram_face.nnz}"
        )
    if blowup["gram_face_data"].dtype.kind not in "iu":
        raise AssertionError("symbolic H is not integral")

    kernel_rows, free_coordinates = parse_kernel_rows(
        blowup, base, equality["gram_kernel_dims"]
    )
    quotient_orders = Counter(map(len, free_coordinates))
    if quotient_orders != Counter(
        {
            154: 1,
            40: 1,
            35: 1,
            33: 1,
            32: 2,
            11: 1,
            8: 2,
            7: 2,
            6: 7,
            5: 3,
            4: 5,
            1: 16,
            0: 10,
        }
    ):
        raise AssertionError(f"unexpected quotient cone orders {quotient_orders}")

    gram_vector = cp.hstack([orbit.variable for orbit in base.gram_orbits])
    if gram_vector.shape != (8647,):
        raise AssertionError("concatenated Gram vector has the wrong shape")
    margin = cp.Variable(name="relative_margin")

    # The base constraint order is normalization, 52 PSD cones, target.
    if len(base.problem.constraints) != 54:
        raise AssertionError("unexpected base constraint count")
    constraints: list[cp.Constraint] = [
        base.problem.constraints[0],
        base.problem.constraints[-1],
        base.multiplier_variable[forced] == 0,
        gram_face @ gram_vector == 0,
        base.multiplier_variable[live] >= margin,
        margin >= 0,
    ]
    for orbit, free in zip(base.gram_orbits, free_coordinates):
        if not free:
            continue
        principal = orbit.matrix[np.ix_(free, free)]
        if len(free) == 1:
            constraints.append(principal[0, 0] >= margin)
        else:
            constraints.append(principal - margin * np.eye(len(free)) >> 0)

    problem = cp.Problem(cp.Maximize(margin), constraints)
    if not problem.is_dcp():
        raise AssertionError("plateau-face relative-interior model is not DCP")

    print(
        "PLATEAU_FACE_BUILD graph=Gamma_11 c=25 d=2 cuts=56 "
        "nu_orbits=2611 gram_orbits=52"
    )
    print(
        f"PLATEAU_FACE_F1 forced={len(forced)} live={len(live)} "
        f"partition={len(forced) + len(live)}"
    )
    print(
        f"PLATEAU_FACE_F2 shape={gram_face.shape} nnz={gram_face.nnz} "
        f"gram_face_dimension={8647 - gram_face.shape[0]}"
    )
    print(
        "PLATEAU_FACE_QUOTIENT_ORDERS="
        + json.dumps(dict(sorted(quotient_orders.items(), reverse=True)))
    )
    print(
        f"PLATEAU_FACE_HASHES base={hashes['base']} "
        f"equality={hashes['equality']} blowup={hashes['blowup']}"
    )
    print("PLATEAU_FACE_ORDER_AUDIT=passed")
    return PlateauModel(
        builder=builder,
        base=base,
        equality_archive=equality,
        blowup_archive=blowup,
        forced=forced,
        live=live,
        gram_vector=gram_vector,
        gram_face=gram_face,
        kernel_rows=kernel_rows,
        free_coordinates=free_coordinates,
        margin=margin,
        problem=problem,
    )


def diagnostics(model: PlateauModel) -> dict[str, float]:
    nu = np.asarray(model.base.multiplier_variable.value, dtype=float)
    q = np.concatenate(
        [
            np.asarray(orbit.variable.value, dtype=float)
            for orbit in model.base.gram_orbits
        ]
    )
    if not np.all(np.isfinite(nu)) or not np.all(np.isfinite(q)):
        raise RuntimeError("solver returned non-finite variables")

    equality = model.equality_archive
    normalization_live = csr_from_archive(equality, "normalization_live")
    target_nu_live = csr_from_archive(equality, "target_nu_live")
    target_gram = csr_from_archive(equality, "target_gram")
    normalization_residual = np.max(
        np.abs(
            normalization_live @ nu[model.live]
            - equality["normalization_rhs"]
        )
    )
    target_residual = np.max(
        np.abs(
            target_nu_live @ nu[model.live]
            + target_gram @ q
            - equality["target_rhs"]
        )
    )
    face_residual = np.max(np.abs(model.gram_face @ q))
    forced_residual = np.max(np.abs(nu[model.forced]))

    minimum_quotient_eigenvalue = float("inf")
    minimum_full_eigenvalue = float("inf")
    maximum_kernel_residual = 0.0
    for orbit, rows, free in zip(
        model.base.gram_orbits,
        model.kernel_rows,
        model.free_coordinates,
    ):
        matrix = np.asarray(orbit.matrix.value, dtype=float)
        matrix = (matrix + matrix.T) / 2
        minimum_full_eigenvalue = min(
            minimum_full_eigenvalue, float(np.linalg.eigvalsh(matrix).min())
        )
        if free:
            principal = matrix[np.ix_(free, free)]
            minimum_quotient_eigenvalue = min(
                minimum_quotient_eigenvalue,
                float(np.linalg.eigvalsh(principal).min()),
            )
        for row in rows:
            maximum_kernel_residual = max(
                maximum_kernel_residual,
                float(np.max(np.abs(matrix @ np.asarray(row, dtype=float)))),
            )
    return {
        "relative_margin": float(model.margin.value),
        "normalization_max_abs_residual": float(normalization_residual),
        "target_max_abs_residual": float(target_residual),
        "gram_face_max_abs_residual": float(face_residual),
        "forced_multiplier_max_abs": float(forced_residual),
        "minimum_live_multiplier": float(np.min(nu[model.live])),
        "minimum_quotient_gram_eigenvalue": minimum_quotient_eigenvalue,
        "minimum_full_gram_eigenvalue": minimum_full_eigenvalue,
        "maximum_kernel_residual": maximum_kernel_residual,
    }


def save_numeric(
    model: PlateauModel, output_path: Path, result: dict[str, float]
) -> None:
    resolved = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output {resolved}")
    if output_path.suffix.lower() != ".npz":
        raise ValueError("numeric output must have suffix .npz")
    if output_path.parent.resolve() != HERE.resolve():
        raise ValueError("numeric output must be a new file in round10")

    nu = np.asarray(model.base.multiplier_variable.value, dtype=np.float64)
    q = np.concatenate(
        [
            np.asarray(orbit.variable.value, dtype=np.float64)
            for orbit in model.base.gram_orbits
        ]
    )
    np.savez_compressed(
        output_path,
        format_version=np.asarray([1], dtype=np.int32),
        numerical_only=np.asarray([1], dtype=np.int8),
        solver_status=np.asarray([str(model.problem.status)]),
        base_sha256=np.asarray([EXPECTED_BASE_SHA256]),
        equality_data_sha256=np.asarray([EXPECTED_EQUALITY_DATA_SHA256]),
        blowup_data_sha256=np.asarray([EXPECTED_BLOWUP_DATA_SHA256]),
        multiplier_orbit_values=nu,
        gram_orbit_values=q,
        forced_multiplier_orbits=model.forced,
        live_multiplier_orbits=model.live,
        diagnostic_names=np.asarray(list(result)),
        diagnostic_values=np.asarray(list(result.values()), dtype=np.float64),
    )
    print(f"NUMERICAL_ONLY_OUTPUT={resolved}")
    print(f"NUMERICAL_ONLY_OUTPUT_SHA256={sha256(output_path)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--solver", default="CLARABEL", choices=("CLARABEL", "SCS"))
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-export", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = time.perf_counter()
    model = build_model()
    print(f"PLATEAU_FACE_BUILD_SECONDS={time.perf_counter() - start:.3f}")
    if not args.solve:
        print("PLATEAU_FACE_BUILD_ONLY: no solver launched and no file written")
        return

    installed = set(cp.installed_solvers())
    if args.solver not in installed:
        raise RuntimeError(
            f"solver {args.solver} is not installed; installed={sorted(installed)}"
        )
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
            acceleration_lookback=20,
        )

    print(
        f"PLATEAU_FACE_SOLVE_START solver={args.solver} "
        f"tol={args.tol:.3e} max_iter={args.max_iter}",
        flush=True,
    )
    solve_start = time.perf_counter()
    model.problem.solve(**options)
    print(
        f"PLATEAU_FACE_SOLVE_DONE status={model.problem.status} "
        f"seconds={time.perf_counter() - solve_start:.3f}",
        flush=True,
    )
    if model.problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        print("NO_EXPORT: no numerical feasible-status iterate")
        return
    result = diagnostics(model)
    for name, value in result.items():
        print(f"{name}={value:.12e}")
    print("NUMERICAL_ONLY: no certificate or theorem claim")
    if not args.no_export:
        save_numeric(model, args.output, result)


if __name__ == "__main__":
    main()
