"""Build and canonicalize the 3045-variable reduced plateau SDP.

This is a resource/structure probe only.  It uses the separately gated
float64 direct-H kernel basis for numerical steering, removes all H rows and
all forced multiplier variables, retains the 388 independent affine rows,
and imposes PSD only on the exact quotient principal matrices.

The script calls CVXPY ``get_problem_data`` for Clarabel.  It never calls a
solver and never treats float64 output as a certificate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

import cvxpy as cp
import numpy as np
import psutil
import scipy
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
ROW_REDUCTION_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)
SUMMARY_PATH = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE_summary.json"
)
REPORT_PATH = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE_REPORT.md"
)

EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "row_reduction": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "numerical_kernel": "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3",
}
PIVOT_PRIME = 2_000_003


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


def unpack_csr(archive, name: str, dtype) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(dtype),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=dtype,
    )


def independent_pivot_columns(
    rows: list[tuple[int, ...]], width: int
) -> list[int]:
    echelon: dict[int, dict[int, int]] = {}
    for source in rows:
        if len(source) != width:
            raise AssertionError("kernel row width mismatch")
        row = {
            column: int(value) % PIVOT_PRIME
            for column, value in enumerate(source)
            if int(value) % PIVOT_PRIME
        }
        while row:
            pivot = min(row)
            base = echelon.get(pivot)
            if base is None:
                inverse = pow(row[pivot], PIVOT_PRIME - 2, PIVOT_PRIME)
                echelon[pivot] = {
                    column: value * inverse % PIVOT_PRIME
                    for column, value in row.items()
                    if value * inverse % PIVOT_PRIME
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % PIVOT_PRIME
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return sorted(echelon)


def free_coordinates(blowup, base) -> list[list[int]]:
    grouped: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append(tuple(int(value) for value in row))
    output = []
    for block, orbit in enumerate(base.gram_orbits):
        pivots = independent_pivot_columns(
            grouped.get(block, []), len(orbit.basis)
        )
        if len(pivots) != len(grouped.get(block, [])):
            raise AssertionError(f"block {block}: dependent kernel rows")
        pivot_set = set(pivots)
        output.append(
            [
                index
                for index in range(len(orbit.basis))
                if index not in pivot_set
            ]
        )
    return output


class RssMonitor:
    def __init__(self) -> None:
        self.process = psutil.Process()
        self.start_rss = int(self.process.memory_info().rss)
        self.peak_rss = self.start_rss
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self.stop_event.wait(0.01):
            self.peak_rss = max(
                self.peak_rss, int(self.process.memory_info().rss)
            )

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> tuple[int, int, int]:
        self.stop_event.set()
        self.thread.join()
        end_rss = int(self.process.memory_info().rss)
        self.peak_rss = max(self.peak_rss, end_rss)
        return self.start_rss, end_rss, self.peak_rss


def main() -> None:
    paths = {
        "base": BASE_PATH,
        "blowup": BLOWUP_PATH,
        "equality": EQUALITY_PATH,
        "row_reduction": ROW_REDUCTION_PATH,
        "exact_kernel": EXACT_KERNEL_PATH,
        "numerical_kernel": NUMERICAL_KERNEL_PATH,
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if observed_hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {observed_hashes}")

    monitor = RssMonitor()
    monitor.start()
    total_started = time.perf_counter()
    builder = load_module("codex_r10_reduced_canonical_base", BASE_PATH)
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    row_reduction = np.load(ROW_REDUCTION_PATH, allow_pickle=False)
    exact_kernel = np.load(EXACT_KERNEL_PATH, allow_pickle=False)
    numerical_kernel = np.load(NUMERICAL_KERNEL_PATH, allow_pickle=False)

    g = unpack_csr(numerical_kernel, "numerical_basis", np.float64)
    affine_nu = unpack_csr(row_reduction, "affine_nu", np.float64)
    affine_q = unpack_csr(row_reduction, "affine_gram", np.float64)
    affine_rhs = row_reduction["affine_rhs"].astype(np.float64)
    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_offsets = exact_kernel["face_column_offsets"].astype(np.int64)
    if g.shape != (8647, 2518):
        raise AssertionError("numerical kernel shape mismatch")
    if affine_nu.shape != (388, 526):
        raise AssertionError("affine nu shape mismatch")
    if affine_q.shape != (388, 8647):
        raise AssertionError("affine Gram shape mismatch")
    if affine_rhs.shape != (388,):
        raise AssertionError("affine RHS shape mismatch")
    if numerical_kernel["role"].tolist() != [
        "numerical-only direct-H QR; never an exact certificate"
    ]:
        raise AssertionError("numerical artifact role mismatch")

    free_by_block = free_coordinates(blowup, base)
    quotient_orders = [len(free) for free in free_by_block]
    expected_orders = Counter(
        {
            154: 1,
            40: 1,
            35: 1,
            33: 1,
            32: 2,
            11: 1,
            8: 2,
            7: 2,
            6: 7,
            5: 3,
            4: 5,
            1: 16,
            0: 10,
        }
    )
    if Counter(quotient_orders) != expected_orders:
        raise AssertionError("quotient order histogram mismatch")
    for block, orbit in enumerate(base.gram_orbits):
        if int(q_dimensions[block]) != int(orbit.variable.size):
            raise AssertionError(f"block {block}: q ordering mismatch")
        if int(face_dimensions[block]) > (
            quotient_orders[block] * (quotient_orders[block] + 1) // 2
        ):
            raise AssertionError(
                f"block {block}: invariant face exceeds Sym quotient"
            )

    transform_started = time.perf_counter()
    affine_y = (affine_q @ g).tocsr()
    affine_reduced = sp.hstack([affine_nu, affine_y], format="csr")
    transform_seconds = time.perf_counter() - transform_started
    if affine_y.shape != (388, 2518):
        raise AssertionError("transformed affine shape mismatch")
    singular_values = np.linalg.svd(
        affine_reduced.toarray(), compute_uv=False
    )
    numerical_affine_rank = int(
        np.count_nonzero(
            singular_values
            > singular_values[0]
            * max(affine_reduced.shape)
            * np.finfo(np.float64).eps
        )
    )
    if numerical_affine_rank != 388:
        raise AssertionError(
            f"transformed affine numerical rank={numerical_affine_rank}"
        )

    build_started = time.perf_counter()
    nu = cp.Variable(526, name="live_multiplier_orbits")
    y = cp.Variable(2518, name="gram_face_coordinates")
    margin = cp.Variable(name="relative_margin")
    constraints: list[cp.Constraint] = [
        affine_nu @ nu + affine_y @ y == affine_rhs,
        nu >= margin,
        margin >= 0,
    ]
    scalar_quotient_constraints = 0
    psd_quotient_constraints = 0
    psd_orders: list[int] = []
    for block, (orbit, free) in enumerate(
        zip(base.gram_orbits, free_by_block)
    ):
        order = len(free)
        if order == 0:
            continue
        q0 = int(q_offsets[block])
        qdim = int(q_dimensions[block])
        f0 = int(face_offsets[block])
        fdim = int(face_dimensions[block])
        local_q = g[q0 : q0 + qdim, f0 : f0 + fdim] @ y[f0 : f0 + fdim]
        ids = orbit.entry_ids[np.ix_(free, free)].astype(np.int64)
        if order == 1:
            constraints.append(local_q[int(ids[0, 0])] >= margin)
            scalar_quotient_constraints += 1
            continue
        principal = cp.reshape(
            local_q[ids.reshape(-1)],
            (order, order),
            order="C",
        )
        constraints.append(principal - margin * np.eye(order) >> 0)
        psd_quotient_constraints += 1
        psd_orders.append(order)
    problem = cp.Problem(cp.Maximize(margin), constraints)
    if not problem.is_dcp():
        raise AssertionError("reduced SDP is not DCP")
    build_seconds = time.perf_counter() - build_started

    canonical_started = time.perf_counter()
    canonical_data, _chain, _inverse = problem.get_problem_data(cp.CLARABEL)
    canonical_seconds = time.perf_counter() - canonical_started
    a_matrix = canonical_data["A"].tocsc()
    b_vector = np.asarray(canonical_data["b"])
    c_vector = np.asarray(canonical_data["c"])
    dims = canonical_data["dims"]
    if a_matrix.shape[1] != 3045:
        raise AssertionError(
            f"canonical variable count={a_matrix.shape[1]}, expected 3045"
        )
    if int(dims.zero) != 388:
        raise AssertionError(f"canonical zero cone={dims.zero}")
    if int(dims.nonneg) != 543:
        raise AssertionError(f"canonical nonnegative cone={dims.nonneg}")
    if list(map(int, dims.psd)) != psd_orders:
        raise AssertionError(
            f"canonical PSD order mismatch: {dims.psd} != {psd_orders}"
        )
    if dims.soc or int(dims.exp) or dims.p3d:
        raise AssertionError("unexpected non-SDP cones")
    expected_rows = (
        int(dims.zero)
        + int(dims.nonneg)
        + sum(order * (order + 1) // 2 for order in dims.psd)
    )
    if a_matrix.shape != (expected_rows, 3045):
        raise AssertionError(
            f"canonical A shape={a_matrix.shape}, expected "
            f"{(expected_rows, 3045)}"
        )
    if b_vector.shape != (expected_rows,) or c_vector.shape != (3045,):
        raise AssertionError("canonical vector dimensions mismatch")
    if (
        not np.all(np.isfinite(a_matrix.data))
        or not np.all(np.isfinite(b_vector))
        or not np.all(np.isfinite(c_vector))
    ):
        raise AssertionError("canonical data contain non-finite values")

    start_rss, end_rss, peak_rss = monitor.stop()
    summary = {
        "status": "PASS",
        "scope": "CVXPY canonicalization only; no SDP solve",
        "exactness_boundary": (
            "G and canonical data are numerical steering only; exact "
            "reconstruction must use the sealed exact-Z archive"
        ),
        "input_sha256": observed_hashes,
        "software": {
            "cvxpy": cp.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "solver_target": "CLARABEL",
        },
        "model": {
            "variables": 3045,
            "live_multiplier_variables": 526,
            "gram_face_variables": 2518,
            "margin_variables": 1,
            "forced_multiplier_variables_removed": 2085,
            "H_equalities_removed": 6129,
            "retained_affine_equalities": 388,
            "scalar_quotient_inequalities": scalar_quotient_constraints,
            "PSD_quotient_cones": psd_quotient_constraints,
            "PSD_orders": psd_orders,
            "quotient_order_histogram": {
                str(key): value
                for key, value in sorted(
                    Counter(quotient_orders).items(), reverse=True
                )
            },
        },
        "affine_transform": {
            "shape": list(affine_reduced.shape),
            "nnz": int(affine_reduced.nnz),
            "numerical_rank": numerical_affine_rank,
            "largest_singular_value": float(singular_values[0]),
            "smallest_singular_value": float(singular_values[-1]),
            "condition_2": float(
                singular_values[0] / singular_values[-1]
            ),
        },
        "canonical_form": {
            "A_shape": list(a_matrix.shape),
            "A_nnz": int(a_matrix.nnz),
            "A_data_bytes": int(a_matrix.data.nbytes),
            "A_csc_bytes": int(
                a_matrix.data.nbytes
                + a_matrix.indices.nbytes
                + a_matrix.indptr.nbytes
            ),
            "b_length": int(b_vector.size),
            "c_length": int(c_vector.size),
            "zero_cone": int(dims.zero),
            "nonnegative_cone": int(dims.nonneg),
            "PSD_cones": list(map(int, dims.psd)),
            "SOC_cones": list(map(int, dims.soc)),
            "exponential_cones": int(dims.exp),
            "power_cones": list(dims.p3d),
        },
        "timing_seconds": {
            "affine_transform": transform_seconds,
            "cvxpy_model_build": build_seconds,
            "canonicalization": canonical_seconds,
            "total": time.perf_counter() - total_started,
        },
        "memory_bytes": {
            "rss_start": start_rss,
            "rss_end": end_rss,
            "rss_peak_sampled": peak_rss,
            "rss_peak_delta": peak_rss - start_rss,
            "resource_cap": 192 * 1024**3,
            "under_resource_cap": peak_rss < 192 * 1024**3,
        },
        "solver_called": False,
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# Reduced plateau SDP: canonicalization-only result",
        "",
        "PASS. CVXPY canonicalized the corrected 3,045-variable model for",
        "Clarabel. No SDP solver was called.",
        "",
        f"- affine equalities: `{dims.zero}`",
        f"- nonnegative cone: `{dims.nonneg}`",
        f"- PSD cone orders: `{list(map(int, dims.psd))}`",
        f"- canonical `A`: `{list(a_matrix.shape)}`, nnz `{a_matrix.nnz}`",
        f"- canonicalization: `{canonical_seconds:.6f}` seconds",
        f"- sampled peak RSS: `{peak_rss}` bytes",
        f"- 192 GiB cap respected: `{peak_rss < 192 * 1024**3}`",
        "",
        "The numerical direct-H basis is steering data only. Exact replay",
        "must use the separately sealed exact-Z artifact.",
        "",
    ]
    REPORT_PATH.write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"SUMMARY={SUMMARY_PATH}")
    print(f"REPORT={REPORT_PATH}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_SUMMARY={sha256(SUMMARY_PATH)}")
    print(f"SHA256_REPORT={sha256(REPORT_PATH)}")
    print("REDUCED_SDP_CANONICALIZATION_PASS: solver_called=false")


if __name__ == "__main__":
    main()
