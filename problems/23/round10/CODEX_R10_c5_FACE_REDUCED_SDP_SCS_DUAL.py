"""Optional dual-export extension for the pinned reduced SCS solve.

This source exists only for the contingency that the primary SCS run ends
with a numerically near-zero margin.  Default execution builds, canonicalizes,
and audits the identical reduced model without solving or writing a file.
Solving requires both ``--solve`` and a new explicit ``--output`` path.

The extension preserves the primary wrapper's SCS 3.2.11 settings and exports
both the complete primal reconstruction and:

* raw canonical SCS ``y`` in the pinned cone order;
* 388 labeled affine-equality duals;
* 526 labeled live-nu/margin inequality duals;
* the scalar margin-nonnegative dual;
* 16 labeled scalar quotient-cone duals; and
* 26 labeled full symmetric PSD dual matrices.

All output is numerical steering data.  A further face or separating
certificate requires independent exact PSD, stationarity, and gap replay.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
PRIMARY_SCS_WRAPPER = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS.py"
)
EXPECTED_PRIMARY_SCS_WRAPPER_SHA256 = (
    "6BD44D50EBB8E8F2D142F055A0F9C073939B1FBE85A7B1381D29601CD921D319"
)
EXPECTED_MODEL_SOURCE_SHA256 = (
    "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1"
)
EXPECTED_SCS_VERSION = "3.2.11"
EXPECTED_SCS_OPTIONS = {
    "eps_abs": 1e-7,
    "eps_rel": 1e-7,
    "max_iters": 200_000,
    "time_limit_secs": 3600.0,
    "acceleration_lookback": 20,
    "normalize": True,
}
EXPECTED_A_SHAPE = (16369, 3045)
EXPECTED_A_NNZ = 8_574_476
ZERO_CONE_SIZE = 388
NONNEGATIVE_CONE_SIZE = 543
RAW_PSD_START = ZERO_CONE_SIZE + NONNEGATIVE_CONE_SIZE


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_primary_wrapper():
    observed_hash = sha256(PRIMARY_SCS_WRAPPER)
    if observed_hash != EXPECTED_PRIMARY_SCS_WRAPPER_SHA256:
        raise AssertionError(
            "primary SCS wrapper SHA-256 mismatch: "
            f"{observed_hash} != {EXPECTED_PRIMARY_SCS_WRAPPER_SHA256}"
        )
    spec = importlib.util.spec_from_file_location(
        "codex_r10_c5_primary_scs_pinned", PRIMARY_SCS_WRAPPER
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {PRIMARY_SCS_WRAPPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.EXPECTED_MODEL_SOURCE_SHA256 != EXPECTED_MODEL_SOURCE_SHA256:
        raise AssertionError("primary wrapper pins a different reduced model")
    if module.EXPECTED_SCS_VERSION != EXPECTED_SCS_VERSION:
        raise AssertionError("primary wrapper pins a different SCS version")
    if module.SCS_OPTIONS != EXPECTED_SCS_OPTIONS:
        raise AssertionError("primary wrapper SCS options drifted")
    return module


def semantic_constraint_layout(model) -> dict[str, np.ndarray]:
    """Gate and label CVXPY's 45 semantic constraints in source order."""
    constraints = model.problem.constraints
    if len(constraints) != 45:
        raise AssertionError(
            f"expected 45 semantic constraints, got {len(constraints)}"
        )
    if (
        type(constraints[0]).__name__ != "Equality"
        or constraints[0].shape != (388,)
    ):
        raise AssertionError("constraint 0 is not the 388-row affine equality")
    if (
        type(constraints[1]).__name__ != "Inequality"
        or constraints[1].shape != (526,)
    ):
        raise AssertionError(
            "constraint 1 is not the 526 live-nu/margin inequality"
        )
    if (
        type(constraints[2]).__name__ != "Inequality"
        or constraints[2].shape != ()
    ):
        raise AssertionError(
            "constraint 2 is not the scalar margin-nonnegative inequality"
        )

    nonempty_blocks: list[int] = []
    nonempty_orders: list[int] = []
    semantic_indices: list[int] = []
    kinds: list[str] = []
    scalar_blocks: list[int] = []
    scalar_constraint_indices: list[int] = []
    psd_blocks: list[int] = []
    psd_constraint_indices: list[int] = []
    psd_orders: list[int] = []
    cursor = 3
    for block, free in enumerate(model.free_by_block):
        order = len(free)
        if order == 0:
            continue
        constraint = constraints[cursor]
        nonempty_blocks.append(block)
        nonempty_orders.append(order)
        semantic_indices.append(cursor)
        if order == 1:
            if (
                type(constraint).__name__ != "Inequality"
                or constraint.shape != ()
            ):
                raise AssertionError(
                    f"block {block} lost its scalar cone constraint"
                )
            kinds.append("scalar_nonnegative")
            scalar_blocks.append(block)
            scalar_constraint_indices.append(cursor)
        else:
            if (
                type(constraint).__name__ != "PSD"
                or constraint.shape != (order, order)
            ):
                raise AssertionError(
                    f"block {block} lost its order-{order} PSD constraint"
                )
            kinds.append("PSD")
            psd_blocks.append(block)
            psd_constraint_indices.append(cursor)
            psd_orders.append(order)
        cursor += 1
    if cursor != len(constraints):
        raise AssertionError("semantic constraint cursor did not close")
    if len(scalar_blocks) != 16:
        raise AssertionError(f"expected 16 scalar blocks, got {scalar_blocks}")
    if len(psd_blocks) != 26:
        raise AssertionError(f"expected 26 PSD blocks, got {psd_blocks}")
    if psd_orders != list(map(int, model.psd_orders)):
        raise AssertionError("semantic PSD order differs from cone order")

    psd_flat_offsets = [0]
    for order in psd_orders:
        psd_flat_offsets.append(psd_flat_offsets[-1] + order * order)
    psd_svec_offsets = [RAW_PSD_START]
    for order in psd_orders:
        psd_svec_offsets.append(
            psd_svec_offsets[-1] + order * (order + 1) // 2
        )
    if psd_svec_offsets[-1] != EXPECTED_A_SHAPE[0]:
        raise AssertionError("raw canonical PSD offsets do not close")
    return {
        "nonempty_block_indices": np.asarray(
            nonempty_blocks, dtype=np.int32
        ),
        "nonempty_block_orders": np.asarray(
            nonempty_orders, dtype=np.int32
        ),
        "semantic_constraint_indices": np.asarray(
            semantic_indices, dtype=np.int32
        ),
        "semantic_constraint_kinds": np.asarray(kinds),
        "scalar_block_indices": np.asarray(scalar_blocks, dtype=np.int32),
        "scalar_constraint_indices": np.asarray(
            scalar_constraint_indices, dtype=np.int32
        ),
        "psd_block_indices": np.asarray(psd_blocks, dtype=np.int32),
        "psd_constraint_indices": np.asarray(
            psd_constraint_indices, dtype=np.int32
        ),
        "psd_orders": np.asarray(psd_orders, dtype=np.int32),
        "psd_flat_offsets": np.asarray(psd_flat_offsets, dtype=np.int64),
        "psd_svec_offsets": np.asarray(psd_svec_offsets, dtype=np.int64),
        "raw_y_cone_offsets": np.asarray(
            [0, ZERO_CONE_SIZE, RAW_PSD_START, EXPECTED_A_SHAPE[0]],
            dtype=np.int64,
        ),
        "raw_y_cone_labels": np.asarray(
            ["zero", "nonnegative", "PSD_svec"]
        ),
    }


