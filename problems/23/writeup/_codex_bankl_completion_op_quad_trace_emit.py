#!/usr/bin/env python3
"""Emit op-level exchange quadruples for orientable Gate-B completions.

For a monotone switch transition S -> S union X with O = V \ (S union X),
the section-6.1 exchange loss is determined by

    q = e_B(X,S) - e_M(X,S) - e_B(X,O) + e_M(X,O),
    rho_a = 25 * max(0, q).

The selected completed switches in the current pressure-cover artifact are
often equivalent only after complementing the switch side.  This script tries
the four equivalent orientations:

    raw -> final,
    V\\raw -> V\\final,
    raw -> V\\final,
    V\\raw -> final,

and emits the minimum-addition monotone orientation when one exists.  Records
with no monotone orientation are carried as explicit pending cases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pressure_term_verify as tv


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def signature_id(key: dict[str, Any]) -> str:
    return "opq_" + hashlib.sha256(canonical_json(key).encode("utf-8")).hexdigest()[:16]


def count_edges(edges: set[tuple[int, int]], A: set[int], B: set[int]) -> int:
    return sum(1 for u, v in edges if ((u in A and v in B) or (v in A and u in B)))


def choose_orientation(n: int, raw: set[int], final: set[int]) -> tuple[str, set[int], set[int]] | None:
    V = set(range(n))
    options = [
        ("raw_to_final", raw, final),
        ("complement_raw_to_complement_final", V - raw, V - final),
        ("raw_to_complement_final", raw, V - final),
        ("complement_raw_to_final", V - raw, final),
    ]
    monotone = [(len(b - a), name, a, b) for name, a, b in options if a <= b]
    if not monotone:
        return None
    _size, name, start, end = min(monotone, key=lambda t: (t[0], t[1]))
    return name, set(start), set(end)


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


def quad_key(rec: dict[str, Any]) -> dict[str, Any]:
    origin = rec["selected_origin"]
    return {
        "op_type": rec.get("op_type"),
        "orientation": rec.get("orientation"),
        "dictionary_class": origin.get("dictionary_class"),
        "origin_family": origin.get("family"),
        "origin_op": origin.get("op"),
        "selected_label": origin.get("label"),
        "eB_XS": rec.get("eB_XS"),
        "eM_XS": rec.get("eM_XS"),
        "eB_XO": rec.get("eB_XO"),
        "eM_XO": rec.get("eM_XO"),
        "exchange_q": rec.get("exchange_q"),
        "rho_a": rec.get("rho_a"),
        "term_kind": rec["term"].get("kind"),
        "term_source_kind": rec["term"].get("source_kind"),
        "term_value": rec["term"].get("value"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_rhoa_trace_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_op_quad_trace_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_op_quad_trace_v1_summary.json")
    args = ap.parse_args()

    rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    graph_cache: dict[tuple[str, str], Any] = {}
    counts: Counter[str] = Counter()
    by_orientation: Counter[str] = Counter()
    by_quad: Counter[str] = Counter()
    pending_examples: list[dict[str, Any]] = []
    signatures: dict[str, dict[str, Any]] = {}
    sig_members: dict[str, list[dict[str, Any]]] = defaultdict(list)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        for row in rows:
            counts["rows"] += 1
            n = int(row["row_id"]["n"])
            raw = set(int(v) for v in row["selected_origin"]["raw_interval_verts"])
            final = set(int(v) for v in row["selected_origin"]["final_verts"])
            choice = choose_orientation(n, raw, final)
            if choice is None:
                counts["no_orientation"] += 1
                if len(pending_examples) < 12:
                    pending_examples.append(
                        {
                            "row_ref": row_ref(row),
                            "selected_origin": row["selected_origin"],
                            "raw_interval_verts": sorted(raw),
                            "final_verts": sorted(final),
                        }
                    )
                record = {
                    "schema": "bankl_completion_op_quad_trace_v1",
                    "status": "pending_no_monotone_orientation",
                    "row_ref": row_ref(row),
                    "selected_origin": row["selected_origin"],
                    "term": row["term"],
                }
                out.write(json.dumps(record, sort_keys=True) + "\n")
                continue

            orientation, S, final_oriented = choice
            X = final_oriented - S
            O = set(range(n)) - final_oriented
            key = tv.row_key_from_lean({"row_id": row["row_id"]})
            graph_key = (key[0], row["side"])
            if graph_key not in graph_cache:
                graph_cache[graph_key] = tv.graph_context(key[0], row["side"])
            ctx = graph_cache[graph_key]
            eB_XS = count_edges(ctx["blue_edges"], X, S)
            eM_XS = count_edges(ctx["bad_edges"], X, S)
            eB_XO = count_edges(ctx["blue_edges"], X, O)
            eM_XO = count_edges(ctx["bad_edges"], X, O)
            q = eB_XS - eM_XS - eB_XO + eM_XO
            rho_a = 25 * max(0, q)
            sigma_before = len(skel.delta(ctx["blue_edges"], S)) - len(skel.delta(ctx["bad_edges"], S))
            sigma_after = len(skel.delta(ctx["blue_edges"], final_oriented)) - len(
                skel.delta(ctx["bad_edges"], final_oriented)
            )
            sigma_drop = sigma_before - sigma_after
            verified = q == sigma_drop

            record = {
                "schema": "bankl_completion_op_quad_trace_v1",
                "status": "ok" if verified else "bad_quad_identity",
                "row_ref": row_ref(row),
                "parameters": row["parameters"],
                "selected_origin": row["selected_origin"],
                "term": row["term"],
                "op_type": "oriented_raw_to_selected_completed_switch",
                "orientation": orientation,
                "S": sorted(S),
                "X": sorted(X),
                "O": sorted(O),
                "final_oriented": sorted(final_oriented),
                "eB_XS": eB_XS,
                "eM_XS": eM_XS,
                "eB_XO": eB_XO,
                "eM_XO": eM_XO,
                "exchange_q": q,
                "sigma_before": sigma_before,
                "sigma_after": sigma_after,
                "sigma_drop": sigma_drop,
                "rho_a": str(rho_a),
                "quad_identity_verified": verified,
                "dictionary_decomposition_status": "empty" if rho_a == 0 else "pending",
            }
            counts["oriented"] += 1
            if not verified:
                counts["bad_quad_identity"] += 1
            if rho_a == 0:
                counts["rho_zero"] += 1
            else:
                counts["rho_positive"] += 1
            by_orientation[orientation] += 1
            qkey = quad_key(record)
            sid = signature_id(qkey)
            signatures.setdefault(sid, qkey)
            sig_members[sid].append(record)
            by_quad[canonical_json(qkey)] += 1
            out.write(json.dumps(record, sort_keys=True) + "\n")

    sig_payload = [
        {
            "signature_id": sid,
            "count": len(sig_members[sid]),
            "key": signatures[sid],
            "representative": sig_members[sid][0],
            "row_refs": [r["row_ref"] for r in sig_members[sid]],
        }
        for sid in sorted(signatures)
    ]
    sig_payload.sort(key=lambda r: (-r["count"], r["signature_id"]))
    summary = {
        "schema": "bankl_completion_op_quad_trace_v1_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "by_orientation": dict(sorted(by_orientation.items())),
        "quad_signature_count": len(signatures),
        "top_quad_signatures": [
            {"signature_id": r["signature_id"], "count": r["count"], "key": r["key"]}
            for r in sig_payload[:40]
        ],
        "pending_examples": pending_examples,
        "signature_representatives": sig_payload,
    }
    Path(args.summary_output).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "PASS op quad trace "
        f"rows={counts['rows']} oriented={counts['oriented']} "
        f"no_orientation={counts['no_orientation']} quad_sigs={len(signatures)} "
        f"bad_quad_identity={counts['bad_quad_identity']}"
    )
    return 0 if counts["bad_quad_identity"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

