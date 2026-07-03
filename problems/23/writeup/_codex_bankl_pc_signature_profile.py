"""Compress pressure-cover certificate JSONL into exact signature classes.

This is an audit/proof-planning helper.  It does not prove the structural
pressure-cover theorem; it shows how many distinct machine certificate shapes
the current exact artifact uses, especially on the P_Q > 0 hard rows.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


def parse_frac(x) -> F:
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise TypeError(x)


def term_signature(term: dict) -> tuple:
    return (
        term.get("kind"),
        term.get("source_kind"),
        term.get("terminal"),
        term.get("i"),
        term.get("sigma"),
        term.get("K_S"),
        term.get("value"),
    )


def cert_signature(rec: dict) -> tuple:
    return (
        rec["pc_kind"],
        rec["L"],
        rec["r"],
        rec["p"],
        rec["h"],
        rec["d"],
        rec["P_Q"],
        tuple(term_signature(t) for t in rec["terms"]),
    )


def coarse_signature(rec: dict) -> tuple:
    term_kinds = tuple(
        (t.get("kind"), t.get("source_kind"), t.get("terminal"))
        for t in rec["terms"]
    )
    return (
        rec["pc_kind"],
        rec["L"],
        rec["r"],
        rec["p"],
        rec["h"],
        rec["d"],
        rec["P_Q"],
        term_kinds,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pc_cover_certs_v1.jsonl")
    ap.add_argument("--output", default="tmp/bankl_pc_signature_profile_v1.json")
    ap.add_argument("--top", type=int, default=80)
    args = ap.parse_args()

    rows = 0
    bad = 0
    kind_counts: Counter = Counter()
    sign_counts: Counter = Counter()
    hard_counts: Counter = Counter()
    exact_sig_counts: Counter = Counter()
    coarse_sig_counts: Counter = Counter()
    examples: dict[tuple, dict] = {}
    hard_by_length: Counter = Counter()
    hard_by_kind: Counter = Counter()
    hard_by_source: Counter = Counter()
    max_terms = 0

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            rows += 1
            kind_counts[rec["pc_kind"]] += 1
            sign_counts[rec["pressure_sign"]] += 1
            max_terms = max(max_terms, len(rec["terms"]))
            target = parse_frac(rec["target"])
            total = sum(parse_frac(t["contribution"]) for t in rec["terms"])
            if total != target or not rec.get("verified"):
                bad += 1
            if parse_frac(rec["P_Q"]) > 0:
                hard_counts["rows"] += 1
                hard_by_length[rec["L"]] += 1
                hard_by_kind[rec["pc_kind"]] += 1
                src = tuple(t.get("source_kind", t.get("kind")) for t in rec["terms"])
                hard_by_source[src] += 1
                esig = cert_signature(rec)
                csig = coarse_signature(rec)
                exact_sig_counts[esig] += 1
                coarse_sig_counts[csig] += 1
                examples.setdefault(esig, {
                    "name": rec["name"],
                    "n": rec["n"],
                    "m": rec["m"],
                    "f": rec["f"],
                    "row": rec["row"],
                    "L": rec["L"],
                    "r": rec["r"],
                    "d": rec["d"],
                    "P_Q": rec["P_Q"],
                    "rho_Q": rec["rho_Q"],
                    "pc_kind": rec["pc_kind"],
                    "terms": rec["terms"],
                })

    def sig_to_json(sig: tuple, count: int) -> dict:
        return {
            "count": count,
            "signature": repr(sig),
            "example": examples.get(sig),
        }

    summary = {
        "input": args.input,
        "rows": rows,
        "bad_identity_rows": bad,
        "max_terms_per_row": max_terms,
        "kind_counts": dict(sorted(kind_counts.items())),
        "sign_counts": dict(sorted(sign_counts.items())),
        "hard_rows": hard_counts["rows"],
        "hard_by_length": dict(sorted(hard_by_length.items())),
        "hard_by_kind": dict(sorted(hard_by_kind.items())),
        "hard_by_source_tuple": {repr(k): v for k, v in hard_by_source.most_common()},
        "hard_exact_signature_count": len(exact_sig_counts),
        "hard_coarse_signature_count": len(coarse_sig_counts),
        "top_exact_signatures": [
            sig_to_json(sig, count)
            for sig, count in exact_sig_counts.most_common(args.top)
        ],
        "top_coarse_signatures": [
            {"count": count, "signature": repr(sig)}
            for sig, count in coarse_sig_counts.most_common(args.top)
        ],
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "input": args.input,
        "output": str(out),
        "rows": rows,
        "bad_identity_rows": bad,
        "hard_rows": hard_counts["rows"],
        "hard_exact_signature_count": len(exact_sig_counts),
        "hard_coarse_signature_count": len(coarse_sig_counts),
        "hard_by_kind": dict(sorted(hard_by_kind.items())),
        "hard_by_length": dict(sorted(hard_by_length.items())),
        "max_terms_per_row": max_terms,
    }, sort_keys=True))
    if bad == 0:
        print("PASS pressure-cover signature profile")
    else:
        print("FAIL pressure-cover signature profile")


if __name__ == "__main__":
    main()
