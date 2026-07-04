import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe


CORE = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_v1.jsonl")
CORE_SOLUTION = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_192prime_solution_v1.jsonl")
OUT = Path("tmp/eq_odl1_rung2_source_solution_k8_G3_near_lexlarge_192prime_multirepair_v1.jsonl")
SUMMARY = Path("tmp/eq_odl1_rung2_source_solution_k8_G3_near_lexlarge_192prime_multirepair_v1_summary.json")


def compute_residual(prepared, columns, source_cols, sol):
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def coeff_at(columns, source_col, row):
    for rr, coeff in columns[source_col].terms:
        if rr == row:
            return coeff
    return Fraction(0)


def row_value(residual, columns, increments, row):
    delta = Fraction(0)
    for source_col, val in increments.items():
        delta += coeff_at(columns, source_col, row) * val
    return residual[row] - delta


def main():
    dim, source_cols, _selected_rows = fullcheck.read_core_maps(CORE)
    sol = fullcheck.read_solution(CORE_SOLUTION, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(8, 10, "near_2s_minus_1", "negative")
    residual = compute_residual(prepared, columns, source_cols, sol)

    used = [21562, 22555, 22772, 22926, 30363, 31747, 31829]

    t = residual[17234] / coeff_at(columns, used[1], 17234)
    u = residual[36401] / coeff_at(columns, used[3], 36401)
    increments = {
        used[0]: Fraction(10, 23) * t,
        used[1]: t,
        used[2]: Fraction(29, 92) * t,
        used[3]: u,
        used[4]: t,
        used[5]: Fraction(23, 20) * t,
        used[6]: t,
    }

    gate_rows = [36401, 17234, 17264, 17218, 16703, 17268, 17271, 15780, 7628]
    gate_values = {str(row): str(row_value(residual, columns, increments, row)) for row in gate_rows}

    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    for source_col, val in increments.items():
        vals[source_col] = vals.get(source_col, Fraction(0)) + val

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if val:
                f.write(json.dumps({
                    "source_col": source_col,
                    "num": val.numerator,
                    "den": val.denominator,
                }, sort_keys=True) + "\n")

    payload = {
        "schema": "eq_odl1_rung2_k8_g3_exact_multirepair_v1",
        "core": str(CORE),
        "core_solution": str(CORE_SOLUTION),
        "source_solution": str(OUT),
        "used_source_cols": used,
        "increments": {
            str(source_col): {"num": val.numerator, "den": val.denominator}
            for source_col, val in increments.items()
        },
        "gate_rows": gate_values,
        "nonzero_source_columns": sum(1 for val in vals.values() if val),
        "solution_negative_count": sum(1 for val in vals.values() if val < 0),
    }
    SUMMARY.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "source_solution": str(OUT),
        "summary": str(SUMMARY),
        "nonzero_source_columns": payload["nonzero_source_columns"],
        "solution_negative_count": payload["solution_negative_count"],
        "gate_rows": gate_values,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
