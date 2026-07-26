"""Independent no-solver replay of the completed reduced-SDP SCS point."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cvxpy as cp
import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
POINT_PATH = HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_numeric.npz"
MODEL_SOURCE = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS_NUMERIC_GATE.log"
EXPECTED_POINT_SHA256 = (
    "EB9BD53E8219BA64FF612465FBB59A6AD44B1BB762674B6C2498DBEF10B386A8"
)
EXPECTED_MODEL_SOURCE_SHA256 = (
    "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1"
)
EXPECTED_WRAPPER_SHA256 = (
    "6BD44D50EBB8E8F2D142F055A0F9C073939B1FBE85A7B1381D29601CD921D319"
)
EXPECTED_OPTIONS = {
    "eps_abs": 1e-7,
    "eps_rel": 1e-7,
    "max_iters": 200_000,
    "time_limit_secs": 3600.0,
    "acceleration_lookback": 20,
    "normalize": True,
}
EXPECTED_FIELDS = {
    "H_residual",
    "ambient_min_eigenvalues",
    "base_sha256",
    "blowup_sha256",
    "canonical_source_sha256",
    "diagnostics_json",
    "equality_sha256",
    "exact_kernel_sha256",
    "forced_multiplier_orbits",
    "format_version",
    "gram_face_coordinates",
    "live_multiplier_orbits",
    "normalization_residual",
    "nu_full",
    "nu_live",
    "numerical_kernel_sha256",
    "q_full",
    "quotient_margin_gaps",
    "quotient_min_eigenvalues",
    "relative_margin",
    "retained_affine_residual",
    "role",
    "row_reduction_sha256",
    "solver_metadata_json",
    "target_residual",
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


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.float64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
    )


def maximum_absolute(vector: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(vector, dtype=np.float64))))


def main() -> int:
    point_hash_before = sha256(POINT_PATH)
    if point_hash_before != EXPECTED_POINT_SHA256:
        raise AssertionError(
            f"numerical point SHA-256 mismatch: {point_hash_before}"
        )
    if sha256(MODEL_SOURCE) != EXPECTED_MODEL_SOURCE_SHA256:
        raise AssertionError("reduced model source SHA-256 mismatch")

    solver_calls = 0
    original_solve = cp.Problem.solve

    def forbidden_solve(*_args, **_kwargs):
        nonlocal solver_calls
        solver_calls += 1
        raise AssertionError("numeric replay attempted to invoke a solver")

    try:
        cp.Problem.solve = forbidden_solve
        reduced = load_module(
            "codex_r10_c5_scs_numeric_gate_model", MODEL_SOURCE
        )
        model = reduced.build_model()
    finally:
        cp.Problem.solve = original_solve
    if solver_calls:
        raise AssertionError("solver tripwire was triggered")
    if model.problem.status is not None:
        raise AssertionError("replay model unexpectedly has solver status")

    with np.load(POINT_PATH, allow_pickle=False) as point:
        if set(point.files) != EXPECTED_FIELDS:
            raise AssertionError(
                "point schema mismatch: "
                f"missing={sorted(EXPECTED_FIELDS - set(point.files))}, "
                f"extra={sorted(set(point.files) - EXPECTED_FIELDS)}"
            )
        if point["format_version"].tolist() != [1]:
            raise AssertionError("unexpected numerical point format")
        if point["role"].tolist() != [
            "numerical steering only; exact replay required"
        ]:
            raise AssertionError("unexpected numerical point role")
        for name, expected_hash in model.hashes.items():
            field = f"{name}_sha256"
            if point[field].tolist() != [expected_hash]:
                raise AssertionError(f"provenance mismatch in {field}")

        solver_metadata = json.loads(
            str(point["solver_metadata_json"][0])
        )
        stored_diagnostics = json.loads(
            str(point["diagnostics_json"][0])
        )
        if (
            solver_metadata.get("solver") != "SCS"
            or solver_metadata.get("solver_version") != "3.2.11"
            or solver_metadata.get("status") != "optimal"
            or solver_metadata.get("options") != EXPECTED_OPTIONS
            or solver_metadata.get("model_source_sha256")
            != EXPECTED_MODEL_SOURCE_SHA256
            or solver_metadata.get("wrapper_source_sha256")
            != EXPECTED_WRAPPER_SHA256
        ):
            raise AssertionError(
                f"solver metadata/provenance mismatch: {solver_metadata}"
            )
        scs_info = solver_metadata.get("scs_info", {})
        if (
            scs_info.get("status") != "solved"
            or int(scs_info.get("status_val", 0)) != 1
            or int(scs_info.get("iter", -1)) != 37350
        ):
            raise AssertionError("unexpected SCS terminal metadata")

        forced = point["forced_multiplier_orbits"].astype(np.int32)
        live = point["live_multiplier_orbits"].astype(np.int32)
        nu_live = point["nu_live"].astype(np.float64)
        nu_full = point["nu_full"].astype(np.float64)
        face_coordinates = point[
            "gram_face_coordinates"
        ].astype(np.float64)
        q = point["q_full"].astype(np.float64)
        margin = float(point["relative_margin"][0])
        arrays = (
            nu_live,
            nu_full,
            face_coordinates,
            q,
            point["normalization_residual"],
            point["target_residual"],
            point["retained_affine_residual"],
            point["H_residual"],
            point["ambient_min_eigenvalues"],
            point["quotient_min_eigenvalues"],
            point["quotient_margin_gaps"],
        )
        if not all(np.all(np.isfinite(array)) for array in arrays):
            raise AssertionError("point contains a nonfinite numeric value")
        if (
            forced.shape != (2085,)
            or live.shape != (526,)
            or nu_live.shape != (526,)
            or nu_full.shape != (2611,)
            or face_coordinates.shape != (2518,)
            or q.shape != (8647,)
        ):
            raise AssertionError("point has a wrong primal array shape")
        expected_forced = model.equality[
            "forced_multiplier_orbits"
        ].astype(np.int32)
        expected_live = model.equality[
            "live_multiplier_orbits"
        ].astype(np.int32)
        if not np.array_equal(forced, expected_forced):
            raise AssertionError("forced multiplier ordering mismatch")
        if not np.array_equal(live, expected_live):
            raise AssertionError("live multiplier ordering mismatch")
        if sorted(map(int, np.concatenate((forced, live)))) != list(
            range(2611)
        ):
            raise AssertionError("forced/live partition is not exhaustive")
        if np.any(nu_full[forced] != 0.0):
            raise AssertionError("a forced multiplier is not exactly zero")
        if not np.array_equal(nu_full[live], nu_live):
            raise AssertionError("full/live multiplier values disagree")

        q_rebuilt = np.asarray(
            model.g @ face_coordinates
        ).reshape(-1)
        q_replay_residual = maximum_absolute(q - q_rebuilt)
        if q_replay_residual != 0.0:
            raise AssertionError(
                f"stored q differs from G*y by {q_replay_residual}"
            )

        normalization = unpack_csr(
            model.equality, "normalization_live"
        )
        target_nu = unpack_csr(
            model.equality, "target_nu_live"
        )
        target_q = unpack_csr(model.equality, "target_gram")
        normalization_residual = np.asarray(
            normalization @ nu_live
            - model.equality["normalization_rhs"].astype(np.float64)
        ).reshape(-1)
        target_residual = np.asarray(
            target_nu @ nu_live
            + target_q @ q
            - model.equality["target_rhs"].astype(np.float64)
        ).reshape(-1)
        retained_residual = np.asarray(
            model.affine_nu @ nu_live
            + model.affine_q @ q
            - model.affine_rhs
        ).reshape(-1)
        h_residual = np.asarray(model.h @ q).reshape(-1)
        if (
            normalization_residual.shape != (56,)
            or target_residual.shape != (392,)
            or retained_residual.shape != (388,)
            or h_residual.shape != (6129,)
        ):
            raise AssertionError("replayed row dimensions mismatch")
        stored_replays = {
            "normalization_residual": normalization_residual,
            "target_residual": target_residual,
            "retained_affine_residual": retained_residual,
            "H_residual": h_residual,
        }
        for name, replay in stored_replays.items():
            difference = maximum_absolute(point[name] - replay)
            if difference > 1e-13:
                raise AssertionError(
                    f"stored {name} differs from replay by {difference}"
                )

        ambient_minimum = np.full(52, np.nan, dtype=np.float64)
        quotient_minimum = np.full(52, np.nan, dtype=np.float64)
        quotient_gaps = np.full(52, np.nan, dtype=np.float64)
        symmetry_residuals = np.zeros(52, dtype=np.float64)
        quotient_orders = np.zeros(52, dtype=np.int32)
        q_offsets = model.blowup["gram_offsets"].astype(np.int64)
        q_dimensions = model.blowup["gram_qdims"].astype(np.int64)
        for block, (orbit, free) in enumerate(
            zip(model.base.gram_orbits, model.free_by_block)
        ):
            q0 = int(q_offsets[block])
            qdim = int(q_dimensions[block])
            local = q[q0 : q0 + qdim]
            ambient = local[orbit.entry_ids]
            symmetry_residuals[block] = maximum_absolute(
                ambient - ambient.T
            )
            ambient_minimum[block] = float(
                np.linalg.eigvalsh((ambient + ambient.T) / 2.0)[0]
            )
            quotient_orders[block] = len(free)
            if free:
                quotient = ambient[np.ix_(free, free)]
                quotient_minimum[block] = float(
                    np.linalg.eigvalsh(
                        (quotient + quotient.T) / 2.0
                    )[0]
                )
                quotient_gaps[block] = (
                    quotient_minimum[block] - margin
                )
        if int(np.count_nonzero(quotient_orders == 0)) != 10:
            raise AssertionError("unexpected empty quotient-block count")
        if int(np.count_nonzero(quotient_orders == 1)) != 16:
            raise AssertionError("unexpected scalar quotient-block count")
        if int(np.count_nonzero(quotient_orders > 1)) != 26:
            raise AssertionError("unexpected PSD quotient-block count")
        comparisons = {
            "ambient_min_eigenvalues": ambient_minimum,
            "quotient_min_eigenvalues": quotient_minimum,
            "quotient_margin_gaps": quotient_gaps,
        }
        for name, replay in comparisons.items():
            if not np.allclose(
                point[name],
                replay,
                rtol=0.0,
                atol=1e-13,
                equal_nan=True,
            ):
                raise AssertionError(f"stored {name} fails replay")

    maximum_symmetry_residual = float(np.max(symmetry_residuals))
    maximum_affine_448_residual = max(
        maximum_absolute(normalization_residual),
        maximum_absolute(target_residual),
    )
    maximum_retained_residual = maximum_absolute(retained_residual)
    maximum_h_residual = maximum_absolute(h_residual)
    combined_residual = max(
        maximum_affine_448_residual,
        maximum_retained_residual,
        maximum_h_residual,
    )
    nonempty = quotient_orders > 0
    minimum_quotient = float(np.min(quotient_minimum[nonempty]))
    minimum_quotient_gap = float(np.min(quotient_gaps[nonempty]))
    worst_block = int(np.nanargmin(quotient_gaps))
    minimum_nu = float(np.min(nu_live))
    minimum_nu_gap = float(np.min(nu_live - margin))
    negative_live_count = int(np.count_nonzero(nu_live < 0.0))
    negative_quotient_count = int(
        np.count_nonzero(quotient_minimum[nonempty] < 0.0)
    )
    negative_gap_count = int(
        np.count_nonzero(quotient_gaps[nonempty] < 0.0)
    )

    exact_strict_inequalities_numerically_hold = bool(
        margin > 0.0
        and minimum_nu_gap >= 0.0
        and minimum_quotient_gap >= 0.0
    )
    scale = max(
        1.0,
        float(
            np.max(
                np.abs(
                    model.equality["normalization_rhs"].astype(
                        np.float64
                    )
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    model.equality["target_rhs"].astype(np.float64)
                )
            )
        ),
    )
    source_feasibility_tolerance = 1e-7 * scale
    source_strict_feasible = bool(
        margin > source_feasibility_tolerance
        and combined_residual <= source_feasibility_tolerance
        and minimum_nu_gap >= -source_feasibility_tolerance
        and minimum_quotient_gap >= -source_feasibility_tolerance
    )
    if stored_diagnostics.get("numerical_strict_feasible") is not False:
        raise AssertionError("stored strict-feasibility classification drift")
    if source_strict_feasible:
        raise AssertionError("independent replay unexpectedly classified strict")
    classification = (
        "NEAR_ZERO_BOUNDARY_NUMERICAL_POINT_NOT_STRICT_FEASIBLE"
    )

    result = {
        "status": "PASS",
        "scope": (
            "independent numerical replay only; "
            "no exact feasibility or infeasibility claim"
        ),
        "classification": classification,
        "point_sha256": point_hash_before,
        "model_source_sha256": EXPECTED_MODEL_SOURCE_SHA256,
        "solver_invoked": False,
        "solver_tripwire_calls": solver_calls,
        "provenance_and_schema": "PASS",
        "row_replay": {
            "normalization_rows": 56,
            "normalization_residual_inf": maximum_absolute(
                normalization_residual
            ),
            "target_rows": 392,
            "target_residual_inf": maximum_absolute(target_residual),
            "all_original_affine_rows": 448,
            "all_original_affine_residual_inf": (
                maximum_affine_448_residual
            ),
            "retained_rows": 388,
            "retained_residual_inf": maximum_retained_residual,
            "H_rows": 6129,
            "H_residual_inf": maximum_h_residual,
            "combined_residual_inf": combined_residual,
        },
        "multiplier_replay": {
            "forced_count": 2085,
            "forced_exact_zero": True,
            "live_count": 526,
            "minimum_live_nu": minimum_nu,
            "margin": margin,
            "minimum_live_nu_minus_margin": minimum_nu_gap,
            "negative_live_count": negative_live_count,
        },
        "quotient_replay": {
            "blocks": 52,
            "empty_blocks": 10,
            "scalar_blocks": 16,
            "PSD_blocks": 26,
            "maximum_symmetry_residual": maximum_symmetry_residual,
            "minimum_quotient_eigenvalue": minimum_quotient,
            "minimum_quotient_eigenvalue_minus_margin": (
                minimum_quotient_gap
            ),
            "negative_quotient_eigenvalue_blocks": (
                negative_quotient_count
            ),
            "negative_margin_gap_blocks": negative_gap_count,
            "worst_block": worst_block,
            "worst_block_order": int(quotient_orders[worst_block]),
        },
        "strict_feasibility": {
            "raw_strict_inequalities_hold": (
                exact_strict_inequalities_numerically_hold
            ),
            "source_feasibility_tolerance": (
                source_feasibility_tolerance
            ),
            "source_rule_strict_feasible": source_strict_feasible,
            "stored_rule_strict_feasible": stored_diagnostics[
                "numerical_strict_feasible"
            ],
            "meaning": (
                "The point is not a strict feasible point and cannot enter "
                "exact reconstruction. It is numerical evidence of a "
                "near-zero boundary only, not proof of a further face or "
                "of infeasibility."
            ),
        },
    }
    if sha256(POINT_PATH) != point_hash_before:
        raise AssertionError("input NPZ changed during read-only replay")
    LOG_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("REDUCED_SDP_SCS_NUMERIC_GATE_PASS solver_invoked=false")
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
