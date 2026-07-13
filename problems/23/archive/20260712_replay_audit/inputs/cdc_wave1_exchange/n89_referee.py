#!/usr/bin/env python3
"""Independent exact referee for the N89 grouped-flow counterexample."""

from __future__ import annotations

from collections import deque
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
FIXTURES = ROOT / "tmp" / "fanout" / "p5_fixtures" / "gate.py"
for path in (HERE, SOFTCAP):
    sys.path.insert(0, str(path))

import global_softcap as soft  # noqa: E402
from exchange_gate import build_metric, shore_profile  # noqa: E402


def load_fixture_module():
    spec = importlib.util.spec_from_file_location("cdc_exchange_p5_fixtures", FIXTURES)
    if spec is None or spec.loader is None:
        raise RuntimeError(FIXTURES)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adjacency(n, edges):
    result = [set() for _ in range(n)]
    for x, y in edges:
        result[x].add(y)
        result[y].add(x)
    return result


def shortest_rows(n, blue, source, target):
    adj = adjacency(n, blue)
    distance = [-1] * n
    distance[target] = 0
    queue = deque([target])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if distance[y] < 0:
                distance[y] = distance[x] + 1
                queue.append(y)
    rows = []

    def visit(path):
        x = path[-1]
        if len(path) == 5:
            if x == target:
                rows.append(tuple(path))
            return
        for y in sorted(adj[x]):
            if y not in path and distance[y] == distance[x] - 1:
                visit(path + (y,))

    if distance[source] == 4:
        visit((source,))
    return distance[source], tuple(rows)


def exact_maxcut_quotient(fixture):
    """Optimize the private three-edge lock paths, then enumerate 12 core bits."""
    n = fixture.n
    if n != 89:
        raise AssertionError(n)
    anchor = 12
    blue_adj = adjacency(n, fixture.blue)
    bad = set(fixture.bad)
    core_blue = {
        (x, y) for x, y in fixture.blue if x < 12 and y < 12
    }
    q = []
    private_seen = set()
    for owner in range(12):
        first = sorted(x for x in blue_adj[owner] if x >= 13)
        q.append(len(first))
        for x in first:
            second = [y for y in blue_adj[x] if y != owner]
            if len(second) != 1:
                raise AssertionError((owner, x, second))
            y = second[0]
            if blue_adj[y] != {x, anchor}:
                raise AssertionError((owner, x, y, blue_adj[y]))
            private_seen.update((x, y))
    if private_seen != set(range(13, 89)):
        raise AssertionError("lock paths do not partition private vertices")

    best = -1
    best_masks = []
    for mask in range(1 << 12):
        value = sum(q[v] * (3 - ((mask >> v) & 1)) for v in range(12))
        value += sum(
            ((mask >> x) & 1) != ((mask >> y) & 1)
            for x, y in core_blue
        )
        value += sum(
            ((mask >> x) & 1) != ((mask >> y) & 1)
            for x, y in bad
        )
        if value > best:
            best = value
            best_masks = [mask]
        elif value == best:
            best_masks.append(mask)
    displayed = (1 << 1) | (1 << 2)
    return {
        "lockMultiplicities": q,
        "assignmentsChecked": 1 << 12,
        "maximumCut": best,
        "maximizerCount": len(best_masks),
        "displayedAttains": displayed in best_masks,
    }


def full_metric(ctx, rows, p4_scope):
    return build_metric(ctx, rows, force_full=True, p4_scope=p4_scope)


def enumerate_shores(ctx, metric):
    owners = metric["owners"]
    best_gap = 0
    best_shores = []
    for mask in range(1, 1 << len(owners)):
        shore = tuple(
            owner for index, owner in enumerate(owners)
            if mask & (1 << index)
        )
        profile = shore_profile(ctx, metric, shore)
        if profile["gap"] > best_gap:
            best_gap = profile["gap"]
            best_shores = [(shore, profile)]
        elif profile["gap"] == best_gap:
            best_shores.append((shore, profile))
    return best_gap, best_shores


