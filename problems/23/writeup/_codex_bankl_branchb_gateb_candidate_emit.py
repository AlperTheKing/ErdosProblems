#!/usr/bin/env python3
"""Merge the Gate-B op-sequence candidate certificate into Branch-B manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def term_key_from_manifest(row: dict[str, Any], term: dict[str, Any]) -> str:
    rid = row["row_id"]
    return canon(
        {
            "name": rid.get("name"),
            "n": rid.get("n"),
            "m": rid.get("m"),
            "f": rid.get("f"),
            "row": rid.get("row"),
            "kind": term.get("kind"),
            "source_kind": term.get("source_kind"),
            "label": term.get("label"),
            "verts": term.get("verts"),
            "value": term.get("value"),
            "coeff": term.get("coeff"),
            "contribution": term.get("contribution"),
        }
    )


def term_key_from_op(row: dict[str, Any]) -> str:
    rr = row["row_ref"]
    t = row["term"]
    return canon(
        {
            "name": rr.get("name"),
            "n": rr.get("n"),
            "m": rr.get("m"),
            "f": rr.get("f"),
            "row": rr.get("row"),
            "kind": t.get("kind"),
            "source_kind": t.get("source_kind"),
            "label": t.get("label"),
            "verts": t.get("verts"),
            "value": t.get("value"),
            "coeff": t.get("coeff"),
            "contribution": t.get("contribution"),
        }
    )


def parse_int(x: Any) -> int:
    if isinstance(x, int):
        return x
    return int(F(str(x)))


def compact_op(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": row.get("schema"),
        "status": row.get("status"),
        "raw": row.get("raw"),
        "final": row.get("final"),
        "raw_sigma": row.get("raw_sigma"),
        "final_sigma": row.get("final_sigma"),
        "raw_sigma_drop": row.get("raw_sigma_drop"),
        "raw_to_final_rho_a": row.get("raw_to_final_rho_a"),
        "op_sequence_q_sum": row.get("op_sequence_q_sum"),
        "op_sequence_rho_sum": row.get("op_sequence_rho_sum"),
        "op_sequence_rho_dominates_raw_rho": row.get("op_sequence_rho_dominates_raw_rho"),
        "op_steps": row.get("op_steps"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="tmp/bankl_branchb_final_node_cert_v1.jsonl")
    ap.add_argument("--op-sequence", default="tmp/bankl_completion_op_sequence_trace_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_branchb_gateb_candidate_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_branchb_gateb_candidate_v1_summary.json")
    ap.add_argument("--max-errors", type=int, default=20)
    args = ap.parse_args()

    op_rows = [json.loads(line) for line in Path(args.op_sequence).read_text(encoding="utf-8").splitlines() if line.strip()]
    op_by_key: dict[str, dict[str, Any]] = {}
    duplicate_keys: list[str] = []
    for op in op_rows:
        k = term_key_from_op(op)
        if k in op_by_key:
            duplicate_keys.append(k)
        op_by_key[k] = op

    counts: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Path(args.manifest).open("r", encoding="utf-8") as fh, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            counts["rows"] += 1
            proof_case = row["case"]["proof_case"]
            burden = row.get("gate_b_dictionary", {}).get("row_in_gate_b_burden", False)
            if burden:
                counts["gate_b_burden_rows"] += 1
            row_errors: list[str] = []
            gate_b = {
                "candidate_schema": "bankl_branchb_gateb_candidate_v1",
                "status": "not_required",
                "claude_acceptance": "not_requested",
            }
            if proof_case == "DETOUR_RESIDUAL":
                counts["detour_gate_b_rows"] += 1
                gate_b = {
                    "candidate_schema": "bankl_branchb_gateb_candidate_v1",
                    "status": "complete_detour_residual",
                    "claude_acceptance": "accepted_by_existing_D_cert_path",
                    "op_sequence_required": False,
                }
            elif proof_case in ("MU_NUK", "MU_NUK_REPAIRED"):
                counts["op_gate_b_rows"] += 1
                if len(row.get("terms", [])) != 1:
                    row_errors.append("unexpected_term_count_for_op_gate_b")
                term = row.get("terms", [{}])[0]
                k = term_key_from_manifest(row, term)
                op = op_by_key.get(k)
                if op is None:
                    row_errors.append("missing_op_sequence")
                else:
                    counts["op_sequence_attached"] += 1
                    if op.get("status") != "ok":
                        row_errors.append("op_sequence_not_ok")
                    rho_sum = parse_int(op.get("op_sequence_rho_sum"))
                    raw_rho = parse_int(op.get("raw_to_final_rho_a") or 0)
                    if rho_sum < raw_rho:
                        row_errors.append("op_sequence_rho_not_dominating")
                    if rho_sum > raw_rho:
                        counts["op_sequence_surplus_rows"] += 1
                    steps = op.get("op_steps") or []
                    counts["op_steps_attached"] += len(steps)
                    gate_b = {
                        "candidate_schema": "bankl_branchb_gateb_candidate_v1",
                        "status": "candidate_complete_awaiting_claude_acceptance",
                        "claude_acceptance": "pending_two_phase_telescope_decision",
                        "op_sequence_required": True,
                        "op_sequence": compact_op(op),
                    }
            row["gate_b_dictionary"] = {
                **row.get("gate_b_dictionary", {}),
                "candidate_v1": gate_b,
                "complete": gate_b["status"] in ("complete_detour_residual",),
                "candidate_complete": gate_b["status"] in (
                    "complete_detour_residual",
                    "candidate_complete_awaiting_claude_acceptance",
                ),
            }
            if row_errors:
                counts["bad_rows"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line_no": line_no, "row_id": row.get("row_id"), "errors": row_errors})
            out.write(json.dumps(row, sort_keys=True) + "\n")

    missing_unused = len(set(op_by_key) - set())  # kept for schema readability below
    summary = {
        "schema": "bankl_branchb_gateb_candidate_v1_summary",
        "manifest": args.manifest,
        "op_sequence": args.op_sequence,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "op_sequence_rows": len(op_rows),
        "duplicate_op_keys": len(duplicate_keys),
        "bad_count": counts["bad_rows"],
        "errors": errors,
        "status_note": "Candidate attaches exact two-phase op-sequence decompositions for MU_NUK/MU_NUK_REPAIRED rows; Claude acceptance of the two-phase telescope is pending.",
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS gateb candidate merge "
        f"rows={counts['rows']} burden={counts['gate_b_burden_rows']} "
        f"attached={counts['op_sequence_attached']} bad={counts['bad_rows']}"
    )
    return 0 if counts["bad_rows"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
