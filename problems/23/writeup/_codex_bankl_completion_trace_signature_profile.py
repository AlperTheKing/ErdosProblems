#!/usr/bin/env python3
"""Profile Gate-B completion traces into finite exact signature classes.

The input is the JSONL trace emitted by
_codex_bankl_completion_trace_emit.py.  This script does not prove the
rho_a dictionary inclusion; it makes the remaining proof target finite by
grouping every traced term under three stable keys:

* full_signature: exact term/recomputed/certificate arithmetic, including
  coefficient and pressure target.
* labelled_shape_signature: switch/dictionary shape including the selected
  local label, but excluding row pressure coefficients.
* shape_signature: same as labelled shape, with the concrete selected label
  forgotten.

All values are copied as exact strings/integers from the trace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sig_id(prefix: str, key: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(key).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_lineno"] = lineno
        rows.append(row)
    return rows


def row_ref(row: dict[str, Any]) -> dict[str, Any]:
    rid = row["row_id"]
    return {
        "lineno": row["_lineno"],
        "name": rid.get("name"),
        "n": rid.get("n"),
        "m": rid.get("m"),
        "f": rid.get("f"),
        "row": rid.get("row"),
        "side": row.get("side"),
    }


def base_fields(row: dict[str, Any]) -> dict[str, Any]:
    sel = row["selected_origin"]
    rec = row["side_recomputed"]["recomputed"]
    term = row["term"]
    params = row["parameters"]
    rid = row["row_id"]
    return {
        "dictionary_class": sel.get("dictionary_class"),
        "origin_family": sel.get("family"),
        "origin_op": sel.get("op"),
        "selected_label": sel.get("label"),
        "term_kind": term.get("kind"),
        "term_source_kind": term.get("source_kind"),
        "term_value": term.get("value"),
        "sigma": rec.get("sigma"),
        "nu": rec.get("nu"),
        "K_S": rec.get("K_S"),
        "nuK": rec.get("nuK"),
        "dB": rec.get("dB"),
        "dM": rec.get("dM"),
        "L": params.get("L"),
        "row_m": rid.get("m"),
        "proof_case": row.get("proof_case"),
    }


def full_key(row: dict[str, Any]) -> dict[str, Any]:
    key = base_fields(row)
    params = row["parameters"]
    term = row["term"]
    key.update(
        {
            "term_coeff": term.get("coeff"),
            "term_contribution": term.get("contribution"),
            "P_Q": params.get("P_Q"),
            "rho_Q": params.get("rho_Q"),
            "target": params.get("target"),
        }
    )
    return key


def labelled_shape_key(row: dict[str, Any]) -> dict[str, Any]:
    return base_fields(row)


def shape_key(row: dict[str, Any]) -> dict[str, Any]:
    key = base_fields(row)
    key.pop("selected_label", None)
    return key


def make_groups(rows: list[dict[str, Any]], key_fn, prefix: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    members: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        key = key_fn(row)
        sid = sig_id(prefix, key)
        buckets.setdefault(sid, key)
        members[sid].append(row)

    out: list[dict[str, Any]] = []
    for sid in sorted(buckets):
        group_rows = members[sid]
        rep = group_rows[0]
        out.append(
            {
                "signature_id": sid,
                "count": len(group_rows),
                "key": buckets[sid],
                "representative": {
                    "row_ref": row_ref(rep),
                    "selected_origin": rep["selected_origin"],
                    "term": rep["term"],
                    "side_recomputed": rep["side_recomputed"],
                    "parameters": rep["parameters"],
                    "origin_candidates": rep.get("origin_candidates", []),
                },
                "row_refs": [row_ref(r) for r in group_rows],
            }
        )
    out.sort(key=lambda r: (-r["count"], r["signature_id"]))
    return out


def count_by(rows: list[dict[str, Any]], path: list[str]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        obj: Any = row
        for part in path:
            obj = obj[part]
        counter[str(obj)] += 1
    return dict(sorted(counter.items()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_trace_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_trace_signatures_v1.json")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_trace_signatures_v1_summary.json")
    args = ap.parse_args()

    rows = load_jsonl(Path(args.input))

    bad: list[dict[str, Any]] = []
    for row in rows:
        if not row.get("trace_verified"):
            bad.append({"lineno": row["_lineno"], "reason": "trace_verified false"})
        term = row.get("term", {})
        if not term.get("product_verified"):
            bad.append({"lineno": row["_lineno"], "reason": "product_verified false"})
        side = row.get("side_recomputed", {})
        if not side.get("ok"):
            bad.append({"lineno": row["_lineno"], "reason": "side_recomputed not ok"})

    full = make_groups(rows, full_key, "full")
    labelled = make_groups(rows, labelled_shape_key, "labelled")
    shape = make_groups(rows, shape_key, "shape")

    payload = {
        "schema": "bankl_completion_trace_signature_profile_v1",
        "input": args.input,
        "rows": len(rows),
        "bad_count": len(bad),
        "bad": bad,
        "full_signatures": full,
        "labelled_shape_signatures": labelled,
        "shape_signatures": shape,
    }

    summary = {
        "schema": "bankl_completion_trace_signature_profile_v1_summary",
        "input": args.input,
        "output": args.output,
        "rows": len(rows),
        "bad_count": len(bad),
        "full_signature_count": len(full),
        "labelled_shape_signature_count": len(labelled),
        "shape_signature_count": len(shape),
        "by_dictionary_class": count_by(rows, ["selected_origin", "dictionary_class"]),
        "by_origin_family": count_by(rows, ["selected_origin", "family"]),
        "by_proof_case": count_by(rows, ["proof_case"]),
        "top_full_signatures": [
            {
                "signature_id": r["signature_id"],
                "count": r["count"],
                "key": r["key"],
            }
            for r in full[:20]
        ],
        "top_labelled_shape_signatures": [
            {
                "signature_id": r["signature_id"],
                "count": r["count"],
                "key": r["key"],
            }
            for r in labelled[:20]
        ],
        "top_shape_signatures": [
            {
                "signature_id": r["signature_id"],
                "count": r["count"],
                "key": r["key"],
            }
            for r in shape[:20]
        ],
    }

    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.summary_output).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        "PASS completion trace signature profile "
        f"rows={len(rows)} bad={len(bad)} full={len(full)} "
        f"labelled={len(labelled)} shape={len(shape)}"
    )
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
