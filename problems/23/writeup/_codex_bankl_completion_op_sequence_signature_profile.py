#!/usr/bin/env python3
"""Group Gate-B op-sequence steps into exact finite signatures."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def signature_id(key: dict[str, Any]) -> str:
    return "opseq_" + hashlib.sha256(canonical_json(key).encode("utf-8")).hexdigest()[:16]


def step_key(row: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    origin = row["selected_origin"]
    return {
        "op_class": step.get("op_class"),
        "step_role": step.get("step_role"),
        "dictionary_class": origin.get("dictionary_class"),
        "origin_family": origin.get("family"),
        "origin_op": origin.get("op"),
        "selected_label": origin.get("label"),
        "eB_XS": step.get("eB_XS"),
        "eM_XS": step.get("eM_XS"),
        "eB_XO": step.get("eB_XO"),
        "eM_XO": step.get("eM_XO"),
        "exchange_q": step.get("exchange_q"),
        "rho_a": step.get("rho_a"),
        "decomposition": step.get("dictionary_decomposition"),
        "term_kind": row["term"].get("kind"),
        "term_source_kind": row["term"].get("source_kind"),
        "term_label": row["term"].get("label"),
        "term_value": row["term"].get("value"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_op_sequence_trace_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_op_sequence_signatures_v1.json")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_op_sequence_signatures_v1_summary.json")
    args = ap.parse_args()

    sigs: dict[str, dict[str, Any]] = {}
    members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counts: Counter[str] = Counter()

    for line in Path(args.input).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        counts["rows"] += 1
        for step in row.get("op_steps", []):
            counts["steps"] += 1
            key = step_key(row, step)
            sid = signature_id(key)
            sigs.setdefault(sid, key)
            members[sid].append(
                {
                    "row_ref": row.get("row_ref"),
                    "raw": row.get("raw"),
                    "final": row.get("final"),
                    "step_index": step.get("step_index"),
                    "S": step.get("S"),
                    "X": step.get("X"),
                    "O": step.get("O"),
                }
            )
            if int(step.get("rho_a", "0")) > 0:
                counts["positive_rho_steps"] += 1
            else:
                counts["zero_rho_steps"] += 1

    payload = []
    for sid, key in sigs.items():
        ms = members[sid]
        payload.append(
            {
                "signature_id": sid,
                "count": len(ms),
                "key": key,
                "representative": ms[0],
                "row_refs": [m["row_ref"] for m in ms],
            }
        )
    payload.sort(key=lambda r: (-r["count"], r["signature_id"]))
    out = {
        "schema": "bankl_completion_op_sequence_signatures_v1",
        "input": args.input,
        "signature_count": len(payload),
        "positive_signature_count": sum(1 for r in payload if int(r["key"].get("rho_a", "0")) > 0),
        "signatures": payload,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "schema": "bankl_completion_op_sequence_signatures_v1_summary",
        "input": args.input,
        "output": args.output,
        "counts": dict(sorted(counts.items())),
        "signature_count": out["signature_count"],
        "positive_signature_count": out["positive_signature_count"],
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS op sequence signatures "
        f"steps={counts['steps']} signatures={out['signature_count']} "
        f"positive={out['positive_signature_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
