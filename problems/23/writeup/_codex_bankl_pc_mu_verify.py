"""Verify the mu_L-form pressure-cover bound on current PC terms.

Claude's CD directive asks for P_Q <= mu_L * sum nu_K + R with
mu_7=100/11, mu_9=100/7, mu_11=100/3.  In the current artifact, this holds
for all positive non-detour rows using the term values already emitted.  Detour
rows are intentionally separated because their value scale is a different
residual.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

MU = {7: F(100, 11), 9: F(100, 7), 11: F(100, 3)}


def parse_frac(x) -> F:
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise TypeError(x)


def frac_s(x: F | None) -> str | None:
    if x is None:
        return None
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pc_mu_verify_v1.json")
    args = ap.parse_args()

    counts: Counter = Counter()
    by_kind: Counter = Counter()
    by_kind_L: Counter = Counter()
    min_margin: F | None = None
    min_detour_margin: F | None = None
    first_bad = None
    first_detour = None

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            Pq = parse_frac(rec["P_Q"])
            if Pq <= 0:
                continue
            counts["positive"] += 1
            by_kind[rec["pc_kind"]] += 1
            by_kind_L[(rec["L"], rec["pc_kind"])] += 1
            if rec["L"] not in MU:
                counts["bad"] += 1
                first_bad = first_bad or {"reason": "no_mu", "record": rec}
                continue
            value = sum(parse_frac(t["value"]) for t in rec["terms"])
            margin = MU[rec["L"]] * value - Pq
            if rec["pc_kind"] == "detour":
                counts["detour_positive"] += 1
                min_detour_margin = margin if min_detour_margin is None or margin < min_detour_margin else min_detour_margin
                if margin < 0:
                    counts["detour_mu_fail"] += 1
                    first_detour = first_detour or {
                        "margin": frac_s(margin),
                        "name": rec["name"],
                        "n": rec["n"],
                        "row": rec["row"],
                        "P_Q": rec["P_Q"],
                        "terms": rec["terms"],
                    }
                continue
            counts["positive_non_detour"] += 1
            min_margin = margin if min_margin is None or margin < min_margin else min_margin
            if margin < 0:
                counts["bad"] += 1
                first_bad = first_bad or {
                    "reason": "mu_fail",
                    "margin": frac_s(margin),
                    "name": rec["name"],
                    "n": rec["n"],
                    "row": rec["row"],
                    "P_Q": rec["P_Q"],
                    "pc_kind": rec["pc_kind"],
                    "terms": rec["terms"],
                }

    summary = {
        "input": args.input,
        "positive_rows": counts["positive"],
        "positive_non_detour_rows": counts["positive_non_detour"],
        "detour_positive_rows": counts["detour_positive"],
        "non_detour_bad": counts["bad"],
        "detour_mu_fail": counts["detour_mu_fail"],
        "min_non_detour_mu_margin": frac_s(min_margin),
        "min_detour_mu_margin": frac_s(min_detour_margin),
        "by_kind": dict(sorted(by_kind.items())),
        "by_L_kind": {repr(k): v for k, v in sorted(by_kind_L.items(), key=lambda kv: repr(kv[0]))},
        "first_bad": first_bad,
        "first_detour_mu_fail": first_detour,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out),
        "positive_rows": summary["positive_rows"],
        "positive_non_detour_rows": summary["positive_non_detour_rows"],
        "detour_positive_rows": summary["detour_positive_rows"],
        "non_detour_bad": summary["non_detour_bad"],
        "detour_mu_fail": summary["detour_mu_fail"],
        "min_non_detour_mu_margin": summary["min_non_detour_mu_margin"],
        "min_detour_mu_margin": summary["min_detour_mu_margin"],
    }, sort_keys=True))
    print("PASS mu_L non-detour pressure-cover verifier" if counts["bad"] == 0 else "FAIL mu_L non-detour pressure-cover verifier")


if __name__ == "__main__":
    main()