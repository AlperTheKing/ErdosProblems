"""Check whether current interval closures reproduce v3 paying switches.

This is a diagnostic for the Branch-B Gate A completion engine.  The v3
pressure artifact contains exact paying terminal switches.  The CD proof says
those switches should arise from completed width-2 seeds Comp([i,i+2]) after
op1-op5.  This script tests how far the current implemented primitives get.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import _codex_bankl_lane_coarea_emit as lane
import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pressure_term_verify as tv


def term_sets(rec: dict[str, Any]) -> list[tuple[dict[str, Any], tuple[int, ...]]]:
    out = []
    for term in rec.get("terms", []):
        if term.get("kind") not in ("lane_prefix_nuK", "nuK"):
            continue
        verts = term.get("verts")
        if not verts:
            continue
        out.append((term, tuple(sorted(int(v) for v in verts))))
    return out


def current_interval_closures(ctx: dict[str, Any], row: tuple[int, ...]) -> dict[tuple[int, ...], list[dict[str, Any]]]:
    n = ctx["n"]
    edges = ctx["edges"]
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
        # The CD proof's op1/op2 completion can turn a width-2 lane seed into a
        # cumulative closed prefix when the row bad edge crosses the switch.
        # Record those longer closed-prefix candidates explicitly. This remains
        # a diagnostic trace: every candidate is still checked below for
        # connectedness and terminal-shadow validity before it counts as a hit.
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
            lo, hi, _size, vertices, attach = comp
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
                        seeds.append((f"component_vertex_pair_attach:{i}:{comp_no}:{v}:{a}:{b}", {v} | pair_vertices))
        for left_idx in range(len(comps)):
            left_vertices = list(comps[left_idx][3])
            for right_idx in range(left_idx + 1, len(comps)):
                right_vertices = list(comps[right_idx][3])
                for a, b in ((i, i + 1), (i + 1, i + 2)):
                    pair_vertices = set(row[a : b + 1])
                    for u in left_vertices:
                        for v in right_vertices:
                            seeds.append((f"component_vertex_pair_bridge:{i}:{left_idx}:{right_idx}:{u}:{v}:{a}:{b}", {u, v} | pair_vertices))
        for j in (i, i + 1, i + 2):
            seeds.append((f"singleton:{i}:{j}", {row[j]}))
        for label, seed in seeds:
            variants = [
                ("seed", set(seed)),
                ("terminal_prefix_closure", skel.terminal_prefix_closure(set(seed), st[4], n)),
            ]
            for op, verts in variants:
                if not verts or len(verts) == n:
                    continue
                key = tuple(sorted(verts))
                mask = sum(1 << v for v in verts)
                terminal = skel.terminal_shadow_details(n, adj, side, st, mask)
                connected = skel.Bconn(n, adj, skel.switched(side, verts))
                out.setdefault(key, []).append({
                    "i": i,
                    "label": label,
                    "op": op,
                    "connected_after": bool(connected),
                    "terminal_shadow_valid": terminal is not None,
                    "verts": list(key),
                })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v3.jsonl")
    ap.add_argument("--output", default="tmp/bankl_completion_mechanism_check_v1.json")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    side_idx = tv.load_side_candidates(tv.SIDE_SOURCES)
    graph_cache: dict[tuple[str, str], Any] = {}
    counts: Counter[str] = Counter()
    first_miss = None
    first_hit = None
    examples: dict[str, Any] = {}

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("proof_case") not in ("MU_NUK", "MU_NUK_REPAIRED"):
                continue
            wanted = term_sets(rec)
            if not wanted:
                continue
            key = tv.row_key_from_lean(rec)
            side_witness = rec.get("side_witness") or {}
            side_s = side_witness.get("side")
            if side_s is None:
                candidates = side_idx.get(key, [])
                side_s = candidates[0] if candidates else None
            if side_s is None:
                counts["missing_side"] += 1
                continue
            cache_key = (key[0], side_s)
            if cache_key not in graph_cache:
                graph_cache[cache_key] = tv.graph_context(key[0], side_s)
            ctx = graph_cache[cache_key]
            if ctx is None:
                counts["missing_context"] += 1
                continue
            closures = current_interval_closures(ctx, key[3])
            for term, verts in wanted:
                counts["terms"] += 1
                hit = verts in closures
                counts["hit" if hit else "miss"] += 1
                shape = "other"
                label = str(term.get("label") or "")
                if len(verts) == 1:
                    shape = "singleton"
                elif label.startswith("('path_interval', 0,") or term.get("kind") == "lane_prefix_nuK":
                    shape = "prefix_or_lane"
                elif label.startswith("('closed_interval'"):
                    shape = "closed_interval"
                hit_key = "hit" if hit else "miss"
                counts[f"shape:{shape}:{hit_key}"] += 1
                label_key = str(term.get("label") or term.get("source_kind") or term.get("kind"))
                counts[f"term_label:{label_key}:{hit_key}"] += 1
                if hit and first_hit is None:
                    first_hit = {"row_id": rec["row_id"], "term": term, "closures": closures[verts][:8]}
                if (not hit) and label_key not in examples:
                    examples[label_key] = {
                        "row_id": rec["row_id"],
                        "proof_case": rec["proof_case"],
                        "term": term,
                        "wanted_verts": list(verts),
                        "row": list(key[3]),
                        "side": side_s,
                    }
                if (not hit) and first_miss is None:
                    first_miss = {
                        "row_id": rec["row_id"],
                        "proof_case": rec["proof_case"],
                        "term": term,
                        "wanted_verts": list(verts),
                        "row": list(key[3]),
                        "side": side_s,
                        "available_sample": [
                            {"verts": list(k), "variants": v[:3]} for k, v in list(closures.items())[:12]
                        ],
                    }
                if args.limit is not None and counts["terms"] >= args.limit:
                    break
            if args.limit is not None and counts["terms"] >= args.limit:
                break

    summary = {
        "schema": "bankl_completion_mechanism_check_v1",
        "input": args.input,
        "counts": dict(sorted(counts.items())),
        "first_hit": first_hit,
        "first_miss": first_miss,
        "examples": examples,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "counts": summary["counts"], "first_miss": first_miss is not None}, sort_keys=True))


if __name__ == "__main__":
    main()








