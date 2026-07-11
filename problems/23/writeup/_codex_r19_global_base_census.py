"""Parallel exact census gate for the GLOBAL R19 base-transfer relation.

Scope: one connected-B Gamma-minimum maximum cut chosen by `_h.loads` for
every connected triangle-free graph; retain all-ell=5 instances in which every
bad edge has a unique shortest row.  The latter makes the row-choice omega
canonical.  Source ordered pairs range over ALL graph vertices.

This is a falsifier search, not a proof of universal Hall completeness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product, repeat
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _h import GENG, dec, loads  # noqa: E402


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def switch_counts(blue, bad, S):
    return (
        sum((u in S) ^ (v in S) for u, v in blue),
        sum((u in S) ^ (v in S) for u, v in bad),
    )


def multiplicities(n, rows):
    count = [[0] * n for _ in range(n)]
    for row in rows:
        for x in row:
            for y in row:
                count[x][y] += 1
    return count


def owner_demands(count, component, active_edges):
    demands = {}
    for x in sorted(component):
        out = demands.setdefault(x, [])
        for y in sorted(component):
            for copy in range(max(0, count[x][y] - 1)):
                out.append(("collision", x, y, copy, 0))
                out.append(("collision", x, y, copy, 1))
    for u, v in sorted(active_edges):
        demands.setdefault(u, []).append(("hit", u, (u, v)))
        demands.setdefault(v, []).append(("hit", v, (u, v)))
    return {owner: rows for owner, rows in demands.items() if rows}


def global_candidates(owner, n, count, adj, blue, bad, relation_policy):
    relation = {}
    for y in range(n):
        if count[owner][y] == 0:
            relation[(owner, y, 0)] = "sameOwner"
            relation[(owner, y, 1)] = "sameOwner"
    if relation_policy not in {"row-only", "row-reserved"}:
        neighbours = sorted(v for v in adj[owner] if edge(owner, v) in blue)
        for x in neighbours:
            for y in neighbours:
                if x == y or count[x][y] != 0:
                    continue
                dB, dM = switch_counts(blue, bad, {x, y})
                if dM + 2 > dB:
                    continue
                relation.setdefault((x, y, 0), "c5Base")
                relation.setdefault((x, y, 1), "c5Base")
    if relation_policy in {"row-companion", "row-only", "row-reserved"}:
        companions = [x for x in range(n) if count[owner][x] > 0]
        for x in companions:
            for y in companions:
                if x == y or count[x][y] != 0:
                    continue
                dB, dM = switch_counts(blue, bad, {x, y})
                if dM > dB:
                    continue
                relation.setdefault((x, y, 0), "rowCompanion")
                relation.setdefault((x, y, 1), "rowCompanion")
    return relation


def full_matching(demands, candidates):
    nodes = [
        (owner, i)
        for owner in sorted(demands)
        for i in range(len(demands[owner]))
    ]
    nodes.sort(key=lambda node: len(candidates[node[0]]))
    source_owner = {}
    demand_source = {}

    def augment(node, seen):
        owner, _ = node
        for source in candidates[owner]:
            if source in seen:
                continue
            seen.add(source)
            previous = source_owner.get(source)
            if previous is None or augment(previous, seen):
                source_owner[source] = node
                demand_source[node] = source
                return True
        return False

    unmatched = []
    for node in nodes:
        if not augment(node, set()):
            unmatched.append(node)
    return demand_source, unmatched


def hall_witness(demands, candidates, matching, unmatched):
    source_owner = {source: node for node, source in matching.items()}
    left = set(unmatched)
    right = set()
    queue = deque(unmatched)
    while queue:
        node = queue.popleft()
        owner, _ = node
        matched_source = matching.get(node)
        for source in candidates[owner]:
            if source == matched_source or source in right:
                continue
            right.add(source)
            next_node = source_owner.get(source)
            if next_node is not None and next_node not in left:
                left.add(next_node)
                queue.append(next_node)
    assert len(left) > len(right)
    return left, right


def evaluate_rows(g6, n, info, rows, relation_policy):
    max_row_intersection = max(
        (len(set(rows[i]) & set(rows[j]))
         for i in range(len(rows)) for j in range(i + 1, len(rows))),
        default=0,
    )
    component = set().union(*(set(row) for row in rows)) if rows else set()
    support = {
        edge(u, v)
        for row in rows
        for u, v in zip(row, row[1:])
    }
    active_edges = {
        e for e in info["Bset"]
        if e[0] in component and e[1] in component and e not in support
    }
    count = multiplicities(n, rows)
    demands = owner_demands(count, component, active_edges)
    reserved_sources = set()
    reserved_hits = 0
    if relation_policy == "row-reserved":
        for u, v in active_edges:
            if count[u][v] != 0:
                return ("fail", g6, {
                    "n": n, "rows": len(rows),
                    "activeEdges": len(active_edges),
                    "demands": sum(map(len, demands.values())), "matched": 0,
                    "hallLeft": 1, "hallRight": 0, "hallDeficiency": 1,
                    "hallSHA256": "off-support-cooccurrence",
                    "maxRowIntersection": max_row_intersection,
                })
            reserved_sources.add((u, v, 0))
            reserved_sources.add((v, u, 0))
            reserved_hits += 2
        demands = {
            owner: [d for d in owner_demands if d[0] == "collision"]
            for owner, owner_demands in demands.items()
        }
        demands = {owner: ds for owner, ds in demands.items() if ds}
    if not demands:
        return ("pass", g6, {
            "n": n, "rows": len(rows), "demands": 0,
            "matched": reserved_hits, "external": 0,
            "reservedHits": reserved_hits,
            "maxRowIntersection": max_row_intersection,
        })
    candidates = {
        owner: global_candidates(
            owner, n, count, info["adj"], info["Bset"], info["Mset"],
            relation_policy,
        )
        for owner in demands
    }
    if reserved_sources:
        candidates = {
            owner: {
                source: kind for source, kind in relation.items()
                if source not in reserved_sources
            }
            for owner, relation in candidates.items()
        }
    matching, unmatched = full_matching(demands, candidates)
    total = sum(map(len, demands.values())) + reserved_hits
    if unmatched:
        left, right = hall_witness(demands, candidates, matching, unmatched)
        payload = json.dumps({
            "g6": g6, "left": sorted(left), "right": sorted(right),
        }, separators=(",", ":")).encode()
        return ("fail", g6, {
            "n": n, "rows": len(rows), "activeEdges": len(active_edges),
            "demands": total, "matched": len(matching) + reserved_hits,
            "reservedHits": reserved_hits,
            "hallLeft": len(left), "hallRight": len(right),
            "hallDeficiency": len(left) - len(right),
            "hallSHA256": hashlib.sha256(payload).hexdigest(),
            "maxRowIntersection": max_row_intersection,
        })
    external = sum(
        source[0] not in component or source[1] not in component
        for source in matching.values()
    )
    kinds = Counter(candidates[node[0]][source] for node, source in matching.items())
    return ("pass", g6, {
        "n": n, "rows": len(rows), "activeEdges": len(active_edges),
        "demands": total, "matched": len(matching) + reserved_hits,
        "reservedHits": reserved_hits, "external": external,
        "maxRowIntersection": max_row_intersection,
        "relations": dict(sorted(kinds.items())),
    })


def evaluate(g6, row_policy, relation_policy="base"):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None:
        return ("skip_no_cut", g6, None)
    if any(L != 5 for L in info["ell"].values()):
        return ("skip_not_all5", g6, None)

    families = [tuple(map(tuple, info["cyc"][f])) for f in info["M"]]
    if row_policy == "unique" and any(len(rows) != 1 for rows in families):
        return ("skip_nonunique", g6, None)
    if row_policy in {"min-demand", "min-collision"}:
        best_rows = None
        best_key = None
        choices_tried = 0
        for chosen in product(*families):
            choices_tried += 1
            chosen = list(chosen)
            count = multiplicities(n, chosen)
            component = set().union(*(set(row) for row in chosen)) if chosen else set()
            support = {
                edge(u, v)
                for row in chosen for u, v in zip(row, row[1:])
            }
            active_edges = {
                e for e in info["Bset"]
                if e[0] in component and e[1] in component and e not in support
            }
            collision_units = sum(
                max(0, count[x][y] - 1)
                for x in component for y in component
            )
            score = (2 * collision_units + 2 * len(active_edges)
                     if row_policy == "min-demand" else collision_units)
            key = (score, tuple(chosen))
            if best_key is None or key < best_key:
                best_key = key
                best_rows = chosen
        assert best_rows is not None
        kind, _, detail = evaluate_rows(
            g6, n, info, best_rows, relation_policy
        )
        detail["rowCombinations"] = choices_tried
        detail["choicesTried"] = choices_tried
        detail["selectionScore"] = best_key[0]
        return (kind, g6, detail)
    if row_policy != "exists":
        return evaluate_rows(
            g6, n, info, [rows[0] for rows in families], relation_policy
        )

    total_combinations = 1
    for rows in families:
        total_combinations *= len(rows)
    best_failure = None
    for choices_tried, chosen in enumerate(product(*families), start=1):
        kind, _, detail = evaluate_rows(
            g6, n, info, list(chosen), relation_policy
        )
        detail["rowCombinations"] = total_combinations
        detail["choicesTried"] = choices_tried
        if kind == "pass":
            return (kind, g6, detail)
        if best_failure is None or (
            detail["hallDeficiency"], -detail["matched"]
        ) < (
            best_failure["hallDeficiency"], -best_failure["matched"]
        ):
            best_failure = detail
    assert best_failure is not None
    return ("fail", g6, best_failure)


def graph6_for_orders(n_min, n_max):
    out = []
    by_n = {}
    for n in range(n_min, n_max + 1):
        run = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True, check=True
        )
        rows = [s.strip() for s in run.stdout.split() if s.strip()]
        by_n[n] = len(rows)
        out.extend(rows)
    return out, by_n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument("--workers", type=int, default=48)
    parser.add_argument("--max-failures", type=int, default=20)
    parser.add_argument(
        "--row-policy",
        choices=("unique", "first", "exists", "min-demand", "min-collision"),
        default="unique"
    )
    parser.add_argument(
        "--relation-policy",
        choices=("base", "row-companion", "row-only", "row-reserved"),
        default="base"
    )
    args = parser.parse_args()

    graph6, generated = graph6_for_orders(args.n_min, args.n_max)
    status = Counter()
    tested_by_n = Counter()
    failures = []
    max_demands = 0
    external_passes = 0
    row_intersections = Counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for kind, g6, detail in pool.map(
            evaluate, graph6, repeat(args.row_policy),
            repeat(args.relation_policy), chunksize=32
        ):
            status[kind] += 1
            if kind in {"pass", "fail"}:
                tested_by_n[detail["n"]] += 1
                max_demands = max(max_demands, detail["demands"])
                row_intersections[detail["maxRowIntersection"]] += 1
            if kind == "pass" and detail["external"] > 0:
                external_passes += 1
            if kind == "fail" and len(failures) < args.max_failures:
                failures.append({"g6": g6, **detail})

    print(json.dumps({
        "orders": [args.n_min, args.n_max],
        "workers": args.workers,
        "rowPolicy": args.row_policy,
        "relationPolicy": args.relation_policy,
        "generatedByN": generated,
        "status": dict(sorted(status.items())),
        "testedByN": {str(k): v for k, v in sorted(tested_by_n.items())},
        "maxDemands": max_demands,
        "passesUsingExternalSources": external_passes,
        "maxRowIntersectionHistogram": {
            str(k): v for k, v in sorted(row_intersections.items())
        },
        "failures": failures,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
