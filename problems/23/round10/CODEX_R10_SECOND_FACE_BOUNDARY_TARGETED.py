"""Target the 14 numerically vanishing multipliers with exact boundary rays."""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
BOUNDARY_PATH = HERE / "CODEX_R10_SECOND_FACE_BOUNDARY_DERIVATIVE_SEARCH.py"
TARGETS = {
    1594,
    2075,
    2123,
    2101,
    1597,
    2105,
    1706,
    2582,
    2439,
    2038,
    2498,
    1361,
    1633,
    1636,
}


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
    boundary = load("codex_r10_second_face_boundary_target_core", BOUNDARY_PATH)
    core = boundary.load(
        "codex_r10_second_face_boundary_target_combo", boundary.CORE_PATH
    )
    search = core.load_module(
        "codex_r10_second_face_boundary_target_derivative", core.SEARCH_PATH
    )
    builder = search.load_module(
        "codex_r10_second_face_boundary_target_builder", search.BASE_PATH
    )
    model = builder.build_model()
    equality = np.load(search.EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    exponents = np.asarray(model.multiplier_monomials, dtype=np.int64)
    target_positions = np.asarray(
        [index for index, orbit in enumerate(live) if int(orbit) in TARGETS],
        dtype=np.int32,
    )
    assert len(target_positions) == 14

    rows = []
    labels = []
    for point_index, a in enumerate(points):
        support = np.flatnonzero(a)
        outside = np.flatnonzero(a == 0)
        for entering in outside:
            for leaving in support:
                h = np.zeros(11, dtype=np.int64)
                h[entering] = 1
                h[leaving] = -1
                row = boundary.boundary_coefficients(
                    core, search, model, exponents, a, h
                )[live]
                if np.all(row == 0):
                    continue
                divisor = int(np.gcd.reduce(np.abs(row)))
                rows.append(row // max(1, divisor))
                labels.append((point_index, int(entering), int(leaving)))
    exact_rows = np.asarray(rows, dtype=np.int64)
    scale = np.maximum(
        1.0, np.max(np.abs(exact_rows), axis=0).astype(float)
    )
    numerical = exact_rows.astype(float) / scale[None, :]
    objective = np.sum(numerical[:, target_positions], axis=1)
    result = linprog(
        objective,
        A_ub=numerical.T,
        b_ub=np.zeros(len(live)),
        A_eq=np.ones((1, len(rows))),
        b_eq=np.ones(1),
        bounds=[(0.0, None)] * len(rows),
        method="highs",
        options={
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
            "ipm_optimality_tolerance": 1e-10,
        },
    )
    print(
        f"rays={len(rows)} success={result.success}"
        f" status={result.status} target_objective="
        f"{None if not result.success else result.fun:.12e}"
    )
    if not result.success or result.fun >= -1e-9:
        return
    support = np.flatnonzero(result.x > 1e-9)
    selected_rows = exact_rows[support].astype(object)
    selected_values = result.x[support]
    print(
        "LP_SUPPORT "
        + " ".join(
            f"{int(index)}:{selected_values[position]:.12g}:{labels[int(index)]}"
            for position, index in enumerate(support)
        )
    )
    for bound in (100, 1000, 10000, 100000, 1000000, 10000000):
        fractions = [
            Fraction(float(value)).limit_denominator(bound)
            for value in selected_values
        ]
        common = 1
        for value in fractions:
            common = lcm(common, value.denominator)
        weights = np.asarray(
            [
                value.numerator * (common // value.denominator)
                for value in fractions
            ],
            dtype=object,
        )
        total = weights @ selected_rows
        positive = sum(value > 0 for value in total)
        negative = sum(value < 0 for value in total)
        print(
            f"RATIONAL bound={bound} positive={positive}"
            f" negative={negative}"
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
                f" weights={weights.tolist()}"
                f" labels={[labels[int(index)] for index in support]}"
                f" newly_forced={forced.tolist()}"
            )
            return


if __name__ == "__main__":
    main()
