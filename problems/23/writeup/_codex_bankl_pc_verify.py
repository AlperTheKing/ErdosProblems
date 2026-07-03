"""Standalone exact verifier for Bank-L pressure-cover JSONL artifacts.

This script intentionally does not import the emitter.  It treats the JSONL as a
candidate Lean-facing certificate artifact and checks exact rational identities
and basic schema/nonnegativity requirements.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

ALLOWED_KINDS = {
    "packet_free",
    "tight",
    "lane_prefix_nuK",
    "nuK",
    "connected_nuK",
    "detour",
}

ALLOWED_TERM_KINDS = {
    "lane_prefix_nuK",
    "nuK",
    "detour",
}


def parse_frac(x) -> F:
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise TypeError(f"not a rational literal: {x!r}")


def sign_of(x: F) -> str:
    return "pos" if x > 0 else "zero" if x == 0 else "neg"


def row_id(rec: dict) -> tuple:
    return (rec.get("name"), rec.get("n"), tuple(rec.get("f", ())), tuple(rec.get("row", ())))


def check_record(rec: dict) -> list[str]:
    errs: list[str] = []
    required = [
        "schema", "name", "n", "m", "f", "row", "L", "p", "h", "d", "r",
        "P_Q", "rho_Q", "pressure_sign", "pc_kind", "target", "terms", "verified",
    ]
    for key in required:
        if key not in rec:
            errs.append(f"missing:{key}")
    if errs:
        return errs

    if rec["schema"] != "bankl_pressure_cover_cert_v1":
        errs.append("bad_schema")
    if rec["pc_kind"] not in ALLOWED_KINDS:
        errs.append(f"bad_pc_kind:{rec['pc_kind']}")
    if rec["pressure_sign"] != sign_of(parse_frac(rec["P_Q"])):
        errs.append("bad_pressure_sign")
    if rec["L"] != len(set(rec["row"])):
        errs.append("bad_L")
    if rec["r"] != rec["n"] - rec["L"]:
        errs.append("bad_r")

    Pq = parse_frac(rec["P_Q"])
    target = parse_frac(rec["target"])
    expected_target = Pq if Pq > 0 else F(0)
    if target != expected_target:
        errs.append("bad_target")
    if target < 0:
        errs.append("negative_target")

    terms = rec["terms"]
    if not isinstance(terms, list):
        return errs + ["terms_not_list"]
    if Pq <= 0 and terms:
        errs.append("free_row_has_terms")
    if Pq > 0 and not terms:
        errs.append("positive_row_no_terms")

    total = F(0)
    for i, term in enumerate(terms):
        kind = term.get("kind")
        if kind not in ALLOWED_TERM_KINDS:
            errs.append(f"term{i}:bad_kind:{kind}")
        try:
            value = parse_frac(term["value"])
            coeff = parse_frac(term["coeff"])
            contrib = parse_frac(term["contribution"])
        except Exception as exc:  # noqa: BLE001 - verifier wants diagnostic string
            errs.append(f"term{i}:bad_rational:{exc}")
            continue
        if value < 0:
            errs.append(f"term{i}:negative_value")
        if coeff < 0:
            errs.append(f"term{i}:negative_coeff")
        if contrib != value * coeff:
            errs.append(f"term{i}:bad_contribution")
        total += contrib
        if kind in {"lane_prefix_nuK", "nuK"} and "value" in term:
            # For nuK-style terms, value should be the visibly nonnegative nu_K.
            if value == 0 and contrib != 0:
                errs.append(f"term{i}:zero_value_positive_contribution")

    if total != target:
        errs.append("bad_sum")
    if bool(rec["verified"]) is not (total == target):
        errs.append("bad_verified_flag")
    if Pq > 0 and parse_frac(rec["rho_Q"]) < Pq:
        # This is not required of a formal proof artifact if rho is proven by
        # external facts, but every current finite certificate row should obey it.
        errs.append("finite_rho_less_than_Pq")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pc_verify_v1.json")
    ap.add_argument("--max-errors", type=int, default=5)
    args = ap.parse_args()

    counts: Counter = Counter()
    by_kind: Counter = Counter()
    by_sign: Counter = Counter()
    by_ph: Counter = Counter()
    by_L_kind: Counter = Counter()
    errors: list[dict] = []
    seen: Counter = Counter()

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            counts["rows"] += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                counts["bad"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line": lineno, "errors": [f"json:{exc}"]})
                continue
            rid = row_id(rec)
            seen[rid] += 1
            by_kind[rec.get("pc_kind")] += 1
            by_sign[rec.get("pressure_sign")] += 1
            by_ph[(rec.get("p"), rec.get("h"))] += 1
            by_L_kind[(rec.get("L"), rec.get("pc_kind"))] += 1
            errs = check_record(rec)
            if errs:
                counts["bad"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line": lineno, "row_id": rid, "errors": errs, "record": rec})

    duplicate_rows = sum(1 for c in seen.values() if c > 1)
    summary = {
        "input": args.input,
        "rows": counts["rows"],
        "bad": counts["bad"],
        "duplicate_row_ids": duplicate_rows,
        "by_kind": {str(k): v for k, v in sorted(by_kind.items(), key=lambda kv: str(kv[0]))},
        "by_sign": {str(k): v for k, v in sorted(by_sign.items(), key=lambda kv: str(kv[0]))},
        "by_p_h": {repr(k): v for k, v in sorted(by_ph.items(), key=lambda kv: repr(kv[0]))},
        "by_L_kind": {repr(k): v for k, v in sorted(by_L_kind.items(), key=lambda kv: repr(kv[0]))},
        "errors": errors,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "input": args.input,
        "output": str(out),
        "rows": summary["rows"],
        "bad": summary["bad"],
        "duplicate_row_ids": duplicate_rows,
        "by_kind": summary["by_kind"],
        "by_p_h": summary["by_p_h"],
    }, sort_keys=True))
    print("PASS pressure-cover artifact verifier" if summary["bad"] == 0 else "FAIL pressure-cover artifact verifier")


if __name__ == "__main__":
    main()