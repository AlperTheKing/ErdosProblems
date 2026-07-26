"""Guarded exact reconstruction of a future reduced-SDP numerical point.

Default execution validates all pinned structural artifacts and prints the
required input schema.  Reconstruction requires ``--run``, an explicit
successful numerical NPZ, an explicit output pickle, and a user-selected
denominator range.

The acceptance path uses exact IEEE-binary Fractions, exact quotient lifting
and Reynolds averaging, the sealed 388-coordinate repair map, direct replay
of H and all 448 affine rows, exact quotient LDL, Q4_verify, and a separate
root-gate process.  No numerical point is bundled and no certificate is
claimed unless every future run-time gate passes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import pickle
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
ROUND7 = HERE.parent / "round7"
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
REPAIR_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP.py"
REPAIR_DATA_PATH = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)
REDUCED_SDP_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
DESIGN_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_RECONSTRUCTION_DESIGN.md"
Q4_VERIFY_PATH = ROUND7 / "Q4_verify.py"
Q4_SOS_PATH = ROUND7 / "Q4_sos.py"
ROOT_GATE_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_ROOT_GATE.py"

EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "row_source": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "row_data": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "repair_source": "97E15D747271552A8F044BEEFA96A2F51D23E162A51F18DF7C7C6DDE04AC14AF",
    "repair_data": "2F82F46A5C740164D47AB74F532C8D7BBED3AE97270894A18BA04D8F78DFF8D2",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "numerical_kernel": "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3",
    "reduced_sdp": "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1",
    "design": "6846D8320E0617CB3A5583041F9B9150CBD304E309E3A83C78CD3DD7753486BC",
    "q4_verify": "42A27DEEC3FFBDADC1DB95BD4759770D8448F88273320DFDC5278814B57D5D57",
    "q4_sos": "1008830AEEEE87BFF0AAD3A9D9859AD403886CE90EE02B06A22A7EE52AD82830",
    "root_gate": "51B86E6CC14AC7436707C379A37AB936AB6304E193E8BC3BA977BCADE6DCB761",
}


class ConeFailure(RuntimeError):
    """A rounded point left the strict relative interior."""


@dataclass
class BlockData:
    index: int
    orbit: object
    q_offset: int
    q_dimension: int
    kernel_rows: list[list[int]]
    z: DomainMatrix
    z_rows: list[list[int]]
    denominator: int
    pivots: list[int]
    free: list[int]
    representatives: list[tuple[int, int]]
    inverse_permutations: list[np.ndarray]


@dataclass
class ReconstructionContext:
    hashes: dict[str, str]
    builder: object
    base: object
    row_data: object
    repair_data: object
    blowup: object
    equality: object
    exact_kernel: object
    numerical_kernel: object
    affine_nu: sp.csr_matrix
    affine_q: sp.csr_matrix
    affine_rhs: list[Fraction]
    h: sp.csr_matrix
    directions: sp.csr_matrix
    repair_matrix: sp.csr_matrix
    repair_domain: DomainMatrix
    selected_nu: np.ndarray
    blocks: list[BlockData]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
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


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.int64,
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    difference = left.astype(np.int64).tocsr() - right.astype(
        np.int64
    ).tocsr()
    difference.eliminate_zeros()
    return difference.shape == left.shape == right.shape and not difference.nnz


def first_pair_representatives(ids: np.ndarray) -> np.ndarray:
    representatives: list[tuple[int, int] | None] = [None] * (
        int(ids.max()) + 1
    )
    for row in range(ids.shape[0]):
        for column in range(ids.shape[1]):
            orbit_id = int(ids[row, column])
            if representatives[orbit_id] is None:
                representatives[orbit_id] = (row, column)
    if any(item is None for item in representatives):
        raise AssertionError("missing multiplier-pair representative")
    return np.asarray(representatives, dtype=np.int32)


def first_entry_representatives(
    entry_ids: np.ndarray,
) -> list[tuple[int, int]]:
    representatives: list[tuple[int, int] | None] = [None] * (
        int(entry_ids.max()) + 1
    )
    for row in range(entry_ids.shape[0]):
        for column in range(row, entry_ids.shape[1]):
            entry_id = int(entry_ids[row, column])
            if representatives[entry_id] is None:
                representatives[entry_id] = (row, column)
    if any(item is None for item in representatives):
        raise AssertionError("missing Gram-entry representative")
    return [item for item in representatives if item is not None]


def inverse_stabilizer_permutations(
    builder, orbit
) -> list[np.ndarray]:
    output = []
    order = len(orbit.basis)
    for element in orbit.stabilizer:
        permutation = builder.image_permutation(
            orbit.basis, orbit.basis, element
        )
        inverse = np.empty_like(permutation)
        inverse[permutation] = np.arange(order, dtype=np.int32)
        output.append(inverse)
    return output


def csr_fraction_matvec(
    matrix: sp.csr_matrix, vector: list[Fraction]
) -> list[Fraction]:
    if matrix.shape[1] != len(vector):
        raise ValueError("exact matrix-vector dimension mismatch")
    output: list[Fraction] = []
    for row in range(matrix.shape[0]):
        total = Fraction(0)
        start = int(matrix.indptr[row])
        stop = int(matrix.indptr[row + 1])
        for column, coefficient in zip(
            matrix.indices[start:stop], matrix.data[start:stop]
        ):
            total += int(coefficient) * vector[int(column)]
        output.append(total)
    return output


def add_vectors(
    left: list[Fraction], right: list[Fraction]
) -> list[Fraction]:
    if len(left) != len(right):
        raise ValueError("vector dimension mismatch")
    return [a + b for a, b in zip(left, right)]


def build_context() -> ReconstructionContext:
    paths = {
        "base": BASE_PATH,
        "row_source": ROW_SOURCE_PATH,
        "row_data": ROW_DATA_PATH,
        "repair_source": REPAIR_SOURCE_PATH,
        "repair_data": REPAIR_DATA_PATH,
        "blowup": BLOWUP_PATH,
        "equality": EQUALITY_PATH,
        "exact_kernel": EXACT_KERNEL_PATH,
        "numerical_kernel": NUMERICAL_KERNEL_PATH,
        "reduced_sdp": REDUCED_SDP_PATH,
        "design": DESIGN_PATH,
        "q4_verify": Q4_VERIFY_PATH,
        "q4_sos": Q4_SOS_PATH,
        "root_gate": ROOT_GATE_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned artifact mismatch: {hashes}")

    row_module = load_module(
        "codex_r10_exact_reconstruction_rows", ROW_SOURCE_PATH
    )
    builder = load_module(
        "codex_r10_exact_reconstruction_base", BASE_PATH
    )
    base = builder.build_model()
    row_data = np.load(ROW_DATA_PATH, allow_pickle=False)
    repair_data = np.load(REPAIR_DATA_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    exact_kernel = np.load(EXACT_KERNEL_PATH, allow_pickle=False)
    numerical_kernel = np.load(NUMERICAL_KERNEL_PATH, allow_pickle=False)

    if not np.array_equal(
        np.asarray([mask for mask, _mono in base.cuts], dtype=np.int32),
        blowup["cut_masks"],
    ):
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
        raise AssertionError("multiplier-pair orbit ordering mismatch")
    cut_action = builder.cut_action_table(base.cuts)
    multiplier_action, _multiplier_index = builder.action_table(
        base.multiplier_monomials
    )
    for group_index in range(len(builder.GROUP)):
        acted_ids = base.multiplier_orbit_ids[
            cut_action[group_index][:, None],
            multiplier_action[group_index][None, :],
        ]
        if not np.array_equal(acted_ids, base.multiplier_orbit_ids):
            raise AssertionError(
                "multiplier orbit expansion is not D22 invariant"
            )

    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    stored_entry_representatives = blowup[
        "gram_entry_representatives"
    ].astype(np.int32)
    rebuilt_entry_representatives = []
    running = 0
    for block, orbit in enumerate(base.gram_orbits):
        if int(q_offsets[block]) != running:
            raise AssertionError("Gram offset mismatch")
        if int(q_dimensions[block]) != int(orbit.variable.size):
            raise AssertionError("Gram dimension mismatch")
        rebuilt_entry_representatives.extend(
            (block, row, column)
            for row, column in first_entry_representatives(orbit.entry_ids)
        )
        for element in orbit.stabilizer:
            permutation = builder.image_permutation(
                orbit.basis, orbit.basis, element
            )
            if not np.array_equal(
                orbit.entry_ids[np.ix_(permutation, permutation)],
                orbit.entry_ids,
            ):
                raise AssertionError(
                    f"Gram block {block} entry IDs are not invariant"
                )
        running += int(orbit.variable.size)
    if running != 8647 or not np.array_equal(
        np.asarray(rebuilt_entry_representatives, dtype=np.int32),
        stored_entry_representatives,
    ):
        raise AssertionError("Gram entry-orbit ordering mismatch")

    forced = equality["forced_multiplier_orbits"].astype(np.int32)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    if (
        len(forced) != 2085
        or len(live) != 526
        or not np.array_equal(forced, blowup["forced_multiplier_orbits"])
        or not np.array_equal(live, blowup["live_multiplier_orbits"])
    ):
        raise AssertionError("multiplier face ordering mismatch")
    if tuple(exact_kernel["exact_basis_shape"]) != (8647, 2518):
        raise AssertionError("sealed exact-Z dimensions mismatch")
    if tuple(numerical_kernel["numerical_basis_shape"]) != (8647, 2518):
        raise AssertionError("sealed numerical-G dimensions mismatch")

    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_q = unpack_csr(row_data, "affine_gram")
    h = unpack_csr(blowup, "gram_face")
    directions = unpack_csr(repair_data, "gram_directions")
    repair_matrix = unpack_csr(repair_data, "repair_matrix")
    selected_nu = repair_data["selected_live_nu_columns"].astype(np.int32)
    if (
        affine_nu.shape != (388, 526)
        or affine_q.shape != (388, 8647)
        or h.shape != (6129, 8647)
        or directions.shape != (8647, 66)
        or repair_matrix.shape != (388, 388)
        or selected_nu.shape != (322,)
    ):
        raise AssertionError("repair-map dimensions mismatch")
    rebuilt_repair = sp.hstack(
        [affine_nu[:, selected_nu], affine_q @ directions],
        format="csr",
    )
    if not sparse_equal(rebuilt_repair, repair_matrix):
        raise AssertionError("repair matrix does not match source maps")
    hd = h @ directions
    hd.eliminate_zeros()
    if hd.nnz:
        raise AssertionError("repair direction leaves exact H-kernel")

    grouped: dict[int, list[list[int]]] = {}
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped.setdefault(int(block), []).append(
            [int(value) for value in row]
        )
    blocks: list[BlockData] = []
    for block, orbit in enumerate(base.gram_orbits):
        kernel_rows = grouped.get(block, [])
        z, denominator, pivots, free = (
            row_module.integer_kernel_parameter(
                kernel_rows, len(orbit.basis)
            )
        )
        blocks.append(
            BlockData(
                index=block,
                orbit=orbit,
                q_offset=int(q_offsets[block]),
                q_dimension=int(q_dimensions[block]),
                kernel_rows=kernel_rows,
                z=z,
                z_rows=[
                    [int(value) for value in row]
                    for row in z.to_list()
                ],
                denominator=int(denominator),
                pivots=list(map(int, pivots)),
                free=list(map(int, free)),
                representatives=first_entry_representatives(
                    orbit.entry_ids
                ),
                inverse_permutations=inverse_stabilizer_permutations(
                    builder, orbit
                ),
            )
        )
    if sum(len(block.kernel_rows) for block in blocks) != 402:
        raise AssertionError("evaluation-kernel rank mismatch")
    repair_domain = DomainMatrix.from_list_sympy(
        388, 388, repair_matrix.toarray().tolist()
    ).convert_to(ZZ)
    return ReconstructionContext(
        hashes=hashes,
        builder=builder,
        base=base,
        row_data=row_data,
        repair_data=repair_data,
        blowup=blowup,
        equality=equality,
        exact_kernel=exact_kernel,
        numerical_kernel=numerical_kernel,
        affine_nu=affine_nu,
        affine_q=affine_q,
        affine_rhs=[
            Fraction(int(value)) for value in row_data["affine_rhs"]
        ],
        h=h,
        directions=directions,
        repair_matrix=repair_matrix,
        repair_domain=repair_domain,
        selected_nu=selected_nu,
        blocks=blocks,
    )


def common_integer_matrix(
    matrix: list[list[Fraction]],
) -> tuple[list[list[int]], int]:
    denominator = 1
    for row in matrix:
        for value in row:
            denominator = math.lcm(denominator, value.denominator)
    numerators = [
        [
            int(value.numerator * (denominator // value.denominator))
            for value in row
        ]
        for row in matrix
    ]
    common = denominator
    for row in numerators:
        for value in row:
            common = math.gcd(common, abs(value))
    if common > 1:
        denominator //= common
        numerators = [
            [value // common for value in row] for row in numerators
        ]
    return numerators, denominator


def exact_lift_matrix(
    block: BlockData, quotient: list[list[Fraction]]
) -> list[list[Fraction]]:
    order = len(block.free)
    if len(quotient) != order or any(
        len(row) != order for row in quotient
    ):
        raise ValueError("quotient matrix shape mismatch")
    numerators, denominator = common_integer_matrix(quotient)
    quotient_domain = DomainMatrix.from_list_sympy(
        order, order, numerators
    ).convert_to(ZZ)
    lifted = block.z.matmul(quotient_domain).matmul(
        block.z.transpose()
    )
    lifted_denominator = denominator * block.denominator**2
    return [
        [
            Fraction(int(value), lifted_denominator)
            for value in row
        ]
        for row in lifted.to_list()
    ]


def lift_reynolds_block(
    block: BlockData, quotient: list[list[Fraction]]
) -> list[Fraction]:
    lifted = exact_lift_matrix(block, quotient)
    stabilizer_order = len(block.inverse_permutations)
    output = []
    for row, column in block.representatives:
        total = sum(
            lifted[int(inverse[row])][int(inverse[column])]
            for inverse in block.inverse_permutations
        )
        output.append(total / stabilizer_order)
    if len(output) != block.q_dimension:
        raise AssertionError("Reynolds output dimension mismatch")
    return output


def lift_reynolds_all(
    context: ReconstructionContext,
    quotients: list[list[list[Fraction]]],
) -> list[Fraction]:
    if len(quotients) != len(context.blocks):
        raise ValueError("quotient block count mismatch")
    q = [Fraction(0)] * 8647
    for block, quotient in zip(context.blocks, quotients):
        local = lift_reynolds_block(block, quotient)
        q[
            block.q_offset : block.q_offset + block.q_dimension
        ] = local
    return q


def binary_quotients_from_q(
    context: ReconstructionContext, q_float: np.ndarray
) -> list[list[list[Fraction]]]:
    if q_float.shape != (8647,) or not np.all(np.isfinite(q_float)):
        raise ValueError("input q_full is not a finite length-8647 vector")
    output = []
    for block in context.blocks:
        local = q_float[
            block.q_offset : block.q_offset + block.q_dimension
        ]
        order = len(block.free)
        quotient = [
            [Fraction(0) for _column in range(order)]
            for _row in range(order)
        ]
        for row in range(order):
            for column in range(row, order):
                left = block.free[row]
                right = block.free[column]
                entry_id = int(block.orbit.entry_ids[left, right])
                reverse_id = int(block.orbit.entry_ids[right, left])
                value = (
                    Fraction.from_float(float(local[entry_id]))
                    + Fraction.from_float(float(local[reverse_id]))
                ) / 2
                quotient[row][column] = value
                quotient[column][row] = value
        output.append(quotient)
    return output


def quotient_matrices_from_exact_q(
    context: ReconstructionContext, q: list[Fraction]
) -> list[list[list[Fraction]]]:
    output = []
    for block in context.blocks:
        local = q[
            block.q_offset : block.q_offset + block.q_dimension
        ]
        output.append(
            [
                [
                    local[
                        int(block.orbit.entry_ids[left, right])
                    ]
                    for right in block.free
                ]
                for left in block.free
            ]
        )
    return output


def round_fraction(
    value: Fraction, denominator: int
) -> Fraction:
    scaled_numerator = value.numerator * denominator
    sign = -1 if scaled_numerator < 0 else 1
    quotient, remainder = divmod(
        abs(scaled_numerator), value.denominator
    )
    twice = 2 * remainder
    if twice > value.denominator or (
        twice == value.denominator and quotient & 1
    ):
        quotient += 1
    return Fraction(sign * quotient, denominator)


def round_quotients(
    quotients: list[list[list[Fraction]]], denominator: int
) -> list[list[list[Fraction]]]:
    output = []
    for source in quotients:
        order = len(source)
        rounded = [
            [Fraction(0) for _column in range(order)]
            for _row in range(order)
        ]
        for row in range(order):
            for column in range(row, order):
                value = round_fraction(
                    (source[row][column] + source[column][row]) / 2,
                    denominator,
                )
                rounded[row][column] = value
                rounded[column][row] = value
        output.append(rounded)
    return output


def solve_repair(
    context: ReconstructionContext, residual: list[Fraction]
) -> tuple[list[Fraction], dict[str, int]]:
    common_denominator = 1
    for value in residual:
        common_denominator = math.lcm(
            common_denominator, value.denominator
        )
    integer_rhs = [
        int(value.numerator * (common_denominator // value.denominator))
        for value in residual
    ]
    rhs_domain = DomainMatrix.from_list_sympy(
        388, 1, [[value] for value in integer_rhs]
    ).convert_to(ZZ)
    numerator, solve_denominator = context.repair_domain.solve_den(
        rhs_domain
    )
    if context.repair_domain.matmul(numerator) != rhs_domain.mul(
        solve_denominator
    ):
        raise AssertionError("fraction-free repair solve failed replay")
    total_denominator = int(solve_denominator) * common_denominator
    values = [
        Fraction(int(row[0]), total_denominator)
        for row in numerator.to_list()
    ]
    return values, {
        "residual_common_denominator_bits": abs(
            common_denominator
        ).bit_length(),
        "solve_denominator_bits": abs(int(solve_denominator)).bit_length(),
        "maximum_delta_numerator_bits": max(
            (abs(value.numerator).bit_length() for value in values),
            default=0,
        ),
        "maximum_delta_denominator_bits": max(
            (value.denominator.bit_length() for value in values),
            default=0,
        ),
    }


def repair_candidate(
    context: ReconstructionContext,
    nu_live: list[Fraction],
    q: list[Fraction],
) -> tuple[list[Fraction], list[Fraction], dict[str, int]]:
    current = add_vectors(
        csr_fraction_matvec(context.affine_nu, nu_live),
        csr_fraction_matvec(context.affine_q, q),
    )
    residual = [
        target - value
        for target, value in zip(context.affine_rhs, current)
    ]
    delta, statistics = solve_repair(context, residual)
    repaired_nu = list(nu_live)
    for coordinate, value in zip(context.selected_nu, delta[:322]):
        repaired_nu[int(coordinate)] += value
    repaired_q = add_vectors(
        q,
        csr_fraction_matvec(context.directions, delta[322:]),
    )
    replay = add_vectors(
        csr_fraction_matvec(context.affine_nu, repaired_nu),
        csr_fraction_matvec(context.affine_q, repaired_q),
    )
    if replay != context.affine_rhs:
        raise AssertionError("repaired 388-row affine system does not replay")
    return repaired_nu, repaired_q, statistics


def exact_ldl_positive_definite(
    matrix: list[list[Fraction]],
) -> tuple[bool, list[Fraction], str]:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        return False, [], "matrix is not square"
    source = [
        [Fraction(matrix[row][column]) for column in range(size)]
        for row in range(size)
    ]
    for row in range(size):
        for column in range(row):
            if source[row][column] != source[column][row]:
                return False, [], "matrix is not symmetric"
    work = [row[:] for row in source]
    permutation = list(range(size))
    lower = [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]
    diagonal = [Fraction(0)] * size
    for step in range(size):
        pivot = max(
            range(step, size), key=lambda index: work[index][index]
        )
        if work[pivot][pivot] <= 0:
            return False, diagonal, f"nonpositive pivot at step {step}"
        if pivot != step:
            work[step], work[pivot] = work[pivot], work[step]
            for row in range(size):
                work[row][step], work[row][pivot] = (
                    work[row][pivot],
                    work[row][step],
                )
            for column in range(step):
                lower[step][column], lower[pivot][column] = (
                    lower[pivot][column],
                    lower[step][column],
                )
            permutation[step], permutation[pivot] = (
                permutation[pivot],
                permutation[step],
            )
        pivot_value = work[step][step]
        diagonal[step] = pivot_value
        for row in range(step + 1, size):
            factor = work[row][step] / pivot_value
            lower[row][step] = factor
            if factor:
                for column in range(step, size):
                    work[row][column] -= factor * work[step][column]
    for row in range(size):
        for column in range(row, size):
            rebuilt = sum(
                lower[row][inner]
                * diagonal[inner]
                * lower[column][inner]
                for inner in range(min(row, column) + 1)
            )
            if rebuilt != source[
                permutation[row]
            ][permutation[column]]:
                raise AssertionError(
                    f"LDL exact reconstruction failed at ({row},{column})"
                )
    return True, diagonal, f"rank {size}"


def exact_candidate_gates(
    context: ReconstructionContext,
    nu_live: list[Fraction],
    q: list[Fraction],
) -> dict[str, object]:
    if len(nu_live) != 526 or len(q) != 8647:
        raise ValueError("candidate dimensions mismatch")
    if any(value <= 0 for value in nu_live):
        raise ConeFailure("a live multiplier is not strictly positive")

    hq = csr_fraction_matvec(context.h, q)
    if any(hq):
        raise AssertionError("exact Hq gate failed")
    retained = add_vectors(
        csr_fraction_matvec(context.affine_nu, nu_live),
        csr_fraction_matvec(context.affine_q, q),
    )
    if retained != context.affine_rhs:
        raise AssertionError("exact retained 388-row gate failed")

    equality = context.equality
    normalization = unpack_csr(equality, "normalization_live")
    target_nu = unpack_csr(equality, "target_nu_live")
    target_q = unpack_csr(equality, "target_gram")
    normalization_values = csr_fraction_matvec(normalization, nu_live)
    normalization_rhs = [
        Fraction(int(value)) for value in equality["normalization_rhs"]
    ]
    target_values = add_vectors(
        csr_fraction_matvec(target_nu, nu_live),
        csr_fraction_matvec(target_q, q),
    )
    target_rhs = [
        Fraction(int(value)) for value in equality["target_rhs"]
    ]
    if normalization_values != normalization_rhs:
        raise AssertionError("one of 56 original normalization rows failed")
    if target_values != target_rhs:
        raise AssertionError("one of 392 original target rows failed")

    minimum_pivot: Fraction | None = None
    for block in context.blocks:
        local = q[
            block.q_offset : block.q_offset + block.q_dimension
        ]
        matrix = [
            [
                local[int(block.orbit.entry_ids[row, column])]
                for column in range(len(block.orbit.basis))
            ]
            for row in range(len(block.orbit.basis))
        ]
        for inverse in block.inverse_permutations:
            for row in range(len(matrix)):
                for column in range(len(matrix)):
                    if matrix[row][column] != matrix[
                        int(inverse[row])
                    ][int(inverse[column])]:
                        raise AssertionError(
                            f"block {block.index}: stabilizer invariance failed"
                        )
        matrix_numerators, _matrix_denominator = (
            common_integer_matrix(matrix)
        )
        matrix_domain = DomainMatrix.from_list_sympy(
            len(matrix), len(matrix), matrix_numerators
        ).convert_to(ZZ)
        if block.kernel_rows:
            kernel_domain = DomainMatrix.from_list_sympy(
                len(block.kernel_rows),
                len(matrix),
                block.kernel_rows,
            ).convert_to(ZZ)
            if matrix_domain.matmul(kernel_domain.transpose()).to_dok():
                raise AssertionError(
                    f"block {block.index}: exact Q U^T gate failed"
                )
        quotient = [
            [matrix[row][column] for column in block.free]
            for row in block.free
        ]
        lifted = exact_lift_matrix(block, quotient)
        if lifted != matrix:
            raise AssertionError(
                f"block {block.index}: Q=B Q[C,C] B^T gate failed"
            )
        if not block.free:
            continue
        positive, diagonal, information = exact_ldl_positive_definite(
            quotient
        )
        if not positive:
            raise ConeFailure(
                f"block {block.index}: quotient is not positive definite: "
                f"{information}"
            )
        block_minimum = min(diagonal)
        minimum_pivot = (
            block_minimum
            if minimum_pivot is None
            else min(minimum_pivot, block_minimum)
        )
    if minimum_pivot is None:
        raise AssertionError("no nonempty quotient blocks")
    return {
        "H_rows_exact": 6129,
        "retained_affine_rows_exact": 388,
        "original_normalization_rows_exact": 56,
        "original_target_rows_exact": 392,
        "minimum_live_multiplier": str(min(nu_live)),
        "minimum_exact_LDL_pivot": str(minimum_pivot),
        "representative_blocks_checked": len(context.blocks),
        "strict_relative_interior": True,
    }


def expand_q4_payload(
    context: ReconstructionContext,
    nu_live: list[Fraction],
    q: list[Fraction],
    reconstruction_metadata: dict[str, object],
) -> dict:
    full_nu = [Fraction(0)] * 2611
    live_ids = context.equality["live_multiplier_orbits"].astype(np.int32)
    for orbit_id, value in zip(live_ids, nu_live):
        full_nu[int(orbit_id)] = value
    forced = context.equality["forced_multiplier_orbits"].astype(np.int32)
    if any(full_nu[int(orbit_id)] for orbit_id in forced):
        raise AssertionError("forced multiplier expansion is nonzero")

    nu = {}
    ids = context.base.multiplier_orbit_ids
    for cut_index in range(len(context.base.cuts)):
        for monomial_index, monomial in enumerate(
            context.base.multiplier_monomials
        ):
            value = full_nu[int(ids[cut_index, monomial_index])]
            if value:
                nu[(cut_index, monomial)] = value

    representative_matrices = {}
    orbit_by_member = {}
    for block in context.blocks:
        local = q[
            block.q_offset : block.q_offset + block.q_dimension
        ]
        representative_matrices[block.index] = [
            [
                local[int(block.orbit.entry_ids[row, column])]
                for column in range(len(block.orbit.basis))
            ]
            for row in range(len(block.orbit.basis))
        ]
        for member in block.orbit.parity_members:
            orbit_by_member[member] = block

    qblocks = []
    for basis in context.builder.parity_blocks(11, 6):
        mask = context.builder.parity(basis[0])
        block = orbit_by_member[mask]
        element = block.orbit.image_elements[mask]
        permutation = context.builder.image_permutation(
            block.orbit.basis, basis, element
        )
        representative = representative_matrices[block.index]
        size = len(basis)
        matrix = [
            [Fraction(0) for _column in range(size)]
            for _row in range(size)
        ]
        for row in range(size):
            for column in range(size):
                matrix[int(permutation[row])][int(permutation[column])] = (
                    representative[row][column]
                )
        qblocks.append((basis, matrix))
    return {
        "format": "Q4-certificate-exact-v1",
        "m": 11,
        "d": 2,
        "c": Fraction(25),
        "n": 11,
        "E": context.base.edges,
        "cuts": context.base.cuts,
        "nu": nu,
        "Q": qblocks,
        "reconstruction": reconstruction_metadata,
    }


def validate_numerical_input(
    context: ReconstructionContext,
    input_path: Path,
    residual_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    archive = np.load(input_path, allow_pickle=False)
    required = {
        "format_version",
        "role",
        "diagnostics_json",
        "solver_metadata_json",
        "relative_margin",
        "forced_multiplier_orbits",
        "live_multiplier_orbits",
        "nu_live",
        "q_full",
        "base_sha256",
        "blowup_sha256",
        "equality_sha256",
        "row_reduction_sha256",
        "exact_kernel_sha256",
        "numerical_kernel_sha256",
    }
    missing = sorted(required - set(archive.files))
    if missing:
        raise ValueError(f"numerical input misses fields: {missing}")
    if archive["format_version"].tolist() != [1]:
        raise ValueError("unsupported numerical input format")
    if archive["role"].tolist() != [
        "numerical steering only; exact replay required"
    ]:
        raise ValueError("input is not marked numerical-only steering data")
    expected_fields = {
        "base_sha256": context.hashes["base"],
        "blowup_sha256": context.hashes["blowup"],
        "equality_sha256": context.hashes["equality"],
        "row_reduction_sha256": context.hashes["row_data"],
        "exact_kernel_sha256": context.hashes["exact_kernel"],
        "numerical_kernel_sha256": context.hashes["numerical_kernel"],
    }
    for field, expected in expected_fields.items():
        if archive[field].tolist() != [expected]:
            raise ValueError(f"numerical input hash mismatch at {field}")
    forced = context.equality["forced_multiplier_orbits"].astype(np.int32)
    live = context.equality["live_multiplier_orbits"].astype(np.int32)
    if not np.array_equal(archive["forced_multiplier_orbits"], forced):
        raise ValueError("input forced multiplier ordering mismatch")
    if not np.array_equal(archive["live_multiplier_orbits"], live):
        raise ValueError("input live multiplier ordering mismatch")

    solver_metadata = json.loads(str(archive["solver_metadata_json"][0]))
    diagnostics = json.loads(str(archive["diagnostics_json"][0]))
    if str(solver_metadata.get("status", "")).lower() not in {
        "optimal",
        "optimal_inaccurate",
    }:
        raise ValueError("input solver status is not successful")
    if diagnostics.get("numerical_strict_feasible") is not True:
        raise ValueError("input is not marked numerically strict feasible")
    nu_live = archive["nu_live"].astype(np.float64)
    q = archive["q_full"].astype(np.float64)
    margin = float(archive["relative_margin"][0])
    if (
        nu_live.shape != (526,)
        or q.shape != (8647,)
        or not np.all(np.isfinite(nu_live))
        or not np.all(np.isfinite(q))
        or not np.isfinite(margin)
        or margin <= 0
        or float(np.min(nu_live)) <= 0
    ):
        raise ValueError("input lacks a finite positive numerical point")
    if "nu_full" in archive.files:
        full = archive["nu_full"].astype(np.float64)
        if (
            full.shape != (2611,)
            or not np.array_equal(full[live], nu_live)
            or np.any(full[forced] != 0)
        ):
            raise ValueError("input full multiplier reconstruction mismatch")

    affine_residual = (
        context.affine_nu.astype(np.float64) @ nu_live
        + context.affine_q.astype(np.float64) @ q
        - np.asarray(context.affine_rhs, dtype=np.float64)
    )
    h_residual = context.h.astype(np.float64) @ q
    maximum_residual = max(
        float(np.max(np.abs(affine_residual))),
        float(np.max(np.abs(h_residual))),
    )
    minimum_quotient_eigenvalue = float("inf")
    for block in context.blocks:
        if not block.free:
            continue
        local = q[
            block.q_offset : block.q_offset + block.q_dimension
        ]
        principal = np.asarray(
            [
                [
                    local[
                        int(block.orbit.entry_ids[left, right])
                    ]
                    for right in block.free
                ]
                for left in block.free
            ],
            dtype=np.float64,
        )
        minimum_quotient_eigenvalue = min(
            minimum_quotient_eigenvalue,
            float(np.linalg.eigvalsh((principal + principal.T) / 2)[0]),
        )
    if (
        maximum_residual > residual_tolerance
        or minimum_quotient_eigenvalue <= 0
    ):
        raise ValueError(
            "input numerical precondition failed: "
            f"residual={maximum_residual}, "
            f"quotient_eigenvalue={minimum_quotient_eigenvalue}"
        )
    return nu_live, q, {
        "input_sha256": sha256(input_path),
        "solver": solver_metadata.get("solver"),
        "solver_status": solver_metadata.get("status"),
        "reported_margin": margin,
        "recomputed_maximum_residual": maximum_residual,
        "recomputed_minimum_quotient_eigenvalue": (
            minimum_quotient_eigenvalue
        ),
    }


def execute_reconstruction(
    context: ReconstructionContext,
    input_path: Path,
    output_path: Path,
    start_exponent: int,
    maximum_exponent: int,
    residual_tolerance: float,
    overwrite: bool,
) -> dict[str, object]:
    if output_path.suffix.lower() != ".pkl":
        raise ValueError("--output must end in .pkl")
    if not output_path.parent.is_dir():
        raise ValueError("output directory does not exist")
    if output_path.exists() and not overwrite:
        raise FileExistsError("refusing to overwrite exact output")
    nu_float, q_float, input_summary = validate_numerical_input(
        context, input_path, residual_tolerance
    )

    nu_binary = [
        Fraction.from_float(float(value)) for value in nu_float
    ]
    binary_quotients = binary_quotients_from_q(context, q_float)
    q_binary = lift_reynolds_all(context, binary_quotients)
    nu_center, q_center, binary_repair = repair_candidate(
        context, nu_binary, q_binary
    )
    binary_gates = exact_candidate_gates(
        context, nu_center, q_center
    )
    centered_quotients = quotient_matrices_from_exact_q(
        context, q_center
    )

    attempts = []
    accepted = None
    for exponent in range(start_exponent, maximum_exponent + 1):
        denominator = 10**exponent
        rounded_nu = [
            round_fraction(value, denominator) for value in nu_center
        ]
        rounded_quotients = round_quotients(
            centered_quotients, denominator
        )
        rounded_q = lift_reynolds_all(context, rounded_quotients)
        candidate_nu, candidate_q, repair_statistics = repair_candidate(
            context, rounded_nu, rounded_q
        )
        try:
            gate_statistics = exact_candidate_gates(
                context, candidate_nu, candidate_q
            )
        except ConeFailure as error:
            attempts.append(
                {
                    "exponent": exponent,
                    "denominator": str(denominator),
                    "status": "RETRY_CONE",
                    "reason": str(error),
                    "repair": repair_statistics,
                }
            )
            continue

        reconstruction_metadata = {
            "scope": (
                "exact certificate for the fixed Gamma_11 c=25 "
                "degree-4 56-cut ansatz only"
            ),
            "input": input_summary,
            "dependency_sha256": context.hashes,
            "binary_repair": binary_repair,
            "binary_center_gates": binary_gates,
            "accepted_decimal_exponent": exponent,
            "accepted_denominator": str(denominator),
            "accepted_repair": repair_statistics,
            "accepted_exact_gates": gate_statistics,
            "rounding": "nearest integer with ties to even",
        }
        payload = expand_q4_payload(
            context,
            candidate_nu,
            candidate_q,
            reconstruction_metadata,
        )
        if str(ROUND7) not in sys.path:
            sys.path.insert(0, str(ROUND7))
        verifier = load_module(
            "codex_r10_future_q4_verify", Q4_VERIFY_PATH
        )
        ok, message = verifier.verify(
            11,
            context.base.edges,
            context.base.cuts,
            2,
            Fraction(25),
            payload["nu"],
            payload["Q"],
            verbose=False,
        )
        if not ok:
            raise AssertionError(f"Q4_verify hard rejection: {message}")
        reconstruction_metadata["Q4_verify"] = "PASS"

        temporary_path = output_path.with_name(
            output_path.name + ".candidate.tmp"
        )
        if temporary_path.exists():
            raise FileExistsError(
                f"stale candidate output exists: {temporary_path}"
            )
        try:
            with temporary_path.open("wb") as handle:
                pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
                handle.flush()
                os.fsync(handle.fileno())
            root_replay = subprocess.run(
                [sys.executable, str(ROOT_GATE_PATH), str(temporary_path)],
                cwd=HERE,
                capture_output=True,
                text=True,
                timeout=7200,
                check=False,
            )
            if root_replay.returncode != 0:
                raise AssertionError(
                    "independent root replay failed:\n"
                    + root_replay.stdout
                    + root_replay.stderr
                )
            reconstruction_metadata["independent_root_gate"] = "PASS"
            # Rewrite metadata after root success, then replay the final bytes.
            with temporary_path.open("wb") as handle:
                pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
                handle.flush()
                os.fsync(handle.fileno())
            final_replay = subprocess.run(
                [sys.executable, str(ROOT_GATE_PATH), str(temporary_path)],
                cwd=HERE,
                capture_output=True,
                text=True,
                timeout=7200,
                check=False,
            )
            if final_replay.returncode != 0:
                raise AssertionError("final-byte root replay failed")
            if output_path.exists() and not overwrite:
                raise FileExistsError("exact output appeared during replay")
            os.replace(temporary_path, output_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
        accepted = {
            "exponent": exponent,
            "denominator": str(denominator),
            "output": str(output_path.resolve()),
            "output_sha256": sha256(output_path),
            "Q4_verify": "PASS",
            "independent_root_gate": "PASS",
            "gate_statistics": gate_statistics,
            "repair": repair_statistics,
        }
        attempts.append(
            {
                "exponent": exponent,
                "denominator": str(denominator),
                "status": "ACCEPT",
            }
        )
        break
    if accepted is None:
        raise ConeFailure(
            "no denominator passed through the requested maximum exponent; "
            "increase --maximum-exponent"
        )
    return {
        "status": "PASS",
        "scope": "fixed Gamma_11 c=25 degree-4 56-cut ansatz",
        "input": input_summary,
        "binary_center": {
            "repair": binary_repair,
            "gates": binary_gates,
        },
        "attempts": attempts,
        "accepted": accepted,
    }


def schema_summary(context: ReconstructionContext) -> dict[str, object]:
    return {
        "status": "READY_BUILD_ONLY",
        "solver_or_reconstruction_run": False,
        "pinned_sha256": context.hashes,
        "required_input": {
            "format_version": [1],
            "role": [
                "numerical steering only; exact replay required"
            ],
            "arrays": {
                "nu_live": [526],
                "q_full": [8647],
                "relative_margin": [1],
                "forced_multiplier_orbits": [2085],
                "live_multiplier_orbits": [526],
            },
            "metadata": [
                "diagnostics_json with numerical_strict_feasible=true",
                "solver_metadata_json with optimal or optimal_inaccurate",
                "base/blowup/equality/row_reduction/exact_kernel/"
                "numerical_kernel SHA-256 fields",
            ],
        },
        "explicit_run_requirements": [
            "--run",
            "--input SUCCESSFUL_POINT.npz",
            "--output EXACT_CERTIFICATE.pkl",
            "--start-exponent K",
            "--maximum-exponent L",
        ],
        "exact_pipeline": [
            "IEEE-binary Fraction centering",
            "exact quotient lift and stabilizer Reynolds average",
            "388x388 fraction-free selected-coordinate repair",
            "exact H and all 448 original affine rows",
            "exact stabilizer/kernel/congruence/strict-LDL gates",
            "monotone decimal denominator refinement",
            "round7 Q4_verify V1-V4",
            "separate exact root replay before atomic output",
        ],
        "dimensions": {
            "live_nu": 526,
            "forced_nu": 2085,
            "q": 8647,
            "H_rows": 6129,
            "retained_affine_rows": 388,
            "original_affine_rows": 448,
            "repair_nu_coordinates": 322,
            "repair_gram_directions": 66,
            "representative_gram_blocks": 52,
        },
        "claim": "No numerical point processed; no certificate claim.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="store_true",
        help="explicitly authorize reconstruction of a supplied successful point",
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--start-exponent", type=int)
    parser.add_argument("--maximum-exponent", type=int)
    parser.add_argument(
        "--residual-tolerance", type=float, default=1e-6
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    run_fields = {
        "--input": args.input,
        "--output": args.output,
        "--start-exponent": args.start_exponent,
        "--maximum-exponent": args.maximum_exponent,
    }
    if args.run:
        missing = [name for name, value in run_fields.items() if value is None]
        if missing:
            parser.error("--run requires " + ", ".join(missing))
        if args.start_exponent < 0:
            parser.error("--start-exponent must be nonnegative")
        if args.maximum_exponent < args.start_exponent:
            parser.error("--maximum-exponent must be >= --start-exponent")
    elif any(value is not None for value in run_fields.values()):
        parser.error(
            "input/output/denominator arguments require explicit --run"
        )
    if args.overwrite and not args.run:
        parser.error("--overwrite requires explicit --run")
    if args.residual_tolerance <= 0:
        parser.error("--residual-tolerance must be positive")
    return args


def main() -> None:
    args = parse_args()
    context = build_context()
    ready = schema_summary(context)
    print(json.dumps(ready, indent=2, sort_keys=True))
    if not args.run:
        print(
            "EXACT_RECONSTRUCTION_READY_BUILD_ONLY: "
            "no numerical point processed"
        )
        return
    result = execute_reconstruction(
        context,
        args.input,
        args.output,
        args.start_exponent,
        args.maximum_exponent,
        args.residual_tolerance,
        args.overwrite,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print(
        "EXACT_RECONSTRUCTION_ACCEPTED: all exact gates passed for "
        "the fixed ansatz"
    )


if __name__ == "__main__":
    main()
