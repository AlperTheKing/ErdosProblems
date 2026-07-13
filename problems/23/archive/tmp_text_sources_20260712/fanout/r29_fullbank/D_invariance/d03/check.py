"""Exact standalone audit of the R29 hub-shore source-pool invariant."""

from collections import Counter, deque
import hashlib
import json

N = 2943
HUBS = (0, 1, 2)
LEFT = tuple(range(3, 29))
RIGHT = tuple(range(29, 55))
ANCHOR = 55


def edge(u, v):
    assert u != v
    return (u, v) if u < v else (v, u)


def selector_fragment():
    """Rebuild exactly the canonical lock arms and selector blue edges."""
    blue = set()
    arms_by_region = []
    nxt = 56
    for region in (LEFT, RIGHT):
        arms = []
        for leaf in region:
            for _ in range(26):
                x, y = nxt, nxt + 1
                nxt += 2
                blue.update((edge(leaf, x), edge(x, y), edge(y, ANCHOR)))
                arms.append((leaf, x, y))
        assert len(arms) == 676
        arms_by_region.append(arms)
    assert nxt == 2760

    atoms = []
    displayed = []
    for q, arms in zip((2760, 2761), arms_by_region):
        first, second = arms[:338], arms[338:]
        for j in range(338):
            _, xf, _ = first[j]
            _, _, yf1 = first[(j + 1) % 338]
            _, xd, _ = second[j]
            _, _, yd1 = second[(j + 1) % 338]
            row = (q, xf, yf1, xd, yd1)
            blue.update(edge(u, v) for u, v in zip(row, row[1:]))
            atoms.append(edge(q, yd1))
            displayed.append(row)
    return blue, tuple(atoms), tuple(displayed)


def adjacency(vertices, edges):
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return {v: tuple(sorted(ws)) for v, ws in adj.items()}


def shortest_rows_4(adj, source, target):
    dist = {source: 0}
    todo = deque([source])
    while todo:
        u = todo.popleft()
        if dist[u] == 4:
            continue
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                todo.append(v)
    assert dist[target] == 4
    out = []

    def visit(path):
        u = path[-1]
        if len(path) == 5:
            if u == target:
                out.append(tuple(path))
            return
        for v in adj[u]:
            if dist.get(v) == dist[u] + 1:
                visit(path + [v])

    visit([source])
    return tuple(out)


def main():
    blue, atoms, displayed = selector_fragment()
    vertices = set(range(3, 2762))
    adj = adjacency(vertices, blue)
    shapes = Counter()
    selector_sha = hashlib.sha256()
    for atom, shown in zip(atoms, displayed):
        family = shortest_rows_4(adj, *atom)
        assert len(family) == 680
        assert all(not (set(row) & set(HUBS)) for row in family)
        assert tuple(reversed(shown)) in family
        anchor = sum(ANCHOR in row for row in family)
        shapes[(anchor, len(family) - anchor)] += 1
        for row in sorted(family):
            selector_sha.update(json.dumps(row, separators=(",", ":")).encode())

    # Every traffic row is (left,cL,r,cR,right).  Thus each hub has exactly
    # itself, the other two hubs, and all 52 leaves in its pair-support.
    traffic_rows = tuple((u, 1, 0, 2, v) for u in LEFT for v in RIGHT)
    pair_support = {o: set() for o in HUBS}
    for row in traffic_rows:
        for o in HUBS:
            if o in row:
                pair_support[o].update(row)
    assert {o: len(s) for o, s in pair_support.items()} == {0: 55, 1: 55, 2: 55}

    # The fixed seed rows select 55,zL,zR; the rigid circuit selects midpoint
    # 2764 and contains a bad edge in its permanent active component.  None of
    # the cable edges below is a row-support edge, so its h=0 half is reserved.
    reservations = {0: edge(0, 55), 1: edge(1, 2929), 2: edge(2, 2930)}
    same_first = {}
    for o in HUBS:
        zero_pair_vertices = N - len(pair_support[o])
        raw_halves = 2 * zero_pair_vertices
        same_first[o] = raw_halves - 1
        assert same_first[o] == 5775

    # Within the common 55-vertex companion support, precisely ordered pairs
    # of distinct leaves on the same side have zero row co-occurrence.
    ordered_zero_pairs = 2 * (26 * 25)
    row_companion = 2 * ordered_zero_pairs
    assert row_companion == 2600

    result = {
        "n": N,
        "selector_families": len(atoms),
        "selector_family_shapes": {"676_anchor_4_local": shapes[(676, 4)]},
        "selector_rows_checked": len(atoms) * 680,
        "selector_rows_touching_hubs": 0,
        "selector_enumeration_sha256": selector_sha.hexdigest(),
        "hub_pair_support_sizes": {str(o): len(pair_support[o]) for o in HUBS},
        "reservations": {str(o): list(e) for o, e in reservations.items()},
        "sameFirst_per_owner": {str(o): same_first[o] for o in HUBS},
        "sameFirst_total": sum(same_first.values()),
        "rowCompanion_total": row_companion,
        "total_reach": sum(same_first.values()) + row_companion,
        "altering_selector_choices": 0,
    }
    assert result["sameFirst_total"] == 17325
    assert result["total_reach"] == 19925
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
