"""Exact PHT gate for the adversarial global-minimum families.

PHT: sum_eta S(eta) <= |Omega| * (S(omega) - defect(A)).
All arithmetic is integer exact. For each Hall-failing tuple we use the
maximum deficiency returned by exact max-flow, which is the strongest shore
instance of the scalar inequality.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_r19_global_base_census import dec, loads
from _codex_r20_c5_nonuniform_global_cpsat import build_fixture
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
    full_owner_flow,
)


def analyze_system(label, n, blue, bad, families, max_product):
    product_size = 1
    for family in families:
        product_size *= len(family)
    if product_size > max_product:
        return {
            "label": label,
            "status": "skipped_product_cap",
            "tuples": product_size,
        }

    choices = tuple(itertools.product(*(range(len(f)) for f in families)))
    rows_by_choice = tuple(
        tuple(families[i][r] for i, r in enumerate(choice))
        for choice in choices
    )
    scores = tuple(
        active_scoped_obligation_score(n, blue, bad, rows)
        for rows in rows_by_choice
    )
    score_sum = sum(scores)
    failures = []
    for choice, rows, score in zip(choices, rows_by_choice, scores):
        if score == 0:
            continue
        flow = full_owner_flow(
            n, blue, bad, rows, label, require_full=False, quiet=True,
            scope="active", include_outside=False,
        )
        if flow["full"]:
            continue
        deficiency = flow["deficiency"]
        residual = product_size * (score - deficiency) - score_sum
        failures.append({
            "choice": choice,
            "score": score,
            "deficiency": deficiency,
            "owners": flow["deficientOwners"],
            "phtResidual": residual,
            "meanGapNumerator": product_size * score - score_sum,
        })

    return {
        "label": label,
        "status": "tested",
        "tuples": product_size,
        "familySizes": [len(f) for f in families],
        "scoreSum": score_sum,
        "minimumScore": min(scores),
        "maximumScore": max(scores),
        "hallFailures": len(failures),
        "phtFailures": sum(x["phtResidual"] < 0 for x in failures),
        "minimumPhtResidual": (
            min((x["phtResidual"] for x in failures), default=None)
        ),
        "smallest": (
            min(failures, key=lambda x: x["phtResidual"])
            if failures else None
        ),
    }


def graph6_system(g6, max_product):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return {"label": f"graph6:{g6}", "status": "not_all_length_five"}
    return analyze_system(
        f"graph6:{g6}", n, set(info["Bset"]), set(info["Mset"]),
        shortest_row_families(info), max_product,
    )


def double_star_89(max_product):
    r, c_left, c_right = 0, 1, 2
    left = [3, 4, 5, 6]
    right = [7, 8, 9, 10, 11]
    anchor = 12
    lock_counts = [0, 0, 0, 4, 6, 4, 5, 5, 3, 3, 3, 5]
    blue = set()

    def add_blue(x, y):
        blue.add(tuple(sorted((x, y))))

    add_blue(r, c_left)
    add_blue(r, c_right)
    for vertex in left:
        add_blue(c_left, vertex)
    for vertex in right:
        add_blue(c_right, vertex)
    bad = {(x, y) for x in left for y in right}
    next_vertex = 13
    for vertex, count in enumerate(lock_counts):
        for _ in range(count):
            x, y = next_vertex, next_vertex + 1
            next_vertex += 2
            add_blue(vertex, x)
            add_blue(x, y)
            add_blue(y, anchor)
    families = tuple(
        ((x, c_left, r, c_right, y),)
        for x in left for y in right
    )
    assert next_vertex == 89
    return analyze_system(
        "double_star_89_singleton", 89, blue, bad, families, max_product
    )


def c5_system(sizes, max_product):
    rotated, _, info, families = build_fixture(sizes)
    return analyze_system(
        f"C5:{','.join(map(str, sizes))}->"
        f"{','.join(map(str, rotated))}",
        info["n"], set(info["Bset"]), set(info["Mset"]), families, max_product,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-product", type=int, default=1_000_000)
    args = parser.parse_args()
    tick = chr(96)
    graph6_fixtures = (
        "I?" + tick + "fBO]]?",
        "I?" + tick + "cjVo{?",
        "I?" + tick + "ebRodO",
        "K?ABBBwerwBw",
    )
    c5_sizes = (
        (1, 1, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (2, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (2, 2, 2, 1, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (2, 2, 2, 2, 1),
        (3, 3, 1, 1, 1),
        (4, 2, 1, 1, 1),
        (3, 2, 2, 1, 1),
        (1, 2, 3, 2, 1),
        (2, 2, 3, 2, 2),
        (2, 3, 2, 3, 2),
        (3, 3, 3, 3, 3),
    )

    systems = [graph6_system(g6, args.max_product) for g6 in graph6_fixtures]
    systems.append(double_star_89(args.max_product))
    systems.extend(c5_system(sizes, args.max_product) for sizes in c5_sizes)
    tested = [x for x in systems if x["status"] == "tested"]
    falsifiers = [
        {"system": x["label"], **x["smallest"]}
        for x in tested if x["phtFailures"]
    ]
    payload = {
        "arithmetic": "integer exact",
        "maxProduct": args.max_product,
        "systems": systems,
        "testedSystems": len(tested),
        "testedTuples": sum(x["tuples"] for x in tested),
        "hallFailures": sum(x["hallFailures"] for x in tested),
        "phtFailures": sum(x["phtFailures"] for x in tested),
        "smallestFalsifier": min(
            falsifiers, key=lambda x: x["phtResidual"], default=None
        ),
        "r29Status": (
            "reconstructed after this finite-family run; see "
            "r29_pht_bound.json for the 680^676 product bound"
        ),
    }
    payload["scriptSha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return int(payload["phtFailures"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
