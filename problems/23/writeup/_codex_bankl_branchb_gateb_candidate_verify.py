#!/usr/bin/env python3
"""Verify the merged Branch-B Gate-B candidate manifest exactly.

This checker is deliberately stricter than the emitters.  It re-reads the
merged 14,247-row artifact and validates the acceptance-facing bookkeeping:
case totals, exact row identities, nonnegative rational terms, side/Gate-B
burden coverage, and op-step rho decompositions for the candidate Gate-B
section-6.1 certificate.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any

EXPECTED_CASES = {
    "TIGHT_ZERO": 34,
    "FREE_PACKET_EXCHANGE": 3688,
    "SPARSE_M1_BANKL_BYPASS": 9463,
    "MU_NUK": 800,
    "MU_NUK_REPAIRED": 126,
    "DETOUR_RESIDUAL": 136,
}
EXPECTED_TOTAL = sum(EXPECTED_CASES.values())
BURDEN_CASES = {"MU_NUK", "MU_NUK_REPAIRED", "DETOUR_RESIDUAL"}
OP_CASES = {"MU_NUK", "MU_NUK_REPAIRED"}
DIRECT_CASES = {"TIGHT_ZERO", "FREE_PACKET_EXCHANGE", "SPARSE_M1_BANKL_BYPASS"}
ALLOWED_DICT = {
    "B-connected-segment/noncrossing-coB",
    "detour_component_deficit",
    "sparse_m1_direct_identity",
    "terminal-prefix",
    "terminal-prefix/noncrossing-coB",
}
ALLOWED_OP_CLASS = {
    "empty",
    "noncrossing-coB-component-addition",
    "noncrossing-coB-extraction",
    "terminal-prefix-lane-addition",
    "terminal-prefix-raw-extraction",
}
ALLOWED_OP_DICT = {
    "noncrossing-coB-component-addition",
    "noncrossing-coB-extraction",
    "terminal-prefix-lane-addition",
    "terminal-prefix-raw-extraction",
}


def frac(x: Any) -> F:
    if x is None:
        raise TypeError("None is not a rational")
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x, 1)
    if isinstance(x, str):
        return F(x)
    raise TypeError(f"not rational-like: {x!r}")


def int_frac(x: Any) -> int:
    f = frac(x)
    if f.denominator != 1:
        raise ValueError(f"not integral: {x!r}")
    return f.numerator


def add_error(errors: list[dict[str, Any]], line_no: int, row: dict[str, Any], msg: str) -> None:
    if len(errors) < 40:
        errors.append({"line_no": line_no, "row_id": row.get("row_id"), "error": msg})


def verify_term(line_no: int, row: dict[str, Any], term: dict[str, Any], errors: list[dict[str, Any]]) -> F:
    value = frac(term.get("value"))
    coeff = frac(term.get("coeff"))
    contribution = frac(term.get("contribution"))
    if value < 0:
        add_error(errors, line_no, row, "negative_term_value")
    if coeff < 0:
        add_error(errors, line_no, row, "negative_term_coeff")
    if contribution != value * coeff:
        add_error(errors, line_no, row, "term_product_mismatch")
    dclass = ((term.get("dictionary") or {}).get("dictionary_class"))
    if dclass not in ALLOWED_DICT:
        add_error(errors, line_no, row, f"unknown_dictionary_class:{dclass}")
    return contribution


def verify_step(line_no: int, row: dict[str, Any], step: dict[str, Any], errors: list[dict[str, Any]]) -> tuple[int, int]:
    op_class = step.get("op_class")
    if op_class not in ALLOWED_OP_CLASS:
        add_error(errors, line_no, row, f"unknown_op_class:{op_class}")
    q = int(step.get("exchange_q"))
    q_formula = int(step.get("eB_XS")) - int(step.get("eM_XS")) - int(step.get("eB_XO")) + int(step.get("eM_XO"))
    if q != q_formula:
        add_error(errors, line_no, row, "op_quad_formula_mismatch")
    sigma_drop = int(step.get("sigma_before")) - int(step.get("sigma_after"))
    if q != sigma_drop:
        add_error(errors, line_no, row, "op_sigma_drop_mismatch")
    rho = int_frac(step.get("rho_a"))
    if rho != 25 * max(0, q):
        add_error(errors, line_no, row, "op_rho_formula_mismatch")
    decomp_sum = F(0)
    for d in step.get("dictionary_decomposition", []):
        dclass = d.get("dictionary_class")
        if dclass not in ALLOWED_OP_DICT:
            add_error(errors, line_no, row, f"unknown_op_dictionary_class:{dclass}")
        value = frac(d.get("value"))
        coeff = frac(d.get("coeff"))
        contribution = frac(d.get("contribution"))
        if value < 0 or coeff < 0 or contribution < 0:
            add_error(errors, line_no, row, "negative_op_decomp_piece")
        if value * coeff != contribution:
            add_error(errors, line_no, row, "op_decomp_product_mismatch")
        decomp_sum += contribution
    if decomp_sum != rho:
        add_error(errors, line_no, row, "op_decomp_sum_mismatch")
    if rho > 0 and not step.get("dictionary_decomposition"):
        add_error(errors, line_no, row, "positive_rho_without_decomposition")
    return q, rho


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_branchb_gateb_candidate_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_branchb_gateb_candidate_v1_verify_summary.json")
    args = ap.parse_args()

    counts: Counter[str] = Counter()
    case_counts: Counter[str] = Counter()
    op_class_counts: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    min_rho_margin: F | None = None
    pending_acceptance = 0

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            counts["rows"] += 1
            proof_case = row.get("case", {}).get("proof_case")
            case_counts[proof_case] += 1
            if proof_case not in EXPECTED_CASES:
                add_error(errors, line_no, row, f"unexpected_case:{proof_case}")
            row_target = frac(row.get("identity", {}).get("target"))
            term_sum = F(0)
            for term in row.get("terms", []):
                counts["terms"] += 1
                term_sum += verify_term(line_no, row, term, errors)
            if term_sum != row_target:
                add_error(errors, line_no, row, "row_identity_sum_mismatch")
            if not row.get("identity", {}).get("verified"):
                add_error(errors, line_no, row, "row_identity_flag_false")
            finite = row.get("finite_row_check") or {}
            if not finite.get("verified"):
                add_error(errors, line_no, row, "finite_row_check_false")
            if finite.get("rho_minus_target") is not None:
                margin = frac(finite.get("rho_minus_target"))
                min_rho_margin = margin if min_rho_margin is None or margin < min_rho_margin else min_rho_margin
                if margin < 0:
                    add_error(errors, line_no, row, "negative_rho_margin")
            burden = proof_case in BURDEN_CASES
            gateb = (row.get("gate_b_dictionary") or {}).get("candidate_v1") or {}
            if burden:
                counts["burden_rows"] += 1
                if proof_case == "DETOUR_RESIDUAL":
                    counts["detour_rows"] += 1
                    if gateb.get("status") != "complete_detour_residual":
                        add_error(errors, line_no, row, "detour_gateb_not_complete")
                elif proof_case in OP_CASES:
                    counts["op_rows"] += 1
                    status = gateb.get("status")
                    if status not in {"candidate_complete_awaiting_claude_acceptance", "accepted_complete"}:
                        add_error(errors, line_no, row, "missing_op_gateb_candidate")
                    if gateb.get("claude_acceptance") == "pending_two_phase_telescope_decision":
                        pending_acceptance += 1
                    opseq = gateb.get("op_sequence") or {}
                    steps = opseq.get("op_steps") or []
                    if not steps:
                        add_error(errors, line_no, row, "missing_op_steps")
                    q_sum = 0
                    rho_sum = 0
                    for step in steps:
                        counts["op_steps"] += 1
                        op_class_counts[step.get("op_class")] += 1
                        q, rho = verify_step(line_no, row, step, errors)
                        q_sum += q
                        rho_sum += rho
                    if q_sum != int(opseq.get("raw_sigma_drop")):
                        add_error(errors, line_no, row, "op_q_sum_raw_sigma_drop_mismatch")
                    if rho_sum != int_frac(opseq.get("op_sequence_rho_sum")):
                        add_error(errors, line_no, row, "op_rho_sum_stored_mismatch")
                    if rho_sum < int_frac(opseq.get("raw_to_final_rho_a") or 0):
                        add_error(errors, line_no, row, "op_rho_not_dominating_raw")
            else:
                counts["direct_rows"] += 1
                if proof_case not in DIRECT_CASES:
                    add_error(errors, line_no, row, "nonburden_nondirect_case")

    for case, expected in EXPECTED_CASES.items():
        if case_counts[case] != expected:
            errors.append({"line_no": None, "row_id": None, "error": f"case_count_mismatch:{case}:{case_counts[case]}!={expected}"})
    if counts["rows"] != EXPECTED_TOTAL:
        errors.append({"line_no": None, "row_id": None, "error": f"total_count_mismatch:{counts['rows']}!={EXPECTED_TOTAL}"})

    summary = {
        "schema": "bankl_branchb_gateb_candidate_v1_verify_summary",
        "input": args.input,
        "counts": dict(sorted(counts.items())),
        "case_counts": dict(sorted(case_counts.items())),
        "op_class_counts": dict(sorted(op_class_counts.items())),
        "expected_cases": EXPECTED_CASES,
        "min_rho_margin": str(min_rho_margin) if min_rho_margin is not None else None,
        "pending_claude_acceptance_rows": pending_acceptance,
        "bad_count": len(errors),
        "errors": errors[:40],
        "status_note": "All exact checks pass iff bad_count=0; pending_claude_acceptance_rows records the external acceptance gate for the two-phase telescope.",
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS branchb gateb candidate verify "
        f"rows={counts['rows']} burden={counts['burden_rows']} op_steps={counts['op_steps']} "
        f"bad={len(errors)} pending_acceptance={pending_acceptance}"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

