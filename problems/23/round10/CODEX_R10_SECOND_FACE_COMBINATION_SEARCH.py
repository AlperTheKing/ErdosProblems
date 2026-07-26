"""Finite search for a positive combination of exact derivative exposures.

The candidate rays are the coefficient-of-t^2 functionals at every sealed
C5-plateau representative ``a`` along every support-preserving pair direction
``e_i-e_j``.  Each candidate is PSD on the Gram cone after the first face.

A numerical LP is used only to select a small support.  Any reported exposure
is reconstructed with rational weights and then checked by exact integer
arithmetic.  No SDP solver is called.
"""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
SEARCH_PATH = HERE / "CODEX_R10_SECOND_FACE_DERIVATIVE_SEARCH.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def vectorized_monomial_coefficients(
    exponent_matrix: np.ndarray, a: np.ndarray, h: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact int64 coefficients through t^2 for every degree-four monomial."""
    c0 = np.ones(exponent_matrix.shape[0], dtype=np.int64)
    c1 = np.zeros_like(c0)
    c2 = np.zeros_like(c0)
    for vertex in range(exponent_matrix.shape[1]):
        power = exponent_matrix[:, vertex]
        ai = int(a[vertex])
        hi = int(h[vertex])
        f0 = np.power(ai, power, dtype=np.int64)
        f1 = np.where(
            power >= 1,
            power * np.power(ai, np.maximum(power - 1, 0), dtype=np.int64) * hi,
            0,
        )
        f2 = np.where(
            power >= 2,
            (power * (power - 1) // 2)
            * np.power(ai, np.maximum(power - 2, 0), dtype=np.int64)
            * hi
            * hi,
            0,
        )
        c0, c1, c2 = (
            c0 * f0,
            c1 * f0 + c0 * f1,
            c2 * f0 + c1 * f1 + c0 * f2,
        )
    return c0, c1, c2


def exact_coefficients(search, model, exponent_matrix, a, h):
    m0, m1, m2 = vectorized_monomial_coefficients(
        exponent_matrix, a, h
    )
    r0, r1, r2 = search.cut_residual_coefficients(model, a, h)
    pair = (
        r0[:, None] * m2[None, :]
        + r1[:, None] * m1[None, :]
        + r2[:, None] * m0[None, :]
    )
    return np.bincount(
        model.multiplier_orbit_ids.reshape(-1),
        weights=pair.reshape(-1),
        minlength=2611,
    ).astype(np.int64)


def rationalize_positive_weights(values: np.ndarray, denominator: int):
    weights = [
        Fraction(float(value)).limit_denominator(denominator)
        for value in values
    ]
    total = sum(weights, Fraction(0))
    if total == 0:
        raise AssertionError("zero reconstructed weight vector")
    return [weight / total for weight in weights]


def exact_weighted_sum(rows: np.ndarray, weights: list[Fraction]):
    common = 1
    for weight in weights:
        common = np.lcm(common, weight.denominator)
    integer_weights = np.asarray(
        [weight.numerator * (common // weight.denominator) for weight in weights],
        dtype=object,
    )
    total = integer_weights @ rows.astype(object)
    return integer_weights, np.asarray(total, dtype=object)


def main() -> None:
    search = load_module("codex_r10_second_face_search_core", SEARCH_PATH)
    builder = search.load_module("codex_r10_second_face_combo_builder", search.BASE_PATH)
    model = builder.build_model()
    equality = np.load(search.EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    exponent_matrix = np.asarray(model.multiplier_monomials, dtype=np.int64)

    labels = []
    rows = []
    for point_index, a in enumerate(points):
        support = np.flatnonzero(a)
        for local_left, left in enumerate(support):
            for right in support[local_left + 1 :]:
                h = np.zeros(11, dtype=np.int64)
                h[left] = 1
                h[right] = -1
                coefficients = exact_coefficients(
                    search, model, exponent_matrix, a, h
                )
                rows.append(coefficients[live])
                labels.append((point_index, int(left), int(right)))
    rows_array = np.asarray(rows, dtype=np.int64)
    print(
        f"candidates={len(rows)} live={len(live)}"
        f" bytes={rows_array.nbytes}"
    )

    individual_positive = np.count_nonzero(rows_array > 0, axis=1)
    accepted = np.flatnonzero(individual_positive == 0)
    print(f"individual_exposures={len(accepted)}")
    for index in accepted[:20]:
        row = rows_array[index]
        print(
            f"INDIVIDUAL index={int(index)} label={labels[int(index)]}"
            f" negative={int(np.count_nonzero(row < 0))}"
        )
    if len(accepted):
        return

    scale = np.maximum(1.0, np.max(np.abs(rows_array), axis=0).astype(float))
    matrix = rows_array.astype(float) / scale[None, :]
    number = len(rows)
    objective = np.r_[np.zeros(number), 1.0]
    inequalities = np.c_[matrix.T, -np.ones(len(live))]
    equality_matrix = np.r_[np.ones(number), 0.0][None, :]
    result = linprog(
        objective,
        A_ub=inequalities,
        b_ub=np.zeros(len(live)),
        A_eq=equality_matrix,
        b_eq=np.ones(1),
        bounds=[(0.0, None)] * number + [(None, None)],
        method="highs",
        options={
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
            "ipm_optimality_tolerance": 1e-10,
        },
    )
    print(
        f"lp_success={result.success} status={result.status}"
        f" scaled_max={result.fun:.12e}"
    )
    if not result.success:
        return
    support = np.flatnonzero(result.x[:number] > 1e-9)
    print(f"lp_support={len(support)}")
    print(
        "LP_WEIGHTS "
        + " ".join(
            f"{int(index)}:{result.x[int(index)]:.12g}:{labels[int(index)]}"
            for index in support
        )
    )
    if result.fun > 1e-8:
        return

    selected_rows = rows_array[support]
    selected_values = result.x[support]
    for denominator in (100, 1000, 10000, 100000, 1000000):
        weights = rationalize_positive_weights(selected_values, denominator)
        integer_weights, total = exact_weighted_sum(selected_rows, weights)
        positive = sum(value > 0 for value in total)
        negative = sum(value < 0 for value in total)
        zero = sum(value == 0 for value in total)
        print(
            f"RATIONAL denominator={denominator}"
            f" positive={positive} negative={negative} zero={zero}"
        )
        if positive == 0:
            newly_forced = live[
                np.asarray([value < 0 for value in total], dtype=bool)
            ]
            print(
                "EXACT_COMBINATION"
                f" support={len(support)}"
                f" integer_weights={integer_weights.tolist()}"
                f" labels={[labels[int(index)] for index in support]}"
                f" newly_forced={newly_forced.tolist()}"
            )
            return


if __name__ == "__main__":
    main()
