"""Profile positive-pressure Bank-L rows.

Input is the JSONL file emitted by _codex_bankl_pq_crosstab.py.  The script is
purely exact: all rational fields are parsed as Fraction values before
aggregation.  It is intended to expose the shape of the pressure-cover hard
set P_Q > 0.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def frac(s) -> F:
    if isinstance(s, int):
        return F(s, 1)
    return F(str(s))


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pq_positive_rows.jsonl")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--summary-output", default="tmp/bankl_pq_positive_profile.json")
    args = ap.parse_args()

    rows = []
    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                rec["P_Q_F"] = frac(rec["P_Q"])
                rec["rho_Q_F"] = frac(rec["rho_Q"])
                rows.append(rec)

    by_signature: Counter = Counter()
    by_lrdhp: Counter = Counter()
    by_kind: Counter = Counter()
    by_L: Counter = Counter()
    by_pressure: Counter = Counter()
    max_pressure = max((rec["P_Q_F"] for rec in rows), default=F(0))
    min_pressure = min((rec["P_Q_F"] for rec in rows), default=F(0))
    max_ratio = max((rec["P_Q_F"] / rec["rho_Q_F"] for rec in rows if rec["rho_Q_F"] > 0), default=F(0))
    ratio_witness = None

    for rec in rows:
        sig = (
            rec["certificate_kind"],
            rec["row_scope"],
            rec["L"],
            rec["r"],
            rec["p"],
            rec["h"],
            rec["d"],
            frac_s(rec["P_Q_F"]),
            frac_s(rec["rho_Q_F"]),
        )
        by_signature[sig] += 1
        by_lrdhp[(rec["L"], rec["r"], rec["d"], rec["h"], rec["p"])] += 1
        by_kind[rec["certificate_kind"]] += 1
        by_L[rec["L"]] += 1
        by_pressure[frac_s(rec["P_Q_F"])] += 1
        if rec["rho_Q_F"] > 0 and rec["P_Q_F"] / rec["rho_Q_F"] == max_ratio:
            ratio_witness = rec

    top_signatures = [
        {
            "count": count,
            "certificate_kind": sig[0],
            "row_scope": sig[1],
            "L": sig[2],
            "r": sig[3],
            "p": sig[4],
            "h": sig[5],
            "d": sig[6],
            "P_Q": sig[7],
            "rho_Q": sig[8],
        }
        for sig, count in by_signature.most_common(args.top)
    ]
    top_lrdhp = [
        {"count": count, "L": sig[0], "r": sig[1], "d": sig[2], "h": sig[3], "p": sig[4]}
        for sig, count in by_lrdhp.most_common(args.top)
    ]
    top_pressures = [
        {"P_Q": p, "count": count}
        for p, count in by_pressure.most_common(args.top)
    ]
    summary = {
        "rows": len(rows),
        "unique_signatures": len(by_signature),
        "unique_L_r_d_h_p": len(by_lrdhp),
        "by_kind": dict(sorted(by_kind.items())),
        "by_L": {str(k): v for k, v in sorted(by_L.items())},
        "min_P_Q": frac_s(min_pressure),
        "max_P_Q": frac_s(max_pressure),
        "max_P_Q_over_rho_Q": frac_s(max_ratio),
        "max_ratio_witness": {
            k: ratio_witness[k]
            for k in ("name", "n", "m", "f", "row", "L", "p", "h", "d", "r", "P_Q", "rho_Q", "certificate_kind")
        }
        if ratio_witness is not None
        else None,
        "top_signatures": top_signatures,
        "top_L_r_d_h_p": top_lrdhp,
        "top_pressures": top_pressures,
    }

    out = Path(args.summary_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "rows": summary["rows"],
        "unique_signatures": summary["unique_signatures"],
        "unique_L_r_d_h_p": summary["unique_L_r_d_h_p"],
        "by_kind": summary["by_kind"],
        "by_L": summary["by_L"],
        "min_P_Q": summary["min_P_Q"],
        "max_P_Q": summary["max_P_Q"],
        "max_P_Q_over_rho_Q": summary["max_P_Q_over_rho_Q"],
        "summary_output": str(out),
    }, sort_keys=True))
    print("TOP_SIGNATURES")
    for item in top_signatures[: args.top]:
        print(json.dumps(item, sort_keys=True))


if __name__ == "__main__":
    main()
