"""Sparse exact-face feasibility model for the R10 Gamma_11 D22 cone.

This replaces the dense projector/margin scaffold.  It keeps the original
fixed-c model unchanged:

    Gamma_11, c=25, d=2 (degree-4 multipliers),
    all 56 cyclic-interval cuts,
    the original D22-reduced PSD blocks and coefficient identities.

It adds only two exact face restrictions independently derived from all 33
tight induced C5 supports:

* F1: 1,147 multiplier-orbit coordinates are exactly zero.
* F2: H q = 0, where H is the exact integer CSR matrix of 1,471 independent
  Gram-kernel equations and q concatenates the 8,647 representative
  Gram-entry orbit variables.

This is intentionally a C5-only face scaffold, not yet a solver-ready full
equality face.  The exact weighting

    (2,1,1,0,2,0,1,1,2,0,0)

has total 10 and arc value 4 = 10^2/25, so it forces additional F1/F2 rows.

There are no dense rational projectors, no extra margin PSD cones, and no
optimization objective beyond feasibility.  Default execution is build-only;
this module intentionally contains no solver call.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cvxpy as cp
import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
FACE_DATA_PATH = HERE / "CODEX_R10_c5_FACE_data.npz"
EXPECTED_FACE_DATA_SHA256 = (
    "86EBAE7DEA9AE43C435B27641971902479085BDDE8EAFF1D504A5C12EC693077"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "codex_r10_d22_sparse_base", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the D22 base constructor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def csr_from_archive(archive, prefix: str) -> sp.csr_matrix:
    shape = tuple(int(value) for value in archive[f"{prefix}_shape"])
    return sp.csr_matrix(
        (
            archive[f"{prefix}_data"],
            archive[f"{prefix}_indices"],
            archive[f"{prefix}_indptr"],
        ),
        shape=shape,
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    difference = (left.tocsr() - right.tocsr()).tocsr()
    difference.eliminate_zeros()
    return difference.nnz == 0


@dataclass
class SparseFaceModel:
    builder: object
    base: object
    forced_multiplier_orbits: np.ndarray
    live_multiplier_orbits: np.ndarray
    gram_offsets: np.ndarray
    gram_qdims: np.ndarray
    gram_face: sp.csr_matrix
    gram_vector: cp.Expression
    problem: cp.Problem
    face_data_sha256: str


def build_sparse_face_model() -> SparseFaceModel:
    data_hash = sha256(FACE_DATA_PATH)
    if data_hash != EXPECTED_FACE_DATA_SHA256:
        raise AssertionError(
            f"face-data SHA-256 mismatch: {data_hash} != {EXPECTED_FACE_DATA_SHA256}"
        )
    archive = np.load(FACE_DATA_PATH, allow_pickle=False)
    if int(archive["format_version"][0]) != 1:
        raise AssertionError("unsupported face-data format")
    expected_scalars = {
        "n": 11,
        "c_fixed": 25,
        "multiplier_degree": 4,
        "target_degree": 6,
    }
    for key, expected in expected_scalars.items():
        actual = int(archive[key][0])
        if actual != expected:
            raise AssertionError(f"{key}={actual}, expected {expected}")

    builder = load_builder()
    base = builder.build_model()
    if len(base.edges) != 22 or len(base.cuts) != 56:
        raise AssertionError("base model is not Gamma_11 with 56 interval cuts")
    if not np.array_equal(archive["edges"], np.asarray(base.edges, dtype=np.int32)):
        raise AssertionError("face-data edge ordering differs from the base model")
    if not np.array_equal(
        archive["cut_masks"],
        np.asarray([mask for mask, _mono in base.cuts], dtype=np.int32),
    ):
        raise AssertionError("face-data cut ordering differs from the base model")

    forced = np.asarray(archive["forced_multiplier_orbits"], dtype=np.int32)
    live = np.asarray(archive["live_multiplier_orbits"], dtype=np.int32)
    number_multiplier_orbits = int(base.multiplier_variable.size)
    if len(forced) != 1147 or len(live) != 1464:
        raise AssertionError("unexpected F1 orbit counts")
    if set(map(int, forced)) & set(map(int, live)):
        raise AssertionError("forced and live multiplier orbit lists overlap")
    if sorted(map(int, np.concatenate((forced, live)))) != list(
        range(number_multiplier_orbits)
    ):
        raise AssertionError("forced/live multiplier lists do not partition all orbits")

    offsets = np.asarray(archive["gram_offsets"], dtype=np.int32)
    qdims = np.asarray(archive["gram_qdims"], dtype=np.int32)
    rep_masks = np.asarray(archive["gram_rep_masks"], dtype=np.int8)
    if len(offsets) != len(base.gram_orbits) or len(qdims) != len(base.gram_orbits):
        raise AssertionError("Gram orbit count mismatch")
    running_offset = 0
    for orbit_index, orbit in enumerate(base.gram_orbits):
        if int(offsets[orbit_index]) != running_offset:
            raise AssertionError("Gram offset mismatch")
        if int(qdims[orbit_index]) != int(orbit.variable.size):
            raise AssertionError("Gram orbit dimension mismatch")
        if not np.array_equal(
            rep_masks[orbit_index], np.asarray(orbit.parity_rep, dtype=np.int8)
        ):
            raise AssertionError("Gram parity representative mismatch")
        running_offset += int(orbit.variable.size)
    if running_offset != 8647:
        raise AssertionError(f"expected 8647 Gram orbit scalars, got {running_offset}")

    gram_face = csr_from_archive(archive, "gram_face")
    if gram_face.shape != (1471, 8647):
        raise AssertionError(f"unexpected Gram-face shape {gram_face.shape}")
    if gram_face.data.dtype.kind not in "iu":
        raise AssertionError("Gram-face matrix is not integral")
    if gram_face.nnz != 28770:
        raise AssertionError(f"unexpected Gram-face nnz {gram_face.nnz}")

    # Cross-check every archived reduced coefficient matrix against the live
    # constructor.  This independently protects all variable orderings used by H.
    archived_normalization = csr_from_archive(archive, "normalization_live")
    archived_target_nu = csr_from_archive(archive, "target_nu_live")
    archived_target_gram = csr_from_archive(archive, "target_gram")
    if not sparse_equal(
        archived_normalization,
        base.multiplier_normalization[:, live],
    ):
        raise AssertionError("archived normalization matrix does not match the base model")
    if not sparse_equal(
        archived_target_nu,
        base.multiplier_target[:, live],
    ):
        raise AssertionError("archived multiplier target matrix does not match the base model")
    live_target_gram = sp.hstack(
        [orbit.coefficient_map for orbit in base.gram_orbits],
        format="csr",
    )
    if not sparse_equal(archived_target_gram, live_target_gram):
        raise AssertionError("archived Gram target matrix does not match the base model")

    gram_vector = cp.hstack([orbit.variable for orbit in base.gram_orbits])
    if gram_vector.shape != (8647,):
        raise AssertionError(f"unexpected concatenated Gram shape {gram_vector.shape}")
    constraints = list(base.problem.constraints)
    constraints.append(base.multiplier_variable[forced] == 0)
    constraints.append(gram_face @ gram_vector == 0)
    problem = cp.Problem(cp.Minimize(0), constraints)
    if not problem.is_dcp():
        raise AssertionError("sparse face feasibility model is not DCP")

    print(
        "SPARSE_FACE_BUILD graph=Gamma_11 c=25 d=2 cuts=56 "
        f"nu_orbits={number_multiplier_orbits} gram_orbits={len(base.gram_orbits)}"
    )
    print(
        f"SPARSE_FACE_F1 forced={len(forced)} live={len(live)} "
        f"partition={len(forced) + len(live)}"
    )
    print(
        f"SPARSE_FACE_F2 shape={gram_face.shape} nnz={gram_face.nnz} "
        f"rank_rows=1471 gram_scalars={running_offset}"
    )
    print(
        f"SPARSE_FACE_DATA_SHA256={data_hash} "
        "COEFFICIENT_ORDER_AUDIT=passed"
    )
    return SparseFaceModel(
        builder=builder,
        base=base,
        forced_multiplier_orbits=forced,
        live_multiplier_orbits=live,
        gram_offsets=offsets,
        gram_qdims=qdims,
        gram_face=gram_face,
        gram_vector=gram_vector,
        problem=problem,
        face_data_sha256=data_hash,
    )


def main() -> None:
    start = time.perf_counter()
    build_sparse_face_model()
    print(f"SPARSE_FACE_BUILD_SECONDS={time.perf_counter() - start:.3f}")
    print(
        "SPARSE_FACE_INCOMPLETE: C5-only face; full small-denominator equality face required"
    )
    print("SPARSE_FACE_BUILD_ONLY: no solver launched and no file written")


if __name__ == "__main__":
    main()
