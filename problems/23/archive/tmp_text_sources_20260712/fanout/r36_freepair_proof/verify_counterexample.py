from itertools import combinations, product


N = 20
X, A, P, Q, R = 0, 1, 2, 3, 4
Y, B, V, T, U = 5, 6, 7, 8, 9
W, C, D, E, F = 10, 11, 12, 13, 14
Z, H, I, J, K = 15, 16, 17, 18, 19

CYCLES = [
    [X, P, Q, R, A],
    [Y, V, T, U, B],
    [W, D, E, F, C],
    [Z, I, J, K, H],
]
BAD = {(X, A), (Y, B), (W, C), (Z, H)}
EXTRA = {(X, V), (V, W), (W, Z), (Z, A)}


def edge(u, v):
    return tuple(sorted((u, v)))


EDGES = set(EXTRA)
for row in CYCLES:
    EDGES.add(edge(row[0], row[-1]))
    EDGES.update(edge(row[i], row[i + 1]) for i in range(4))
EDGES = {edge(*e) for e in EDGES}
BAD = {edge(*e) for e in BAD}

# The displayed maximum cut. True and False are its two shores.
SIDE_TRUE = {X, Q, A, Y, T, B, W, E, C, I, K}


def side(v):
    return v in SIDE_TRUE


def blue(u, v):
    return edge(u, v) in EDGES and side(u) != side(v)


def bad(u, v):
    return edge(u, v) in EDGES and side(u) == side(v)


def all_rows(u, v):
    ans = []
    for middle in product(range(N), repeat=3):
        row = (u,) + middle + (v,)
        if len(set(row)) == 5 and all(blue(row[i], row[i + 1]) for i in range(4)):
            ans.append(row)
    return sorted(ans)


ROW_DB = {
    edge(X, A): all_rows(X, A),
    edge(Y, B): all_rows(Y, B),
    edge(W, C): all_rows(W, C),
    edge(Z, H): all_rows(Z, H),
}
SELECTED = [tuple(row) for row in CYCLES]


def cut_size(mask):
    return sum(((mask >> u) & 1) != ((mask >> v) & 1) for u, v in EDGES)


def pair_count(x, y):
    return sum(x in row and y in row for row in SELECTED)


def sigma(vertices):
    vertices = set(vertices)
    d_blue = sum(blue(u, v) and ((u in vertices) != (v in vertices)) for u, v in EDGES)
    d_bad = sum(bad(u, v) and ((u in vertices) != (v in vertices)) for u, v in EDGES)
    return d_blue, d_bad, d_blue - d_bad


def main():
    assert len(EDGES) == 24
    assert not any(
        edge(a, b) in EDGES and edge(b, c) in EDGES and edge(a, c) in EDGES
        for a, b, c in combinations(range(N), 3)
    )
    assert {e for e in EDGES if side(e[0]) == side(e[1])} == BAD
    shown_cut = sum(blue(*e) for e in EDGES)
    # Independent exhaustive maximum-cut check (2^20 assignments).
    max_cut = max(cut_size(mask) for mask in range(1 << N))
    assert shown_cut == max_cut == 20

    expected_db = {
        edge(X, A): [(X, P, Q, R, A), (X, V, W, Z, A)],
        edge(Y, B): [(Y, V, T, U, B)],
        edge(W, C): [(W, D, E, F, C)],
        edge(Z, H): [(Z, I, J, K, H)],
    }
    assert ROW_DB == expected_db

    support = {
        edge(row[i], row[i + 1]) for row in SELECTED for i in range(4)
    }
    selected_vertices = set().union(*map(set, SELECTED))
    active = {
        e for e in EDGES
        if e[0] in selected_vertices and e[1] in selected_vertices
        and blue(*e) and e not in support
    }
    assert active == {edge(X, V), edge(V, W), edge(W, Z), edge(Z, A)}

    # The active path contains both endpoints X,A of a selected bad atom,
    # so V is an ActiveOwner. X is its active neighbour and Y its selected-
    # support neighbour.
    assert blue(V, X) and edge(V, X) in active
    assert blue(V, Y) and edge(V, Y) in support
    assert side(X) == side(Y) and pair_count(X, Y) == 0
    d_blue, d_bad, sig = sigma([X, Y])
    assert (d_blue, d_bad, sig) == (3, 2, 1)
    # ScopedReserved is false for both halves because X-Y is not blue.
    assert not blue(X, Y)
    # Production CommonBlueOwner requires dM + 2 <= dB, which fails 4 <= 3.
    assert not (d_bad + 2 <= d_blue)

    print("REPLAY=PASS")
    print(f"N={N} edges={len(EDGES)} triangle_free=true maxcut={max_cut}")
    print("row_family_sizes=" + repr(tuple(len(ROW_DB[e]) for e in sorted(BAD))))
    print("active_path=(0,7,10,15,1) owner=7 active_x=0 support_y=5")
    print("pairCount(0,5)=0 scopedReserved=false/false")
    print("dB({0,5})=3 dM({0,5})=2 sigma=1 commonBlueValid=false")


if __name__ == "__main__":
    main()
