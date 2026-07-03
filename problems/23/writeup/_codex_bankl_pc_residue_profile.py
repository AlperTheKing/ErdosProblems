"""Profile positive-pressure residue branches in the PC certificate artifact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def parse_frac(x) -> F:
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise TypeError(x)


def compact_example(rec: dict) -> dict:
    return {
        "name": rec["name"],
        "n": rec["n"],
        "m": rec["m"],
        "f": rec["f"],
        "row": rec["row"],
        "L": rec["L"],
        "p": rec["p"],
        "h": rec["h"],
        "d": rec["d"],
        "r": rec["r"],
        "P_Q": rec["P_Q"],
        "rho_Q": rec["rho_Q"],
        "pc_kind": rec["pc_kind"],
        "terms": rec["terms"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pc_residue_profile_v1.json")
    ap.add_argument("--top", type=int, default=80)
    args = ap.parse_args()

    positive_by_ph: Counter = Counter()
    positive_by_ph_kind: Counter = Counter()
    positive_by_branch: Counter = Counter()
    clean_by_branch: Counter = Counter()
    nonclean_by_branch: Counter = Counter()
    examples: dict[tuple, dict] = {}
    nonclean_examples: dict[tuple, dict] = {}
    rows = 0
    positive = 0

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            rows += 1
            if parse_frac(rec["P_Q"]) <= 0:
                continue
            positive += 1
            ph = (rec["p"], rec["h"])
            positive_by_ph[ph] += 1
            positive_by_ph_kind[(ph, rec["pc_kind"])] += 1
            branch = (ph, rec["pc_kind"], rec["L"], rec["r"], rec["d"], rec["P_Q"])
            positive_by_branch[branch] += 1
            examples.setdefault(branch, compact_example(rec))
            if ph == (1, 0):
                clean_by_branch[(rec["pc_kind"], rec["L"], rec["r"], rec["d"], rec["P_Q"])] += 1
            else:
                nonclean_by_branch[branch] += 1
                nonclean_examples.setdefault((ph, rec["pc_kind"]), compact_example(rec))

    summary = {
        "input": args.input,
        "rows": rows,
        "positive_rows": positive,
        "clean_positive_rows": positive_by_ph[(1, 0)],
        "nonclean_positive_rows": positive - positive_by_ph[(1, 0)],
        "positive_by_p_h": {repr(k): v for k, v in positive_by_ph.most_common()},
        "positive_by_p_h_kind": {repr(k): v for k, v in positive_by_ph_kind.most_common()},
        "top_positive_branches": [
            {"count": count, "branch": repr(branch), "example": examples[branch]}
            for branch, count in positive_by_branch.most_common(args.top)
        ],
        "top_clean_branches": [
            {"count": count, "branch": repr(branch)}
            for branch, count in clean_by_branch.most_common(args.top)
        ],
        "top_nonclean_branches": [
            {"count": count, "branch": repr(branch), "example": examples[branch]}
            for branch, count in nonclean_by_branch.most_common(args.top)
        ],
        "nonclean_examples_by_p_h_kind": {repr(k): v for k, v in nonclean_examples.items()},
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "input": args.input,
        "output": str(out),
        "rows": rows,
        "positive_rows": positive,
        "clean_positive_rows": summary["clean_positive_rows"],
        "nonclean_positive_rows": summary["nonclean_positive_rows"],
        "positive_by_p_h": summary["positive_by_p_h"],
        "positive_by_p_h_kind": summary["positive_by_p_h_kind"],
    }, sort_keys=True))
    print("PASS pressure-cover residue profile")


if __name__ == "__main__":
    main()