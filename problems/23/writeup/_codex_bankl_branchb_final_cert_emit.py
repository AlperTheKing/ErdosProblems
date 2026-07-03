"""Emit a consolidated Branch-B Bank-L final-node certificate manifest.

This is a Lean-facing normal form built from the current pressure-cover
artifact.  It does not invent new proof facts: it packages the verified row
split, exact rational identities, mu_L checks, and side-witness recomputation
status into one manifest, while explicitly marking the remaining Gate-B
dictionary inclusion obligation.

Input expectation:
    tmp/bankl_pressure_cover_lean_v3.jsonl

Output:
    tmp/bankl_branchb_final_node_cert_v1.jsonl
    tmp/bankl_branchb_final_node_cert_v1_summary.json
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any


MU = {7: F(100, 11), 9: F(100, 7), 11: F(100, 3)}
SIDE_CASES = {"MU_NUK", "MU_NUK_REPAIRED", "DETOUR_RESIDUAL"}


def parse_frac(x: Any) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x, 1)
    if isinstance(x, str):
        return F(x)
    raise TypeError(f"not a rational literal: {x!r}")


def frac_s(x: F | int | None) -> str | None:
    if x is None:
        return None
    if not isinstance(x, F):
        x = F(x, 1)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def label_value(term: dict[str, Any]) -> Any:
    label = term.get("label")
    if not isinstance(label, str):
        return None
    try:
        return ast.literal_eval(label)
    except Exception:
        return label


def case_bucket(proof_case: str) -> str:
    if proof_case in ("TIGHT_ZERO", "FREE_PACKET_EXCHANGE", "SPARSE_M1_BANKL_BYPASS"):
        return "direct_zero_tight_free"
    if proof_case in ("MU_NUK", "MU_NUK_REPAIRED"):
        return "positive_non_detour_mu_nuK"
    if proof_case == "DETOUR_RESIDUAL":
        return "detour_residual"
    return "unknown"


def dictionary_bucket(proof_case: str, term: dict[str, Any]) -> dict[str, Any]:
    """Assign the named proof bucket visible from current row-level data.

    The field ``gate_b_status`` is intentionally conservative.  The row-level
    term is exact and recomputed, but the per-completion-op rho_a Farkas
    decomposition is a separate Gate-B proof object unless explicitly marked
    otherwise by a future artifact.
    """

    kind = term.get("kind")
    source = term.get("source_kind")
    label = label_value(term)

    if kind == "detour":
        return {
            "dictionary_class": "detour_component_deficit",
            "completion_op": "D-cert negative blue-detour component",
            "gate_b_status": "exact_nonnegative_residual_not_a_completion_op",
        }

    if kind == "lane_prefix_nuK" or source == "lane_interval_nuK":
        return {
            "dictionary_class": "terminal-prefix",
            "completion_op": "op2 terminal prefix closure of width-2 lane interval",
            "gate_b_status": "row_level_exact; per_op_rho_a_dictionary_pending",
        }

    if source == "terminal_shadow_repair":
        return {
            "dictionary_class": "terminal-prefix/noncrossing-coB",
            "completion_op": "op2/op3 terminal-shadow repair",
            "gate_b_status": "row_level_exact; per_op_rho_a_dictionary_pending",
        }

    if isinstance(label, tuple) and label:
        if label[0] in ("singleton", "path_interval"):
            return {
                "dictionary_class": "terminal-prefix",
                "completion_op": "op2 terminal prefix/suffix closure",
                "gate_b_status": "row_level_exact; per_op_rho_a_dictionary_pending",
            }
        if label[0] == "closed_interval":
            return {
                "dictionary_class": "B-connected-segment/noncrossing-coB",
                "completion_op": "op1 segment absorption plus op3 co-B closure",
                "gate_b_status": "row_level_exact; per_op_rho_a_dictionary_pending",
            }

    if kind in ("sparse_m1_gap_square", "sparse_m1_length_gap"):
        return {
            "dictionary_class": "sparse_m1_direct_identity",
            "completion_op": "not_applicable",
            "gate_b_status": "not_required",
        }

    return {
        "dictionary_class": "unknown",
        "completion_op": "unknown",
        "gate_b_status": "missing_classification",
    }


def normalize_term(term: dict[str, Any], proof_case: str) -> tuple[dict[str, Any], list[str]]:
    errs: list[str] = []
    value = parse_frac(term["value"])
    coeff = parse_frac(term["coeff"])
    contribution = parse_frac(term["contribution"])
    if value < 0:
        errs.append("negative_term_value")
    if coeff < 0:
        errs.append("negative_term_coeff")
    if contribution != value * coeff:
        errs.append("term_product_mismatch")

    out = {
        "kind": term.get("kind"),
        "source_kind": term.get("source_kind"),
        "label": term.get("label"),
        "value": frac_s(value),
        "coeff": frac_s(coeff),
        "contribution": frac_s(contribution),
        "dictionary": dictionary_bucket(proof_case, term),
    }
    for key in (
        "verts",
        "vertices",
        "terminal",
        "sigma",
        "nu",
        "K_S",
        "dB",
        "dM",
        "size",
        "TQ",
        "i",
        "explanation",
    ):
        if key in term:
            out[key] = term[key]
    return out, errs


def side_status(rec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    if rec["proof_case"] not in SIDE_CASES:
        return {"required": False, "verified": None}, []
    sw = rec.get("side_witness")
    if not sw:
        return {"required": True, "verified": False, "reason": "missing_side_witness"}, ["missing_side_witness"]
    details = sw.get("term_details", [])
    ok = bool(details) and all(bool(d.get("ok")) for d in details)
    out = {
        "required": True,
        "verified": ok,
        "side": sw.get("side"),
        "term_count": len(details),
    }
    return out, [] if ok else ["side_recompute_failed"]


def normalize_record(rec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errs: list[str] = []
    params = rec["parameters"]
    proof_case = rec["proof_case"]
    Pq = parse_frac(params["P_Q"])
    rho = parse_frac(params["rho_Q"])
    target = parse_frac(rec["identity"]["target"])
    term_sum_recorded = parse_frac(rec["identity"]["term_contribution_sum"])
    terms = []
    term_sum = F(0)
    pending_gateb = 0

    for term in rec.get("terms", []):
        norm, term_errs = normalize_term(term, proof_case)
        errs.extend(term_errs)
        terms.append(norm)
        term_sum += parse_frac(norm["contribution"])
        if norm["dictionary"]["gate_b_status"].endswith("pending"):
            pending_gateb += 1

    if term_sum != target or term_sum_recorded != target:
        errs.append("identity_sum_mismatch")
    if not bool(rec.get("identity", {}).get("verified")):
        errs.append("source_identity_unverified")
    if not bool(rec.get("finite_row_check", {}).get("verified")):
        errs.append("finite_row_check_unverified")
    if Pq > 0 and rho < Pq:
        errs.append("rho_less_than_positive_pressure")

    bucket = case_bucket(proof_case)
    if bucket == "unknown":
        errs.append("unknown_proof_case")

    # Case-local sanity checks.
    if proof_case == "TIGHT_ZERO" and Pq != 0:
        errs.append("tight_nonzero_pressure")
    if proof_case == "FREE_PACKET_EXCHANGE" and Pq >= 0:
        errs.append("packet_free_nonnegative_pressure")
    if proof_case == "SPARSE_M1_BANKL_BYPASS":
        n = int(rec["row_id"]["n"])
        L = int(params["L"])
        m = int(rec["row_id"]["m"])
        r = n - L
        expected = r * r + 2 * L * r
        if m != 1 or term_sum != expected:
            errs.append("sparse_m1_identity_mismatch")
    if proof_case in ("MU_NUK", "MU_NUK_REPAIRED"):
        mu = rec.get("mu_bound", {})
        if not bool(mu.get("verified")):
            errs.append("mu_bound_unverified")
        L = int(params["L"])
        if L not in MU:
            errs.append("missing_mu_constant")
    if proof_case == "DETOUR_RESIDUAL" and any(t["kind"] != "detour" for t in terms):
        errs.append("detour_case_non_detour_term")

    side, side_errs = side_status(rec)
    errs.extend(side_errs)

    out = {
        "schema": "bankl_branchb_final_node_cert_v1",
        "row_id": rec["row_id"],
        "case": {
            "proof_case": proof_case,
            "bucket": bucket,
        },
        "parameters": params,
        "source": {
            "artifact_schema": rec.get("schema"),
            "pc_kind": rec.get("source", {}).get("pc_kind"),
            "source_certificate_kind": rec.get("source", {}).get("source_certificate_kind"),
            "v2_transform": rec.get("source", {}).get("v2_transform"),
        },
        "identity": {
            "target": frac_s(target),
            "term_contribution_sum": frac_s(term_sum),
            "verified": term_sum == target,
            "identity_kind": rec.get("identity", {}).get("identity_kind", "pressure_cover"),
        },
        "finite_row_check": rec.get("finite_row_check"),
        "mu_bound": rec.get("mu_bound"),
        "side_recomputation": side,
        "terms": terms,
        "gate_b_dictionary": {
            "row_in_gate_b_burden": proof_case in SIDE_CASES,
            "pending_per_op_rho_a_terms": pending_gateb,
            "complete": pending_gateb == 0,
        },
        "verified": not errs,
    }
    return out, errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v3.jsonl")
    ap.add_argument("--output", default="tmp/bankl_branchb_final_node_cert_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_branchb_final_node_cert_v1_summary.json")
    ap.add_argument("--max-errors", type=int, default=10)
    args = ap.parse_args()

    counts: Counter[str] = Counter()
    by_L_case: Counter[tuple[int, str]] = Counter()
    dictionary_classes: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    min_mu_margin: F | None = None
    min_rho_margin: F | None = None

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            src = json.loads(line)
            rec, errs = normalize_record(src)
            proof_case = rec["case"]["proof_case"]
            bucket = rec["case"]["bucket"]
            L = int(rec["parameters"]["L"])
            counts["rows"] += 1
            counts[f"case:{proof_case}"] += 1
            counts[f"bucket:{bucket}"] += 1
            by_L_case[(L, proof_case)] += 1
            if rec["gate_b_dictionary"]["row_in_gate_b_burden"]:
                counts["gate_b_burden_rows"] += 1
            if not rec["gate_b_dictionary"]["complete"]:
                counts["gate_b_pending_rows"] += 1
                counts["gate_b_pending_terms"] += rec["gate_b_dictionary"]["pending_per_op_rho_a_terms"]
            for term in rec["terms"]:
                dictionary_classes[term["dictionary"]["dictionary_class"]] += 1
            rho_margin = parse_frac(rec["finite_row_check"]["rho_minus_target"])
            min_rho_margin = rho_margin if min_rho_margin is None or rho_margin < min_rho_margin else min_rho_margin
            mu = rec.get("mu_bound") or {}
            if mu.get("margin") is not None:
                margin = parse_frac(mu["margin"])
                min_mu_margin = margin if min_mu_margin is None or margin < min_mu_margin else min_mu_margin
            if errs:
                counts["bad"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line_no": line_no, "errors": errs, "record": rec})
            out.write(json.dumps(rec, sort_keys=True) + "\n")

    summary = {
        "schema": "bankl_branchb_final_node_cert_v1_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "by_L_case": {repr(k): v for k, v in sorted(by_L_case.items(), key=lambda kv: repr(kv[0]))},
        "dictionary_classes": dict(sorted(dictionary_classes.items())),
        "min_mu_margin": frac_s(min_mu_margin),
        "min_rho_minus_target": frac_s(min_rho_margin),
        "bad_count": counts["bad"],
        "errors": errors,
        "gate_b_note": (
            "This manifest assigns row-level named residual buckets and verifies exact "
            "values. Per-completion-op rho_a Farkas decompositions are still pending "
            "for rows with gate_b_pending_terms > 0."
        ),
    }
    Path(args.summary_output).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(out_path),
                "rows": counts["rows"],
                "bad_count": counts["bad"],
                "gate_b_burden_rows": counts["gate_b_burden_rows"],
                "gate_b_pending_rows": counts["gate_b_pending_rows"],
                "gate_b_pending_terms": counts["gate_b_pending_terms"],
                "min_mu_margin": frac_s(min_mu_margin),
            },
            sort_keys=True,
        )
    )
    print("PASS Branch-B final-node manifest" if counts["bad"] == 0 else "FAIL Branch-B final-node manifest")


if __name__ == "__main__":
    main()
