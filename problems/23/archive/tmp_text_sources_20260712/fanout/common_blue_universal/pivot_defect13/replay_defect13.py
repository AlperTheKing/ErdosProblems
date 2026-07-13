"""Independent exact replay of the first N12 MicroMatching falsifier."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHT = ROOT / "tmp/fanout/pht_n12_direct"
WRITEUP = ROOT / "problems/23/writeup"
sys.path[:0] = [str(PHT), str(WRITEUP)]

import n12_pht as n12  # noqa: E402


G6 = "K??E@cyjFgWk"
CHOICE = (0, 4, 5, 7)


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def connected_and_gamma(n: int, edges: set[tuple[int, int]], mask: int):
    side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
    blue = {e for e in edges if side[e[0]] != side[e[1]]}
    bad = edges - blue
    adj = [set() for _ in range(n)]
    for x, y in blue:
        adj[x].add(y)
        adj[y].add(x)
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x] - seen:
            seen.add(y)
            stack.append(y)
    if len(seen) != n:
        return len(blue), None
    gamma = 0
    for source, target in bad:
        dist = [-1] * n
        dist[source] = 0
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    queue.append(y)
        assert dist[target] >= 0
        gamma += (dist[target] + 1) ** 2
    return len(blue), gamma


def all_shortest_rows(n: int, blue, source: int, target: int):
    adj = [set() for _ in range(n)]
    for x, y in blue:
        adj[x].add(y)
        adj[y].add(x)
    dist = [-1] * n
    dist[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    length = dist[target]
    rows = []

    def visit(path):
        x = path[-1]
        if len(path) == length + 1:
            if x == target:
                rows.append(tuple(path))
            return
        for y in sorted(adj[x]):
            if dist[y] == dist[x] + 1:
                visit(path + [y])

    visit([source])
    return rows


def active_data(n, blue, bad, rows):
    pair = Counter()
    selected = set()
    support = set()
    for row in rows:
        selected.update(row)
        support.update(norm(x, y) for x, y in zip(row, row[1:]))
        for x in row:
            for y in row:
                pair[x, y] += 1
    active = {
        e for e in blue
        if e[0] in selected and e[1] in selected and e not in support
    }
    adj = defaultdict(set)
    for x, y in active:
        adj[x].add(y)
        adj[y].add(x)
    seen = set()
    components = []
    active_vertices = set()
    for root in sorted(selected):
        if root in seen:
            continue
        component = set()
        stack = [root]
        seen.add(root)
        while stack:
            x = stack.pop()
            component.add(x)
            for y in adj[x] - seen:
                seen.add(y)
                stack.append(y)
        components.append(sorted(component))
        if any(x in component and y in component for x, y in bad):
            active_vertices.update(component)
    active_edges = {e for e in active if e[0] in active_vertices}
    degree = Counter()
    for x, y in active_edges:
        degree[x] += 1
        degree[y] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, x] - 1) for x in range(n))
        for v in active_vertices
    }
    hit = {
        v: max(0, degree[v] - max(0, n - 5 * pair[v, v]))
        for v in active_vertices
    }
    return pair, selected, support, active, components, active_vertices, active_edges, degree, collision, hit


def source_masks(n, blue, bad, pair, active_vertices, active_edges, owners):
    def sigma(x, y):
        switch = {x, y}
        return (
            sum((a in switch) ^ (b in switch) for a, b in blue)
            - sum((a in switch) ^ (b in switch) for a, b in bad)
        )

    keys = []
    histogram = Counter()
    reason_counts = Counter()
    for x in range(n):
        for y in range(n):
            if x == y or pair[x, y] != 0:
                continue
            for half in (0, 1):
                if half == 0 and norm(x, y) in active_edges and x in active_vertices:
                    continue
                mask = 0
                reasons = []
                for index, owner in enumerate(owners):
                    same = x == owner
                    row = pair[owner, x] > 0 and pair[owner, y] > 0 and sigma(x, y) >= 0
                    common_blue = (
                        norm(x, owner) in blue and norm(y, owner) in blue
                        and sigma(x, y) >= 2
                    )
                    if same or row or common_blue:
                        mask |= 1 << index
                        reasons.append((owner, same, row, common_blue))
                if mask:
                    keys.append((x, y, half, mask))
                    histogram[mask] += 1
                    for owner, same, row, common_blue in reasons:
                        reason_counts[owner, "same"] += int(same)
                        reason_counts[owner, "row"] += int(row)
                        reason_counts[owner, "commonBlue"] += int(common_blue)
    return keys, histogram, reason_counts


def maximum_matching(demand, owners, keys):
    copies = [(owner, copy) for owner in owners for copy in range(demand[owner])]
    key_masks = [key[3] for key in keys]
    match_key = {}

    def augment(copy_index, seen):
        owner = copies[copy_index][0]
        owner_bit = 1 << owners.index(owner)
        for key_index, mask in enumerate(key_masks):
            if not (mask & owner_bit) or key_index in seen:
                continue
            seen.add(key_index)
            if key_index not in match_key or augment(match_key[key_index], seen):
                match_key[key_index] = copy_index
                return True
        return False

    value = sum(augment(i, set()) for i in range(len(copies)))
    assignment = [
        {"owner": copies[copy][0], "copy": copies[copy][1], "source": list(keys[key][:3])}
        for key, copy in sorted(match_key.items())
    ]
    return value, assignment


def main():
    n, decoded = n12.dec(G6)
    edges = {norm(*e) for e in decoded}
    assert n == 12 and len(edges) == 23
    assert not any(
        norm(x, y) in edges and norm(x, z) in edges and norm(y, z) in edges
        for x in range(n) for y in range(x + 1, n) for z in range(y + 1, n)
    )

    cut_records = [(*connected_and_gamma(n, edges, mask), mask) for mask in range(1 << (n - 1))]
    max_cut = max(record[0] for record in cut_records)
    connected_max = [record for record in cut_records if record[0] == max_cut and record[1] is not None]
    min_gamma = min(record[1] for record in connected_max)
    gamma_masks = [record[2] for record in connected_max if record[1] == min_gamma]
    assert max_cut == 19 and min_gamma == 100 and len(gamma_masks) == 10

    target_mask = 2016
    assert target_mask in gamma_masks
    side = [0] + [(target_mask >> (v - 1)) & 1 for v in range(1, n)]
    blue = {e for e in edges if side[e[0]] != side[e[1]]}
    bad = edges - blue
    # Preserve graph6 decoder order: the accepted row-family enumeration is
    # ordered, even though the graph and cut certificates below use edge sets.
    info = n12.loads(n, decoded)
    assert info is not None and blue == set(info["Bset"]) and bad == set(info["Mset"])
    families = n12.shortest_row_families(info)
    independent_families = [all_shortest_rows(n, blue, *edge) for edge in info["M"]]
    assert [len(family) for family in families] == [6, 5, 8, 10]
    assert all(set(map(tuple, left)) == set(right) for left, right in zip(families, independent_families))
    rows = n12.rows_for_choice(families, CHOICE)
    tuple_index = CHOICE[0] * 5 * 8 * 10 + CHOICE[1] * 8 * 10 + CHOICE[2] * 10 + CHOICE[3]
    assert tuple_index == 377

    data = active_data(n, blue, bad, rows)
    pair, selected, support, active, components, active_vertices, active_edges, degree, collision, hit = data
    assert {k: v for k, v in collision.items() if v} == {7: 6, 10: 14, 11: 8}
    assert {k: v for k, v in hit.items() if v} == {10: 2}
    owners = [7, 10, 11]
    demand = {owner: collision[owner] + 25 * hit[owner] for owner in owners}
    assert demand == {7: 6, 10: 64, 11: 8}
    keys, histogram, reason_counts = source_masks(
        n, blue, bad, pair, active_vertices, active_edges, owners
    )
    cuts = []
    for shore in range(1 << len(owners)):
        shore_demand = sum(demand[owner] for i, owner in enumerate(owners) if shore & (1 << i))
        reach = sum(1 for key in keys if key[3] & shore)
        cuts.append({
            "mask": shore,
            "owners": [owner for i, owner in enumerate(owners) if shore & (1 << i)],
            "demand": shore_demand,
            "reach": reach,
            "defect": shore_demand - reach,
        })
    assert max(cut["defect"] for cut in cuts) == 13
    assert cuts[6] == {"mask": 6, "owners": [10, 11], "demand": 72, "reach": 59, "defect": 13}
    flow, assignment = maximum_matching(demand, owners, keys)
    assert flow == 65

    result = {
        "schema": "N12_MICRO_DEFECT13_INDEPENDENT_V1",
        "fixture": {
            "g6": G6, "n": n, "edges": len(edges), "triangleFree": True,
            "targetCutMask": target_mask, "maxCut": max_cut,
            "maximumCutCount": sum(record[0] == max_cut for record in cut_records),
            "connectedMaximumCutCount": len(connected_max),
            "minimumGamma": min_gamma, "minimumGammaCutMasks": gamma_masks,
            "badEdges": [list(edge) for edge in info["M"]],
            "familySizes": [len(family) for family in families],
            "choice": list(CHOICE), "tupleIndex": tuple_index,
            "rows": [list(row) for row in rows],
        },
        "active": {
            "selected": sorted(selected), "support": [list(e) for e in sorted(support)],
            "offSupportEdges": [list(e) for e in sorted(active)],
            "components": components, "activeVertices": sorted(active_vertices),
            "activeEdges": [list(e) for e in sorted(active_edges)],
            "activeDegree": {str(k): degree[k] for k in sorted(active_vertices)},
        },
        "demand": {
            "collisionByOwner": {str(k): collision[k] for k in owners},
            "hitNeedByOwner": {str(k): hit[k] for k in owners},
            "microByOwner": {str(k): demand[k] for k in owners},
            "collisionTotal": sum(collision.values()), "hitNeedTotal": sum(hit.values()),
            "microTotal": sum(demand.values()),
        },
        "relation": {
            "sourceKeys": len(keys),
            "maskHistogram": {str(k): v for k, v in sorted(histogram.items())},
            "reasonCounts": {f"{owner}:{reason}": value for (owner, reason), value in sorted(reason_counts.items())},
            "cuts": cuts,
        },
        "flow": {"maximum": flow, "defect": sum(demand.values()) - flow, "assignment": assignment},
        "sha256": {
            "n12Pht": sha256(PHT / "n12_pht.py"),
            "ownerFlowNotImported": sha256(WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py"),
            "microProduction": sha256(ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean"),
        },
    }
    output = HERE / "replay_defect13_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": "REPRODUCED_DEFECT13", "flow": flow,
        "demand": sum(demand.values()), "shore": cuts[6],
        "resultSha256": sha256(output),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
