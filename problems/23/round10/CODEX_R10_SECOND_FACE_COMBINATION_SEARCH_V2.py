"""Continue the exact derivative-exposure search after removing zero rays."""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
CORE_PATH = HERE / "CODEX_R10_SECOND_FACE_COMBINATION_SEARCH.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def lcm(left: int, right: int) -> int:
    import math

    return abs(left * right) // math.gcd(left, right)


def main() -> None:
    core = load("codex_r10_second_face_combo_core", CORE_PATH)
    search = core.load_module(
        "codex_r10_second_face_derivative_core", core.SEARCH_PATH
    )
    builder = search.load_module(
        "codex_r10_second_face_combo_v2_builder", search.BASE_PATH
    )
    model = builder.build_model()
    equality = np.load(search.EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    exponents = np.asarray(model.multiplier_monomials, dtype=np.int64)

    rows = []
    labels = []
    zero_rays = 0
    for point_index, a in enumerate(points):
        support = np.flatnonzero(a)
        for local_left, left in enumerate(support):
            for right in support[local_left + 1 :]:
                h = np.zeros(11, dtype=np.int64)
                h[left] = 1
                h[right] = -1
                row = core.exact_coefficients(
                    search, model, exponents, a, h
                )[live]
                if np.all(row == 0):
                    zero_rays += 1
                    continue
                rows.append(row)
                labels.append((point_index, int(left), int(right)))
    exact_rows = np.asarray(rows, dtype=np.int64)
    print(
        f"nonzero_candidates={len(rows)} zero_rays={zero_rays}"
        f" live={len(live)}"
    )

    column_scale = np.maximum(
        1.0, np.max(np.abs(exact_rows), axis=0).astype(float)
    )
    numerical_rows = exact_rows.astype(float) / column_scale[None, :]
    number = len(rows)
    result = linprog(
        np.r_[np.zeros(number), 1.0],
        A_ub=np.c_[
            numerical_rows.T,
            -np.ones(len(live), dtype=float),
        ],
        b_ub=np.zeros(len(live)),
        A_eq=np.r_[np.ones(number), 0.0][None, :],
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

    selected_rows = exact_rows[support].astype(object)
    selected_values = result.x[support]
    for denominator_bound in (
        100,
        1000,
        10000,
        100000,
        1000000,
        10000000,
    ):
        rational = [
            Fraction(float(value)).limit_denominator(denominator_bound)
            for value in selected_values
        ]
        common = 1
        for value in rational:
            common = lcm(common, value.denominator)
        weights = np.asarray(
            [
                value.numerator * (common // value.denominator)
                for value in rational
            ],
            dtype=object,
        )
        total = weights @ selected_rows
        positive = sum(value > 0 for value in total)
        negative = sum(value < 0 for value in total)
        zero = sum(value == 0 for value in total)
        print(
            f"RATIONAL bound={denominator_bound}"
            f" positive={positive} negative={negative} zero={zero}"
        )
        if positive == 0 and negative:
            forced = live[
                np.fromiter(
                    (value < 0 for value in total),
                    dtype=bool,
                    count=len(total),
                )
            ]
            print(
                "EXACT_EXPOSURE"
                f" support={len(support)}"
                f" common_denominator={common}"
                f" weights={weights.tolist()}"
                f" labels={[labels[int(index)] for index in support]}"
                f" newly_forced={forced.tolist()}"
            )
            return


if __name__ == "__main__":
    main()
