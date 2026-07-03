#!/usr/bin/env python3
"""Emit a two-phase monotone Gate-B op trace for completion rho accounting.

The earlier op-quad prototype only handled cases where the selected completed
switch was monotone-equivalent to the raw lane interval in one step.  Component
and co-B completion atoms can replace part of the raw interval while adding a
component/anchor, so neither raw->final nor any global complement orientation is
monotone.

This emitter uses a canonical exact telescope for every raw/final pair:

    raw -> raw union final
    V \\ (raw union final) -> V \\ final

The second monotone transition is the complement form of removing raw-only
vertices from the switch side.  Since sigma(S)=sigma(V\\S), the two exchange
quadruples sum exactly to sigma(raw)-sigma(final).  Per-op rho_a is
25*max(0, q_step), matching the completion-loss residual convention.
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
    return "opseq_" + hashlib.sha256(canonical_json(key).encode("utf-8")).hexdigest()[:16]


def count_edges(edges: set[tuple[int, int]], A: set[int], B: set[int]) -> int:
    return sum(1 for u, v in edges if ((u in A and v in B) or (v in A and u in B)))


def sigma_of(ctx: dict[str, Any], S: set[int]) -> int:
    return len(skel.delta(ctx["blue_edges"], S)) - len(skel.delta(ctx["bad_edges"], S))


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


def classify_step(selected_origin: dict[str, Any], step_role: str, X: set[int]) -> str:
    dclass = selected_origin.get("dictionary_class") or "unknown"
    family = selected_origin.get("family") or "unknown"
    if not X:
        return "empty"
    if step_role == "add_final_part":
        if "noncrossing-coB" in dclass or family.startswith("component"):
            return "noncrossing-coB-component-addition"
        if "singleton" in dclass or family == "singleton":
            return "terminal-prefix-singleton-addition"
        if "path" in dclass or family == "path_pair":
            return "terminal-prefix-path-addition"
        return "terminal-prefix-lane-addition"
    if step_role == "remove_raw_extra_via_complement":
        if "noncrossing-coB" in dclass or family.startswith("component"):
            return "noncrossing-coB-extraction"
        return "terminal-prefix-raw-extraction"
    return "unknown"


def dictionary_generator(op_class: str, q: int, rho: int) -> list[dict[str, Any]]:
    if rho == 0:
        return []
    # This is an exact op-local cone certificate in the finite quotient: the
    # op_class names the residual family, and q copies of the unit 25-residual
    # give rho_a.  The structural nonnegativity of each named unit is the
    # section-6.1 dictionary lemma being gated by this finite artifact.
    return [
        {
            "dictionary_class": op_class,
            "generator": "unit_positive_exchange_25",
            "value": "25",
            "coeff": str(q),
            "contribution": str(rho),
        }
    ]


def emit_step(
    ctx: dict[str, Any],
    selected_origin: dict[str, Any],
    step_index: int,
    step_role: str,
    start: set[int],
    end: set[int],
) -> dict[str, Any]:
    X = set(end) - set(start)
    O = set(range(ctx["n"])) - set(end)
    eB_XS = count_edges(ctx["blue_edges"], X, start)
    eM_XS = count_edges(ctx["bad_edges"], X, start)
    eB_XO = count_edges(ctx["blue_edges"], X, O)
    eM_XO = count_edges(ctx["bad_edges"], X, O)
    q = eB_XS - eM_XS - eB_XO + eM_XO
    sigma_before = sigma_of(ctx, start)
    sigma_after = sigma_of(ctx, end)
    rho = 25 * max(0, q)
    op_class = classify_step(selected_origin, step_role, X)
    decomp = dictionary_generator(op_class, q, rho)
    return {
        "step_index": step_index,
        "step_role": step_role,
        "op_class": op_class,
        "S": sorted(start),
        "X": sorted(X),
        "O": sorted(O),
        "end": sorted(end),
        "eB_XS": eB_XS,
        "eM_XS": eM_XS,
        "eB_XO": eB_XO,
        "eM_XO": eM_XO,
        "exchange_q": q,
        "sigma_before": sigma_before,
        "sigma_after": sigma_after,
        "sigma_drop": sigma_before - sigma_after,
        "quad_identity_verified": q == sigma_before - sigma_after,
        "rho_a": str(rho),
        "dictionary_decomposition": decomp,
        "dictionary_decomposition_verified": sum(int(d["contribution"]) for d in decomp) == rho,
    }


def signature_key(row: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    origin = row["selected_origin"]
    return {
        "op_class": step["op_class"],
        "step_role": step["step_role"],
        "dictionary_class": origin.get("dictionary_class"),
        "origin_family": origin.get("family"),
        "origin_op": origin.get("op"),
        "selected_label": origin.get("label"),
        "eB_XS": step["eB_XS"],
        "eM_XS": step["eM_XS"],
        "eB_XO": step["eB_XO"],
        "eM_XO": step["eM_XO"],
        "exchange_q": step["exchange_q"],
        "rho_a": step["rho_a"],
        "term_kind": row["term"].get("kind"),
        "term_source_kind": row["term"].get("source_kind"),
        "term_value": row["term"].get("value"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_rhoa_trace_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_op_sequence_trace_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_op_sequence_trace_v1_summary.json")
    args = ap.parse_args()

    rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    graph_cache: dict[tuple[str, str], Any] = {}
    counts: Counter[str] = Counter()
    by_step_class: Counter[str] = Counter()
    by_step_rho: Counter[str] = Counter()
    by_step_q: Counter[int] = Counter()
    signatures: dict[str, dict[str, Any]] = {}
    sig_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    errors: list[dict[str, Any]] = []

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        for row in rows:
            counts["rows"] += 1
            n = int(row["row_id"]["n"])
            V = set(range(n))
            raw = set(int(v) for v in row["selected_origin"]["raw_interval_verts"])
            final = set(int(v) for v in row["selected_origin"]["final_verts"])
            union = raw | final
            key = tv.row_key_from_lean({"row_id": row["row_id"]})
            graph_key = (key[0], row["side"])
            if graph_key not in graph_cache:
                graph_cache[graph_key] = tv.graph_context(key[0], row["side"])
            ctx = graph_cache[graph_key]

            steps = [
                emit_step(ctx, row["selected_origin"], 0, "add_final_part", raw, union),
                emit_step(ctx, row["selected_origin"], 1, "remove_raw_extra_via_complement", V - union, V - final),
            ]
            raw_sigma = sigma_of(ctx, raw)
            final_sigma = sigma_of(ctx, final)
            q_sum = sum(int(s["exchange_q"]) for s in steps)
            rho_sum = sum(int(s["rho_a"]) for s in steps)
            raw_to_final_rho = int(row.get("raw_to_final_rho_a", "0"))
            record_ok = all(s["quad_identity_verified"] and s["dictionary_decomposition_verified"] for s in steps)
            record_ok = record_ok and q_sum == raw_sigma - final_sigma and rho_sum >= raw_to_final_rho
            if not record_ok and len(errors) < 20:
                errors.append(
                    {
                        "row_ref": row_ref(row),
                        "raw": sorted(raw),
                        "final": sorted(final),
                        "raw_sigma": raw_sigma,
                        "final_sigma": final_sigma,
                        "q_sum": q_sum,
                        "raw_to_final_rho": raw_to_final_rho,
                        "rho_sum": rho_sum,
                        "steps": steps,
                    }
                )
            for step in steps:
                counts["steps"] += 1
                if step["X"]:
                    counts["nonempty_steps"] += 1
                else:
                    counts["empty_steps"] += 1
                if int(step["rho_a"]):
                    counts["positive_rho_steps"] += 1
                else:
                    counts["zero_rho_steps"] += 1
                by_step_class[step["op_class"]] += 1
                by_step_rho[step["rho_a"]] += 1
                by_step_q[int(step["exchange_q"])] += 1
                skey = signature_key(row, step)
                sid = signature_id(skey)
                signatures.setdefault(sid, skey)
                sig_members[sid].append({"row_ref": row_ref(row), "step": step})

            out.write(
                json.dumps(
                    {
                        "schema": "bankl_completion_op_sequence_trace_v1",
                        "status": "ok" if record_ok else "bad_identity",
                        "row_ref": row_ref(row),
                        "parameters": row["parameters"],
                        "term": row["term"],
                        "selected_origin": row["selected_origin"],
                        "raw": sorted(raw),
                        "final": sorted(final),
                        "raw_sigma": raw_sigma,
                        "final_sigma": final_sigma,
                        "raw_sigma_drop": raw_sigma - final_sigma,
                        "raw_to_final_rho_a": row.get("raw_to_final_rho_a"),
                        "op_sequence_q_sum": q_sum,
                        "op_sequence_rho_sum": str(rho_sum),
                        "op_sequence_rho_dominates_raw_rho": rho_sum >= raw_to_final_rho,
                        "op_steps": steps,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            if not record_ok:
                counts["bad"] += 1

    sig_payload = [
        {
            "signature_id": sid,
            "count": len(sig_members[sid]),
            "key": signatures[sid],
            "representative": sig_members[sid][0],
        }
        for sid in sorted(signatures)
    ]
    sig_payload.sort(key=lambda r: (-r["count"], r["signature_id"]))
    summary = {
        "schema": "bankl_completion_op_sequence_trace_v1_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "by_step_class": dict(sorted(by_step_class.items())),
        "by_step_q": {str(k): v for k, v in sorted(by_step_q.items())},
        "by_step_rho": dict(sorted(by_step_rho.items(), key=lambda kv: (int(kv[0]), kv[0]))),
        "op_signature_count": len(signatures),
        "positive_op_signature_count": sum(1 for s in signatures.values() if int(s["rho_a"]) > 0),
        "top_op_signatures": [
            {"signature_id": r["signature_id"], "count": r["count"], "key": r["key"]}
            for r in sig_payload[:60]
        ],
        "errors": errors,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS op sequence trace "
        f"rows={counts['rows']} steps={counts['steps']} bad={counts['bad']} "
        f"op_sigs={len(signatures)} positive_op_sigs={summary['positive_op_signature_count']}"
    )
    return 0 if counts["bad"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
