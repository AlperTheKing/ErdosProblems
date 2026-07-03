"""Annotate Bank-L pressure-cover v2 rows with exact cut-side witnesses.

The v2 row id intentionally remains compact, but proof audit needs the cut side
for recomputing switch and detour terms.  This script finds a side from the
side-bearing gate artifacts for every pressure/detour row and records it inside
a v3 artifact, together with recomputed term data.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import _codex_bankl_pressure_term_verify as tv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pressure_cover_lean_v3.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_pressure_cover_lean_v3_summary.json")
    ap.add_argument("--side-source", action="append", default=[])
    args = ap.parse_args()

    side_sources = args.side_source or list(tv.SIDE_SOURCES)
    side_idx = tv.load_side_candidates(side_sources)
    graph_cache: dict[tuple[str, str], Any] = {}
    counts: Counter = Counter()
    first_bad = None

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            key = tv.row_key_from_lean(rec)
            if rec["proof_case"] not in ("MU_NUK", "MU_NUK_REPAIRED", "DETOUR_RESIDUAL"):
                rec["schema"] = "bankl_pressure_cover_lean_v3"
                rec["side_witness"] = None
                counts[f"case:{rec['proof_case']}"] += 1
                counts["not_side_needed"] += 1
                out.write(json.dumps(rec, sort_keys=True) + "\n")
                continue

            found = None
            for side_s in side_idx.get(key, []):
                cache_key = (key[0], side_s)
                if cache_key not in graph_cache:
                    graph_cache[cache_key] = tv.graph_context(key[0], side_s)
                ctx = graph_cache[cache_key]
                if ctx is None:
                    continue
                term_details = []
                ok_all = True
                for term in rec.get("terms", []):
                    if term["kind"] in ("lane_prefix_nuK", "nuK"):
                        ok, got = tv.verify_munuk_term(ctx, term)
                    elif term["kind"] == "detour":
                        ok, got = tv.verify_detour_term(ctx, term, key[2], key[3])
                    else:
                        ok, got = False, {"reason": f"unsupported kind {term['kind']}"}
                    ok_all = ok_all and ok
                    term_details.append({"ok": ok, "recomputed": got})
                if ok_all:
                    found = {"side": side_s, "term_details": term_details}
                    break
            rec["schema"] = "bankl_pressure_cover_lean_v3"
            rec["side_witness"] = found
            counts[f"case:{rec['proof_case']}"] += 1
            if found is None:
                counts["side_witness_missing"] += 1
                if first_bad is None:
                    first_bad = {"line_no": line_no, "row_id": rec["row_id"], "proof_case": rec["proof_case"]}
            else:
                counts["side_witness_found"] += 1
            out.write(json.dumps(rec, sort_keys=True) + "\n")

    summary = {
        "schema": "bankl_pressure_cover_lean_v3_summary",
        "input": args.input,
        "output": args.output,
        "side_sources": side_sources,
        "side_index_keys": len(side_idx),
        "graph_contexts_built": len(graph_cache),
        "counts": dict(sorted(counts.items())),
        "first_bad": first_bad,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "summary_output": args.summary_output, "counts": summary["counts"], "first_bad": first_bad}, sort_keys=True))
    print("PASS bankl pressure-cover side annotator" if first_bad is None else "FAIL bankl pressure-cover side annotator")


if __name__ == "__main__":
    main()