from itertools import combinations, product


COPIES = 2
BLOCK = 20
N = COPIES * BLOCK

BASE_CYCLES = (
    (0, 2, 3, 4, 1),
    (5, 7, 8, 9, 6),
    (10, 12, 13, 14, 11),
    (15, 17, 18, 19, 16),
)
BASE_BAD = ((0, 1), (5, 6), (10, 11), (15, 16))
BASE_EXTRA = ((0, 7), (7, 10), (10, 15), (15, 1))
BASE_TRUE = {0, 1, 3, 5, 6, 8, 10, 11, 13, 17, 19}


def edge(u, v):
    return tuple(sorted((u, v)))


def lift(vertices, copy):
    return tuple(v + BLOCK * copy for v in vertices)


CYCLES = [lift(row, copy) for copy in range(COPIES) for row in BASE_CYCLES]
BAD = {edge(*lift(e, copy)) for copy in range(COPIES) for e in BASE_BAD}
EXTRA = {edge(*lift(e, copy)) for copy in range(COPIES) for e in BASE_EXTRA}
# One inter-copy edge per adjacency in the copy tree.  The endpoints 3 and 2
# avoid every weak pair and lie on opposite displayed shores.
BRIDGES = {edge(3 + BLOCK * copy, 2 + BLOCK * (copy + 1)) for copy in range(COPIES - 1)}

EDGES = set(EXTRA) | set(BRIDGES)
for row in CYCLES:
    EDGES.add(edge(row[0], row[-1]))
    EDGES.update(edge(row[i], row[i + 1]) for i in range(4))

SIDE_TRUE = {v + BLOCK * copy for copy in range(COPIES) for v in BASE_TRUE}
SELECTED = tuple(CYCLES)
WEAK = tuple(
    (7 + BLOCK * copy, 0 + BLOCK * copy, 5 + BLOCK * copy)
    for copy in range(COPIES)
)


def side(v):
    return v in SIDE_TRUE


def blue(u, v):
    return edge(u, v) in EDGES and side(u) != side(v)


def bad(u, v):
    return edge(u, v) in EDGES and side(u) == side(v)


def signed_weight(u, v):
    return int(blue(u, v)) - int(bad(u, v))


def sigma(vertices):
    vertices = set(vertices)
    d_blue = sum(blue(u, v) and ((u in vertices) != (v in vertices)) for u, v in EDGES)
    d_bad = sum(bad(u, v) and ((u in vertices) != (v in vertices)) for u, v in EDGES)
    return d_blue, d_bad, d_blue - d_bad


def all_rows(u, v):
    rows = []
    for middle in product(range(N), repeat=3):
        row = (u,) + middle + (v,)
        if len(set(row)) == 5 and all(blue(row[i], row[i + 1]) for i in range(4)):
            rows.append(row)
    return sorted(rows)


def pair_count(x, y):
    return sum(x in row and y in row for row in SELECTED)


def connected_component(start, graph_edges):
    seen = {start}
    todo = [start]
    while todo:
        u = todo.pop()
        for a, b in graph_edges:
            if a == u and b not in seen:
                seen.add(b)
                todo.append(b)
            elif b == u and a not in seen:
                seen.add(a)
                todo.append(a)
    return seen


def interaction(pair_a, pair_b):
    return sum(signed_weight(u, v) for u in pair_a for v in pair_b)


def main():
    assert len(EDGES) == 49
    assert len(BAD) == 8
    assert {e for e in EDGES if side(e[0]) == side(e[1])} == BAD
    assert not any(
        edge(a, b) in EDGES and edge(b, c) in EDGES and edge(a, c) in EDGES
        for a, b, c in combinations(range(N), 3)
    )
    blue_edges = {e for e in EDGES if blue(*e)}
    assert connected_component(0, blue_edges) == set(range(N))

    # The eight displayed C5 edge sets are disjoint, so every cut misses at
    # least eight of 49 edges.  The displayed cut misses exactly the bad edges.
    cycle_edges = [
        {edge(row[i], row[(i + 1) % 5]) for i in range(5)} for row in CYCLES
    ]
    assert all(len(es) == 5 for es in cycle_edges)
    assert all(cycle_edges[i].isdisjoint(cycle_edges[j])
               for i in range(len(cycle_edges)) for j in range(i))
    shown_cut = sum(blue(*e) for e in EDGES)
    maxcut_upper_bound = len(EDGES) - len(CYCLES)
    assert shown_cut == maxcut_upper_bound == 41

    row_db = {e: all_rows(*e) for e in sorted(BAD)}
    expected = {}
    for copy in range(COPIES):
        offset = BLOCK * copy
        expected[edge(offset, offset + 1)] = [
            lift(BASE_CYCLES[0], copy),
            lift((0, 7, 10, 15, 1), copy),
        ]
        for bad_edge, row in zip(BASE_BAD[1:], BASE_CYCLES[1:]):
            expected[edge(*lift(bad_edge, copy))] = [lift(row, copy)]
    assert row_db == expected
    selected_by_bad = {edge(row[0], row[-1]): row for row in SELECTED}
    assert all(selected_by_bad[e] == rows[0] for e, rows in row_db.items())

    support = {edge(row[i], row[i + 1]) for row in SELECTED for i in range(4)}
    selected_vertices = set().union(*map(set, SELECTED))
    active = {
        e for e in EDGES
        if e[0] in selected_vertices and e[1] in selected_vertices
        and blue(*e) and e not in support
    }

    pair_sets = []
    for copy, (owner, x, y) in enumerate(WEAK):
        component = connected_component(x, active)
        bad_u, bad_v = lift(BASE_BAD[0], copy)
        assert owner in component and bad_u in component and bad_v in component
        assert edge(owner, x) in active and edge(owner, y) in support
        assert blue(owner, x) and blue(owner, y)
        assert side(x) == side(y) and edge(x, y) not in EDGES
        assert pair_count(x, y) == 0
        assert sigma((x, y)) == (3, 2, 1)
        pair_sets.append((x, y))

    assert all(interaction(pair_sets[i], pair_sets[j]) == 0
               for i in range(len(pair_sets)) for j in range(i))

    # Check every subfamily, not just the full two-pair switch.
    for mask in range(1 << COPIES):
        chosen = [pair_sets[i] for i in range(COPIES) if mask & (1 << i)]
        union = set().union(*(set(pair) for pair in chosen)) if chosen else set()
        d_blue, d_bad, aggregate = sigma(union)
        individual = sum(sigma(pair)[2] for pair in chosen)
        correction = 2 * sum(
            interaction(chosen[i], chosen[j])
            for i in range(len(chosen)) for j in range(i)
        )
        assert aggregate == individual - correction == len(chosen)
        assert aggregate < 2 * len(chosen) if chosen else aggregate == 0

    full_union = set().union(*map(set, pair_sets))
    d_blue, d_bad, aggregate = sigma(full_union)
    print("REPLAY=PASS")
    print(f"N={N} edges={len(EDGES)} triangle_free=true maxcut={shown_cut}")
    print("row_family_sizes=" + repr(tuple(len(row_db[e]) for e in sorted(row_db))))
    print("canonical_choice=lex-first active_owners=(7,27)")
    print("weak_pairs=((0,5),(20,25)) individual_sigma=(1,1)")
    print(f"cross_interaction=0 union_dB={d_blue} union_dM={d_bad} union_sigma={aggregate}")
    print("required_two_per_terminal=4 shortfall=2")


if __name__ == "__main__":
    main()
