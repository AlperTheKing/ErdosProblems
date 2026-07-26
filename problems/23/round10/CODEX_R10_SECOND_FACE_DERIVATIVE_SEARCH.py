"""Search exact second-order exposing functionals on the sealed C5 face.

For an equality ray ``a`` and an integer direction ``h`` supported on
``supp(a)`` with ``sum(h)=0``, take the coefficient of ``t^2`` after
substituting ``x=a+t*h`` in the reduced polynomial identity.

On the already imposed C5 Gram face, the coefficient functional is positive
semidefinite on every Gram block: the constant evaluation vector is in the
kernel, so only the outer square of its first derivative remains.  If every
live multiplier coefficient is nonpositive, the resulting exact identity is
an exposing certificate for a further face.

This script performs no conic optimization and writes no files.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def monomial_coefficients(
    exponents: list[tuple[int, ...]], a: np.ndarray, h: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return coefficients of t^0,t^1,t^2 in (a+t*h)^beta."""
    out = np.zeros((3, len(exponents)), dtype=np.int64)
    for column, beta in enumerate(exponents):
        coefficients = [1, 0, 0]
        for ai, hi, power in zip(a, h, beta):
            if power == 0:
                continue
            factor = [
                math.comb(power, degree)
                * int(ai) ** (power - degree)
                * int(hi) ** degree
                for degree in range(min(2, power) + 1)
            ]
            product = [0, 0, 0]
            for left_degree in range(3):
                for right_degree, value in enumerate(factor):
                    if left_degree + right_degree <= 2:
                        product[left_degree + right_degree] += (
                            coefficients[left_degree] * value
                        )
            coefficients = product
        out[:, column] = coefficients
    return out[0], out[1], out[2]


def cut_residual_coefficients(model, a: np.ndarray, h: np.ndarray):
    """Return t^0,t^1,t^2 coefficients of L^2-25*q_S."""
    total0 = int(np.sum(a))
    total1 = int(np.sum(h))
    assert total1 == 0
    residual = np.empty((3, len(model.cuts)), dtype=np.int64)
    for cut_index, (_mask, monochromatic_edges) in enumerate(model.cuts):
        q0 = q1 = q2 = 0
        for edge_index in monochromatic_edges:
            u, v = model.edges[edge_index]
            q0 += int(a[u]) * int(a[v])
            q1 += int(a[u]) * int(h[v]) + int(h[u]) * int(a[v])
            q2 += int(h[u]) * int(h[v])
        residual[0, cut_index] = total0 * total0 - 25 * q0
        residual[1, cut_index] = 2 * total0 * total1 - 25 * q1
        residual[2, cut_index] = total1 * total1 - 25 * q2
    return residual


def exposing_coefficients(model, a: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Aggregate exact multiplier coefficients by D22 orbit."""
    m0, m1, m2 = monomial_coefficients(
        model.multiplier_monomials, a, h
    )
    r0, r1, r2 = cut_residual_coefficients(model, a, h)
    pair_coefficients = (
        r0[:, None] * m2[None, :]
        + r1[:, None] * m1[None, :]
        + r2[:, None] * m0[None, :]
    )
    return np.bincount(
        model.multiplier_orbit_ids.reshape(-1),
        weights=pair_coefficients.reshape(-1),
        minlength=2611,
    ).astype(np.int64)


def primitive(vector: np.ndarray) -> tuple[int, ...]:
    values = [int(value) for value in vector]
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(value))
    if divisor:
        values = [value // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return tuple(values)


def main() -> None:
    builder = load_module("codex_r10_second_face_builder", BASE_PATH)
    model = builder.build_model()
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)

    candidates: dict[tuple[tuple[int, ...], tuple[int, ...]], np.ndarray] = {}
    for a in points:
        if int(np.sum(a)) != 5:
            continue
        support = np.flatnonzero(a)
        for left in support:
            for right in support:
                if left >= right:
                    continue
                h = np.zeros(11, dtype=np.int64)
                h[left] = 1
                h[right] = -1
                key = (primitive(a), primitive(h))
                candidates[key] = exposing_coefficients(model, a, h)

    print(f"q5_pair_directions={len(candidates)}")
    accepted = []
    for (a, h), coefficients in candidates.items():
        live_coefficients = coefficients[live]
        positive = int(np.count_nonzero(live_coefficients > 0))
        negative = int(np.count_nonzero(live_coefficients < 0))
        zero = int(np.count_nonzero(live_coefficients == 0))
        if positive == 0:
            accepted.append((a, h, negative, zero, coefficients))
        print(
            "CANDIDATE"
            f" a={a} h={h} positive={positive}"
            f" negative={negative} zero={zero}"
            f" min={int(np.min(live_coefficients))}"
            f" max={int(np.max(live_coefficients))}"
        )
    print(f"accepted={len(accepted)}")
    for a, h, negative, zero, coefficients in accepted:
        newly_forced = live[coefficients[live] < 0]
        print(
            "EXPOSURE"
            f" a={a} h={h} newly_forced={len(newly_forced)}"
            f" ids={','.join(map(str, newly_forced.tolist()))}"
        )


if __name__ == "__main__":
    main()