def collect_duals(model, layout) -> tuple[dict[str, np.ndarray], dict]:
    constraints = model.problem.constraints
    equality_dual = np.asarray(
        constraints[0].dual_value, dtype=np.float64
    ).reshape(-1)
    live_dual = np.asarray(
        constraints[1].dual_value, dtype=np.float64
    ).reshape(-1)
    margin_dual = np.asarray(
        [constraints[2].dual_value], dtype=np.float64
    ).reshape(-1)
    if equality_dual.shape != (388,):
        raise AssertionError(f"wrong equality dual shape {equality_dual.shape}")
    if live_dual.shape != (526,):
        raise AssertionError(f"wrong live dual shape {live_dual.shape}")
    if margin_dual.shape != (1,):
        raise AssertionError(f"wrong margin dual shape {margin_dual.shape}")

    scalar_values: list[float] = []
    for index in layout["scalar_constraint_indices"]:
        scalar_values.append(
            float(np.asarray(constraints[int(index)].dual_value).reshape(()))
        )
    scalar_duals = np.asarray(scalar_values, dtype=np.float64)

    psd_flat: list[np.ndarray] = []
    psd_symmetry_residuals: list[float] = []
    psd_minimum_eigenvalues: list[float] = []
    for index, order in zip(
        layout["psd_constraint_indices"], layout["psd_orders"]
    ):
        matrix = np.asarray(
            constraints[int(index)].dual_value, dtype=np.float64
        )
        order = int(order)
        if matrix.shape != (order, order):
            raise AssertionError(
                f"wrong PSD dual shape {matrix.shape} at constraint {index}"
            )
        symmetry = float(np.max(np.abs(matrix - matrix.T)))
        psd_symmetry_residuals.append(symmetry)
        psd_minimum_eigenvalues.append(
            float(np.linalg.eigvalsh((matrix + matrix.T) / 2.0)[0])
        )
        psd_flat.append(matrix.reshape(-1, order="C"))

    stats = model.problem.solver_stats
    if not isinstance(stats.extra_stats, dict):
        raise RuntimeError("SCS returned no extra_stats dictionary")
    raw_y = np.asarray(
        stats.extra_stats.get("y"), dtype=np.float64
    ).reshape(-1)
    if raw_y.shape != (EXPECTED_A_SHAPE[0],):
        raise AssertionError(f"wrong raw canonical y shape {raw_y.shape}")
    arrays = {
        "raw_canonical_y": raw_y,
        "dual_affine_equalities": equality_dual,
        "dual_live_nu_minus_margin": live_dual,
        "dual_margin_nonnegative": margin_dual,
        "dual_scalar_quotient_values": scalar_duals,
        "dual_psd_matrices_flat": np.concatenate(psd_flat),
        "dual_psd_symmetry_residuals": np.asarray(
            psd_symmetry_residuals, dtype=np.float64
        ),
        "dual_psd_minimum_eigenvalues": np.asarray(
            psd_minimum_eigenvalues, dtype=np.float64
        ),
    }
    for name, array in arrays.items():
        if not np.all(np.isfinite(array)):
            raise RuntimeError(f"nonfinite dual output in {name}")
    diagnostics = {
        "scope": (
            "numerical dual steering only; "
            "exact PSD/stationarity/gap replay required"
        ),
        "raw_canonical_y_length": int(raw_y.size),
        "raw_canonical_y_inf_norm": float(np.max(np.abs(raw_y))),
        "minimum_live_constraint_dual": float(np.min(live_dual)),
        "margin_nonnegative_dual": float(margin_dual[0]),
        "minimum_scalar_quotient_dual": float(np.min(scalar_duals)),
        "maximum_PSD_dual_symmetry_residual": float(
            np.max(psd_symmetry_residuals)
        ),
        "minimum_PSD_dual_eigenvalue": float(
            np.min(psd_minimum_eigenvalues)
        ),
        "semantic_dual_counts": {
            "affine_equalities": int(equality_dual.size),
            "live_nu_minus_margin": int(live_dual.size),
            "margin_nonnegative": int(margin_dual.size),
            "scalar_quotient_blocks": int(scalar_duals.size),
            "PSD_matrices": int(len(psd_flat)),
        },
    }
    return arrays, diagnostics


