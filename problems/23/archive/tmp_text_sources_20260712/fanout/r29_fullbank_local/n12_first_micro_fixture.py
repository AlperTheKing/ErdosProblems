"""Exact anatomy of the first N=12 common-blue micro-Hall failure."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tmp/fanout/pht_n12_direct"))
sys.path.insert(0, str(ROOT / "problems/23/writeup"))

import n12_pht as n12


G6 = "K??E@cyjFgWk"
CHOICE = (0, 4, 5, 7)


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def main() -> None:
    n, edges = n12.dec(G6)
    assert n == 12
    info = n12.loads(n, edges)
    assert info is not None and all(v == 5 for v in info["ell"].values())
    families = n12.shortest_row_families(info)
    assert tuple(map(len, families)) == (6, 5, 8, 10)
    rows = tuple(n12.rows_for_choice(families, CHOICE))
    blue = set(info["Bset"])
    bad = set(info["Mset"])

    pair = Counter()
    row_count = [0] * n
    support = set()
    for row in rows:
        for x in row:
            row_count[x] += 1
            for y in row:
                pair[x, y] += 1
        support.update(norm(x, y) for x, y in zip(row, row[1:]))
    selected = {x for row in rows for x in row}
    active = {
        e for e in blue
        if e[0] in selected and e[1] in selected and e not in support
    }

    parent = {v: v for v in selected}

    def find(v: int) -> int:
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(x: int, y: int) -> None:
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    for x, y in active:
        union(x, y)
    active_roots = {
        find(x) for x, y in bad
        if x in selected and y in selected and find(x) == find(y)
    }
    active_vertices = {v for v in selected if find(v) in active_roots}
    demanded_active = {e for e in active if find(e[0]) in active_roots}
    active_degree = [0] * n
    for x, y in demanded_active:
        active_degree[x] += 1
        active_degree[y] += 1

    collision = {}
    hit_need = {}
    micro_demand = {}
    for owner in sorted(active_vertices):
        collision[owner] = 2 * sum(
            multiplicity - 1
            for (x, _), multiplicity in pair.items()
            if x == owner and multiplicity >= 2
        )
        hit_need[owner] = max(
            0, active_degree[owner] - max(0, n - 5 * row_count[owner])
        )
        micro_demand[owner] = collision[owner] + 25 * hit_need[owner]
    owners = [o for o in sorted(active_vertices) if micro_demand[o] > 0]
    assert sum(collision[o] for o in owners) == 28
    assert sum(hit_need[o] for o in owners) == 2
    assert sum(micro_demand[o] for o in owners) == 78

    blue_adj = [set() for _ in range(n)]
    signed_degree = [0] * n
    edge_sign = {}
    for x, y in blue:
        blue_adj[x].add(y)
        blue_adj[y].add(x)
        signed_degree[x] += 1
        signed_degree[y] += 1
        edge_sign[norm(x, y)] = 1
    for x, y in bad:
        signed_degree[x] -= 1
        signed_degree[y] -= 1
        edge_sign[norm(x, y)] = -1

    def sigma_pair(x: int, y: int) -> int:
        return (
            signed_degree[x] + signed_degree[y]
            - 2 * edge_sign.get(norm(x, y), 0)
        )

    masks = {}
    reasons = defaultdict(lambda: defaultdict(set))
    reserved = set()
    for x in range(n):
        for y in range(n):
            if x == y or pair[x, y] != 0:
                continue
            for half in (0, 1):
                source = (x, y, half)
                if half == 0 and norm(x, y) in demanded_active and x in active_vertices:
                    reserved.add(source)
                    continue
                mask = 0
                for index, owner in enumerate(owners):
                    if x == owner:
                        mask |= 1 << index
                        reasons[source][owner].add("sameFirst")
                    if (
                        pair[owner, x] > 0 and pair[owner, y] > 0
                        and sigma_pair(x, y) >= 0
                    ):
                        mask |= 1 << index
                        reasons[source][owner].add("rowCompanion")
                    if (
                        x in blue_adj[owner] and y in blue_adj[owner]
                        and sigma_pair(x, y) >= 2
                    ):
                        mask |= 1 << index
                        reasons[source][owner].add("commonBlue")
                if mask:
                    masks[source] = mask

    cuts = []
    for shore_mask in range(1 << len(owners)):
        shore = [owners[i] for i in range(len(owners)) if shore_mask & (1 << i)]
        demand = sum(micro_demand[o] for o in shore)
        reach = sum(mask & shore_mask != 0 for mask in masks.values())
        cuts.append({
            "shoreMask": shore_mask,
            "shore": shore,
            "demand": demand,
            "reach": reach,
            "defect": demand - reach,
        })
    assert max(cut["defect"] for cut in cuts) == 13

    source_records = []
    for source, mask in sorted(masks.items()):
        x, y, half = source
        source_records.append({
            "source": list(source),
            "ownerMask": mask,
            "sigma": sigma_pair(x, y),
            "reasons": {
                str(owner): sorted(reasons[source][owner])
                for owner in owners if reasons[source][owner]
            },
        })

    components = defaultdict(list)
    for v in selected:
        components[find(v)].append(v)
    outside = sorted(set(range(n)) - selected)
    outside_components = []
    seen = set()
    for root in outside:
        if root in seen:
            continue
        comp, attach = set(), set()
        todo = deque([root])
        seen.add(root)
        while todo:
            x = todo.popleft()
            comp.add(x)
            for y in blue_adj[x]:
                if y in selected:
                    attach.add(y)
                elif y not in seen:
                    seen.add(y)
                    todo.append(y)
        outside_components.append({
            "vertices": sorted(comp), "attachments": sorted(attach)
        })

    result = {
        "schema": "N12_FIRST_COMMON_BLUE_MICRO_FAILURE_V1",
        "g6": G6,
        "choice": list(CHOICE),
        "familySizes": list(map(len, families)),
        "edges": [list(e) for e in sorted(edges)],
        "blue": [list(e) for e in sorted(blue)],
        "bad": [list(e) for e in sorted(bad)],
        "rows": [list(row) for row in rows],
        "selected": sorted(selected),
        "support": [list(e) for e in sorted(support)],
        "activeEdges": [list(e) for e in sorted(active)],
        "demandedActiveEdges": [list(e) for e in sorted(demanded_active)],
        "activeComponents": [sorted(vs) for _, vs in sorted(components.items())],
        "outsideComponents": outside_components,
        "owners": owners,
        "ownerData": {
            str(o): {
                "rowCount": row_count[o],
                "selectedLoad": 5 * row_count[o],
                "activeDegree": active_degree[o],
                "vertexSlack": max(0, n - 5 * row_count[o]),
                "collision": collision[o],
                "hitNeedSlots": hit_need[o],
                "microDemand": micro_demand[o],
                "blueNeighbors": sorted(blue_adj[o]),
                "signedDegree": signed_degree[o],
            }
            for o in owners
        },
        "reservedSources": [list(s) for s in sorted(reserved)],
        "sourceCount": len(masks),
        "sourceMaskHistogram": dict(sorted(Counter(masks.values()).items())),
        "sources": source_records,
        "cuts": cuts,
    }
    out = HERE / "n12_first_micro_fixture.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "g6": G6,
        "owners": owners,
        "ownerData": result["ownerData"],
        "selected": len(selected),
        "activeEdges": len(active),
        "outsideComponents": outside_components,
        "sourceCount": len(masks),
        "sourceMaskHistogram": result["sourceMaskHistogram"],
        "cuts": cuts,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
