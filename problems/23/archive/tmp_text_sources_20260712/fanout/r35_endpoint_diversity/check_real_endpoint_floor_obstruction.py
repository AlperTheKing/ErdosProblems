"""Exact integer gate for the R35 endpoint-diversity source-floor obstruction.

The graph is a 24-vertex realization of the 3x3 double-star rows, augmented
with three private selected rows and cut edges that make the middle double-star
vertex active while keeping every vertex in the selected-row union.

No floating-point arithmetic is used.  Maximum cut is checked over all
2^23 cuts with vertex 0 fixed, using an exact Gray-code update.
"""

from __future__ import annotations

from collections import Counter, deque
from hashlib import sha256
from pathlib import Path


N = 24
LEFT = (0, 1, 2)
RIGHT = (3, 4, 5)
C_LEFT, OWNER, C_RIGHT = 6, 7, 8
A_LEFT = (9, 10, 11)
Z_LEFT = (12, 13, 14)
MID = (15, 16, 17)
Z_RIGHT = (18, 19, 20)
A_RIGHT = (21, 22, 23)


def norm_edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def construct() -> tuple[set[tuple[int, int]], list[tuple[int, int]], list[tuple[int, ...]]]:
    edges: set[tuple[int, int]] = set()

    def add(x: int, y: int) -> None:
        edges.add(norm_edge(x, y))

    def link(xs: tuple[int, ...], ys: tuple[int, ...]) -> None:
        for x in xs:
            for y in ys:
                add(x, y)

    # Nine anchored double-star rows.
    for x in LEFT:
        add(x, C_LEFT)
    add(C_LEFT, OWNER)
    add(OWNER, C_RIGHT)
    for y in RIGHT:
        add(C_RIGHT, y)
    link(LEFT, RIGHT)

    # The original 24-vertex anchor web.
    link(LEFT, A_LEFT)
    link(A_LEFT, Z_LEFT)
    link(Z_LEFT, MID)
    link(MID, Z_RIGHT)
    link(Z_RIGHT, A_RIGHT)
    link(A_RIGHT, RIGHT)

    # Three extra bad edges, with selected private rows covering the web.
    private_bad = []
    private_rows = []
    for i in range(3):
        add(A_LEFT[i], A_RIGHT[i])
        private_bad.append(norm_edge(A_LEFT[i], A_RIGHT[i]))
        private_rows.append((A_LEFT[i], Z_LEFT[i], MID[i], Z_RIGHT[i], A_RIGHT[i]))

    # Off-support cut edges.  They activate OWNER and restore maximum-cut
    # optimality after the three private bad edges are introduced.
    for x in A_LEFT + MID:
        add(OWNER, x)
    for x in Z_LEFT[:2]:
        add(C_RIGHT, x)

    main_bad = [norm_edge(x, y) for x in LEFT for y in RIGHT]
    main_rows = [(x, C_LEFT, OWNER, C_RIGHT, y) for x in LEFT for y in RIGHT]
    return edges, main_bad + private_bad, main_rows + private_rows


EDGES, INTENDED_BAD, SELECTED_ROWS = construct()
INTENDED_BAD_SET = set(INTENDED_BAD)
INTENDED_SIDE_ZERO = set(LEFT + RIGHT + (OWNER,) + Z_LEFT + Z_RIGHT)
SIDE = tuple(0 if v in INTENDED_SIDE_ZERO else 1 for v in range(N))
BLUE = {e for e in EDGES if SIDE[e[0]] != SIDE[e[1]]}
BAD = {e for e in EDGES if SIDE[e[0]] == SIDE[e[1]]}


