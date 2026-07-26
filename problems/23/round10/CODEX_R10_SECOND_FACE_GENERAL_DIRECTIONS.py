"""Search the exact derivative-exposure cone using all ternary directions.

For each sealed equality ray through q=20, enumerate every primitive,
support-preserving h in {-1,0,1}^supp with sum(h)=0, modulo h -> -h.
The resulting rows are exact coefficient-of-t^2 functionals on the already
sealed C5 face.  A numerical LP only selects candidates; any success is
rationally reconstructed and checked over the integers.

No SDP solver is called.
"""

from __future__ import annotations

import importlib.util
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
CORE_PATH = HERE / "CODEX_R10_SECOND_FACE_COMBINATION_SEARCH.py"
TARGET_ZERO_ORBITS = {
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


def primitive_ternary_directions(support: np.ndarray):
    for values in itertools.product((-1, 0, 1), repeat=len(support)):
        if not any(values) or sum(values) != 0:
            continue
        first = next(value for value in values if value)
        if first < 0:
            continue
        h = np.zeros(11, dtype=np.int64)
        h[support] = values
        yield h


def lcm(left: int, right: int) -> int:
    import math

    return abs(left * right) // math.gcd(left, right)


def main() -> None:
    core = load("codex_r10_second_face_general_core", CORE_PATH)
    search = core.load_module(
        "codex_r10_second_face_general_derivative", core.SEARCH_PATH
    )
    builder = search.load_module(
        "codex_r10_second_face_general_builder", search.BASE_PATH
    )
    model = builder.build_model()
    equality = np.load(search.EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    exponents = np.asarray(model.multiplier_monomials, dtype=np.int64)
    target_positions = np.asarray(
        [index for index, orbit in enumerate(live) if int(orbit) in TARGET_ZERO_ORBITS],
        dtype=np.int32,
    )
    other_positions = np.asarray(
        [index for index, orbit in enumerate(live) if int(orbit) not in TARGET_ZERO_ORBITS],
        dtype=np.int32,
    )
    assert len(target_positions) == 14 and len(other_positions) == 512

    labels = []
    rows = []
    row_keys = set()
    generated = zero = duplicate = 0
    for point_index, a in enumerate(points):
        if int(np.sum(a)) > 20:
            continue
        support = np.flatnonzero(a)
        for h in primitive_ternary_directions(support):
            generated += 1
            row = core.exact_coefficients(
                search, model, exponents, a, h
            )[live]
            if np.all(row == 0):
                zero += 1
                continue
            divisor = int(np.gcd.reduce(np.abs(row)))
            normalized = row // max(1, divisor)
            key = normalized.tobytes()
            if key in row_keys:
                duplicate += 1
                continue
            row_keys.add(key)
            rows.append(normalized)
            labels.append((point_index, tuple(map(int, h))))
    exact_rows = np.asarray(rows, dtype=np.int64)
    print(
        f"generated={generated} nonzero_unique={len(rows)}"
        f" zero={zero} duplicate={duplicate}"
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
        f"minimax_success={result.success} status={result.status}"
        f" scaled_max={result.fun:.12e}"
    )
    if not result.success:
        return
    support = np.flatnonzero(result.x[:number] > 1e-9)
    print(f"minimax_support={len(support)}")
    if result.fun > 1e-8:
        # A second targeted feasibility test asks for zero on the 512
        # numerically positive multipliers and negative mass on the 14 targets.
        target_objective = np.zeros(number)
        target_objective[:] = np.sum(
            numerical_rows[:, target_positions], axis=1
        )
        targeted = linprog(
            target_objective,
            A_ub=numerical_rows[:, target_positions].T,
            b_ub=np.zeros(len(target_positions)),
            A_eq=np.vstack(
                (
                    np.ones(number),
                    numerical_rows[:, other_positions].T,
                )
            ),
            b_eq=np.r_[1.0, np.zeros(len(other_positions))],
            bounds=[(0.0, None)] * number,
            method="highs",
            options={
                "dual_feasibility_tolerance": 1e-9,
                "primal_feasibility_tolerance": 1e-9,
            },
        )
        print(
            f"targeted_success={targeted.success}"
            f" status={targeted.status} message={targeted.message}"
        )
        return

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
        rationals = [
            Fraction(float(value)).limit_denominator(bound)
            for value in selected_values
        ]
        common = 1
        for value in rationals:
            common = lcm(common, value.denominator)
        weights = np.asarray(
            [
                value.numerator * (common // value.denominator)
                for value in rationals
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
