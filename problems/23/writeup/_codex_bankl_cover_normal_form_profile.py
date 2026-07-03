"""Profile normal forms of the current Bank-L pressure-cover artifact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def normal_form(row: list[int], verts: list[int], term_kind: str) -> str:
    vt = tuple(verts)
    if term_kind == "detour":
        return "detour"
    if len(vt) == 1 and vt[0] in (row[0], row[-1]):
        return "endpoint_singleton"
    if len(vt) == 1:
        return "singleton"
    if vt == tuple(row[: len(vt)]):
        return "prefix_path"
    if vt == tuple(row[-len(vt) :]):
        return "suffix_path"
    if set(vt).issubset(set(row)):
        return "row_subset_other"
    return "offrow_or_closed"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_cover_normal_form_profile_v1.json")
    args = ap.parse_args()

    by_case: Counter[str] = Counter()
    by_case_form: Counter[tuple[str, str]] = Counter()
    by_L_case_form: Counter[tuple[int, str, str]] = Counter()
    by_m_case_form: Counter[tuple[int, str, str]] = Counter()
    examples = {}

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            Pq = rec["parameters"]["P_Q"]
            if Pq.startswith("-") or Pq == "0":
                continue
            case = rec["proof_case"]
            by_case[case] += 1
            row = rec["row_id"]["row"]
            m = rec["row_id"]["m"]
            L = rec["parameters"]["L"]
            if rec["terms"]:
                term = rec["terms"][0]
                verts = term.get("verts", term.get("vertices", []))
                form = normal_form(row, verts, term["kind"])
            else:
                form = "no_term"
            by_case_form[(case, form)] += 1
            by_L_case_form[(L, case, form)] += 1
            by_m_case_form[(m, case, form)] += 1
            examples.setdefault(
                repr((case, form)),
                {
                    "name": rec["row_id"]["name"],
                    "n": rec["row_id"]["n"],
                    "m": m,
                    "row": row,
                    "P_Q": rec["parameters"]["P_Q"],
                    "term": rec["terms"][:1],
                },
            )

    summary = {
        "input": args.input,
        "positive_rows": sum(by_case.values()),
        "by_case": dict(sorted(by_case.items())),
        "by_case_form": {repr(k): v for k, v in sorted(by_case_form.items(), key=lambda kv: repr(kv[0]))},
        "by_L_case_form": {repr(k): v for k, v in sorted(by_L_case_form.items(), key=lambda kv: repr(kv[0]))},
        "by_m_case_form": {repr(k): v for k, v in sorted(by_m_case_form.items(), key=lambda kv: repr(kv[0]))},
        "examples": examples,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "positive_rows": summary["positive_rows"], "by_case": summary["by_case"]}, sort_keys=True))


if __name__ == "__main__":
    main()
