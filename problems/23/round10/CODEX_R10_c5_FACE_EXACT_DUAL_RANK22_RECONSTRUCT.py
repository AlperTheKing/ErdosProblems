"""Exact rank-22 zero-bound dual from the sealed block-0 pencil.

The exact four-dimensional rank-drop slice is independently rebuilt from the
sealed ten-dimensional lambda/q pencil.  A fixed simple rational combination
is accepted only after exact rank, kernel, PSD, stationarity, normalization,
and zero-objective gates.  This proves a zero upper bound with necessary face
constraints; it does not prove primal feasibility and is not a separator.

Default execution is build-only.  Reconstruction requires three explicit new
output paths.  No conic solver is called and no file is overwritten.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import scipy.sparse as sp
from sympy import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
PENCIL_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
DUAL_NPZ_PATH = (
    HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"
)
VERIFIER_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "row_source": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "pencil": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "dual_npz": "6DFD3A35C8B93144D45479BEE1E00BB72F82797BBF6CC6CA59A7D56E573C1982",
    "verifier": "9366CCD624C32CAC644D9E6DE79F17EA758450893EAE77D935A2AFFE42F72A60",
}
RANK_PRIMES = (1_000_003, 1_000_033, 1_000_037)
SLICE_GENERATORS = (
    (0, 6, 0, 0, -1, 0, 0, 0, 0, 0),
    (0, 0, 0, 12, -4, -2, -3, 0, 4, -8),
    (6, 0, 0, 0, -4, -1, -3, 0, 2, -4),
    (0, 0, 6, 0, -5, -1, -3, 0, 2, -4),
)
RATIONAL_MEMBER = (
    Fraction(-4),
    Fraction(-1),
    Fraction(-1),
    Fraction(3),
)
EXPECTED_SLICE_RANK = 22
EXPECTED_KERNEL_DIMENSION = 132


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def primitive(values: list[int]) -> list[int]:
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor == 0:
        raise ValueError("zero kernel vector")
    output = [int(value) // divisor for value in values]
    first = next(value for value in output if value)
    if first < 0:
        output = [-value for value in output]
    return output


def independent_rows_mod(
    matrix: np.ndarray, prime: int
) -> tuple[list[int], list[int]]:
    rows, columns = matrix.shape
    reduced = np.empty((rows, columns), dtype=np.int64)
    for row in range(rows):
        reduced[row] = [
            int(value) % prime for value in matrix[row]
        ]
    source = np.arange(rows, dtype=np.int32)
    rank = 0
    pivots: list[int] = []
    selected: list[int] = []
    for column in range(columns):
        candidates = np.flatnonzero(reduced[rank:, column])
        if candidates.size == 0:
            continue
        pivot = rank + int(candidates[0])
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
            source[[rank, pivot]] = source[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), prime - 2, prime)
        reduced[rank] = (reduced[rank] * inverse) % prime
        affected = np.flatnonzero(
            reduced[rank + 1 :, column]
        ) + rank + 1
        for start in range(0, len(affected), 128):
            batch = affected[start : start + 128]
            factors = reduced[batch, column].copy()
            reduced[batch] = (
                reduced[batch]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        selected.append(int(source[rank]))
        pivots.append(column)
        rank += 1
        if rank == columns:
            break
    return selected, pivots


def exact_sparse_zero(
    matrix: sp.csr_matrix, vector: list[int]
) -> bool:
    for row in range(matrix.shape[0]):
        total = 0
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            total += (
                int(matrix.data[cursor])
                * vector[int(matrix.indices[cursor])]
            )
        if total:
            return False
    return True


def exact_transpose_product(
    matrix: sp.csr_matrix, vector: list[int]
) -> list[int]:
    output = [0] * matrix.shape[1]
    for row, coefficient in enumerate(vector):
        if coefficient == 0:
            continue
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            output[int(matrix.indices[cursor])] += (
                int(matrix.data[cursor]) * coefficient
            )
    return output


def fraction_json(value: Fraction) -> int | str:
    if value.denominator == 1:
        return int(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def upper_triangle_json(
    matrix: list[list[Fraction]],
) -> list[int | str]:
    return [
        fraction_json(matrix[row][column])
        for row in range(len(matrix))
        for column in range(row, len(matrix))
    ]


def common_integer_matrix(
    matrix: list[list[Fraction]],
) -> tuple[np.ndarray, int]:
    denominator = 1
    for row in matrix:
        for value in row:
            denominator = math.lcm(denominator, value.denominator)
    numerator = np.asarray(
        [
            [
                value.numerator * (denominator // value.denominator)
                for value in row
            ]
            for row in matrix
        ],
        dtype=object,
    )
    divisor = denominator
    for value in numerator.flat:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor > 1:
        numerator = numerator // divisor
        denominator //= divisor
    return numerator, denominator


def rebuild():
    paths = {
        "base": BASE_PATH,
        "row_source": ROW_SOURCE_PATH,
        "blowup": BLOWUP_PATH,
        "pencil": PENCIL_PATH,
        "dual_npz": DUAL_NPZ_PATH,
        "verifier": VERIFIER_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input mismatch: {hashes}")
    builder = load_module("codex_r10_rank22_base", BASE_PATH)
    row_source = load_module("codex_r10_rank22_rows", ROW_SOURCE_PATH)
    verifier = load_module("codex_r10_rank22_verifier", VERIFIER_PATH)
    context = verifier.build_context()
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    sealed = np.load(PENCIL_PATH, allow_pickle=False)
    dual_npz = np.load(DUAL_NPZ_PATH, allow_pickle=False)
    lambda_basis = [
        [int(value) for value in row]
        for row in sealed["lambda_basis_decimal"]
    ]
    q_basis = [
        [int(value) for value in row]
        for row in sealed["block0_q_pencil_decimal"]
    ]
    if len(lambda_basis) != 10 or any(len(row) != 388 for row in lambda_basis):
        raise AssertionError("sealed lambda basis shape mismatch")
    if len(q_basis) != 10 or any(len(row) != 1946 for row in q_basis):
        raise AssertionError("sealed q basis shape mismatch")

    face_map = (context.affine_q @ context.exact_basis).tocsr()
    lambda_constraints = sp.vstack(
        [
            context.affine_nu.T,
            sp.csr_matrix(context.affine_rhs.reshape(1, -1)),
            face_map[:, 582:].T,
        ],
        format="csr",
        dtype=np.int64,
    )
    for index, row in enumerate(lambda_basis):
        if not exact_sparse_zero(lambda_constraints, row):
            raise AssertionError(f"sealed lambda row {index} fails")
        if exact_transpose_product(
            context.affine_q[:, :1946].tocsr(), row
        ) != q_basis[index]:
            raise AssertionError(f"sealed q row {index} fails")

    slice_lambda = [
        [
            sum(
                SLICE_GENERATORS[slice_index][basis_index]
                * lambda_basis[basis_index][coordinate]
                for basis_index in range(10)
            )
            for coordinate in range(388)
        ]
        for slice_index in range(4)
    ]
    slice_q = [
        [
            sum(
                SLICE_GENERATORS[slice_index][basis_index]
                * q_basis[basis_index][coordinate]
                for basis_index in range(10)
            )
            for coordinate in range(1946)
        ]
        for slice_index in range(4)
    ]
    for index, row in enumerate(slice_lambda):
        if not exact_sparse_zero(lambda_constraints, row):
            raise AssertionError(f"slice lambda row {index} fails")
        if exact_transpose_product(
            context.affine_q[:, :1946].tocsr(), row
        ) != slice_q[index]:
            raise AssertionError(f"slice q row {index} fails")

    grouped = []
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        if int(block) == 0:
            grouped.append([int(value) for value in row])
    orbit = base.gram_orbits[0]
    z, z_denominator, _pivots, free = (
        row_source.integer_kernel_parameter(
            grouped, len(orbit.basis)
        )
    )
    if z.shape != (286, 154) or z_denominator != 24 or len(free) != 154:
        raise AssertionError("block-0 quotient parameter mismatch")
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    multiplicity_lcm = math.lcm(*map(int, multiplicities))
    if sorted(set(map(int, multiplicities))) != [11, 22, 44]:
        raise AssertionError("block-0 multiplicity mismatch")
    pencil_denominator = multiplicity_lcm * z_denominator**2

    pencil_numerators: list[np.ndarray] = []
    for q_row in slice_q:
        ambient = [
            [
                q_row[int(ids[row, column])]
                * (
                    multiplicity_lcm
                    // int(multiplicities[int(ids[row, column])])
                )
                for column in range(len(orbit.basis))
            ]
            for row in range(len(orbit.basis))
        ]
        ambient_domain = DomainMatrix.from_list_sympy(
            286, 286, ambient
        ).convert_to(ZZ)
        quotient = z.transpose().matmul(ambient_domain).matmul(z)
        pencil_numerators.append(
            np.asarray(
                [
                    [int(value) for value in row]
                    for row in quotient.to_list()
                ],
                dtype=object,
            )
        )
    stacked = np.vstack(pencil_numerators)
    modular = [
        independent_rows_mod(stacked, prime) for prime in RANK_PRIMES
    ]
    ranks = [len(item[0]) for item in modular]
    if ranks != [EXPECTED_SLICE_RANK] * len(RANK_PRIMES):
        raise AssertionError(f"rank-22 slice ranks drifted: {ranks}")
    selected = stacked[modular[0][0], :]
    kernel_domain = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    common_kernel = [
        primitive([int(value) for value in row])
        for row in kernel_domain.to_list()
    ]
    if len(common_kernel) != EXPECTED_KERNEL_DIMENSION:
        raise AssertionError("rank-22 slice kernel dimension mismatch")
    for matrix in pencil_numerators:
        for vector in common_kernel:
            for row in range(154):
                if sum(
                    int(matrix[row, column]) * vector[column]
                    for column in range(154)
                ):
                    raise AssertionError("exact common-kernel replay failed")

    support_rows = selected
    support_coordinates = modular[0][1]
    if len(support_coordinates) != EXPECTED_SLICE_RANK:
        raise AssertionError("support coordinate count mismatch")
    for prime in RANK_PRIMES:
        minor = support_rows[:, support_coordinates]
        if len(independent_rows_mod(minor, prime)[0]) != EXPECTED_SLICE_RANK:
            raise AssertionError(f"support minor singular modulo {prime}")

    member = [
        [
            sum(
                (
                    RATIONAL_MEMBER[index]
                    * int(pencil_numerators[index][row, column])
                    for index in range(4)
                ),
                Fraction(0),
            )
            / pencil_denominator
            for column in range(154)
        ]
        for row in range(154)
    ]
    reduced = [
        [member[row][column] for column in support_coordinates]
        for row in support_coordinates
    ]
    reduced_rank, reduced_pivots = verifier.exact_psd(
        reduced, "rank-22 reduced dual"
    )
    full_rank, full_pivots = verifier.exact_psd(
        member, "rank-22 full dual"
    )
    if reduced_rank != 22 or full_rank != 22:
        raise AssertionError(
            f"rank-22 member ranks {reduced_rank}/{full_rank}"
        )
    trace = sum(
        (member[index][index] for index in range(154)),
        Fraction(0),
    )
    if trace <= 0:
        raise AssertionError("rank-22 member trace is nonpositive")
    scale = Fraction(2) / trace
    member = [[scale * value for value in row] for row in member]
    lam_unscaled = [
        sum(
            (
                RATIONAL_MEMBER[index] * slice_lambda[index][coordinate]
                for index in range(4)
            ),
            Fraction(0),
        )
        for coordinate in range(388)
    ]
    lam = [scale * value for value in lam_unscaled]
    objective = sum(
        (
            Fraction(int(context.affine_rhs[index])) * lam[index]
            for index in range(388)
        ),
        Fraction(0),
    )
    if objective != 0:
        raise AssertionError(f"exact objective is {objective}")
    if sum(
        (member[index][index] for index in range(154)),
        Fraction(0),
    ) != 2:
        raise AssertionError("scaled trace is not two")

    numerical_lambda = dual_npz[
        "dual_affine_equalities"
    ].astype(np.float64)
    numerical_candidate = np.asarray(
        [float(value) for value in lam]
    )
    numerical_scale = float(
        np.dot(numerical_lambda, numerical_candidate)
        / np.dot(numerical_candidate, numerical_candidate)
    )
    projection_relative = float(
        np.linalg.norm(
            numerical_lambda - numerical_scale * numerical_candidate
        )
        / np.linalg.norm(numerical_lambda)
    )
    return {
        "hashes": hashes,
        "verifier": verifier,
        "context": context,
        "slice_lambda": slice_lambda,
        "slice_q": slice_q,
        "pencil_numerators": pencil_numerators,
        "pencil_denominator": pencil_denominator,
        "ranks": ranks,
        "common_kernel": common_kernel,
        "support_coordinates": support_coordinates,
        "member": member,
        "lam": lam,
        "objective": objective,
        "scale": scale,
        "reduced_pivots": reduced_pivots,
        "full_pivots": full_pivots,
        "projection_relative": projection_relative,
        "multiplicity_lcm": multiplicity_lcm,
        "z_denominator": z_denominator,
    }


def build_candidate(state) -> tuple[dict[str, Any], dict[str, Any]]:
    verifier = state["verifier"]
    context = state["context"]
    psd_payload = []
    for block in context.blocks:
        if block.order <= 1:
            continue
        matrix = (
            state["member"]
            if block.index == 0
            else [
                [Fraction(0) for _ in range(block.order)]
                for _ in range(block.order)
            ]
        )
        psd_payload.append(
            {
                "block": block.index,
                "order": block.order,
                "upper_triangle": upper_triangle_json(matrix),
            }
        )
    candidate = {
        "format": "R10-c5-face-exact-semantic-dual-v1",
        "mode": "zero_bound",
        "pinned_sha256": context.hashes,
        "dual": {
            "affine_equalities": [
                fraction_json(value) for value in state["lam"]
            ],
            "live_nu_minus_margin": [0] * 526,
            "margin_nonnegative": 1,
            "scalar_quotient_duals": [
                {"block": block, "value": 0}
                for block in verifier.EXPECTED_SCALAR_BLOCKS
            ],
            "psd_duals": psd_payload,
        },
    }
    metadata = {
        "classification": "zero_bound_with_necessary_face",
        "exact_dual_objective": "0",
        "separator": False,
        "primal_feasibility_established": False,
        "exposing_face_claim": False,
        "necessary_face_statement": (
            "For every feasible primal, t=0 and the order-154 block-0 "
            "quotient has range contained in this dual's exact "
            "132-dimensional kernel."
        ),
        "fixed_scope": {
            "c": 25,
            "degree": 4,
            "cuts": 56,
            "symmetry": "D22",
        },
        "rank_drop_slice": {
            "generators": [list(row) for row in SLICE_GENERATORS],
            "ranks_mod_primes": state["ranks"],
            "common_kernel_dimension": len(state["common_kernel"]),
            "support_coordinates": state["support_coordinates"],
        },
        "rational_member": {
            "slice_coefficients": [
                str(value) for value in RATIONAL_MEMBER
            ],
            "full_exact_rank": 22,
            "minimum_reduced_LDL_pivot": str(
                min(state["reduced_pivots"])
            ),
            "minimum_full_LDL_pivot": str(min(state["full_pivots"])),
            "trace": "2",
            "margin_dual": "1",
            "scale_from_unscaled_member": str(state["scale"]),
        },
        "numerical_steering": {
            "input_dual_npz_sha256": state["hashes"]["dual_npz"],
            "candidate_ray_projection_relative_residual": (
                state["projection_relative"]
            ),
        },
        "construction": {
            "ambient_kernel_denominator": state["z_denominator"],
            "entry_multiplicity_lcm": state["multiplicity_lcm"],
            "canonical_pencil_denominator": state["pencil_denominator"],
        },
        "claim_boundary": (
            "Exact zero bound and conditional necessary face only; "
            "not a separator and not a primal-feasibility/exposing-face claim."
        ),
    }
    return candidate, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", action="store_true")
    parser.add_argument("--candidate-output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--data-output", type=Path)
    args = parser.parse_args()
    outputs = [
        args.candidate_output, args.metadata_output, args.data_output
    ]
    if args.reconstruct and any(path is None for path in outputs):
        parser.error("--reconstruct requires all three explicit outputs")
    if not args.reconstruct and any(path is not None for path in outputs):
        parser.error("output paths require --reconstruct")
    if args.reconstruct:
        for path in outputs:
            resolved = path.resolve()
            if resolved.exists():
                parser.error(f"refusing to overwrite {resolved}")
            if not resolved.parent.is_dir():
                parser.error(f"missing output directory {resolved.parent}")
        if args.candidate_output.suffix.lower() != ".json":
            parser.error("candidate output must end in .json")
        if args.metadata_output.suffix.lower() != ".json":
            parser.error("metadata output must end in .json")
        if args.data_output.suffix.lower() != ".npz":
            parser.error("data output must end in .npz")
    return args


def main() -> int:
    args = parse_args()
    if not args.reconstruct:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "scope": "build-only; no input processed",
                    "slice_dimension": 4,
                    "expected_rank": 22,
                    "expected_kernel_dimension": 132,
                    "rational_member": [
                        str(value) for value in RATIONAL_MEMBER
                    ],
                    "solver_called": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        print(
            "EXACT_DUAL_RANK22_BUILD_ONLY_PASS "
            "solver_called=false input_processed=false"
        )
        return 0
    state = rebuild()
    candidate, metadata = build_candidate(state)
    member_numerator, member_denominator = common_integer_matrix(
        state["member"]
    )
    maximum_member = max(abs(int(value)) for value in member_numerator.flat)
    if maximum_member >= (1 << 62):
        raise OverflowError("exact member numerator does not fit int64")
    candidate_path = args.candidate_output.resolve()
    metadata_path = args.metadata_output.resolve()
    data_path = args.data_output.resolve()
    candidate_path.write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    metadata["candidate_sha256"] = sha256(candidate_path)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    np.savez_compressed(
        data_path,
        format_version=np.asarray([1], dtype=np.int32),
        role=np.asarray(
            ["exact zero bound with conditional necessary rank-22 face"]
        ),
        candidate_sha256=np.asarray([metadata["candidate_sha256"]]),
        sealed_pencil_sha256=np.asarray([state["hashes"]["pencil"]]),
        rank_primes=np.asarray(RANK_PRIMES, dtype=np.int64),
        slice_ranks=np.asarray(state["ranks"], dtype=np.int32),
        slice_generators=np.asarray(SLICE_GENERATORS, dtype=np.int64),
        slice_lambda_basis=np.asarray(
            state["slice_lambda"], dtype=np.int64
        ),
        slice_q_basis=np.asarray(state["slice_q"], dtype=np.int64),
        common_kernel_decimal=np.asarray(
            [[str(value) for value in row] for row in state["common_kernel"]]
        ),
        support_coordinates=np.asarray(
            state["support_coordinates"], dtype=np.int32
        ),
        rational_member_numerators=np.asarray(
            [value.numerator for value in RATIONAL_MEMBER], dtype=np.int64
        ),
        rational_member_denominators=np.asarray(
            [value.denominator for value in RATIONAL_MEMBER], dtype=np.int64
        ),
        block0_dual_numerator=member_numerator.astype(np.int64),
        block0_dual_denominator=np.asarray(
            [member_denominator], dtype=np.int64
        ),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    print(f"CANDIDATE={candidate_path}")
    print(f"SHA256_CANDIDATE={sha256(candidate_path)}")
    print(f"METADATA={metadata_path}")
    print(f"SHA256_METADATA={sha256(metadata_path)}")
    print(f"DATA={data_path}")
    print(f"SHA256_DATA={sha256(data_path)}")
    print(
        "EXACT_ZERO_BOUND_WITH_NECESSARY_FACE_WRITTEN "
        "separator=false exposing_face=false verification_required=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
