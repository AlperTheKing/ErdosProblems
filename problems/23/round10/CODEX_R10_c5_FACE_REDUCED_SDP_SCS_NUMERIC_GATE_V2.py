"""Corrected independent no-solver replay of the reduced-SDP SCS point.

The ten empty quotient blocks are intentionally represented by NaN in the two
stored quotient-eigenvalue arrays.  All live numerical fields must be finite.
"""

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
MODEL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS_NUMERIC_GATE_V2.log"
EXPECTED_POINT_SHA256 = (
    "EB9BD53E8219BA64FF612465FBB59A6AD44B1BB762674B6C2498DBEF10B386A8"
)
EXPECTED_MODEL_SHA256 = (
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


def inf_norm(values) -> float:
    return float(np.max(np.abs(np.asarray(values, dtype=np.float64))))


def main() -> int:
    point_hash = sha256(POINT_PATH)
    if point_hash != EXPECTED_POINT_SHA256:
        raise AssertionError(f"point SHA-256 mismatch: {point_hash}")
    if sha256(MODEL_PATH) != EXPECTED_MODEL_SHA256:
        raise AssertionError("model source SHA-256 mismatch")

    solver_calls = 0
    original_solve = cp.Problem.solve

    def forbidden_solve(*_args, **_kwargs):
        nonlocal solver_calls
        solver_calls += 1
        raise AssertionError("replay attempted a solver call")

    try:
        cp.Problem.solve = forbidden_solve
        reduced = load_module(
            "codex_r10_c5_scs_numeric_gate_v2_model", MODEL_PATH
        )
        model = reduced.build_model()
    finally:
        cp.Problem.solve = original_solve
    if solver_calls != 0 or model.problem.status is not None:
        raise AssertionError("no-solver model gate failed")

    with np.load(POINT_PATH, allow_pickle=False) as point:
        if point["format_version"].tolist() != [1]:
            raise AssertionError("point format mismatch")
        if point["role"].tolist() != [
            "numerical steering only; exact replay required"
        ]:
            raise AssertionError("point role mismatch")
        for name, expected in model.hashes.items():
            if point[f"{name}_sha256"].tolist() != [expected]:
                raise AssertionError(f"point provenance mismatch: {name}")
        metadata = json.loads(str(point["solver_metadata_json"][0]))
        stored_diagnostics = json.loads(
            str(point["diagnostics_json"][0])
        )
        if (
            metadata.get("solver") != "SCS"
            or metadata.get("solver_version") != "3.2.11"
            or metadata.get("status") != "optimal"
            or metadata.get("options") != EXPECTED_OPTIONS
            or metadata.get("model_source_sha256")
            != EXPECTED_MODEL_SHA256
            or metadata.get("wrapper_source_sha256")
            != EXPECTED_WRAPPER_SHA256
        ):
            raise AssertionError("solver metadata/provenance mismatch")
        scs_info = metadata.get("scs_info", {})
        if (
            scs_info.get("status") != "solved"
            or int(scs_info.get("status_val", 0)) != 1
            or int(scs_info.get("iter", -1)) != 37350
        ):
            raise AssertionError("SCS terminal metadata mismatch")

        forced = point["forced_multiplier_orbits"].astype(np.int32)
        live = point["live_multiplier_orbits"].astype(np.int32)
        nu_live = point["nu_live"].astype(np.float64)
        nu_full = point["nu_full"].astype(np.float64)
        y = point["gram_face_coordinates"].astype(np.float64)
        q = point["q_full"].astype(np.float64)
        margin = float(point["relative_margin"][0])
        if (
            forced.shape != (2085,)
            or live.shape != (526,)
            or nu_live.shape != (526,)
            or nu_full.shape != (2611,)
            or y.shape != (2518,)
            or q.shape != (8647,)
            or not np.isfinite(margin)
            or not all(
                np.all(np.isfinite(values))
                for values in (nu_live, nu_full, y, q)
            )
        ):
            raise AssertionError("primal shape/finiteness gate failed")
        expected_forced = model.equality[
            "forced_multiplier_orbits"
        ].astype(np.int32)
        expected_live = model.equality[
            "live_multiplier_orbits"
        ].astype(np.int32)
        if not np.array_equal(forced, expected_forced):
            raise AssertionError("forced ordering mismatch")
        if not np.array_equal(live, expected_live):
            raise AssertionError("live ordering mismatch")
        if sorted(map(int, np.concatenate((forced, live)))) != list(
            range(2611)
        ):
            raise AssertionError("forced/live partition mismatch")
        if np.any(nu_full[forced] != 0.0):
            raise AssertionError("forced nu is not exactly zero")
        if not np.array_equal(nu_full[live], nu_live):
            raise AssertionError("full/live nu mismatch")
        q_replay_error = inf_norm(q - model.g @ y)
        if q_replay_error != 0.0:
            raise AssertionError(f"q != G*y: {q_replay_error}")

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
        replay_rows = {
            "normalization_residual": (normalization_residual, 56),
            "target_residual": (target_residual, 392),
            "retained_affine_residual": (retained_residual, 388),
            "H_residual": (h_residual, 6129),
        }
        for name, (values, expected_length) in replay_rows.items():
            if values.shape != (expected_length,):
                raise AssertionError(f"{name} has wrong shape")
            if not np.all(np.isfinite(values)):
                raise AssertionError(f"{name} is nonfinite")
            if inf_norm(point[name] - values) > 1e-13:
                raise AssertionError(f"stored {name} fails replay")

        quotient_orders = np.zeros(52, dtype=np.int32)
        symmetry = np.zeros(52, dtype=np.float64)
        ambient_minimum = np.full(52, np.nan, dtype=np.float64)
        quotient_minimum = np.full(52, np.nan, dtype=np.float64)
        quotient_gaps = np.full(52, np.nan, dtype=np.float64)
        q_offsets = model.blowup["gram_offsets"].astype(np.int64)
        qdims = model.blowup["gram_qdims"].astype(np.int64)
        for block, (orbit, free) in enumerate(
            zip(model.base.gram_orbits, model.free_by_block)
        ):
            q0 = int(q_offsets[block])
            local = q[q0 : q0 + int(qdims[block])]
            ambient = local[orbit.entry_ids]
            symmetry[block] = inf_norm(ambient - ambient.T)
            ambient_minimum[block] = float(
                np.linalg.eigvalsh(ambient)[0]
            )
            quotient_orders[block] = len(free)
            if free:
                quotient = ambient[np.ix_(free, free)]
                quotient_minimum[block] = float(
                    np.linalg.eigvalsh(quotient)[0]
                )
                quotient_gaps[block] = (
                    quotient_minimum[block] - margin
                )
        if (
            int(np.count_nonzero(quotient_orders == 0)) != 10
            or int(np.count_nonzero(quotient_orders == 1)) != 16
            or int(np.count_nonzero(quotient_orders > 1)) != 26
        ):
            raise AssertionError("quotient block census mismatch")
        if not np.all(np.isfinite(ambient_minimum)):
            raise AssertionError("ambient eigenvalue replay is nonfinite")
        for values in (quotient_minimum, quotient_gaps):
            if (
                int(np.count_nonzero(np.isnan(values))) != 10
                or not np.all(np.isfinite(values[~np.isnan(values)]))
            ):
                raise AssertionError("quotient empty/live finiteness mismatch")
        comparisons = {
            "ambient_min_eigenvalues": ambient_minimum,
            "quotient_min_eigenvalues": quotient_minimum,
            "quotient_margin_gaps": quotient_gaps,
        }
        for name, values in comparisons.items():
            if not np.allclose(
                point[name],
                values,
                rtol=0.0,
                atol=1e-13,
                equal_nan=True,
            ):
                raise AssertionError(f"stored {name} fails replay")

    original_448_residual = max(
        inf_norm(normalization_residual), inf_norm(target_residual)
    )
    retained_residual_inf = inf_norm(retained_residual)
    h_residual_inf = inf_norm(h_residual)
    combined_residual = max(
        original_448_residual, retained_residual_inf, h_residual_inf
    )
    nonempty = quotient_orders > 0
    minimum_quotient = float(np.min(quotient_minimum[nonempty]))
    minimum_quotient_gap = float(np.min(quotient_gaps[nonempty]))
    worst_block = int(np.nanargmin(quotient_gaps))
    minimum_nu = float(np.min(nu_live))
    minimum_nu_gap = float(np.min(nu_live - margin))
    scale = max(
        1.0,
        float(np.max(np.abs(model.equality["normalization_rhs"]))),
        float(np.max(np.abs(model.equality["target_rhs"]))),
    )
    feasibility_tolerance = 1e-7 * scale
    source_strict = bool(
        margin > feasibility_tolerance
        and combined_residual <= feasibility_tolerance
        and minimum_nu_gap >= -feasibility_tolerance
        and minimum_quotient_gap >= -feasibility_tolerance
    )
    raw_strict = bool(
        margin > 0.0
        and minimum_nu_gap >= 0.0
        and minimum_quotient_gap >= 0.0
    )
    if (
        source_strict
        or raw_strict
        or stored_diagnostics.get("numerical_strict_feasible") is not False
    ):
        raise AssertionError("strict-feasibility classification mismatch")

    result = {
        "status": "PASS",
        "scope": (
            "independent numerical replay only; "
            "no exact feasibility/infeasibility or further-face claim"
        ),
        "classification": (
            "NEAR_ZERO_BOUNDARY_NUMERICAL_POINT_NOT_STRICT_FEASIBLE"
        ),
        "point_sha256": point_hash,
        "model_source_sha256": EXPECTED_MODEL_SHA256,
        "solver_invoked": False,
        "solver_tripwire_calls": solver_calls,
        "provenance_schema_q_replay": "PASS",
        "affine_and_H": {
            "normalization_rows": 56,
            "normalization_residual_inf": inf_norm(
                normalization_residual
            ),
            "target_rows": 392,
            "target_residual_inf": inf_norm(target_residual),
            "all_original_affine_rows": 448,
            "all_original_affine_residual_inf": original_448_residual,
            "retained_rows": 388,
            "retained_residual_inf": retained_residual_inf,
            "H_rows": 6129,
            "H_residual_inf": h_residual_inf,
            "combined_residual_inf": combined_residual,
        },
        "multipliers": {
            "forced_count": 2085,
            "forced_exact_zero": True,
            "live_count": 526,
            "margin": margin,
            "minimum_live_nu": minimum_nu,
            "minimum_live_nu_minus_margin": minimum_nu_gap,
            "negative_live_count": int(np.count_nonzero(nu_live < 0.0)),
        },
        "quotients": {
            "blocks": 52,
            "empty": 10,
            "scalar": 16,
            "PSD": 26,
            "maximum_symmetry_residual": float(np.max(symmetry)),
            "minimum_quotient_eigenvalue": minimum_quotient,
            "minimum_quotient_eigenvalue_minus_margin": (
                minimum_quotient_gap
            ),
            "negative_eigenvalue_blocks": int(
                np.count_nonzero(quotient_minimum[nonempty] < 0.0)
            ),
            "negative_margin_gap_blocks": int(
                np.count_nonzero(quotient_gaps[nonempty] < 0.0)
            ),
            "worst_block": worst_block,
            "worst_block_order": int(quotient_orders[worst_block]),
        },
        "strict_feasibility": {
            "raw_strict_inequalities_hold": raw_strict,
            "source_tolerance": feasibility_tolerance,
            "source_rule_strict_feasible": source_strict,
            "stored_rule_strict_feasible": False,
            "meaning": (
                "This point cannot enter exact reconstruction. It is "
                "near-zero boundary evidence only; a dual exact replay is "
                "required before asserting a further face or separation."
            ),
        },
    }
    if sha256(POINT_PATH) != point_hash:
        raise AssertionError("input NPZ changed during replay")
    LOG_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("REDUCED_SDP_SCS_NUMERIC_GATE_V2_PASS solver_invoked=false")
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
