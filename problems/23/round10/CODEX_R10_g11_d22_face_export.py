"""Build, optionally solve, audit, and export the R10 D22 exact-face model.

This companion keeps CODEX_R10_g11_d22_face.py build-only by default while
providing the required safe export path for an authorized face solve.  It
never overwrites CODEX_R10_g11_d22_numeric.pkl.  A feasible-status iterate is
expanded to the standard Q4 layout in a separate pickle explicitly marked
NUMERICAL_ONLY, together with exact Fraction-valued face metadata and complete
post-solve diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import pickle
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
FACE_PATH = HERE / "CODEX_R10_g11_d22_face.py"
RAW_NUMERIC_PATH = HERE / "CODEX_R10_g11_d22_numeric.pkl"
DEFAULT_OUTPUT = HERE / "CODEX_R10_g11_d22_face_numeric.pkl"
DEFAULT_REPORT = HERE / "CODEX_R10_D22_FACE_RUN.md"


def load_face_module():
    spec = importlib.util.spec_from_file_location("codex_r10_d22_face", FACE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the D22 face scaffold")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def post_solve_diagnostics(face) -> dict[str, object]:
    """Check the original equalities and every exact face condition."""
    base = face.base
    nu = np.asarray(base.multiplier_variable.value, dtype=float)
    if nu.ndim != 1 or not np.all(np.isfinite(nu)):
        raise RuntimeError("face solve returned no finite multiplier vector")
    normalization_residual = float(
        np.max(np.abs(base.problem.constraints[0].violation()))
    )
    target_residual = float(
        np.max(np.abs(base.problem.constraints[-1].violation()))
    )
    forced_zero_residual = (
        float(np.max(np.abs(nu[face.forced_zero_multiplier_orbits])))
        if face.forced_zero_multiplier_orbits
        else 0.0
    )

    kernel_residuals = []
    complement_minimum_eigenvalues = []
    representative_minimum_eigenvalues = []
    reduced_gram_values = []
    for orbit, data in zip(base.gram_orbits, face.orbit_data):
        matrix = np.asarray(orbit.matrix.value, dtype=float)
        matrix = (matrix + matrix.T) / 2
        reduced_gram_values.append(np.asarray(orbit.variable.value, dtype=float))
        representative_minimum_eigenvalues.append(
            float(matrix[0, 0])
            if matrix.shape == (1, 1)
            else float(np.linalg.eigvalsh(matrix).min())
        )
        if data.kernel:
            kernel_float = np.asarray(
                [[float(value) for value in row] for row in data.kernel],
                dtype=float,
            )
            kernel_residuals.append(float(np.max(np.abs(matrix @ kernel_float.T))))
        else:
            kernel_residuals.append(0.0)

        projector = np.asarray(
            [[float(value) for value in row] for row in data.projector],
            dtype=float,
        )
        projector_eigenvalues, projector_basis = np.linalg.eigh(projector)
        complement_basis = projector_basis[:, projector_eigenvalues > 0.5]
        if complement_basis.shape[1] == 0:
            complement_minimum_eigenvalues.append(float("nan"))
        else:
            compressed = complement_basis.T @ matrix @ complement_basis
            complement_minimum_eigenvalues.append(
                float(compressed[0, 0])
                if compressed.shape == (1, 1)
                else float(np.linalg.eigvalsh((compressed + compressed.T) / 2).min())
            )

    solver_stats = face.problem.solver_stats
    finite_complement_margins = [
        value for value in complement_minimum_eigenvalues if np.isfinite(value)
    ]
    return {
        "status": face.problem.status,
        "margin": float(face.margin.value),
        "normalization_max_abs_residual": normalization_residual,
        "target_max_abs_residual": target_residual,
        "forced_zero_max_abs_residual": forced_zero_residual,
        "kernel_max_abs_residual": max(kernel_residuals, default=0.0),
        "kernel_max_abs_residual_by_orbit": kernel_residuals,
        "minimum_multiplier": float(np.min(nu)),
        "minimum_representative_gram_eigenvalue": min(
            representative_minimum_eigenvalues, default=float("nan")
        ),
        "minimum_complement_eigenvalue": min(
            finite_complement_margins, default=float("nan")
        ),
        "complement_minimum_eigenvalue_by_orbit": complement_minimum_eigenvalues,
        "solver_name": solver_stats.solver_name,
        "solver_num_iters": solver_stats.num_iters,
        "solver_setup_time": solver_stats.setup_time,
        "solver_solve_time": solver_stats.solve_time,
        "reduced_multiplier_values": nu,
        "reduced_gram_values": reduced_gram_values,
    }


def expand_payload(face_module, face, diagnostics: dict[str, object]) -> dict[str, object]:
    """Expand D22 orbit values to the standard numerical Q4 certificate layout."""
    base = face.base
    builder = face_module.load_builder()
    nu_orbit = np.asarray(base.multiplier_variable.value, dtype=float)
    nu = {}
    for cut_index in range(len(base.cuts)):
        for monomial_index, monomial in enumerate(base.multiplier_monomials):
            value = float(
                nu_orbit[base.multiplier_orbit_ids[cut_index, monomial_index]]
            )
            if value != 0.0:
                nu[(cut_index, monomial)] = value

    orbit_by_member = {}
    for orbit in base.gram_orbits:
        for member in orbit.parity_members:
            orbit_by_member[member] = orbit
    full_qblocks = []
    for block in builder.parity_blocks(builder.N, builder.DT):
        parity_mask = builder.parity(block[0])
        orbit = orbit_by_member[parity_mask]
        representative_matrix = np.asarray(orbit.matrix.value, dtype=float)
        element = orbit.image_elements[parity_mask]
        permutation = builder.image_permutation(orbit.basis, block, element)
        matrix = np.zeros_like(representative_matrix)
        matrix[np.ix_(permutation, permutation)] = representative_matrix
        full_qblocks.append((block, matrix.tolist()))

    exact_orbit_faces = []
    for orbit, data in zip(base.gram_orbits, face.orbit_data):
        exact_orbit_faces.append(
            {
                "parity_rep": orbit.parity_rep,
                "parity_members": orbit.parity_members,
                "kernel": data.kernel,
                "projector": data.projector,
            }
        )
    public_diagnostics = {
        key: value
        for key, value in diagnostics.items()
        if key not in ("reduced_multiplier_values", "reduced_gram_values")
    }
    return {
        "format": "Q4-certificate-layout-numerical-face-v1",
        "NUMERICAL_ONLY": True,
        "m": 11,
        "d": 2,
        "c": Fraction(25, 1),
        "n": builder.N,
        "E": base.edges,
        "cuts": base.cuts,
        "nu": nu,
        "Q": full_qblocks,
        "face": {
            "cycles": face.cycles,
            "forced_zero_multiplier_orbits": face.forced_zero_multiplier_orbits,
            "gram_orbits": exact_orbit_faces,
        },
        "reduced": {
            "multiplier_values": diagnostics["reduced_multiplier_values"],
            "gram_values": diagnostics["reduced_gram_values"],
        },
        "diagnostics": public_diagnostics,
        "next_exact_step": (
            "Reconstruct exact orbit scalars on the stored rational face, expand "
            "Fractions, and pass Q4_verify.verify with d=2 plus an independent root gate."
        ),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_report(
    output_path: Path,
    report_path: Path,
    diagnostics: dict[str, object],
    command: str,
) -> None:
    keys = (
        "status",
        "margin",
        "normalization_max_abs_residual",
        "target_max_abs_residual",
        "forced_zero_max_abs_residual",
        "kernel_max_abs_residual",
        "minimum_multiplier",
        "minimum_representative_gram_eigenvalue",
        "minimum_complement_eigenvalue",
        "solver_name",
        "solver_num_iters",
        "solver_setup_time",
        "solver_solve_time",
    )
    lines = [
        "# R10 D22 exact-face numerical run",
        "",
        "This is numerical steering evidence only, not an exact certificate.",
        "",
        "## Command",
        "",
        "```text",
        command,
        "```",
        "",
        "## Diagnostics",
        "",
        "```text",
    ]
    lines.extend(f"{key}={diagnostics[key]}" for key in keys)
    lines.extend(
        [
            "```",
            "",
            "## SHA-256",
            "",
            "```text",
            f"{sha256(output_path)}  {output_path.name}",
            f"{sha256(FACE_PATH)}  {FACE_PATH.name}",
            f"{sha256(Path(__file__))}  {Path(__file__).name}",
            "```",
            "",
            "Exact Fraction reconstruction and independent Q4 verification remain mandatory.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--solver", choices=("CLARABEL", "SCS"), default="CLARABEL")
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument("--max-iter", type=int, default=500)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    face_module = load_face_module()
    face = face_module.build_face_model()
    if not args.solve:
        print("FACE_EXPORT_BUILD_ONLY: no solver launched and no file written")
        return
    if args.output.resolve() == RAW_NUMERIC_PATH.resolve():
        raise SystemExit("refusing to overwrite the raw numerical pickle")
    for path in (args.output, args.report):
        if path.exists() and not args.overwrite:
            raise SystemExit(f"refusing to overwrite {path}; pass --overwrite explicitly")

    options: dict[str, object] = {"solver": args.solver, "verbose": args.verbose}
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
        )
    start = time.perf_counter()
    face.problem.solve(**options)
    elapsed = time.perf_counter() - start
    print(f"FACE_SOLVE status={face.problem.status} seconds={elapsed:.3f}")
    if face.problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        print("NO_EXPORT: no feasible-status iterate")
        return

    diagnostics = post_solve_diagnostics(face)
    for key in (
        "margin",
        "normalization_max_abs_residual",
        "target_max_abs_residual",
        "forced_zero_max_abs_residual",
        "kernel_max_abs_residual",
        "minimum_multiplier",
        "minimum_representative_gram_eigenvalue",
        "minimum_complement_eigenvalue",
    ):
        print(f"{key}={diagnostics[key]}")
    payload = expand_payload(face_module, face, diagnostics)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    command = subprocess.list2cmdline([sys.executable, *sys.argv])
    write_report(args.output, args.report, diagnostics, command)
    print(f"NUMERICAL_ONLY_FACE_EXPORT={args.output.resolve()}")
    print(f"FACE_RUN_REPORT={args.report.resolve()}")
    print(f"FACE_EXPORT_SHA256={sha256(args.output)}")


if __name__ == "__main__":
    main()
