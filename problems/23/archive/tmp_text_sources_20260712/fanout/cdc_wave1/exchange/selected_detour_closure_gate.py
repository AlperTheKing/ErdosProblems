#!/usr/bin/env python3
"""Exhaust the smallest selected-support closures of the unit-detour core."""

from __future__ import annotations

import argparse
from itertools import product
import json
import math
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, SOFTCAP):
    sys.path.insert(0, str(path))

from ortools.sat.python import cp_model  # noqa: E402
import global_softcap as soft  # noqa: E402
from exchange_gate import build_metric  # noqa: E402
from unit_detour_core_gate import (  # noqa: E402
    adjacency,
    build_graph,
    edge,
    shortest_rows,
)


def triangle_free(n, blue, bad):
    adj = adjacency(n, set(blue) | set(bad))
    for x in range(n):
        for y in adj[x]:
            if x < y and any(y < z for z in set(adj[x]) & set(adj[y])):
                return False
    return True


def minimum_sigma(n, blue, bad):
    ctx = soft.make_graph_context(n, blue, bad)
    best = 10**9
    best_mask = None
    for mask in range(1 << (n - 1)):
        value = ctx.sigma(mask)
        if value < best:
            best = value
            best_mask = mask
    return best, best_mask


def and_var(model, left, right, name):
    out = model.new_bool_var(name)
    model.add(out <= left)
    model.add(out <= right)
    model.add(out >= left + right - 1)
    return out


def global_c5_payload(n, blue, bad, workers):
    graph_edges = sorted(set(blue) | set(bad))
    m = len(bad)
    model = cp_model.CpModel()
    x = [[model.new_bool_var(f"x_{v}_{i}") for i in range(5)] for v in range(n)]
    for row in x:
        model.add(sum(row) == 1)
    first_bad = min(bad)
    model.add(x[first_bad[0]][0] == 1)
    model.add(x[first_bad[1]][4] == 1)
    for index, (u, v) in enumerate(sorted(bad)):
        forward = and_var(model, x[u][0], x[v][4], f"bad_{index}_forward")
        reverse = and_var(model, x[u][4], x[v][0], f"bad_{index}_reverse")
        model.add(forward + reverse == 1)
    sizes = [model.new_int_var(0, n, f"size_{i}") for i in range(5)]
    for i in range(5):
        model.add(sizes[i] == sum(x[v][i] for v in range(n)))
    for i in range(5):
        j = (i + 1) % 5
        size_product = model.new_int_var(0, n * n, f"product_{i}")
        model.add_multiplication_equality(size_product, [sizes[i], sizes[j]])
        model.add(size_product >= m)
        between = []
        for index, (u, v) in enumerate(graph_edges):
            between.append(and_var(model, x[u][i], x[v][j], f"e_{i}_{index}_f"))
            between.append(and_var(model, x[v][i], x[u][j], f"e_{i}_{index}_r"))
        model.add(sum(between) >= m)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": solver.status_name(status), "classes": None}
    return {
        "status": solver.status_name(status),
        "classes": [[v for v in range(n) if solver.value(x[v][i])] for i in range(5)],
    }


def evaluate_rows(n, blue, bad, max_product):
    families = []
    for start, target in sorted(bad):
        distance, rows = shortest_rows(n, blue, start, target)
        if distance != 4:
            return {"allEll5": False, "distance": distance}
        families.append(rows)
    family_sizes = [len(items) for items in families]
    row_product = math.prod(family_sizes)
    if row_product > max_product:
        return {
            "allEll5": True,
            "familySizes": family_sizes,
            "rowProduct": row_product,
            "status": "ROW_PRODUCT_LIMIT",
        }
    ctx = soft.make_graph_context(n, blue, bad)
    best_pair = None
    best_choice = None
    best_flow = None
    collision_minimum = None
    cmin_defects = []
    for choice in product(*(range(size) for size in family_sizes)):
        rows = tuple(families[i][choice[i]] for i in range(len(families)))
        metric = build_metric(ctx, rows, force_full=True, p4_scope="unscoped")
        pair = (metric["collision"], metric["defect"])
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_choice = choice
            best_flow = metric["flow"]
        if collision_minimum is None or metric["collision"] < collision_minimum:
            collision_minimum = metric["collision"]
            cmin_defects = [metric["defect"]]
        elif metric["collision"] == collision_minimum:
            cmin_defects.append(metric["defect"])
    return {
        "allEll5": True,
        "familySizes": family_sizes,
        "rowProduct": row_product,
        "status": "EXHAUSTED",
        "lexMinimum": list(best_pair),
        "lexChoice": list(best_choice),
        "lexMaximumFlow": best_flow,
        "collisionMinimum": collision_minimum,
        "minimumDefectOnCollisionFace": min(cmin_defects),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--max-row-product", type=int, default=1_000_000)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")

    n, blue, base_bad, protection = build_graph(6)
    candidates = tuple(
        edge(path[i], path[i + 4])
        for path in protection
        for i in range(len(path) - 4)
    )
    if len(candidates) != 6 or len(set(candidates)) != 6:
        raise AssertionError(candidates)

    counts = {
        "subsets": 0,
        "triangleFree": 0,
        "maximumCut": 0,
        "allEll5": 0,
        "rowProductsExhausted": 0,
        "positiveLexDefect": 0,
        "positiveLexDefectWithoutGlobalC5": 0,
    }
    records = []
    for subset_mask in range(1 << len(candidates)):
        counts["subsets"] += 1
        added = {candidates[i] for i in range(len(candidates)) if subset_mask & (1 << i)}
        bad = frozenset(set(base_bad) | added)
        if not triangle_free(n, blue, bad):
            continue
        counts["triangleFree"] += 1
        sigma, sigma_mask = minimum_sigma(n, blue, bad)
        if sigma < 0:
            continue
        counts["maximumCut"] += 1
        row_data = evaluate_rows(n, blue, bad, args.max_row_product)
        if not row_data.get("allEll5"):
            continue
        counts["allEll5"] += 1
        if row_data.get("status") != "EXHAUSTED":
            records.append({"subsetMask": subset_mask, "minimumSigma": sigma, "rows": row_data})
            continue
        counts["rowProductsExhausted"] += 1
        lex_defect = row_data["lexMinimum"][1]
        record = {
            "subsetMask": subset_mask,
            "addedBads": sorted(added),
            "badCount": len(bad),
            "minimumSigma": sigma,
            "minimumSigmaMask": sigma_mask,
            "rows": row_data,
        }
        if lex_defect > 0:
            counts["positiveLexDefect"] += 1
            c5 = global_c5_payload(n, blue, bad, args.workers)
            record["globalC5"] = c5
            if c5["classes"] is None:
                counts["positiveLexDefectWithoutGlobalC5"] += 1
        records.append(record)

    payload = {
        "schema": "SELECTED_DETOUR_CLOSURE_V1",
        "arithmetic": "exhaustive integer cuts and row products; exact Dinic flow; integer CP-SAT globalC5",
        "n": n,
        "candidateBads": candidates,
        "counts": counts,
        "records": records,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if counts["positiveLexDefectWithoutGlobalC5"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
