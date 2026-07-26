"""Independent numerical replay of the pinned reduced-SDP dual archive.

This script does not invoke a solver and does not write a certificate.  It
checks archive metadata, raw-versus-semantic cone coordinates, canonical and
semantic stationarity, dual normalization, objective, and cone membership.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
NPZ_PATH = (
    HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"
)
VERIFIER_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py"
MODEL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
EXPECTED_SHA256 = {
    "npz": "6DFD3A35C8B93144D45479BEE1E00BB72F82797BBF6CC6CA59A7D56E573C1982",
    "verifier": "9366CCD624C32CAC644D9E6DE79F17EA758450893EAE77D935A2AFFE42F72A60",
    "model": "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    paths = {
        "npz": NPZ_PATH,
        "verifier": VERIFIER_PATH,
        "model": MODEL_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")
    archive = np.load(NPZ_PATH, allow_pickle=False)
    if archive["format_version"].tolist() != [1]:
        raise AssertionError("dual archive format mismatch")
    if archive["role"].tolist() != [
        "numerical primal-dual steering only; exact replay required"
    ]:
        raise AssertionError("dual archive role mismatch")
    if archive["dual_wrapper_sha256"].tolist() != [
        "B0C4A2EB4D50C21A6DEB1F0D83D1327546793D6B1D9B10DE9E92DABC7E6C168A"
    ]:
        raise AssertionError("dual-export wrapper pin mismatch")

    verifier = load_module("codex_r10_dual_npz_replay_exact", VERIFIER_PATH)
    context = verifier.build_context()
    model_module = load_module("codex_r10_dual_npz_replay_model", MODEL_PATH)
    model = model_module.build_model()

    raw = archive["raw_canonical_y"].astype(np.float64)
    lam = archive["dual_affine_equalities"].astype(np.float64)
    alpha = archive["dual_live_nu_minus_margin"].astype(np.float64)
    beta = float(archive["dual_margin_nonnegative"][0])
    gamma = archive["dual_scalar_quotient_values"].astype(np.float64)
    flat = archive["dual_psd_matrices_flat"].astype(np.float64)
    flat_offsets = archive["psd_flat_offsets"].astype(np.int64)
    svec_offsets = archive["psd_svec_offsets"].astype(np.int64)
    psd_orders = archive["psd_orders"].astype(np.int64)
    if raw.shape != (16369,) or lam.shape != (388,):
        raise AssertionError("raw/equality dual dimension mismatch")
    if alpha.shape != (526,) or gamma.shape != (16,):
        raise AssertionError("nonnegative semantic dual dimension mismatch")
    if flat.shape != (30432,) or psd_orders.shape != (26,):
        raise AssertionError("PSD semantic dual dimension mismatch")

    raw_errors = {
        "equalities": float(np.max(np.abs(raw[:388] - lam))),
        "live_nu": float(np.max(np.abs(raw[388:914] - alpha))),
        "margin": float(abs(raw[914] - beta)),
        "scalar_blocks": float(np.max(np.abs(raw[915:931] - gamma))),
    }
    psd_matrices: list[np.ndarray] = []
    psd_svec_errors: list[float] = []
    for index, order_value in enumerate(psd_orders):
        order = int(order_value)
        matrix = flat[
            int(flat_offsets[index]) : int(flat_offsets[index + 1])
        ].reshape(order, order)
        psd_matrices.append(matrix)
        rows, columns = np.triu_indices(order)
        semantic_svec = matrix[rows, columns].copy()
        semantic_svec[rows != columns] *= np.sqrt(2.0)
        raw_block = raw[
            int(svec_offsets[index]) : int(svec_offsets[index + 1])
        ]
        psd_svec_errors.append(
            float(np.max(np.abs(raw_block - semantic_svec)))
        )
    raw_errors["PSD_svec"] = max(psd_svec_errors)

    cone_adjoint = np.zeros(8647, dtype=np.float64)
    scalar_cursor = 0
    psd_cursor = 0
    for block in context.blocks:
        if block.order == 0:
            continue
        if block.order == 1:
            cone_adjoint[
                block.offset + int(block.entry_ids[0, 0])
            ] += gamma[scalar_cursor]
            scalar_cursor += 1
        else:
            matrix = psd_matrices[psd_cursor]
            for row in range(block.order):
                for column in range(block.order):
                    cone_adjoint[
                        block.offset + int(block.entry_ids[row, column])
                    ] += matrix[row, column]
            psd_cursor += 1
    if scalar_cursor != 16 or psd_cursor != 26:
        raise AssertionError("semantic cone cursor mismatch")

    nu_residual = np.asarray(context.affine_nu.T @ lam).reshape(-1) - alpha
    q_full_residual = (
        np.asarray(context.affine_q.T @ lam).reshape(-1) - cone_adjoint
    )
    q_kernel_residual = np.asarray(
        context.exact_basis.T @ q_full_residual
    ).reshape(-1)
    cone_weight = (
        float(np.sum(alpha))
        + float(np.sum(gamma))
        + sum(float(np.trace(matrix)) for matrix in psd_matrices)
    )
    normalization_residual = cone_weight - beta - 1.0
    semantic_objective = float(context.affine_rhs @ lam)

    data, _chain, _inverse = model.problem.get_problem_data(cp.SCS)
    canonical_a = data["A"]
    canonical_b = np.asarray(data["b"], dtype=np.float64)
    canonical_c = np.asarray(data["c"], dtype=np.float64)
    if canonical_a.shape != (16369, 3045):
        raise AssertionError("canonical A shape drift")
    canonical_stationarity = np.asarray(
        canonical_a.T @ raw
    ).reshape(-1) + canonical_c
    canonical_dual_objective = -float(canonical_b @ raw)

    psd_minima = [
        float(np.linalg.eigvalsh((matrix + matrix.T) / 2.0)[0])
        for matrix in psd_matrices
    ]
    psd_traces = [float(np.trace(matrix)) for matrix in psd_matrices]
    block_zero_spectrum = np.linalg.eigvalsh(
        (psd_matrices[0] + psd_matrices[0].T) / 2.0
    )
    output = {
        "status": "PASS",
        "scope": "independent numerical replay only; no exact dual claim",
        "hashes": hashes,
        "raw_semantic_consistency": {
            "maximum_errors": raw_errors,
            "PSD_block_errors": psd_svec_errors,
            "SCS_PSD_map": (
                "upper-row-major semantic entries; "
                "off-diagonals multiplied by sqrt(2)"
            ),
        },
        "canonical_replay": {
            "stationarity_inf": float(
                np.max(np.abs(canonical_stationarity))
            ),
            "dual_objective": canonical_dual_objective,
            "A_shape": list(canonical_a.shape),
            "A_nnz": int(canonical_a.nnz),
        },
        "semantic_replay": {
            "nu_stationarity_inf": float(np.max(np.abs(nu_residual))),
            "q_kernel_stationarity_inf": float(
                np.max(np.abs(q_kernel_residual))
            ),
            "q_full_residual_inf": float(
                np.max(np.abs(q_full_residual))
            ),
            "normalization_residual": normalization_residual,
            "cone_weight": cone_weight,
            "margin_dual": beta,
            "lambda_T_b": semantic_objective,
            "canonical_minus_semantic_objective": (
                canonical_dual_objective - semantic_objective
            ),
        },
        "cones": {
            "minimum_alpha": float(np.min(alpha)),
            "minimum_gamma": float(np.min(gamma)),
            "minimum_PSD_eigenvalue": min(psd_minima),
            "block_zero_trace": psd_traces[0],
            "other_PSD_maximum_trace": max(psd_traces[1:]),
            "block_zero_eigenvalues_gt_1e-6": int(
                np.count_nonzero(block_zero_spectrum > 1e-6)
            ),
            "block_zero_eigenvalues_gt_1e-8": int(
                np.count_nonzero(block_zero_spectrum > 1e-8)
            ),
            "block_zero_minimum_eigenvalue": float(
                block_zero_spectrum[0]
            ),
            "block_zero_maximum_eigenvalue": float(
                block_zero_spectrum[-1]
            ),
            "PSD_traces": psd_traces,
        },
        "classification": (
            "numerical near-zero negative objective only; "
            "neither separator nor zero bound nor exposing face"
        ),
        "solver_called": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("DUAL_NPZ_REPLAY_PASS exact_claim=false solver_called=false")
    print(f"SHA256_REPLAY={sha256(Path(__file__))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
