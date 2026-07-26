"""Measure the coefficient map c -> S(c)K at the exported rank-22 dual."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = load("zero_nu_map_base", "CODEX_R10_g11_d22_sdp.py")
    rows = load(
        "zero_nu_map_rows", "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
    )
    model = builder.build_model()
    blowup = np.load(
        HERE / "CODEX_R10_BLOWUP_FACE_data.npz", allow_pickle=False
    )
    space = np.load(
        HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz",
        allow_pickle=False,
    )
    dual = np.load(
        HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz",
        allow_pickle=False,
    )
    grouped = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, _denominator, _pivots, _free = (
        rows.integer_kernel_parameter(grouped[0], len(orbit.basis))
    )
    quotient = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=float,
    )
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    common = np.lcm.reduce(counts)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    pencil = np.asarray(
        [
            quotient.T
            @ (
                coefficients[ids]
                * (common // counts[ids])
            )
            @ quotient
            for coefficients in q_pencil
        ]
    )

    blocks = dual["psd_block_indices"].astype(np.int32)
    position = int(np.flatnonzero(blocks == 0)[0])
    offsets = dual["psd_flat_offsets"].astype(np.int64)
    numerical = dual["dual_psd_matrices_flat"][
        int(offsets[position]) : int(offsets[position + 1])
    ].reshape(154, 154)
    eigenvalues, eigenvectors = np.linalg.eigh(
        (numerical + numerical.T) / 2.0
    )
    kernel = eigenvectors[:, :132]
    coefficient_map = np.column_stack(
        [(matrix @ kernel).reshape(-1) for matrix in pencil]
    )
    singular_values = np.linalg.svd(
        coefficient_map, compute_uv=False
    )
    _u, _s, vt = np.linalg.svd(
        coefficient_map, full_matrices=False
    )
    candidate = vt[-1]
    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=float,
    )
    exported = (
        space["dual_coordinates_in_row_normalized_basis"]
        / np.linalg.norm(lambda_basis, axis=1)
    )
    candidate *= np.dot(candidate, exported) / np.dot(candidate, candidate)
    relative = float(
        np.linalg.norm(candidate - exported) / np.linalg.norm(exported)
    )
    print(
        "COEFFICIENT_MAP_SINGULAR_VALUES="
        + ",".join(f"{value:.12e}" for value in singular_values)
    )
    print(
        f"relative_candidate_error={relative:.12e}"
        f" sigma9_over_sigma10="
        f"{singular_values[-2]/singular_values[-1]:.12e}"
    )
    print("candidate=" + repr(candidate.tolist()))
    print("exported=" + repr(exported.tolist()))


if __name__ == "__main__":
    main()