def export_dual_point(
    output: Path,
    reduced,
    model,
    primal_diagnostics: dict,
    primal_arrays: dict[str, np.ndarray],
    solver_metadata: dict,
    layout: dict[str, np.ndarray],
    dual_arrays: dict[str, np.ndarray],
    dual_diagnostics: dict,
) -> str:
    output = output.resolve()
    if output.suffix.lower() != ".npz":
        raise ValueError("--output must end in .npz")
    if not output.parent.is_dir():
        raise ValueError(f"output directory does not exist: {output.parent}")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "numerical primal-dual steering only; "
                "exact replay required"
            ]
        ),
        "primal_diagnostics_json": np.asarray(
            [json.dumps(primal_diagnostics, sort_keys=True)]
        ),
        "dual_diagnostics_json": np.asarray(
            [json.dumps(dual_diagnostics, sort_keys=True)]
        ),
        "solver_metadata_json": np.asarray(
            [json.dumps(solver_metadata, sort_keys=True)]
        ),
        "relative_margin": np.asarray(
            [float(primal_diagnostics["margin"])], dtype=np.float64
        ),
        "forced_multiplier_orbits": model.forced.astype(np.int32),
        "live_multiplier_orbits": model.live.astype(np.int32),
        "model_source_sha256": np.asarray(
            [EXPECTED_MODEL_SOURCE_SHA256]
        ),
        "primary_scs_wrapper_sha256": np.asarray(
            [EXPECTED_PRIMARY_SCS_WRAPPER_SHA256]
        ),
        "dual_wrapper_sha256": np.asarray([sha256(Path(__file__))]),
        "scs_version": np.asarray([EXPECTED_SCS_VERSION]),
        "scs_options_json": np.asarray(
            [json.dumps(EXPECTED_SCS_OPTIONS, sort_keys=True)]
        ),
        "canonical_A_shape": np.asarray(
            EXPECTED_A_SHAPE, dtype=np.int64
        ),
        "canonical_A_nnz": np.asarray(
            [EXPECTED_A_NNZ], dtype=np.int64
        ),
        "canonical_zero_cone": np.asarray(
            [ZERO_CONE_SIZE], dtype=np.int64
        ),
        "canonical_nonnegative_cone": np.asarray(
            [NONNEGATIVE_CONE_SIZE], dtype=np.int64
        ),
    }
    for name, value in model.hashes.items():
        payload[f"pinned_{name}_sha256"] = np.asarray([value])
    payload.update(primal_arrays)
    payload.update(layout)
    payload.update(dual_arrays)
    np.savez_compressed(output, **payload)
    print(
        f"REDUCED_SDP_SCS_DUAL_EXPORT path={output} "
        f"sha256={sha256(output)} raw_y_length="
        f"{dual_arrays['raw_canonical_y'].size}"
    )
    return sha256(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solve",
        action="store_true",
        help="explicitly authorize the pinned SCS primal-dual solve",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="new .npz destination required together with --solve",
    )
    args = parser.parse_args()
    if args.solve and args.output is None:
        parser.error("--solve requires an explicit --output NEW_FILE.npz")
    if args.output is not None and not args.solve:
        parser.error("--output is accepted only together with --solve")
    if args.output is not None:
        output = args.output.resolve()
        if output.suffix.lower() != ".npz":
            parser.error("--output must end in .npz")
        if not output.parent.is_dir():
            parser.error(f"output directory does not exist: {output.parent}")
        if output.exists():
            parser.error(f"refusing to overwrite existing output: {output}")
        args.output = output
    return args