def adjacency(edges: set[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(N)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    return adj


ADJ = adjacency(EDGES)
BLUE_ADJ = adjacency(BLUE)


def triangle_count() -> int:
    return sum(
        1
        for x in range(N)
        for y in ADJ[x]
        if x < y
        for z in ADJ[x] & ADJ[y]
        if y < z
    )


def connected(adj: list[set[int]]) -> bool:
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return len(seen) == N


def exact_maxcut() -> tuple[int, int]:
    """Return maximum cut size and number of cuts with vertex 0 fixed."""
    adj = [tuple(xs) for xs in ADJ]
    side = [0] * N
    cut = 0
    best = 0
    count = 1
    for step in range(1, 1 << (N - 1)):
        bit = (step & -step).bit_length() - 1
        v = bit + 1
        old = side[v]
        cut_incident = sum(side[u] != old for u in adj[v])
        cut += len(adj[v]) - 2 * cut_incident
        side[v] ^= 1
        if cut > best:
            best = cut
            count = 1
        elif cut == best:
            count += 1
    return best, count


def distances(start: int, adj: list[set[int]]) -> list[int | None]:
    dist: list[int | None] = [None] * N
    dist[start] = 0
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] is None:
                dist[y] = dist[x] + 1  # type: ignore[operator]
                queue.append(y)
    return dist


def shortest_rows(x: int, y: int) -> list[tuple[int, ...]]:
    dist = distances(x, BLUE_ADJ)
    assert dist[y] == 4
    out: list[tuple[int, ...]] = []

    def visit(path: tuple[int, ...]) -> None:
        if len(path) == 5:
            if path[-1] == y:
                out.append(path)
            return
        for z in sorted(BLUE_ADJ[path[-1]]):
            if z not in path:
                visit(path + (z,))

    visit((x,))
    return out


def pair_count(x: int, y: int) -> int:
    return sum(x in row and y in row for row in SELECTED_ROWS)


def owner_obligation_count(rows: list[tuple[int, ...]]) -> int:
    return 2 * sum(
        max(0, sum(OWNER in row and y in row for row in rows) - 1)
        for y in range(N)
    )


def sigma(vertices: tuple[int, ...]) -> int:
    shore = set(vertices)
    delta_b = sum((x in shore) != (y in shore) for x, y in BLUE)
    delta_m = sum((x in shore) != (y in shore) for x, y in BAD)
    return delta_b - delta_m


def selected_support() -> set[tuple[int, int]]:
    return {
        norm_edge(row[i], row[i + 1])
        for row in SELECTED_ROWS
        for i in range(4)
    }


SUPPORT = selected_support()
ACTIVE_EDGES = BLUE - SUPPORT
ACTIVE_ADJ = adjacency(ACTIVE_EDGES)


def components(adj: list[set[int]]) -> tuple[list[int], list[set[int]]]:
    label = [-1] * N
    comps: list[set[int]] = []
    for root in range(N):
        if label[root] >= 0:
            continue
        cid = len(comps)
        comp = {root}
        label[root] = cid
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if label[y] < 0:
                    label[y] = cid
                    comp.add(y)
                    queue.append(y)
        comps.append(comp)
    return label, comps


ACTIVE_LABEL, ACTIVE_COMPONENTS = components(ACTIVE_ADJ)


def active_owner(v: int) -> bool:
    cid = ACTIVE_LABEL[v]
    return any(ACTIVE_LABEL[x] == cid == ACTIVE_LABEL[y] for x, y in BAD)


def scoped_reserved(source: tuple[int, int, int]) -> bool:
    x, y, half = source
    return half == 0 and norm_edge(x, y) in ACTIVE_EDGES and active_owner(x)


def collision_obligations(owner: int) -> list[tuple[int, int, int]]:
    # (other, copy, half), exactly matching CollisionHalf.
    out = []
    for other in range(N):
        for copy in range(max(0, pair_count(owner, other) - 1)):
            for half in range(2):
                out.append((other, copy, half))
    return out


def free_sources() -> list[tuple[int, int, int]]:
    return [
        (x, y, half)
        for x in range(N)
        for y in range(N)
        if x != y and pair_count(x, y) == 0
        for half in range(2)
    ]


def p1(source: tuple[int, int, int]) -> bool:
    return source[0] == OWNER


def p3(source: tuple[int, int, int]) -> bool:
    x, y, _ = source
    return (
        pair_count(OWNER, x) > 0
        and pair_count(OWNER, y) > 0
        and sigma((x, y)) >= 0
    )


def main() -> int:
    assert len(EDGES) == 82
    assert triangle_count() == 0
    assert BAD == INTENDED_BAD_SET and len(BAD) == 12
    assert connected(BLUE_ADJ)

    intended_cut = len(BLUE)
    maximum_cut, maximum_cut_count = exact_maxcut()
    assert intended_cut == maximum_cut == 70

    row_families = {bad: shortest_rows(*bad) for bad in sorted(BAD)}
    assert all(len(rows) > 0 for rows in row_families.values())
    assert all(distances(x, BLUE_ADJ)[y] == 4 for x, y in BAD)
    for bad, selected in zip(INTENDED_BAD, SELECTED_ROWS):
        assert selected[0] == bad[0] and selected[-1] == bad[1]
        assert selected in row_families[bad]
        assert len(selected) == 5 and len(set(selected)) == 5
    assert len(set(SELECTED_ROWS)) == len(SELECTED_ROWS) == 12
    assert set().union(*(set(row) for row in SELECTED_ROWS)) == set(range(N))

    # Every maximum cut has 12 bad edges.  Triangle-freeness gives ell >= 5;
    # this connected cut attains ell = 5 for all twelve, hence Gamma-minimal.
    gamma = sum((distances(x, BLUE_ADJ)[y] + 1) ** 2 for x, y in BAD)  # type: ignore[operator]
    assert gamma == 25 * len(BAD) == 300

    active_vertices = {v for v in range(N) if active_owner(v)}
    assert OWNER in active_vertices
    assert active_vertices == set(range(N)) - {C_LEFT}
    assert len(ACTIVE_COMPONENTS) == 2

    obligations = collision_obligations(OWNER)
    by_other = Counter(other for other, _copy, _half in obligations)
    assert len(obligations) == 72
    assert by_other[OWNER] == by_other[C_LEFT] == by_other[C_RIGHT] == 16
    assert all(by_other[x] == 4 for x in LEFT + RIGHT)

    free = free_sources()
    p1_sources = {s for s in free if p1(s) and not scoped_reserved(s)}
    p3_sources = {s for s in free if p3(s) and not scoped_reserved(s)}
    available = p1_sources | p3_sources
    assert len(p1_sources) == 24
    assert len(p3_sources) == 24
    assert p1_sources.isdisjoint(p3_sources)
    assert len(available) == 48

    # The real cage does not by itself falsify the canonical selector: the
    # first main atom has an alternative shortest row avoiding OWNER.  This
    # one-row change already lowers the central shore demand from 72 to 62.
    alternative = (LEFT[0], A_LEFT[0], Z_LEFT[0], C_RIGHT, RIGHT[0])
    assert alternative in row_families[norm_edge(LEFT[0], RIGHT[0])]
    changed_rows = list(SELECTED_ROWS)
    changed_rows[0] = alternative
    changed_owner_obligations = owner_obligation_count(changed_rows)
    assert changed_owner_obligations == 62

    # strict-P4: U is the selected-row union, here U=V, so no outside source.
    selected_union = set().union(*(set(row) for row in SELECTED_ROWS))
    outside = set(range(N)) - selected_union
    assert not outside

    # P5 requires two distinct quiescent source endpoints.  Exactly one
    # vertex is outside every active selected component.
    quiescent = set(range(N)) - active_vertices
    assert quiescent == {C_LEFT}
    assert len(quiescent) < 2

    # Every central obligation sees every P1/P3 source, and every obligation
    # has the same active-component label.  Therefore coherence is vacuous,
    # maximum matched cardinality is 48, and the honest shore defect is 24.
    max_coherent_matched = min(len(obligations), len(available))
    defect = len(obligations) - max_coherent_matched
    assert max_coherent_matched == 48 and defect == 24

    histogram = Counter(len(rows) for rows in row_families.values())
    print(f"vertices={N} edges={len(EDGES)} triangles=0")
    print(
        f"intended_cut={intended_cut} exact_maxcut={maximum_cut} "
        f"maxcuts_vertex0_fixed={maximum_cut_count}"
    )
    print(f"bad_edges={len(BAD)} gamma={gamma} row_family_hist={dict(sorted(histogram.items()))}")
    print(
        f"selected_rows={len(SELECTED_ROWS)} distinct_anchored=12 "
        f"selected_union={len(selected_union)}"
    )
    print(
        f"active_vertices={len(active_vertices)} quiescent={sorted(quiescent)} "
        f"owner_active={active_owner(OWNER)}"
    )
    print(
        f"owner_obligations={len(obligations)} P1={len(p1_sources)} "
        f"P3={len(p3_sources)} strictP4=0 P5=0 reachable={len(available)} defect={defect}"
    )
    print(f"explicit_one_row_alternative_owner_obligations={changed_owner_obligations}")
    print("VERDICT=ENDPOINT_DIVERSITY_SOURCE_FLOOR_FALSE_AT_REAL_GAMMA_MIN_CAGE")
    digest = sha256(Path(__file__).read_bytes()).hexdigest().upper()
    print(f"script_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
