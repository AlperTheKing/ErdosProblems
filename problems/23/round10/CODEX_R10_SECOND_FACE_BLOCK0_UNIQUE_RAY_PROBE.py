"""Test whether the numerical rank-22 kernel selects one pencil ray.

No solver is called.  Exact integer pencil generators are reconstructed, then
used in float64 only for this diagnostic.  The 132-dimensional kernel comes
from the stable eigengap of the already-exported block-0 SCS dual matrix.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_pencil() -> tuple[np.ndarray, np.ndarray]:
    helper = load_module(
        "codex_r10_unique_helper",
        "CODEX_R10_ZERO_NU_BLOCK0_PSD_EXPOSURE.py",
    )
    builder = load_module(
        "codex_r10_unique_base", "CODEX_R10_g11_d22_sdp.py"
    )
    row_helpers = load_module(
        "codex_r10_unique_rows", "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
    )
    model = builder.build_model()
    blowup = np.load(helper.BLOWUP_PATH, allow_pickle=False)
    space = np.load(helper.SPACE_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    quotient = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=np.int64,
    )
    if denominator != 24 or quotient.shape != (286, 154):
        raise AssertionError((denominator, quotient.shape, len(free)))
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = int(np.lcm.reduce(multiplicities))
    matrices = []
    for coefficients in q_pencil:
        ambient = (
            coefficients[ids] * (common // multiplicities[ids])
        ).astype(np.int64)
        matrices.append(quotient.T @ (ambient @ quotient))
    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=np.float64,
    )
    normalized_coordinates = space[
        "dual_coordinates_in_row_normalized_basis"
    ].astype(np.float64)
    primitive_coordinates = normalized_coordinates / np.linalg.norm(
        lambda_basis, axis=1
    )
    return np.asarray(matrices), primitive_coordinates


def raw_block0() -> np.ndarray:
    dual = np.load(
        HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz",
        allow_pickle=False,
    )
    position = int(np.flatnonzero(dual["psd_block_indices"] == 0)[0])
    offsets = dual["psd_flat_offsets"].astype(int)
    return dual["dual_psd_matrices_flat"][
        offsets[position] : offsets[position + 1]
    ].reshape((154, 154))


def main() -> None:
    pencil_integer, steering = exact_pencil()
    pencil = pencil_integer.astype(np.float64)
    raw = raw_block0()
    eigenvalues, eigenvectors = np.linalg.eigh((raw + raw.T) / 2)
    kernel = eigenvectors[:, :132]
    columns = np.column_stack(
        [(matrix @ kernel).reshape(-1) for matrix in pencil]
    )
    column_norms = np.linalg.norm(columns, axis=0)
    normalized = columns / column_norms
    _u, singular, vt = np.linalg.svd(normalized, full_matrices=False)
    candidate = vt[-1] / column_norms
    if candidate @ steering < 0:
        candidate = -candidate
    candidate /= np.linalg.norm(candidate)
    steering_unit = steering / np.linalg.norm(steering)
    print(
        "annihilation"
        f" shape={columns.shape}"
        f" singular_values={','.join(f'{value:.12e}' for value in singular)}"
        f" gap_penultimate_over_last={singular[-2] / singular[-1]:.12e}"
        f" candidate_residual={np.linalg.norm(columns @ candidate):.12e}"
    )
    print(
        "ray_comparison"
        f" cosine={candidate @ steering_unit:.15g}"
        f" inf={np.max(np.abs(candidate - steering_unit)):.12e}"
        f" candidate={candidate.tolist()}"
    )

    matrix = np.tensordot(candidate, pencil, axes=(0, 0))
    spectrum = np.linalg.eigvalsh((matrix + matrix.T) / 2)
    scale = max(abs(spectrum[0]), abs(spectrum[-1]))
    print(
        "candidate_spectrum"
        f" min={spectrum[0]:.12e}"
        f" eig_132={spectrum[131]:.12e}"
        f" eig_133={spectrum[132]:.12e}"
        f" max={spectrum[-1]:.12e}"
        f" rank_1e-8={np.sum(np.abs(spectrum) > 1e-8 * scale)}"
    )


if __name__ == "__main__":
    main()
