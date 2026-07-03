#!/usr/bin/env python3
"""Promote the accepted Gate-B candidate manifest to final accepted status."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ACCEPT_STAMP = "2026-07-03T23:15:00Z"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_branchb_gateb_candidate_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_branchb_gateb_final_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_branchb_gateb_final_v1_summary.json")
    args = ap.parse_args()

    counts = Counter()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            counts["rows"] += 1
            gd = rec.setdefault("gate_b_dictionary", {})
            cv1 = gd.get("candidate_v1") or {}
            status = cv1.get("status")
            if status == "candidate_complete_awaiting_claude_acceptance":
                counts["accepted_op_rows"] += 1
                cv1["status"] = "accepted_complete"
                cv1["claude_acceptance"] = f"accepted_by_claude_{ACCEPT_STAMP}"
                cv1["acceptance_note"] = "Two-phase monotone telescope accepted as Gate B section-6.1 artifact; residual over-coverage is conservative."
            elif status == "complete_detour_residual":
                counts["detour_rows"] += 1
                cv1["claude_acceptance"] = "accepted_by_existing_D_cert_path"
            gd["candidate_v1"] = cv1
            gd["complete"] = cv1.get("status") in {"accepted_complete", "complete_detour_residual"}
            gd["candidate_complete"] = gd["complete"]
            rec["schema"] = "bankl_branchb_gateb_final_v1"
            out.write(json.dumps(rec, sort_keys=True) + "\n")
    summary = {
        "schema": "bankl_branchb_gateb_final_v1_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "claude_acceptance_stamp": ACCEPT_STAMP,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS gateb final emit "
        f"rows={counts['rows']} accepted_op_rows={counts['accepted_op_rows']} detour={counts['detour_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
