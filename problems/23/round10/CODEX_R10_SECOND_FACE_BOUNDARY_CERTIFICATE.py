"""Build an exact second exposing face for the fixed Gamma_11 SDP cone.

The certificate is the sum of two one-sided derivatives at

    a = (0,0,1,0,1,0,1,0,0,1,1),
    h_1 = e_0-e_4,  h_2 = e_3-e_9.

On all 526 live multiplier orbits, the coefficient of t in

    x^beta * ((sum x)^2 - 25 q_S(x))

sums to zero.  On the sealed C5 Gram face, each derivative is an explicit
sum of nonnegative rank-one Gram evaluations.  Their sum therefore exposes
a further exact Gram face.

This producer writes only new, add-only artifacts and calls no solver.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
EXACT_KERNEL_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
OUTPUT_PATH = HERE / "CODEX_R10_SECOND_FACE_BOUNDARY_CERTIFICATE_data.npz"
SUMMARY_PATH = HERE / "CODEX_R10_SECOND_FACE_BOUNDARY_CERTIFICATE_summary.json"
REPORT_PATH = HERE / "CODEX_R10_SECOND_FACE_BOUNDARY_CERTIFICATE_REPORT.md"

EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
}

POINT = (0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1)
DIRECTIONS = (
    (1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 1, 0, 0, 0, 0, 0, -1, 0),
)


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


def first_coefficient(
    exponent: tuple[int, ...],
    point: tuple[int, ...],
    direction: tuple[int, ...],
) -> int:
    constant = 1
    linear = 0
    for power, value, delta in zip(exponent, point, direction):
        factor_constant = value**power
        factor_linear = (
            power * value ** (power - 1) * delta if power else 0
        )
        linear = linear * factor_constant + constant * factor_linear
        constant *= factor_constant
    return linear


def cut_coefficients(model, point, direction):
    constant = []
    linear = []
    for _mask, monochromatic_edges in model.cuts:
        q0 = 0
        q1 = 0
        for edge_index in monochromatic_edges:
            left, right = model.edges[edge_index]
            q0 += point[left] * point[right]
            q1 += (
                direction[left] * point[right]
                + point[left] * direction[right]
            )
        constant.append(q0)
        linear.append(q1)
    return constant, linear


def multiplier_derivatives(builder, model):
    total_mass = sum(POINT)
    assert total_mass == 5
    normalization = np.zeros(2611, dtype=np.int64)
    target = np.zeros(2611, dtype=np.int64)
    for direction in DIRECTIONS:
        assert sum(direction) == 0
        q0, q1 = cut_coefficients(model, POINT, direction)
        monomial0 = [
            math.prod(value**power for value, power in zip(POINT, exponent))
            for exponent in model.multiplier_monomials
        ]
        monomial1 = [
            first_coefficient(exponent, POINT, direction)
            for exponent in model.multiplier_monomials
        ]
        for cut_index in range(len(model.cuts)):
            for monomial_index in range(len(model.multiplier_monomials)):
                orbit = int(
                    model.multiplier_orbit_ids[cut_index, monomial_index]
                )
                normalization[orbit] += (
                    total_mass * total_mass * monomial1[monomial_index]
                )
                target[orbit] += (
                    q0[cut_index] * monomial1[monomial_index]
                    + q1[cut_index] * monomial0[monomial_index]
                )
    residual = normalization - 25 * target

    multiplier_action, _index = builder.action_table(
        model.multiplier_monomials
    )
    monomial_orbit_ids, monomial_reps, _members = builder.orbit_ids(
        multiplier_action
    )
    del monomial_orbit_ids
    lambda4 = np.zeros(len(monomial_reps), dtype=np.int64)
    for direction in DIRECTIONS:
        coefficients = np.asarray(
            [
                first_coefficient(exponent, POINT, direction)
                for exponent in model.multiplier_monomials
            ],
            dtype=np.int64,
        )
        action_ids, _reps, _members = builder.orbit_ids(multiplier_action)
        lambda4 += np.bincount(
            action_ids,
            weights=coefficients,
            minlength=len(monomial_reps),
        ).astype(np.int64)
    normalization_from_rows = (
        total_mass
        * total_mass
        * np.asarray(lambda4 @ model.multiplier_normalization).reshape(-1)
    ).astype(np.int64)
    if not np.array_equal(normalization, normalization_from_rows):
        raise AssertionError("normalization derivative reconstruction failed")
    normalization_rhs = np.asarray(
        [
            25 * builder.multinom(model.multiplier_monomials[index])
            for index in monomial_reps
        ],
        dtype=np.int64,
    )
    if int(lambda4 @ normalization_rhs) != 0:
        raise AssertionError("normalization derivative RHS is nonzero")
    return normalization, target, residual


def target_functional(builder, model):
    target_action, _index = builder.action_table(model.target_monomials)
    target_ids, target_reps, _members = builder.orbit_ids(target_action)
    if target_reps != model.target_representatives:
        raise AssertionError("target representative ordering mismatch")
    functional = np.zeros(len(target_reps), dtype=np.int64)
    for direction in DIRECTIONS:
        coefficients = np.asarray(
            [
                first_coefficient(exponent, POINT, direction)
                for exponent in model.target_monomials
            ],
            dtype=np.int64,
        )
        functional += np.bincount(
            target_ids,
            weights=coefficients,
            minlength=len(target_reps),
        ).astype(np.int64)
    rhs = np.asarray(
        [
            builder.multinom(model.target_monomials[index])
            for index in target_reps
        ],
        dtype=np.int64,
    )
    if int(functional @ rhs) != 0:
        raise AssertionError("target derivative RHS is nonzero")
    target_gram = sp.hstack(
        [orbit.coefficient_map for orbit in model.gram_orbits],
        format="csr",
    ).astype(np.int64)
    gram_coefficients = np.asarray(functional @ target_gram).reshape(-1)
    target_multiplier = np.asarray(
        functional @ model.multiplier_target
    ).reshape(-1)
    return functional, gram_coefficients.astype(np.int64), target_multiplier.astype(np.int64)


def rank_one_exposure(builder, model):
    rows: list[tuple[int, int, tuple[int, ...]]] = []
    matrices = [
        np.zeros((len(orbit.basis), len(orbit.basis)), dtype=object)
        for orbit in model.gram_orbits
    ]
    for direction in DIRECTIONS:
        entering = next(
            index
            for index, value in enumerate(direction)
            if value > 0 and POINT[index] == 0
        )
        for block, orbit in enumerate(model.gram_orbits):
            for member in orbit.parity_members:
                missing = [
                    vertex
                    for vertex, parity in enumerate(member)
                    if parity and POINT[vertex] == 0
                ]
                if missing != [entering]:
                    continue
                scale = math.prod(
                    POINT[vertex]
                    for vertex, parity in enumerate(member)
                    if parity and vertex != entering
                )
                if scale <= 0:
                    raise AssertionError("nonpositive boundary Gram scale")
                element = orbit.image_elements[member]
                vector = []
                for exponent in orbit.basis:
                    acted = builder.exponent_image(exponent, element)
                    value = 1
                    for vertex in range(11):
                        power = (acted[vertex] - member[vertex]) // 2
                        if power:
                            value *= POINT[vertex] ** power
                    vector.append(value)
                if not any(vector):
                    raise AssertionError("zero rank-one boundary row")
                row = np.asarray(vector, dtype=object)
                matrices[block] += scale * np.outer(row, row)
                rows.append((block, scale, tuple(vector)))

    offsets = []
    coefficients = []
    offset = 0
    for block, (orbit, matrix) in enumerate(
        zip(model.gram_orbits, matrices)
    ):
        qdim = int(orbit.variable.size)
        local = np.zeros(qdim, dtype=object)
        for row in range(len(orbit.basis)):
            for column in range(len(orbit.basis)):
                local[int(orbit.entry_ids[row, column])] += matrix[row, column]
        offsets.append(offset)
        coefficients.extend(int(value) for value in local)
        offset += qdim
    if offset != 8647:
        raise AssertionError("Gram coordinate count mismatch")
    return rows, matrices, np.asarray(coefficients, dtype=np.int64)


def kernel_dimension_update(builder, equality_core, model, blowup, equality, rows):
    grouped_existing: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped_existing[int(block)].append(tuple(map(int, row)))
    grouped_new: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for block, _scale, row in rows:
        grouped_new[block].append(row)

    records = []
    selected_new = []
    for block, orbit in enumerate(model.gram_orbits):
        span = equality_core.ExactRowSpan()
        for row in grouped_existing.get(block, []):
            if not span.add(row):
                raise AssertionError(f"dependent sealed kernel row in block {block}")
        old_kernel_rank = span.rank
        for row in grouped_new.get(block, []):
            if span.add(row):
                selected_new.append((block, row))
        new_kernel_rank = span.rank
        original_dimension, new_face_dimension = (
            equality_core.invariant_face_dimension_fast(
                builder, orbit, span
            )
        )
        old_face_dimension = int(equality["gram_face_dimensions"][block])
        if original_dimension != int(orbit.variable.size):
            raise AssertionError("invariant Gram dimension mismatch")
        if new_face_dimension > old_face_dimension:
            raise AssertionError("second face enlarged a block")
        records.append(
            {
                "block": block,
                "basis_order": len(orbit.basis),
                "old_kernel_rank": old_kernel_rank,
                "new_kernel_rank": new_kernel_rank,
                "added_kernel_rank": new_kernel_rank - old_kernel_rank,
                "old_face_dimension": old_face_dimension,
                "new_face_dimension": new_face_dimension,
                "face_dimension_reduction": (
                    old_face_dimension - new_face_dimension
                ),
                "rank_one_terms": len(grouped_new.get(block, [])),
            }
        )
    return records, selected_new


def main() -> None:
    for path in (OUTPUT_PATH, SUMMARY_PATH, REPORT_PATH):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
    hashes = {
        "base": sha256(BASE_PATH),
        "blowup": sha256(BLOWUP_PATH),
        "equality": sha256(EQUALITY_PATH),
        "exact_kernel": sha256(EXACT_KERNEL_PATH),
    }
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")

    builder = load_module("codex_r10_second_face_certificate_builder", BASE_PATH)
    equality_core = load_module(
        "codex_r10_second_face_certificate_equality_core",
        EQUALITY_SOURCE_PATH,
    )
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    exact_kernel = np.load(EXACT_KERNEL_PATH, allow_pickle=False)
    if not any(
        tuple(map(int, row)) == POINT
        for row in equality["equality_representatives"]
    ):
        raise AssertionError("exposure point is not in the sealed equality set")

    normal, target, residual = multiplier_derivatives(builder, model)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    forced = equality["forced_multiplier_orbits"].astype(np.int32)
    if np.any(residual[live] != 0):
        raise AssertionError("live multiplier cancellation failed")

    target_weights, gram_map, target_from_rows = target_functional(
        builder, model
    )
    if not np.array_equal(target, target_from_rows):
        raise AssertionError("target derivative reconstruction failed")
    rank_rows, matrices, gram_rank_one = rank_one_exposure(builder, model)
    difference = gram_map - gram_rank_one
    exact_basis = sp.csr_matrix(
        (
            exact_kernel["exact_basis_data"].astype(np.int64),
            exact_kernel["exact_basis_indices"].astype(np.int32),
            exact_kernel["exact_basis_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, exact_kernel["exact_basis_shape"])),
        dtype=np.int64,
    )
    face_residual = np.asarray(difference @ exact_basis).reshape(-1)
    if np.any(face_residual):
        raise AssertionError("rank-one Gram derivative mismatch modulo H")
    if not rank_rows or not np.any(gram_rank_one):
        raise AssertionError("zero Gram exposure")

    records, selected_new = kernel_dimension_update(
        builder, equality_core, model, blowup, equality, rank_rows
    )
    added_kernel_rank = sum(row["added_kernel_rank"] for row in records)
    old_face_dimension = sum(row["old_face_dimension"] for row in records)
    new_face_dimension = sum(row["new_face_dimension"] for row in records)
    face_reduction = old_face_dimension - new_face_dimension
    if added_kernel_rank <= 0 or face_reduction <= 0:
        raise AssertionError("exposure does not reduce the sealed face")

    rank_rows_json = np.asarray(
        [
            json.dumps([block, scale, list(row)], separators=(",", ":"))
            for block, scale, row in rank_rows
        ]
    )
    selected_rows_json = np.asarray(
        [
            json.dumps([block, list(row)], separators=(",", ":"))
            for block, row in selected_new
        ]
    )
    per_block_json = np.asarray(
        [json.dumps(record, sort_keys=True) for record in records]
    )
    np.savez_compressed(
        OUTPUT_PATH,
        format_version=np.asarray([1], dtype=np.int32),
        role=np.asarray(
            ["exact second exposing face; no numerical solver evidence"]
        ),
        point=np.asarray(POINT, dtype=np.int16),
        directions=np.asarray(DIRECTIONS, dtype=np.int16),
        live_multiplier_orbits=live,
        forced_multiplier_orbits=forced,
        live_multiplier_residual=residual[live],
        full_multiplier_residual=residual,
        normalization_derivative=normal,
        target_derivative=target,
        target_orbit_functional=target_weights,
        gram_exposure_coefficients=gram_rank_one,
        raw_target_gram_functional=gram_map,
        gram_functional_H_rowspace_difference=difference,
        rank_one_rows_json=rank_rows_json,
        selected_new_kernel_rows_json=selected_rows_json,
        per_block_json=per_block_json,
        added_kernel_rank=np.asarray([added_kernel_rank], dtype=np.int32),
        old_gram_face_dimension=np.asarray(
            [old_face_dimension], dtype=np.int32
        ),
        new_gram_face_dimension=np.asarray(
            [new_face_dimension], dtype=np.int32
        ),
        gram_face_dimension_reduction=np.asarray(
            [face_reduction], dtype=np.int32
        ),
        base_sha256=np.asarray([hashes["base"]]),
        blowup_sha256=np.asarray([hashes["blowup"]]),
        equality_sha256=np.asarray([hashes["equality"]]),
    )
    artifact_hash = sha256(OUTPUT_PATH)
    summary = {
        "status": "PASS",
        "scope": "exact second exposing face; fixed c=25,d=2,56 cuts,D22",
        "point": list(POINT),
        "directions": [list(row) for row in DIRECTIONS],
        "live_multiplier_cancellation": {
            "orbits": len(live),
            "nonzero": int(np.count_nonzero(residual[live])),
        },
        "forced_multiplier_coefficients_ignored_on_first_face": {
            "orbits": len(forced),
            "nonzero": int(np.count_nonzero(residual[forced])),
        },
        "rank_one_terms": len(rank_rows),
        "blocks_with_rank_one_terms": [
            row["block"] for row in records if row["rank_one_terms"]
        ],
        "blocks_with_added_kernel": [
            row["block"] for row in records if row["added_kernel_rank"]
        ],
        "added_kernel_rank": added_kernel_rank,
        "old_gram_face_dimension": old_face_dimension,
        "new_gram_face_dimension": new_face_dimension,
        "gram_face_dimension_reduction": face_reduction,
        "per_block": records,
        "input_sha256": hashes,
        "artifact_sha256": artifact_hash,
        "solver_called": False,
        "implication": (
            "For every feasible PSD tuple on the sealed C5 face, "
            "sum scale*v^T Q_block v=0; hence Q_block*v=0 for every "
            "stored rank-one row."
        ),
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    changed = [row for row in records if row["face_dimension_reduction"]]
    table = "\n".join(
        "| {block} | {basis_order} | {old_kernel_rank} | "
        "{added_kernel_rank} | {old_face_dimension} | "
        "{new_face_dimension} | {face_dimension_reduction} |".format(**row)
        for row in changed
    )
    REPORT_PATH.write_text(
        f"""# Exact second boundary-derivative face

