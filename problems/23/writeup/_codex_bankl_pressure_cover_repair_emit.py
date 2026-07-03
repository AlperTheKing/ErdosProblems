"""Emit a repaired Branch-B pressure-cover / Bank-L certificate artifact.

This v2 artifact keeps the pressure-cover rows that are already terminal-shadow
valid, replaces compact nonterminal nuK rows when an exact terminal-shadow repair
was found, and moves positive m=1 rows to the direct sparse Bank-L identity

    -Delta_Q = (N-L)^2 + 2L(N-L)

which is valid because m=1.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any


def parse_frac(x: Any) -> F:
    if isinstance(x, int):
        return F(x, 1)
    if isinstance(x, str):
        return F(x)
    raise TypeError(x)


def frac_s(x: F | int | None) -> str | None:
    if x is None:
        return None
    if not isinstance(x, F):
        x = F(x, 1)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def row_key(rid: dict[str, Any]) -> tuple[str, int, tuple[int, int], tuple[int, ...]]:
    f = tuple(sorted(int(x) for x in rid["f"]))
    return (rid["name"], int(rid["n"]), f, tuple(int(x) for x in rid["row"]))


def load_repairs(path: str) -> dict[tuple[str, int, tuple[int, int], tuple[int, ...]], dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for item in data.get("repairs", []):
        repair = item.get("repair")
        if repair is None:
            continue
        out[row_key(item["row_id"])] = repair
    return out


def contribution_sum(terms: list[dict[str, Any]]) -> F:
    total = F(0)
    for t in terms:
        total += parse_frac(t.get("contribution", "0"))
    return total


def sparse_m1_terms(n: int, L: int) -> list[dict[str, Any]]:
    r = n - L
    return [
        {
            "kind": "sparse_m1_gap_square",
            "value": str(r * r),
            "coeff": "1",
            "contribution": str(r * r),
            "explanation": "(N-L)^2 term in -Delta_Q for m=1",
        },
        {
            "kind": "sparse_m1_length_gap",
            "value": str(2 * L * r),
            "coeff": "1",
            "contribution": str(2 * L * r),
            "explanation": "2L(N-L) term in -Delta_Q for m=1",
        },
    ]


def normalize_repair_term(repair: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "nuK",
        "source_kind": "terminal_shadow_repair",
        "value": repair["value"],
        "coeff": repair["coeff"],
        "contribution": repair["contribution"],
        "verts": repair["verts"],
        "sigma": repair["sigma"],
        "nu": repair["nu"],
        "K_S": repair["K_S"],
        "terminal": True,
        "dB": repair["dB"],
        "dM": repair["dM"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v1.jsonl")
    ap.add_argument("--repairs", default="tmp/bankl_pressure_term_repairs_v1.json")
    ap.add_argument("--output", default="tmp/bankl_pressure_cover_lean_v2.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_pressure_cover_lean_v2_summary.json")
    args = ap.parse_args()

    repairs = load_repairs(args.repairs)
    counts: Counter = Counter()
    bad = []

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec["row_id"]
            key = row_key(rid)
            params = rec["parameters"]
            n = int(rid["n"])
            m = int(rid["m"])
            L = int(params["L"])
            Pq = parse_frac(params["P_Q"])
            bank_target = parse_frac(rec["finite_row_check"]["rho_minus_target"])
            new = dict(rec)
            new["schema"] = "bankl_pressure_cover_lean_v2"
            new_source = dict(new.get("source", {}))
            terms = list(rec.get("terms", []))

            if Pq > 0 and m == 1:
                terms = sparse_m1_terms(n, L)
                new["proof_case"] = "SPARSE_M1_BANKL_BYPASS"
                new_source["v2_transform"] = "positive m=1 row closed by -Delta_Q=(N-L)^2+2L(N-L); pressure cover not needed"
                new["identity"] = {
                    "target": frac_s(bank_target),
                    "term_contribution_sum": frac_s(contribution_sum(terms)),
                    "verified": contribution_sum(terms) == bank_target,
                    "identity_kind": "bankl_sparse_m1",
                }
                new["mu_bound"] = {"applies": False, "verified": None, "reason": "m=1 sparse Bank-L bypass"}
            elif Pq > 0 and key in repairs:
                terms = [normalize_repair_term(repairs[key])]
                new["proof_case"] = "MU_NUK_REPAIRED"
                new_source["v2_transform"] = "replaced compact nonterminal nuK term by exact terminal-shadow repair"
                new["identity"] = {
                    "target": frac_s(Pq),
                    "term_contribution_sum": frac_s(contribution_sum(terms)),
                    "verified": contribution_sum(terms) == Pq,
                    "identity_kind": "pressure_cover",
                }
                mu = rec.get("mu_bound", {})
                if mu.get("applies"):
                    value_sum = sum(parse_frac(t["value"]) for t in terms)
                    mu_L = parse_frac(mu["mu_L"])
                    new["mu_bound"] = {
                        "applies": True,
                        "mu_L": frac_s(mu_L),
                        "value_sum": frac_s(value_sum),
                        "margin": frac_s(mu_L * value_sum - Pq),
                        "verified": mu_L * value_sum >= Pq,
                    }
            else:
                # Preserve v1 cases exactly.
                if rec.get("identity", {}).get("target") is not None:
                    target = parse_frac(rec["identity"]["target"])
                    new["identity"] = dict(rec["identity"])
                    new["identity"]["verified"] = contribution_sum(terms) == target

            new["source"] = new_source
            new["terms"] = terms
            new["verified"] = bool(new.get("identity", {}).get("verified")) and bool(new.get("finite_row_check", {}).get("verified"))
            counts[f"case:{new['proof_case']}"] += 1
            counts[f"verified:{new['verified']}"] += 1
            if not new["verified"]:
                bad.append({"line_no": line_no, "row_id": rid, "proof_case": new["proof_case"], "identity": new.get("identity"), "terms": terms})
            out.write(json.dumps(new, sort_keys=True) + "\n")

    summary = {
        "schema": "bankl_pressure_cover_lean_v2_summary",
        "input": args.input,
        "repairs": args.repairs,
        "output": args.output,
        "counts": dict(sorted(counts.items())),
        "bad_count": len(bad),
        "first_bad": bad[0] if bad else None,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "summary_output": args.summary_output, "counts": summary["counts"], "bad_count": len(bad)}, sort_keys=True))
    print("PASS bankl pressure-cover lean v2 emitter" if not bad else "FAIL bankl pressure-cover lean v2 emitter")


if __name__ == "__main__":
    main()