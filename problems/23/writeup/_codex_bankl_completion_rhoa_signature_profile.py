#!/usr/bin/env python3
"""Group positive Gate-B rho_a records into exact representative signatures."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sig_id(key: dict[str, Any]) -> str:
    return "rhoa_" + hashlib.sha256(canonical_json(key).encode("utf-8")).hexdigest()[:16]


def row_ref(row: dict[str, Any]) -> dict[str, Any]:
    rid = row["row_id"]
    return {
        "name": rid.get("name"),
        "n": rid.get("n"),
        "m": rid.get("m"),
        "f": rid.get("f"),
        "row": rid.get("row"),
        "side": row.get("side"),
    }


def signature_key(row: dict[str, Any], include_label: bool) -> dict[str, Any]:
    origin = row["selected_origin"]
    key = {
        "dictionary_class": origin.get("dictionary_class"),
        "origin_family": origin.get("family"),
        "origin_op": origin.get("op"),
        "L": row["parameters"].get("L"),
        "proof_case": row.get("proof_case"),
        "raw_interval_sigma": row.get("raw_interval_sigma"),
        "final_sigma": row.get("terminal_final_sigma"),
        "raw_to_final_sigma_drop": row.get("raw_to_final_sigma_drop"),
        "raw_to_final_rho_a": row.get("raw_to_final_rho_a"),
        "term_kind": row["term"].get("kind"),
        "term_source_kind": row["term"].get("source_kind"),
        "term_value": row["term"].get("value"),
    }
    if include_label:
        key["selected_label"] = origin.get("label")
        key["raw_interval_verts_len"] = len(origin.get("raw_interval_verts") or [])
        key["final_verts_len"] = len(origin.get("final_verts") or [])
    return key


def make_groups(rows: list[dict[str, Any]], include_label: bool) -> list[dict[str, Any]]:
    keys: dict[str, dict[str, Any]] = {}
    members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = signature_key(row, include_label)
        sid = sig_id(key)
        keys.setdefault(sid, key)
        members[sid].append(row)
    groups: list[dict[str, Any]] = []
    for sid in sorted(keys):
        rep = members[sid][0]
        groups.append(
            {
                "signature_id": sid,
                "count": len(members[sid]),
                "key": keys[sid],
                "representative": rep,
                "row_refs": [row_ref(r) for r in members[sid]],
            }
        )
    groups.sort(key=lambda g: (-g["count"], g["signature_id"]))
    return groups


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_rhoa_trace_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_rhoa_signatures_v1.json")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_rhoa_signatures_v1_summary.json")
    args = ap.parse_args()

    all_rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    positive = [r for r in all_rows if r.get("raw_to_final_rho_a") != "0"]
    zero = len(all_rows) - len(positive)

    labelled = make_groups(positive, include_label=True)
    shape = make_groups(positive, include_label=False)

    by_dict_rho: Counter[str] = Counter()
    for row in positive:
        key = (row["selected_origin"].get("dictionary_class"), row.get("raw_to_final_rho_a"))
        by_dict_rho[canonical_json(key)] += 1

    payload = {
        "schema": "bankl_completion_rhoa_signature_profile_v1",
        "input": args.input,
        "rows": len(all_rows),
        "positive_rows": len(positive),
        "zero_rows": zero,
        "labelled_positive_signatures": labelled,
        "shape_positive_signatures": shape,
    }
    summary = {
        "schema": "bankl_completion_rhoa_signature_profile_v1_summary",
        "input": args.input,
        "output": args.output,
        "rows": len(all_rows),
        "positive_rows": len(positive),
        "zero_rows": zero,
        "labelled_positive_signature_count": len(labelled),
        "shape_positive_signature_count": len(shape),
        "by_dictionary_class_and_rho": dict(sorted(by_dict_rho.items())),
        "top_labelled_positive_signatures": [
            {"signature_id": g["signature_id"], "count": g["count"], "key": g["key"]}
            for g in labelled[:30]
        ],
        "top_shape_positive_signatures": [
            {"signature_id": g["signature_id"], "count": g["count"], "key": g["key"]}
            for g in shape[:30]
        ],
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS rho_a signature profile "
        f"rows={len(all_rows)} positive={len(positive)} zero={zero} "
        f"labelled={len(labelled)} shape={len(shape)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