## Exact identity

At

`a = {POINT}`,

sum the one-sided coefficient-of-`t` functionals along

`h1 = {DIRECTIONS[0]}` and `h2 = {DIRECTIONS[1]}`.

Both rays `a+t*h_i` remain nonnegative for sufficiently small `t >= 0`
and preserve `sum(x)=5`.  On all {len(live)} live multiplier orbits, the
coefficient of

`x^beta * ((sum x)^2 - 25*q_S(x))`

cancels exactly.  The {len(forced)} other multiplier orbits are already
exact zeros on the first face.

For a parity block supported at `a`, the constant Gram evaluation vector is
already in the sealed kernel, so its linear term is zero.  A block containing
the entering coordinate has linear term

`scale * v^T Q_block v`, with stored integer `scale > 0`.

Therefore the summed derivative identity is exactly

`sum scale * v^T Q_block v = 0`.

Every term is nonnegative for a feasible PSD tuple.  Hence
`Q_block*v = 0` for every stored rank-one row, exposing a further exact face.

## Dimension reduction

- rank-one terms: {len(rank_rows)}
- added ordinary Gram-kernel rank: {added_kernel_rank}
- old invariant Gram-face dimension: {old_face_dimension}
- new invariant Gram-face dimension: {new_face_dimension}
- exact dimension reduction: {face_reduction}

| block | basis order | old kernel rank | added kernel rank | old face dim | new face dim | reduction |
|---:|---:|---:|---:|---:|---:|---:|
{table}

## Artifact

`{OUTPUT_PATH.name}` stores the exact point, directions, zero live-multiplier
residual, the Gram exposure coefficients, every positive rank-one term, the
independent new kernel rows, and the per-block dimension calculation.

SHA-256: `{artifact_hash}`

No SDP solver was called.  This is an exact facial-reduction identity on the
registered fixed cone; it is not yet the final Q4 certificate.
""",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"OUTPUT={OUTPUT_PATH}")
    print(f"SHA256_OUTPUT={artifact_hash}")
    print("SECOND_FACE_BOUNDARY_CERTIFICATE_PASS solver_called=false")


if __name__ == "__main__":
    main()