def main() -> int:
    args = parse_args()
    primary = load_primary_wrapper()
    reduced = primary.load_pinned_model_module()
    model = reduced.build_model()
    build_summary = primary.canonicalize_scs(model)
    layout = semantic_constraint_layout(model)
    build_summary.update(
        {
            "scope": "dual-export build-only; no solve",
            "semantic_constraints": 45,
            "affine_duals": 388,
            "live_nu_duals": 526,
            "margin_duals": 1,
            "scalar_quotient_duals": int(
                layout["scalar_block_indices"].size
            ),
            "PSD_dual_matrices": int(layout["psd_block_indices"].size),
            "raw_y_length": EXPECTED_A_SHAPE[0],
            "primary_scs_wrapper_sha256": (
                EXPECTED_PRIMARY_SCS_WRAPPER_SHA256
            ),
        }
    )
    print(json.dumps(build_summary, indent=2, sort_keys=True))
    if not args.solve:
        print(
            "REDUCED_SDP_SCS_DUAL_BUILD_ONLY_PASS "
            "solver_called=false no_file_written=true"
        )
        return 0

    value, elapsed = primary.solve_scs(model)
    if model.problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        raise RuntimeError(
            f"SCS returned status {model.problem.status}; "
            "no primal-dual archive written"
        )
    if value is None or not np.isfinite(value):
        raise RuntimeError("SCS returned no finite objective value")
    if (
        model.nu_live.value is None
        or model.face_coordinates.value is None
        or model.margin.value is None
    ):
        raise RuntimeError("SCS status has no primal variable values")

    primal_diagnostics, primal_arrays = (
        reduced.reconstruct_and_diagnose(
            model,
            model.nu_live.value,
            model.face_coordinates.value,
            float(model.margin.value),
        )
    )
    solver_metadata = primary.solve_metadata(model, value, elapsed)
    solver_metadata["dual_export_wrapper_sha256"] = sha256(Path(__file__))
    dual_arrays, dual_diagnostics = collect_duals(model, layout)
    output_hash = export_dual_point(
        args.output,
        reduced,
        model,
        primal_diagnostics,
        primal_arrays,
        solver_metadata,
        layout,
        dual_arrays,
        dual_diagnostics,
    )
    print(json.dumps(primal_diagnostics, indent=2, sort_keys=True))
    print(json.dumps(dual_diagnostics, indent=2, sort_keys=True))
    print(f"OUTPUT={args.output}")
    print(f"SHA256_OUTPUT={output_hash}")
    print(
        "REDUCED_SDP_SCS_PRIMAL_DUAL_RESULT_WRITTEN "
        "exact_dual_replay_required=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
