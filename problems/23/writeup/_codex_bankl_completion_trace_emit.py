"""Emit per-term completion-origin traces for Branch-B Gate B.

The v3 pressure-cover artifact proves row-level identities and side-recomputes
all nuK / detour term values.  The completion mechanism diagnostic proves that
every paying nuK switch is produced by a finite family of completed width-2 lane
trace candidates.  This emitter writes that matching as JSONL so the remaining
Gate-B rho_a dictionary inclusion can work over explicit trace classes instead
of rediscovering the row-level switch.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import _codex_bankl_completion_mechanism_check as cm
import _codex_bankl_pressure_term_verify as tv


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


def label_tuple(term: dict[str, Any]) -> Any:
    label = term.get("label")
    if not isinstance(label, str):
        return None
    try:
        return ast.literal_eval(label)
    except Exception:
        return label


def origin_family(origin: dict[str, Any]) -> str:
    label = str(origin.get("label", ""))
    if label.startswith("raw_interval"):
        return "raw_interval"
    if label.startswith("closed_prefix"):
        return "closed_prefix"
    if label.startswith("closed_interval"):
        return "closed_interval"
    if label.startswith("path_pair"):
        return "path_pair"
    if label.startswith("singleton"):
        return "singleton"
    if label.startswith("component_vertex_pair_bridge"):
        return "component_vertex_pair_bridge"
    if label.startswith("component_vertex_pair_attach"):
        return "component_vertex_pair_attach"
    if label.startswith("component_pair_attach"):
        return "component_pair_attach"
    if label.startswith("component_vertex"):
        return "component_vertex"
    if label.startswith("component"):
        return "component"
    return "other"


def dictionary_class_for_origin(term: dict[str, Any], origin: dict[str, Any]) -> str:
    family = origin_family(origin)
    source = term.get("source_kind")
    label = label_tuple(term)
    if source == "terminal_shadow_repair" and family == "component_vertex_pair_bridge":
        return "noncrossing-coB-exterior-anchor"
    if source == "terminal_shadow_repair" and family.startswith("component"):
        return "terminal-prefix/noncrossing-coB-component-extraction"
    if source == "lane_interval_nuK":
        return "terminal-prefix-lane-interval"
    if isinstance(label, tuple) and label:
        if label[0] == "singleton":
            return "terminal-prefix-singleton-extraction"
        if label[0] == "path_interval":
            return "terminal-prefix-path-interval"
        if label[0] == "closed_interval":
            return "B-connected-closed-prefix/noncrossing-coB"
    if family in ("closed_prefix", "closed_interval"):
        return "B-connected-closed-prefix/noncrossing-coB"
    if family in ("path_pair", "singleton"):
        return "terminal-prefix"
    return "unclassified-origin"


def origin_score(term: dict[str, Any], origin: dict[str, Any]) -> tuple[int, int, str, str]:
    family = origin_family(origin)
    source = term.get("source_kind")
    label = label_tuple(term)
    op = str(origin.get("op", ""))
    priority = 50
    if source == "terminal_shadow_repair" and family == "component_vertex_pair_bridge":
        priority = 0
    elif source == "lane_interval_nuK" and family in ("raw_interval", "closed_interval", "closed_prefix", "path_pair"):
        priority = 1
    elif isinstance(label, tuple) and label:
        if label[0] == "singleton" and family == "singleton":
            priority = 0
        elif label[0] == "path_interval" and family == "path_pair":
            priority = 0
        elif label[0] == "closed_interval" and family in ("closed_prefix", "closed_interval"):
            priority = 0
    if op == "terminal_prefix_closure":
        op_penalty = 0
    else:
        op_penalty = 1
    return (priority, op_penalty, family, str(origin.get("label", "")))


def select_origin(term: dict[str, Any], origins: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [o for o in origins if o.get("connected_after") and o.get("terminal_shadow_valid")]
    if not valid:
        return None
    return sorted(valid, key=lambda o: origin_score(term, o))[0]


def row_key_s(rec: dict[str, Any]) -> str:
    rid = rec["row_id"]
    return json.dumps(
        {
            "name": rid["name"],
            "n": rid["n"],
            "f": rid["f"],
            "row": rid["row"],
        },
        sort_keys=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v3.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_trace_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_trace_v1_summary.json")
    ap.add_argument("--max-errors", type=int, default=10)
    args = ap.parse_args()

    side_idx = tv.load_side_candidates(tv.SIDE_SOURCES)
    graph_cache: dict[tuple[str, str], Any] = {}
    closure_cache: dict[tuple[str, str, tuple[int, ...]], dict[tuple[int, ...], list[dict[str, Any]]]] = {}
    counts: Counter[str] = Counter()
    by_origin: Counter[str] = Counter()
    by_dict: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("proof_case") not in ("MU_NUK", "MU_NUK_REPAIRED"):
                continue
            key = tv.row_key_from_lean(rec)
            side_s = (rec.get("side_witness") or {}).get("side")
            if side_s is None:
                candidates = side_idx.get(key, [])
                side_s = candidates[0] if candidates else None
            if side_s is None:
                err = {"line_no": line_no, "reason": "missing_side", "row_id": rec["row_id"]}
                counts["missing_side"] += 1
                if len(errors) < args.max_errors:
                    errors.append(err)
                continue
            graph_key = (key[0], side_s)
            if graph_key not in graph_cache:
                graph_cache[graph_key] = tv.graph_context(key[0], side_s)
            ctx = graph_cache[graph_key]
            if ctx is None:
                err = {"line_no": line_no, "reason": "missing_context", "row_id": rec["row_id"], "side": side_s}
                counts["missing_context"] += 1
                if len(errors) < args.max_errors:
                    errors.append(err)
                continue
            closure_key = (key[0], side_s, key[3])
            if closure_key not in closure_cache:
                closure_cache[closure_key] = cm.current_interval_closures(ctx, key[3])
            closures = closure_cache[closure_key]

            term_details = (rec.get("side_witness") or {}).get("term_details", [])
            recompute_by_verts = {}
            for td in term_details:
                r = td.get("recomputed", {})
                verts = r.get("verts")
                if verts is not None:
                    recompute_by_verts[tuple(sorted(int(v) for v in verts))] = td

            for term_no, (term, verts) in enumerate(cm.term_sets(rec)):
                counts["terms"] += 1
                origins = closures.get(verts, [])
                selected = select_origin(term, origins)
                if selected is None:
                    counts["miss"] += 1
                    err = {
                        "line_no": line_no,
                        "term_no": term_no,
                        "reason": "no_valid_origin",
                        "row_id": rec["row_id"],
                        "side": side_s,
                        "term": term,
                        "verts": list(verts),
                        "origin_count": len(origins),
                    }
                    if len(errors) < args.max_errors:
                        errors.append(err)
                    continue
                counts["hit"] += 1
                family = origin_family(selected)
                dclass = dictionary_class_for_origin(term, selected)
                by_origin[family] += 1
                by_dict[dclass] += 1
                recomputed = recompute_by_verts.get(verts)
                value = parse_frac(term["value"])
                coeff = parse_frac(term["coeff"])
                contribution = parse_frac(term["contribution"])
                record = {
                    "schema": "bankl_completion_trace_v1",
                    "row_key": row_key_s(rec),
                    "row_id": rec["row_id"],
                    "side": side_s,
                    "proof_case": rec["proof_case"],
                    "parameters": rec["parameters"],
                    "term": {
                        "kind": term.get("kind"),
                        "source_kind": term.get("source_kind"),
                        "label": term.get("label"),
                        "verts": list(verts),
                        "value": term["value"],
                        "coeff": term["coeff"],
                        "contribution": term["contribution"],
                        "product_verified": value * coeff == contribution,
                    },
                    "selected_origin": {
                        "family": family,
                        "dictionary_class": dclass,
                        "label": selected.get("label"),
                        "op": selected.get("op"),
                        "i": selected.get("i"),
                        "verts": selected.get("verts"),
                        "connected_after": selected.get("connected_after"),
                        "terminal_shadow_valid": selected.get("terminal_shadow_valid"),
                    },
                    "origin_candidates": [
                        {
                            "family": origin_family(o),
                            "label": o.get("label"),
                            "op": o.get("op"),
                            "i": o.get("i"),
                            "connected_after": o.get("connected_after"),
                            "terminal_shadow_valid": o.get("terminal_shadow_valid"),
                            "verts": o.get("verts"),
                        }
                        for o in origins
                    ],
                    "side_recomputed": recomputed,
                    "trace_verified": bool(
                        selected.get("connected_after")
                        and selected.get("terminal_shadow_valid")
                        and value >= 0
                        and coeff >= 0
                        and value * coeff == contribution
                        and (recomputed is None or recomputed.get("ok"))
                    ),
                    "gate_b_status": "rho_a_dictionary_decomposition_pending",
                }
                if not record["trace_verified"]:
                    counts["bad_trace"] += 1
                    if len(errors) < args.max_errors:
                        errors.append({"line_no": line_no, "term_no": term_no, "record": record})
                out.write(json.dumps(record, sort_keys=True) + "\n")

    summary = {
        "schema": "bankl_completion_trace_v1_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "by_origin_family": dict(sorted(by_origin.items())),
        "by_dictionary_class": dict(sorted(by_dict.items())),
        "graph_contexts_built": len(graph_cache),
        "closure_contexts_built": len(closure_cache),
        "errors": errors,
        "bad_count": counts["miss"] + counts["bad_trace"] + counts["missing_side"] + counts["missing_context"],
    }
    Path(args.summary_output).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(out_path),
                "terms": counts["terms"],
                "hit": counts["hit"],
                "bad_count": summary["bad_count"],
                "by_origin_family": summary["by_origin_family"],
            },
            sort_keys=True,
        )
    )
    print("PASS completion trace emitter" if summary["bad_count"] == 0 else "FAIL completion trace emitter")


if __name__ == "__main__":
    main()