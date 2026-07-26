"""Search exact one-sided boundary derivative exposures of the C5 face.

Let ``a`` be a sealed C5 equality ray and let
``h=e_out-e_in``, where ``out`` is outside ``supp(a)`` and ``in`` is inside.
Then ``a+t*h`` remains in the nonnegative orthant for small ``t>=0`` and has
constant total mass.

On the already imposed C5 Gram face, the coefficient of ``t`` is PSD:
blocks supported at ``a`` have zero constant and linear terms because their
evaluation vector lies in the Gram kernel; blocks containing the entering
coordinate acquire a nonnegative linear monomial factor times a Gram square.
Thus a candidate whose live multiplier coefficients are all nonpositive is
an exact further exposing identity.

No conic solver is called and this script writes no files.
"""

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


def boundary_coefficients(core, search, model, exponents, a, h):
    m0, m1, _m2 = core.vectorized_monomial_coefficients(exponents, a, h)
    r0, r1, _r2 = search.cut_residual_coefficients(model, a, h)
    pair = r0[:, None] * m1[None, :] + r1[:, None] * m0[None, :]
    return np.bincount(
        model.multiplier_orbit_ids.reshape(-1),
        weights=pair.reshape(-1),
        minlength=2611,
    ).astype(np.int64)


def lcm(left: int, right: int) -> int:
    import math

    return abs(left * right) // math.gcd(left, right)


def main() -> None:
    core = load("codex_r10_second_face_boundary_core", CORE_PATH)
    search = core.load_module(
        "codex_r10_second_face_boundary_derivative", core.SEARCH_PATH
    )
    builder = search.load_module(
        "codex_r10_second_face_boundary_builder", search.BASE_PATH
    )
    model = builder.build_model()
    equality = np.load(search.EQUALITY_PATH, allow_pickle=False)
    points = equality["equality_representatives"].astype(np.int64)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    exponents = np.asarray(model.multiplier_monomials, dtype=np.int64)

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
                rows.append(
                    boundary_coefficients(
                        core, search, model, exponents, a, h
                    )[live]
                )
                labels.append(
                    (point_index, int(entering), int(leaving))
                )
    exact_rows = np.asarray(rows, dtype=np.int64)
    print(f"candidates={len(rows)} live={len(live)}")
    nonpositive = np.all(exact_rows <= 0, axis=1)
    nonzero = np.any(exact_rows < 0, axis=1)
    accepted = np.flatnonzero(nonpositive & nonzero)
    zero = int(np.count_nonzero(np.all(exact_rows == 0, axis=1)))
    print(f"individual_exposures={len(accepted)} zero_rays={zero}")
    for index in accepted[:50]:
        row = exact_rows[int(index)]
        forced = live[row < 0]
        print(
            f"EXACT_INDIVIDUAL index={int(index)}"
            f" label={labels[int(index)]}"
            f" newly_forced={forced.tolist()}"
        )
    if len(accepted):
        return

    useful = ~np.all(exact_rows == 0, axis=1)
    exact_rows = exact_rows[useful]
    labels = [label for label, keep in zip(labels, useful) if keep]
    column_scale = np.maximum(
        1.0, np.max(np.abs(exact_rows), axis=0).astype(float)
    )
    numerical_rows = exact_rows.astype(float) / column_scale[None, :]
    number = len(exact_rows)
    result = linprog(
        np.r_[np.zeros(number), 1.0],
        A_ub=np.c_[numerical_rows.T, -np.ones(len(live))],
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
    if not result.success or result.fun > 1e-8:
        return
    support = np.flatnonzero(result.x[:number] > 1e-9)
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
        values = [
            Fraction(float(value)).limit_denominator(bound)
            for value in selected_values
        ]
        common = 1
        for value in values:
            common = lcm(common, value.denominator)
        weights = np.asarray(
            [
                value.numerator * (common // value.denominator)
                for value in values
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
                "EXACT_COMBINATION"
                f" weights={weights.tolist()}"
                f" labels={[labels[int(index)] for index in support]}"
                f" newly_forced={forced.tolist()}"
            )
            return


if __name__ == "__main__":
    main()
