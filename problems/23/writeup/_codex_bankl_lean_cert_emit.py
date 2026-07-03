"""Emit and verify a Lean-facing Bank-L pressure-cover certificate artifact.

Input is the already exact pressure-cover certificate JSONL.  This normalizer
keeps the row identity target = max(P_Q, 0), but records proof cases in the
shape we want to hand to a formal proof:

* FREE/TIGHT: target is zero, no local certificate terms are needed.
* MU_NUK: positive non-detour rows, with a checked exact identity and the
  stronger coarse inequality P_Q <= mu_L * sum(nu_K values).
* DETOUR: positive detour-residual rows, with a checked exact identity but no
  mu_L claim because the value scale is the detour deficit.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any

MU = {7: F(100, 11), 9: F(100, 7), 11: F(100, 3)}

FREE_KINDS = {"packet_free", "tight"}
NUK_KINDS = {"lane_prefix_nuK", "nuK", "connected_nuK"}


def parse_frac(x: Any) -> F:
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise TypeError(f"not a rational literal: {x!r}")


def frac_s(x: F | None) -> str | None:
    if x is None:
        return None
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def sign_s(x: F) -> str:
    return "positive" if x > 0 else "zero" if x == 0 else "negative"


def row_id(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": rec["name"],
        "n": rec["n"],
        "m": rec["m"],
        "f": rec["f"],
        "row": rec["row"],
    }


def normalized_term(term: dict[str, Any]) -> dict[str, Any]:
    value = parse_frac(term["value"])
    coeff = parse_frac(term["coeff"])
    contribution = parse_frac(term["contribution"])
    out: dict[str, Any] = {
        "kind": term["kind"],
        "value": frac_s(value),
        "coeff": frac_s(coeff),
        "contribution": frac_s(contribution),
    }
    for key in (
        "source_kind",
        "label",
        "i",
        "verts",
        "vertices",
        "terminal",
        "sigma",
        "nu",
        "K_S",
        "size",
        "TQ",
    ):
        if key in term:
            out[key] = term[key]
    return out


def classify(rec: dict[str, Any]) -> str:
    Pq = parse_frac(rec["P_Q"])
    if Pq < 0:
        return "FREE_PACKET_EXCHANGE"
    if Pq == 0:
        return "TIGHT_ZERO"
    if rec["pc_kind"] == "detour":
        return "DETOUR_RESIDUAL"
    if rec["pc_kind"] in NUK_KINDS:
        return "MU_NUK"
    return "UNKNOWN"


def normalize_record(rec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errs: list[str] = []
    Pq = parse_frac(rec["P_Q"])
    rho = parse_frac(rec["rho_Q"])
    target = Pq if Pq > 0 else F(0)
    proof_case = classify(rec)
    terms = [normalized_term(t) for t in rec.get("terms", [])]
    contribution_sum = sum(parse_frac(t["contribution"]) for t in terms)
    value_sum = sum(parse_frac(t["value"]) for t in terms)

    if contribution_sum != target:
        errs.append("identity_sum")
    if target < 0:
        errs.append("negative_target")
    if any(parse_frac(t["value"]) < 0 for t in terms):
        errs.append("negative_value")
    if any(parse_frac(t["coeff"]) < 0 for t in terms):
        errs.append("negative_coeff")
    if Pq <= 0 and terms:
        errs.append("free_terms")
    if Pq > 0 and not terms:
        errs.append("positive_no_terms")
    if proof_case == "UNKNOWN":
        errs.append("unknown_case")
    if Pq > 0 and rho < Pq:
        errs.append("finite_rho_less_than_pressure")

    mu_L = MU.get(rec["L"])
    mu_margin: F | None = None
    if proof_case == "MU_NUK":
        if mu_L is None:
            errs.append("missing_mu")
        else:
            mu_margin = mu_L * value_sum - Pq
            if mu_margin < 0:
                errs.append("mu_margin_negative")
    elif proof_case == "DETOUR_RESIDUAL":
        if any(t["kind"] != "detour" for t in terms):
            errs.append("detour_non_detour_term")
    elif proof_case in {"FREE_PACKET_EXCHANGE", "TIGHT_ZERO"}:
        if target != 0:
            errs.append("zero_case_nonzero_target")

    out = {
        "schema": "bankl_pressure_cover_lean_v1",
        "row_id": row_id(rec),
        "parameters": {
            "L": rec["L"],
            "p": rec["p"],
            "h": rec["h"],
            "d": rec["d"],
            "r": rec["r"],
            "P_Q": frac_s(Pq),
            "rho_Q": frac_s(rho),
            "P_Q_sign": sign_s(Pq),
            "target": frac_s(target),
        },
        "proof_case": proof_case,
        "source": {
            "schema": rec.get("schema"),
            "pc_kind": rec.get("pc_kind"),
            "source_certificate_kind": rec.get("source_certificate_kind"),
        },
        "identity": {
            "term_contribution_sum": frac_s(contribution_sum),
            "target": frac_s(target),
            "verified": contribution_sum == target,
        },
        "terms": terms,
        "mu_bound": {
            "applies": proof_case == "MU_NUK",
            "mu_L": frac_s(mu_L) if proof_case == "MU_NUK" else None,
            "value_sum": frac_s(value_sum) if proof_case == "MU_NUK" else None,
            "margin": frac_s(mu_margin) if proof_case == "MU_NUK" else None,
            "verified": (mu_margin is not None and mu_margin >= 0)
            if proof_case == "MU_NUK"
            else None,
        },
        "finite_row_check": {
            "rho_minus_target": frac_s(rho - target),
            "verified": rho >= target,
        },
        "verified": not errs,
    }
    return out, errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pressure_cover_lean_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_pressure_cover_lean_v1_summary.json")
    ap.add_argument("--max-errors", type=int, default=5)
    args = ap.parse_args()

    counts: Counter[str] = Counter()
    by_L_case: Counter[tuple[int, str]] = Counter()
    min_mu_margin: F | None = None
    min_rho_margin: F | None = None
    errors: list[dict[str, Any]] = []

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, out_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as out:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            src = json.loads(line)
            rec, errs = normalize_record(src)
            counts["rows"] += 1
            counts[f"case:{rec['proof_case']}"] += 1
            counts[f"P:{rec['parameters']['P_Q_sign']}"] += 1
            by_L_case[(rec["parameters"]["L"], rec["proof_case"])] += 1

            rho_margin = parse_frac(rec["finite_row_check"]["rho_minus_target"])
            min_rho_margin = rho_margin if min_rho_margin is None or rho_margin < min_rho_margin else min_rho_margin
            if rec["proof_case"] == "MU_NUK":
                margin = parse_frac(rec["mu_bound"]["margin"])
                min_mu_margin = margin if min_mu_margin is None or margin < min_mu_margin else min_mu_margin

            if errs:
                counts["bad"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line": lineno, "errors": errs, "record": rec})
            out.write(json.dumps(rec, sort_keys=True) + "\n")

    summary = {
        "input": args.input,
        "output": str(out_path),
        "rows": counts["rows"],
        "bad": counts["bad"],
        "proof_cases": {
            k.removeprefix("case:"): v for k, v in sorted(counts.items()) if k.startswith("case:")
        },
        "pressure_signs": {
            k.removeprefix("P:"): v for k, v in sorted(counts.items()) if k.startswith("P:")
        },
        "by_L_case": {repr(k): v for k, v in sorted(by_L_case.items(), key=lambda kv: repr(kv[0]))},
        "min_mu_margin": frac_s(min_mu_margin),
        "min_rho_minus_target": frac_s(min_rho_margin),
        "errors": errors,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("output", "rows", "bad", "proof_cases", "min_mu_margin", "min_rho_minus_target")}, sort_keys=True))
    print("PASS Bank-L Lean certificate normalizer" if counts["bad"] == 0 else "FAIL Bank-L Lean certificate normalizer")


if __name__ == "__main__":
    main()
