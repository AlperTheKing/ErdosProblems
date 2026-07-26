"""Numerical sparse-support probe for the new block-0 kernel."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import scipy.linalg as la


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rank(array: np.ndarray) -> int:
    singular = la.svdvals(array)
    if not singular.size:
        return 0
    return int(np.sum(singular > 1e-9 * singular[0]))


def main() -> None:
    builder = load_module("codex_r10_support_base", "CODEX_R10_g11_d22_sdp.py")
    canonical = load_module(
        "codex_r10_support_canonical",
        "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py",
    )
    model = builder.build_model()
    blowup = np.load(HERE / "CODEX_R10_BLOWUP_FACE_data.npz")
    dual = np.load(
        HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"
    )
    basis = model.gram_orbits[0].basis
    free = canonical.free_coordinates(blowup, model)[0]
    kernel = np.asarray(
        [
            [int(value) for value in json.loads(str(encoded))[1]]
            for encoded in blowup["kernel_rows_json"]
            if int(json.loads(str(encoded))[0]) == 0
        ],
        dtype=float,
    )
    pivot = sorted(set(range(len(basis))) - set(free))
    quotient = np.zeros((len(basis), len(free)))
    quotient[pivot] = -la.solve(kernel[:, pivot], kernel[:, free])
    quotient[free] = np.eye(len(free))

    position = int(np.flatnonzero(dual["psd_block_indices"] == 0)[0])
    offsets = dual["psd_flat_offsets"].astype(int)
    matrix = dual["dual_psd_matrices_flat"][
        offsets[position] : offsets[position + 1]
    ].reshape((len(free), len(free)))
    _eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.T) / 2)
    target = eigenvectors[:, -22:]
    residual = quotient - (quotient @ target) @ target.T

    index = {tuple(exponent): i for i, exponent in enumerate(basis)}
    unseen = set(range(len(basis)))
    orbits: list[list[int]] = []
    while unseen:
        seed = min(unseen)
        orbit = sorted(
            {
                index[builder.exponent_image(basis[seed], element)]
                for element in builder.GROUP
            }
        )
        orbits.append(orbit)
        unseen.difference_update(orbit)

    hits = []
    for left in range(len(orbits)):
        for right in range(left, len(orbits)):
            support = sorted(set(orbits[left]) | set(orbits[right]))
            old_nullity = len(support) - rank(quotient[support])
            new_nullity = len(support) - rank(residual[support])
            gain = new_nullity - old_nullity
            if gain:
                hits.append(
                    (
                        len(support),
                        -gain,
                        left,
                        right,
                        old_nullity,
                        new_nullity,
                    )
                )

    print(f"coordinate_orbits={len(orbits)} support_hits={len(hits)}")
    for size, negative_gain, left, right, old, new in sorted(hits):
        left_rep = tuple(int(value // 2) for value in basis[orbits[left][0]])
        right_rep = tuple(int(value // 2) for value in basis[orbits[right][0]])
        print(
            f"SUPPORT size={size} gain={-negative_gain}"
            f" old_nullity={old} new_nullity={new}"
            f" left={left}:{left_rep} right={right}:{right_rep}"
        )


if __name__ == "__main__":
    main()
