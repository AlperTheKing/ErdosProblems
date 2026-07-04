import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe

CORE = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_v1.jsonl")
SOLUTION = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_192prime_solution_v1.jsonl")
REPORT = Path("tmp/probe_k8_g3_repair_lp_scaled_tight_v1.json")


def compute_residual(prepared, columns, source_cols, sol):
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


dim, source_cols, _selected_rows = fullcheck.read_core_maps(CORE)
sol = fullcheck.read_solution(SOLUTION, dim)
prepared, columns, _mat, _b_ub = probe.build_lp(8, 10, "near_2s_minus_1", "negative")
residual = compute_residual(prepared, columns, source_cols, sol)
report = json.loads(REPORT.read_text())
last = report["history"][-1]
used = [(item["source_col"], item["t"]) for item in last["used_prefix"]]
active = set(report["initial_negative_rows"])
for h in report["history"]:
    active.update(h.get("violated_prefix", []))

delta = [0.0] * len(residual)
for source_col, t in used:
    for row, coeff in columns[source_col].terms:
        delta[row] += float(coeff) * float(t)
new_float = [float(r) - d for r, d in zip(residual, delta)]
tight_active = sorted(active, key=lambda r: abs(new_float[r]))
payload = {
    "used": used,
    "active_count": len(active),
    "tight_active_prefix": [
        {
            "row": r,
            "beta": list(prepared.betas[r]),
            "new_float": new_float[r],
            "residual": str(residual[r]),
            "coeffs": [str(next((c for rr, c in columns[col].terms if rr == r), Fraction(0))) for col, _t in used],
        }
        for r in tight_active[:80]
    ],
}
Path("tmp/probe_k8_g3_repair_tight_rows_tight_v1.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))

