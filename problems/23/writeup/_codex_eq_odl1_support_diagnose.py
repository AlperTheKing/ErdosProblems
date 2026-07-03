#!/usr/bin/env python3
"""Support diagnostics for the EQ-ODL1 shifted-cone LP.

This does not prove the certificate.  It reports exact combinatorial
coverage of negative target monomials by the currently allowed shifted-cone
generator columns, plus a greedy negative-row cover that can seed smaller LPs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_shifted_lp as eq


def monomial_key(exp: tuple[int, ...]) -> str:
    return ",".join(str(x) for x in exp)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--greedy-limit", type=int, default=5000)
    ap.add_argument("--summary", default="tmp/eq_odl1_support_diagnose_v1.json")
    args = ap.parse_args()

    target_expr, _meta = eq.build_target()
    target = eq.coeff_map(target_expr)
    generators = eq.build_generators()
    neg_target = {exp: -coeff for exp, coeff in target.items() if coeff < 0}

    candidate_data = []
    by_generator: dict[str, dict[str, object]] = {}
    covered_by_gen: dict[str, set[tuple[int, ...]]] = defaultdict(set)

    for gi, gen in enumerate(generators):
        gmap = eq.coeff_map(gen.expr)
        neg_gen = [(exp, -coeff) for exp, coeff in gmap.items() if coeff < 0]
        seen_cols = set()
        gen_column_count = 0
        pending: dict[tuple[int, tuple[int, ...]], dict[tuple[int, ...], Fraction]] = {}
        for beta, beta_weight in neg_target.items():
            for alpha, alpha_weight in neg_gen:
                gamma = eq.sub_exp(beta, alpha)
                if gamma is None or sum(gamma) > gen.cap:
                    continue
                key = (gi, gamma)
                pending.setdefault(key, {})[beta] = alpha_weight
        for key, covers in pending.items():
            if key in seen_cols:
                continue
            seen_cols.add(key)
            gen_column_count += 1
            covered_by_gen[gen.name].update(covers)
            score = sum(neg_target[exp] for exp in covers)
            candidate_data.append({
                "gen_index": gi,
                "generator": gen.name,
                "exp": key[1],
                "covers": covers,
                "score": score,
            })
        by_generator[gen.name] = {
            "cap": gen.cap,
            "degree": gen.degree,
            "negative_terms": len(neg_gen),
            "candidate_columns": gen_column_count,
        }

    uncovered = set(neg_target)
    greedy = []
    candidates = candidate_data[:]
    while uncovered and candidates and len(greedy) < args.greedy_limit:
        best_i = -1
        best_score = Fraction(0)
        best_count = -1
        for i, cand in enumerate(candidates):
            fresh = set(cand["covers"]) & uncovered
            if not fresh:
                continue
            score = sum(neg_target[exp] for exp in fresh)
            if score > best_score or (score == best_score and len(fresh) > best_count):
                best_score = score
                best_count = len(fresh)
                best_i = i
        if best_i < 0:
            break
        cand = candidates.pop(best_i)
        fresh = set(cand["covers"]) & uncovered
        uncovered -= fresh
        greedy.append({
            "generator": cand["generator"],
            "monomial_exp": list(cand["exp"]),
            "fresh_count": len(fresh),
            "fresh_weight": str(sum(neg_target[exp] for exp in fresh)),
            "total_cover_count": len(cand["covers"]),
        })

    for name, stats in by_generator.items():
        stats["covered_negative_terms"] = len(covered_by_gen[name])
        stats["covered_negative_weight"] = str(sum(neg_target[exp] for exp in covered_by_gen[name]))

    out = {
        "schema": "eq_odl1_support_diagnose_v1",
        "target_negative_terms": len(neg_target),
        "target_negative_weight": str(sum(neg_target.values())),
        "candidate_columns": len(candidate_data),
        "by_generator": by_generator,
        "union_covered_negative_terms": len(set().union(*(set(c["covers"]) for c in candidate_data)) if candidate_data else set()),
        "greedy_limit": args.greedy_limit,
        "greedy_columns": len(greedy),
        "greedy_uncovered_terms": len(uncovered),
        "greedy_uncovered_weight": str(sum(neg_target[exp] for exp in uncovered)),
        "greedy": greedy,
        "greedy_first": greedy[:200],
        "uncovered_terms": [
            {"monomial": monomial_key(exp), "weight": str(neg_target[exp])}
            for exp in sorted(uncovered)[:200]
        ],
    }
    path = Path(args.summary)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "candidate_columns": out["candidate_columns"],
        "greedy_columns": out["greedy_columns"],
        "greedy_uncovered_terms": out["greedy_uncovered_terms"],
        "target_negative_terms": out["target_negative_terms"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()