def main():
    fixture_module = load_fixture_module()
    fixture = fixture_module.build_89()
    fixture_module.validate_fixture(fixture)
    n = fixture.n
    all_edges = set(fixture.blue) | set(fixture.bad)
    adj = adjacency(n, all_edges)
    triangle_count = sum(
        1
        for x, y in all_edges
        for z in adj[x] & adj[y]
        if y < z
    )

    blue_adj = adjacency(n, fixture.blue)
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in blue_adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)

    database = []
    rows = []
    for edge in sorted(fixture.bad):
        distance, family = shortest_rows(n, fixture.blue, *edge)
        database.append({
            "edge": list(edge),
            "distance": distance,
            "familySize": len(family),
        })
        if len(family) != 1:
            raise AssertionError((edge, family))
        rows.append(family[0])
    if tuple(rows) != tuple(fixture.rows):
        raise AssertionError("fixture rows differ from complete singleton database")

    ctx = soft.make_graph_context(n, fixture.blue, fixture.bad)
    strict_metric = full_metric(ctx, rows, "strict")
    metric = full_metric(ctx, rows, "unscoped")
    if not strict_metric["full"] or not metric["full"]:
        raise AssertionError("all six relations were not evaluated")
    state = metric["state"]
    if state.active_edges:
        raise AssertionError(state.active_edges)
    for base in metric["relation"]:
        x, y = divmod(base, n)
        if x == y or state.pair[x][y] != 0:
            raise AssertionError(("non-FreeHalf relation base", x, y))

    owners = metric["owners"]
    strict_gap, strict_shores = enumerate_shores(ctx, strict_metric)
    best_gap, best_shores = enumerate_shores(ctx, metric)
    strict_hub_profile = shore_profile(ctx, strict_metric, (0, 1, 2))
    hub_profile = shore_profile(ctx, metric, (0, 1, 2))
    maxcut = exact_maxcut_quotient(fixture)
    checks = {
        "order89": n == 89,
        "edgeCounts": len(fixture.blue) == 125 and len(fixture.bad) == 20,
        "triangleFree": triangle_count == 0,
        "blueConnected": len(seen) == n,
        "maxCut125": maxcut["maximumCut"] == 125 and maxcut["displayedAttains"],
        "singletonCompleteRows": all(item["familySize"] == 1 for item in database),
        "uniqueRowChoice": len(rows) == 20,
        "collisionUnits388": metric["collision"] == 388,
        "globalDemand776": sum(metric["demand"]) == 776,
        "allSixRelations": len(metric["evaluated"]) == 6,
        "actualFreeHalfBases": all(
            (base // n) != (base % n)
            and state.pair[base // n][base % n] == 0
            for base in metric["relation"]
        ),
        "strictMaximumFlow774": strict_metric["flow"] == 774,
        "strictDefect2": strict_metric["defect"] == 2,
        "unscopedMaximumFlow776": metric["flow"] == 776,
        "unscopedDefect0": metric["defect"] == 0,
        "allOwnerShores": len(owners) == 12,
        "strictHubDual": strict_hub_profile["demand"] == 528
        and strict_hub_profile["capacity"] == 526
        and strict_hub_profile["gap"] == 2,
        "strictMaximumShoreGap2": strict_gap == 2,
        "unscopedHubRepaired": hub_profile["demand"] == 528
        and hub_profile["capacity"] >= 528
        and hub_profile["gap"] <= 0,
        "unscopedMaximumShoreGap0": best_gap == 0,
    }
    if not all(checks.values()):
        raise AssertionError(checks)

    payload = {
        "schema": "CDC_WAVE1_N89_REFEREE_V1",
        "arithmetic": "Python integers only",
        "checks": checks,
        "graph": {
            "order": n,
            "blueEdges": len(fixture.blue),
            "badEdges": len(fixture.bad),
            "maxcut": maxcut,
            "rowFamilySizes": [item["familySize"] for item in database],
        },
        "strictP4Flow": {
            "globalCollisionHalfDemand": sum(strict_metric["demand"]),
            "maximumFlow": strict_metric["flow"],
            "defect": strict_metric["defect"],
            "hubProfile": strict_hub_profile,
            "maximumShoreGap": strict_gap,
            "maxGapShoreCount": len(strict_shores),
        },
        "unscopedP4Flow": {
            "collisionUnits": metric["collision"],
            "globalCollisionHalfDemand": sum(metric["demand"]),
            "maximumFlow": metric["flow"],
            "defect": metric["defect"],
            "relations": list(metric["evaluated"]),
            "activeEdges": len(state.active_edges),
        },
        "unscopedDual": {
            "ownerShoreCount": (1 << len(owners)) - 1,
            "maximumGap": best_gap,
            "hubShore": [0, 1, 2],
            "hubProfile": hub_profile,
            "maxGapShoreCount": len(best_shores),
        },
        "verdict": "STRICT_P4_COUNTEREXAMPLE_REPAIRED_BY_UNSCOPED_P4",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
