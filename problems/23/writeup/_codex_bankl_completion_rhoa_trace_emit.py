#!/usr/bin/env python3
"""Emit op-level rho_a traces for the observed Gate-B completions.

This is the first instrumented layer for the remaining dictionary-inclusion
gate.  The existing completion trace proves that each paying final switch is
realized by the current completion candidates.  Gate B additionally asks for
the completion loss

    rho_a = 25 * max(0, sigma(before) - sigma(after))

to be decomposed into the residual dictionary.

At present all observed selected completions are terminal_prefix_closure
instances.  This script records two losses:

* terminal_rho_a: the selected seed -> terminal_prefix_closure loss.  This is
  zero on the current battery because the selected candidates are already
  repaired seeds.
* raw_to_final_rho_a: the raw width-2 interval -> selected final-switch loss.
  This is the aggregate loss that still needs to be split into op-level
  dictionary residuals.

It intentionally marks positive raw_to_final_rho_a records as
"dictionary_decomposition_pending".
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import _codex_bankl_completion_mechanism_check as cm
import _codex_bankl_completion_trace_emit as trace
import _codex_bankl_lane_coarea_emit as lane
import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pressure_term_verify as tv


def frac_s(x: F | int) -> str:
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def sigma_of(ctx: dict[str, Any], verts: set[int]) -> int:
    dB = skel.delta(ctx["blue_edges"], verts)
    dM = skel.delta(ctx["bad_edges"], verts)
    return len(dB) - len(dM)


def instrumented_interval_closures(
    ctx: dict[str, Any], row: tuple[int, ...]
) -> dict[tuple[int, ...], list[dict[str, Any]]]:
    """Return final-verts -> origin candidates with seed/final sigma data."""
    n = ctx["n"]
    side = ctx["side"]
    st = ctx["st"]
    adj = ctx["adj"]
    comps = skel.component_info(n, adj, side, row)
    out: dict[tuple[int, ...], list[dict[str, Any]]] = {}

    for i in range(len(row) - 2):
        seeds: list[tuple[str, set[int]]] = [
            (f"raw_interval:{i}", set(row[i : i + 3])),
            (f"closed_interval:{i}", lane.closed_interval_seed(row, comps, i)),
        ]
        for k in range(i + 2, len(row)):
            base = set(row[i : k + 1])
            closed = set(base)
            for lo, hi, _size, vertices, _attach in comps:
                if i <= lo and hi <= k:
                    closed.update(vertices)
            seeds.append((f"closed_prefix:{i}:{k}", closed))
        for a, b in ((i, i + 1), (i + 1, i + 2)):
            seeds.append((f"path_pair:{i}:{a}:{b}", set(row[a : b + 1])))
        for comp_no, comp in enumerate(comps):
            _lo, _hi, _size, vertices, attach = comp
            attach_in = [j for j in attach if i <= j <= i + 2]
            if not attach_in:
                continue
            comp_vertices = set(vertices)
            seeds.append((f"component_only:{i}:{comp_no}", comp_vertices))
            for v in comp_vertices:
                seeds.append((f"component_vertex:{i}:{comp_no}:{v}", {v}))
            seeds.append((f"component_attach:{i}:{comp_no}", comp_vertices | {row[j] for j in attach_in}))
            for j in attach_in:
                seeds.append((f"component_single_attach:{i}:{comp_no}:{j}", comp_vertices | {row[j]}))
            for a, b in ((i, i + 1), (i + 1, i + 2)):
                if a in attach_in or b in attach_in:
                    pair_vertices = set(row[a : b + 1])
                    seeds.append((f"component_pair_attach:{i}:{comp_no}:{a}:{b}", comp_vertices | pair_vertices))
                    for v in comp_vertices:
                        seeds.append(
                            (
                                f"component_vertex_pair_attach:{i}:{comp_no}:{v}:{a}:{b}",
                                {v} | pair_vertices,
                            )
                        )
        for left_idx in range(len(comps)):
            left_vertices = list(comps[left_idx][3])
            for right_idx in range(left_idx + 1, len(comps)):
                right_vertices = list(comps[right_idx][3])
                for a, b in ((i, i + 1), (i + 1, i + 2)):
                    pair_vertices = set(row[a : b + 1])
                    for u in left_vertices:
                        for v in right_vertices:
                            seeds.append(
                                (
                                    f"component_vertex_pair_bridge:{i}:{left_idx}:{right_idx}:{u}:{v}:{a}:{b}",
                                    {u, v} | pair_vertices,
                                )
                            )
        for j in (i, i + 1, i + 2):
            seeds.append((f"singleton:{i}:{j}", {row[j]}))

        for label, seed0 in seeds:
            seed = set(seed0)
            variants = [
                ("seed", seed),
                ("terminal_prefix_closure", skel.terminal_prefix_closure(set(seed), st[4], n)),
            ]
            seed_sigma = sigma_of(ctx, seed)
            for op, verts0 in variants:
                verts = set(verts0)
                if not verts or len(verts) == n:
                    continue
                key = tuple(sorted(verts))
                mask = sum(1 << v for v in verts)
                terminal = skel.terminal_shadow_details(n, adj, side, st, mask)
                connected = skel.Bconn(n, adj, skel.switched(side, verts))
                final_sigma = sigma_of(ctx, verts)
                sigma_drop = max(0, seed_sigma - final_sigma)
                out.setdefault(key, []).append(
                    {
                        "i": i,
                        "label": label,
                        "op": op,
                        "connected_after": bool(connected),
                        "terminal_shadow_valid": terminal is not None,
                        "verts": list(key),
                        "seed_verts": sorted(seed),
                        "seed_sigma": seed_sigma,
                        "final_sigma": final_sigma,
                        "sigma_drop": sigma_drop,
                        "rho_a": frac_s(25 * sigma_drop),
                    }
                )
    return out


def matching_origin_key(o: dict[str, Any]) -> tuple[Any, ...]:
    return (o.get("label"), o.get("op"), tuple(o.get("verts") or ()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v3.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_rhoa_trace_v2.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_rhoa_trace_v2_summary.json")
    ap.add_argument("--max-errors", type=int, default=10)
    args = ap.parse_args()

    side_idx = tv.load_side_candidates(tv.SIDE_SOURCES)
    graph_cache: dict[tuple[str, str], Any] = {}
    closure_cache: dict[tuple[str, str, tuple[int, ...]], dict[tuple[int, ...], list[dict[str, Any]]]] = {}
    counts: Counter[str] = Counter()
    by_dict: Counter[str] = Counter()
    by_rho: Counter[str] = Counter()
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
                counts["missing_side"] += 1
                continue
            graph_key = (key[0], side_s)
            if graph_key not in graph_cache:
                graph_cache[graph_key] = tv.graph_context(key[0], side_s)
            ctx = graph_cache[graph_key]
            if ctx is None:
                counts["missing_context"] += 1
                continue
            closure_key = (key[0], side_s, key[3])
            if closure_key not in closure_cache:
                closure_cache[closure_key] = instrumented_interval_closures(ctx, key[3])
            closures = closure_cache[closure_key]

            for term_no, (term, verts) in enumerate(cm.term_sets(rec)):
                counts["terms"] += 1
                origins = closures.get(verts, [])
                selected = trace.select_origin(term, origins)
                if selected is None:
                    counts["miss"] += 1
                    if len(errors) < args.max_errors:
                        errors.append(
                            {
                                "line_no": line_no,
                                "term_no": term_no,
                                "reason": "no_origin",
                                "row_id": rec["row_id"],
                                "verts": list(verts),
                            }
                        )
                    continue

                dclass = trace.dictionary_class_for_origin(term, selected)
                terminal_rho_a = F(selected["rho_a"])
                i = int(selected["i"])
                raw_verts = set(key[3][i : i + 3])
                raw_sigma = sigma_of(ctx, raw_verts)
                final_sigma = int(selected["final_sigma"])
                raw_sigma_drop = max(0, raw_sigma - final_sigma)
                raw_to_final_rho_a = F(25 * raw_sigma_drop)
                by_dict[dclass] += 1
                by_rho[frac_s(raw_to_final_rho_a)] += 1
                counts["hit"] += 1
                if terminal_rho_a == 0:
                    counts["terminal_rho_zero"] += 1
                else:
                    counts["terminal_rho_positive"] += 1
                if raw_to_final_rho_a == 0:
                    counts["raw_rho_zero"] += 1
                    status = "dictionary_decomposition_empty"
                    decomp = []
                    verified = True
                else:
                    counts["raw_rho_positive"] += 1
                    status = "dictionary_decomposition_pending"
                    decomp = [
                        {
                            "dictionary_class": dclass,
                            "value": frac_s(raw_to_final_rho_a),
                            "coeff": "1",
                            "contribution": frac_s(raw_to_final_rho_a),
                            "note": "candidate bucket only; residual nonnegativity proof still pending",
                        }
                    ]
                    verified = False

                out.write(
                    json.dumps(
                        {
                            "schema": "bankl_completion_rhoa_trace_v2",
                            "row_id": rec["row_id"],
                            "row_key": trace.row_key_s(rec),
                            "side": side_s,
                            "proof_case": rec["proof_case"],
                            "parameters": rec["parameters"],
                            "term": {
                                "kind": term.get("kind"),
                                "source_kind": term.get("source_kind"),
                                "label": term.get("label"),
                                "verts": list(verts),
                                "value": term.get("value"),
                                "coeff": term.get("coeff"),
                                "contribution": term.get("contribution"),
                            },
                            "selected_origin": {
                                "family": trace.origin_family(selected),
                                "dictionary_class": dclass,
                                "label": selected.get("label"),
                                "op": selected.get("op"),
                                "i": selected.get("i"),
                                "seed_verts": selected.get("seed_verts"),
                                "raw_interval_verts": sorted(raw_verts),
                                "final_verts": selected.get("verts"),
                                "connected_after": selected.get("connected_after"),
                                "terminal_shadow_valid": selected.get("terminal_shadow_valid"),
                            },
                            "terminal_seed_sigma": selected["seed_sigma"],
                            "terminal_final_sigma": selected["final_sigma"],
                            "terminal_sigma_drop": selected["sigma_drop"],
                            "terminal_rho_a": frac_s(terminal_rho_a),
                            "raw_interval_sigma": raw_sigma,
                            "raw_to_final_sigma_drop": raw_sigma_drop,
                            "raw_to_final_rho_a": frac_s(raw_to_final_rho_a),
                            "dictionary_decomposition_status": status,
                            "dictionary_decomposition": decomp,
                            "dictionary_decomposition_verified": verified,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )

    summary = {
        "schema": "bankl_completion_rhoa_trace_v2_summary",
        "input": args.input,
        "output": str(out_path),
        "counts": dict(sorted(counts.items())),
        "by_dictionary_class": dict(sorted(by_dict.items())),
        "by_rho_a": dict(sorted(by_rho.items(), key=lambda kv: (F(kv[0]), kv[0]))),
        "graph_contexts_built": len(graph_cache),
        "closure_contexts_built": len(closure_cache),
        "errors": errors,
        "bad_count": counts["miss"] + counts["missing_side"] + counts["missing_context"],
        "pending_dictionary_decompositions": counts["raw_rho_positive"],
    }
    Path(args.summary_output).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "PASS completion rho_a trace "
        f"terms={counts['terms']} hit={counts['hit']} bad={summary['bad_count']} "
        f"raw_rho_zero={counts['raw_rho_zero']} raw_rho_positive={counts['raw_rho_positive']}"
    )


if __name__ == "__main__":
    main()






