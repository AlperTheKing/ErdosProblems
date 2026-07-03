#!/usr/bin/env python3
"""Build custom EQ-ODL1 reduced-support JSON files.

The output has a `greedy` list compatible with _codex_eq_odl1_reduced_lp.py.
Selection is combinatorial: columns are ranked by the exact weight of negative
target monomials they can repair, without expanding full products.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_shifted_lp as eq


def build_candidates(selected_names: set[str]):
    target_expr, _ = eq.build_target()
    target = eq.coeff_map(target_expr)
    generators = eq.build_generators()
    neg_target = {exp: -coeff for exp, coeff in target.items() if coeff < 0}
    out = []
    for gi, gen in enumerate(generators):
        if selected_names and gen.name not in selected_names:
            continue
        gmap = eq.coeff_map(gen.expr)
        neg_gen = [(exp, -coeff) for exp, coeff in gmap.items() if coeff < 0]
        pending: dict[tuple[int, tuple[int, ...]], set[tuple[int, ...]]] = {}
        for beta in neg_target:
            for alpha, _alpha_weight in neg_gen:
                gamma = eq.sub_exp(beta, alpha)
                if gamma is None or sum(gamma) > gen.cap:
                    continue
                pending.setdefault((gi, gamma), set()).add(beta)
        for (_gi, gamma), covers in pending.items():
            score = sum(neg_target[exp] for exp in covers)
            out.append({
                "generator": gen.name,
                "monomial_exp": list(gamma),
                "cover_count": len(covers),
                "cover_weight": score,
            })
    return out, len(neg_target), str(sum(neg_target.values()))


def item_json(item, fresh_count=None, fresh_weight=None):
    return {
        "generator": item["generator"],
        "monomial_exp": item["monomial_exp"],
        "fresh_count": int(fresh_count if fresh_count is not None else item["cover_count"]),
        "fresh_weight": str(fresh_weight if fresh_weight is not None else item["cover_weight"]),
        "total_cover_count": int(item["cover_count"]),
        "total_cover_weight": str(item["cover_weight"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generators", default="F1,F2,F3,F4,F5,F6,F7,B0_eta25_25,G1_UV_T,G2_UZ_T,G4_VZ_XY,G5_VZ_T,G6_A2_9T,G7_B2_4T")
    ap.add_argument("--top-per-generator", type=int, default=300)
    ap.add_argument("--global-top", type=int, default=0)
    ap.add_argument("--summary", default="tmp/eq_odl1_support_selected_v1.json")
    args = ap.parse_args()

    names = {x.strip() for x in args.generators.split(",") if x.strip()}
    candidates, neg_terms, neg_weight = build_candidates(names)
    by_gen = defaultdict(list)
    for item in candidates:
        by_gen[item["generator"]].append(item)
    selected = []
    seen = set()
    per_gen_counts = {}
    for name, items in sorted(by_gen.items()):
        ranked = sorted(items, key=lambda x: (x["cover_weight"], x["cover_count"]), reverse=True)
        chosen = ranked[: args.top_per_generator]
        per_gen_counts[name] = len(chosen)
        for item in chosen:
            key = (item["generator"], tuple(item["monomial_exp"]))
            if key not in seen:
                seen.add(key)
                selected.append(item_json(item))
    if args.global_top > 0:
        ranked = sorted(candidates, key=lambda x: (x["cover_weight"], x["cover_count"]), reverse=True)
        for item in ranked[: args.global_top]:
            key = (item["generator"], tuple(item["monomial_exp"]))
            if key not in seen:
                seen.add(key)
                selected.append(item_json(item))
    out = {
        "schema": "eq_odl1_support_selected_v1",
        "generators": sorted(names),
        "target_negative_terms": neg_terms,
        "target_negative_weight": neg_weight,
        "candidate_columns": len(candidates),
        "top_per_generator": args.top_per_generator,
        "global_top": args.global_top,
        "per_generator_selected": per_gen_counts,
        "greedy_columns": len(selected),
        "greedy": selected,
        "greedy_first": selected[:200],
    }
    path = Path(args.summary)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "candidate_columns": out["candidate_columns"],
        "selected_columns": out["greedy_columns"],
        "generators": len(names),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
