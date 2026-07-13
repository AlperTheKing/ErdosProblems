"""Independent exact replay of the N=12 CommonBlue MicroHall falsifier."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PHT = ROOT / "tmp/fanout/pht_n12_direct"
sys.path.insert(0, str(PHT))

import n12_pht as n12


G6 = "K??E@cyjFgWk"
CHOICE = (0, 4, 5, 7)
CUT_MASK = 2016
BAD_ORDER = ((6, 8), (6, 7), (7, 11), (8, 11))
SELECTED_ROWS = (
    (6, 0, 9, 2, 8),
    (6, 1, 10, 3, 7),
    (7, 3, 10, 5, 11),
    (8, 3, 10, 5, 11),
)


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cut_data(n: int, edges: set[tuple[int, int]], mask: int):
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
        return blue, bad, None
    gamma = 0
    for source, target in bad:
        dist = [-1] * n
        dist[source] = 0
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if dist[y] >= 0:
                    continue
                dist[y] = dist[x] + 1
                queue.append(y)
        assert dist[target] >= 0
        gamma += (dist[target] + 1) ** 2
    return blue, bad, gamma


def shortest_rows(n: int, blue: set[tuple[int, int]], source: int, target: int):
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
            if dist[y] == -1:
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


def family_with_selected_index(rows, selected, index):
    """Give a complete sorted family a pinned literal list order."""
    family = sorted(rows)
    current = family.index(selected)
    family[index], family[current] = family[current], family[index]
    return tuple(family)


def active_state(n, blue, bad, rows):
    pair = Counter()
    selected = set()
    support = set()
    for row in rows:
        selected.update(row)
        support.update(norm(x, y) for x, y in zip(row, row[1:]))
        for x in row:
            for y in row:
                pair[x, y] += 1
    off_support = {
        edge for edge in blue
        if edge[0] in selected and edge[1] in selected and edge not in support
    }
    adj = defaultdict(set)
    for x, y in off_support:
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
    active_edges = {e for e in off_support if e[0] in active_vertices}
    degree = Counter()
    for x, y in active_edges:
        degree[x] += 1
        degree[y] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, x] - 1) for x in range(n))
        for v in active_vertices
    }
    hit_need = {
        v: max(0, degree[v] - max(0, n - 5 * pair[v, v]))
        for v in active_vertices
    }
    return pair, selected, support, off_support, components, active_vertices, active_edges, degree, collision, hit_need


def legal_sources(n, blue, bad, pair, active_vertices, active_edges, owners):
    def sigma(x, y):
        switch = {x, y}
        return (
            sum((a in switch) ^ (b in switch) for a, b in blue)
            - sum((a in switch) ^ (b in switch) for a, b in bad)
        )

    keys = []
    histogram = Counter()
    for x in range(n):
        for y in range(n):
            if x == y or pair[x, y] != 0:
                continue
            for half in (0, 1):
                if half == 0 and norm(x, y) in active_edges:
                    continue
                mask = 0
                for index, owner in enumerate(owners):
                    same_owner = x == owner
                    row_companion = (
                        pair[owner, x] > 0
                        and pair[owner, y] > 0
                        and sigma(x, y) >= 0
                    )
                    common_blue = (
                        norm(x, owner) in blue
                        and norm(y, owner) in blue
                        and sigma(x, y) >= 2
                    )
                    if same_owner or row_companion or common_blue:
                        mask |= 1 << index
                if mask:
                    keys.append((x, y, half, mask))
                    histogram[mask] += 1
    return keys, histogram


def maximum_matching(demand, owners, keys):
    copies = [(owner, copy) for owner in owners for copy in range(demand[owner])]
    match = {}

    def augment(copy_index, seen):
        owner_bit = 1 << owners.index(copies[copy_index][0])
        for key_index, key in enumerate(keys):
            if not key[3] & owner_bit or key_index in seen:
                continue
            seen.add(key_index)
            if key_index not in match or augment(match[key_index], seen):
                match[key_index] = copy_index
                return True
        return False

    value = sum(augment(index, set()) for index in range(len(copies)))
    assignment = [
        {
            "owner": copies[copy][0],
            "copy": copies[copy][1],
            "source": list(keys[key][:3]),
        }
        for key, copy in sorted(match.items())
    ]
    return value, assignment


def main():
    n, decoded = n12.dec(G6)
    edges = {norm(*edge) for edge in decoded}
    assert n == 12 and len(edges) == 23
    assert not any(
        norm(x, y) in edges and norm(x, z) in edges and norm(y, z) in edges
        for x in range(n) for y in range(x + 1, n) for z in range(y + 1, n)
    )

    cuts = []
    for mask in range(1 << (n - 1)):
        blue, bad, gamma = cut_data(n, edges, mask)
        cuts.append((len(blue), gamma, mask))
    max_cut = max(size for size, _, _ in cuts)
    connected_max = [record for record in cuts if record[0] == max_cut and record[1] is not None]
    min_gamma = min(gamma for _, gamma, _ in connected_max)
    gamma_masks = [mask for _, gamma, mask in connected_max if gamma == min_gamma]
    assert max_cut == 19 and min_gamma == 100 and CUT_MASK in gamma_masks

    blue, bad, gamma = cut_data(n, edges, CUT_MASK)
    assert gamma == min_gamma and len(blue) == 19 and len(bad) == 4
    assert bad == set(BAD_ORDER)
    independent = [shortest_rows(n, blue, *edge) for edge in BAD_ORDER]
    families = tuple(
        family_with_selected_index(rows, selected, index)
        for rows, selected, index in zip(independent, SELECTED_ROWS, CHOICE)
    )
    assert [len(family) for family in families] == [6, 5, 8, 10]
    assert all(len(set(map(tuple, family))) == len(family) for family in families)
    assert all(set(left) == set(right) for left, right in zip(families, independent))
    rows = tuple(family[index] for family, index in zip(families, CHOICE))
    assert rows == SELECTED_ROWS
    tuple_index = CHOICE[0] * 5 * 8 * 10 + CHOICE[1] * 8 * 10 + CHOICE[2] * 10 + CHOICE[3]
    assert tuple_index == 377

    state = active_state(n, blue, bad, rows)
    pair, selected, support, off_support, components, active_vertices, active_edges, degree, collision, hit_need = state
    assert {v: units for v, units in collision.items() if units} == {7: 6, 10: 14, 11: 8}
    assert {v: units for v, units in hit_need.items() if units} == {10: 2}
    owners = [7, 10, 11]
    demand = {owner: collision[owner] + 25 * hit_need[owner] for owner in owners}
    assert demand == {7: 6, 10: 64, 11: 8}

    keys, histogram = legal_sources(n, blue, bad, pair, active_vertices, active_edges, owners)
    shores = []
    for mask in range(1 << len(owners)):
        shore_demand = sum(demand[v] for i, v in enumerate(owners) if mask & (1 << i))
        reach = sum(1 for key in keys if key[3] & mask)
        shores.append({
            "mask": mask,
            "owners": [v for i, v in enumerate(owners) if mask & (1 << i)],
            "demand": shore_demand,
            "reach": reach,
            "defect": shore_demand - reach,
        })
    witness = shores[6]
    assert witness == {"mask": 6, "owners": [10, 11], "demand": 72, "reach": 59, "defect": 13}
    assert max(shore["defect"] for shore in shores) == 13
    flow, assignment = maximum_matching(demand, owners, keys)
    assert flow == 65

    result = {
        "schema": "COMMON_BLUE_MICRO_REAL_FALSIFIER_V1",
        "fixture": {
            "g6": G6,
            "n": n,
            "edges": [list(edge) for edge in sorted(edges)],
            "triangleFree": True,
            "cutMask": CUT_MASK,
            "maxCut": max_cut,
            "connectedMaxCutCount": len(connected_max),
            "minimumGamma": min_gamma,
            "minimumGammaCutMasks": gamma_masks,
            "badEdges": [list(edge) for edge in BAD_ORDER],
            "familySizes": [len(family) for family in families],
            "completeRowFamilies": [[list(row) for row in family] for family in families],
            "choice": list(CHOICE),
            "tupleIndex": tuple_index,
            "selectedRows": [list(row) for row in rows],
        },
        "active": {
            "selected": sorted(selected),
            "support": [list(edge) for edge in sorted(support)],
            "offSupport": [list(edge) for edge in sorted(off_support)],
            "components": components,
            "activeVertices": sorted(active_vertices),
            "activeEdges": [list(edge) for edge in sorted(active_edges)],
            "degree": {str(v): degree[v] for v in sorted(active_vertices)},
        },
        "demand": {
            "collisionByOwner": {str(v): collision[v] for v in owners},
            "hitNeedByOwner": {str(v): hit_need[v] for v in owners},
            "microByOwner": {str(v): demand[v] for v in owners},
            "collisionTotal": sum(collision.values()),
            "hitNeedSlots": sum(hit_need.values()),
            "microTotal": sum(demand.values()),
        },
        "relation": {
            "sourceCount": len(keys),
            "maskHistogram": {str(mask): count for mask, count in sorted(histogram.items())},
            "shores": shores,
            "witness": witness,
        },
        "flow": {"maximum": flow, "defect": sum(demand.values()) - flow, "assignment": assignment},
        "sourceSha256": {
            "n12Pht": sha256(PHT / "n12_pht.py"),
            "production": sha256(ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean"),
            "replay": sha256(Path(__file__)),
        },
    }
    output = HERE / "defect13_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": "REAL_MICRO_HALL_FALSIFIER",
        "demand": sum(demand.values()),
        "flow": flow,
        "witness": witness,
        "resultSha256": sha256(output),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
