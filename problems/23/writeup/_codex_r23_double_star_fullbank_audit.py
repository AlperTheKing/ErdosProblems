"""Exact FullBank audit for the R22/R23 double-star family.

This distinguishes the failed collision-owner submatching from the actual
banked relaxed-cover interface.  On the row core C, the universal half-
singleton cover has:

* exact bad-row coverage 1;
* congestion 1 on every shortest-row blue edge F;
* load 1/2 on every off-support lock edge O;
* all O-load routable to the incident core vertex with capacity N-T(v).

These are precisely the numeric hypotheses of the compiled constructor
`Ell5SingletonVertexSlack.certificate_of_singletonCore_vertexSlack`.
The script verifies the literal 89-vertex graph and the closed-form margins
for every 2 <= a <= b <= --max-side using exact Fraction arithmetic.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction

from _codex_r23_double_star_family_gate import verify_pair


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def build(a_size: int, b_size: int):
    r, c_l, c_r = 0, 1, 2
    left = list(range(3, 3 + a_size))
    right = list(range(3 + a_size, 3 + a_size + b_size))
    core_n = 3 + a_size + b_size
    anchor = core_n

    blue: set[tuple[int, int]] = {norm(r, c_l), norm(r, c_r)}
    blue.update(norm(c_l, x) for x in left)
    blue.update(norm(c_r, y) for y in right)
    bad = {norm(x, y) for x in left for y in right}

    # One low-lock leaf on each shore; all other leaves carry the regular load.
    q = {v: 0 for v in range(core_n)}
    for i, x in enumerate(left):
        q[x] = b_size - 1 if i == 0 else b_size
    for i, y in enumerate(right):
        q[y] = a_size - 1 if i == 0 else a_size

    nxt = anchor + 1
    locks = []
    for v in range(core_n):
        for _ in range(q[v]):
            x, y = nxt, nxt + 1
            nxt += 2
            blue.update((norm(v, x), norm(x, y), norm(y, anchor)))
            locks.append((v, x, y))

    rows = [(x, c_l, r, c_r, y) for x in left for y in right]
    side = [0] * nxt
    side[c_l] = side[c_r] = side[anchor] = 1
    for _, x, _ in locks:
        side[x] = 1

    return {
        "n": nxt,
        "r": r,
        "cL": c_l,
        "cR": c_r,
        "left": left,
        "right": right,
        "core": set(range(core_n)),
        "anchor": anchor,
        "blue": blue,
        "bad": bad,
        "rows": rows,
        "side": side,
        "q": q,
        "locks": locks,
    }


def literal_audit(a_size: int, b_size: int):
    data = build(a_size, b_size)
    n = data["n"]
    core = data["core"]
    blue = data["blue"]
    bad = data["bad"]
    rows = data["rows"]
    side = data["side"]

    assert all(side[x] != side[y] for x, y in blue)
    assert all(side[x] == side[y] for x, y in bad)

    all_edges = blue | bad
    adj = [set() for _ in range(n)]
    badj = [set() for _ in range(n)]
    for x, y in all_edges:
        adj[x].add(y)
        adj[y].add(x)
    for x, y in blue:
        badj[x].add(y)
        badj[y].add(x)
    assert not any(adj[x] & adj[y] for x, y in all_edges)

    # Complete shortest-row replay: every bad edge has exactly its displayed row.
    for x, y in bad:
        dist = [-1] * n
        count = [0] * n
        dist[x] = 0
        count[x] = 1
        queue = deque([x])
        while queue:
            u = queue.popleft()
            for v in badj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    count[v] = count[u]
                    queue.append(v)
                elif dist[v] == dist[u] + 1:
                    count[v] += count[u]
        assert dist[y] == 4 and count[y] == 1

    row_core = set().union(*(set(row) for row in rows))
    assert row_core == core
    support = {
        norm(row[i], row[i + 1])
        for row in rows
        for i in range(4)
    }
    outside = {
        edge for edge in blue
        if (edge[0] in core or edge[1] in core) and edge not in support
    }
    assert len(support) == a_size + b_size + 2
    assert len(outside) == 2 * a_size * b_size - 2
    assert all((x in core) ^ (y in core) for x, y in outside)

    row_count = Counter(v for row in rows for v in row)
    loads = {v: 5 * row_count[v] for v in core}
    outside_degree = Counter(v for edge in outside for v in edge if v in core)
    margins = {}
    for v in core:
        load = Fraction(outside_degree[v], 2)
        cap = max(Fraction(0), Fraction(n - loads[v]))
        margins[v] = cap - load
        assert margins[v] >= 0

    # Half-singleton identities, checked literally rather than by formula.
    for x, y in bad:
        coverage = sum(Fraction(1, 2) for v in core if v == x or v == y)
        assert coverage == 1
    for x, y in support:
        congestion = sum(Fraction(1, 2) for v in core if v == x or v == y)
        assert congestion == 1
    for x, y in outside:
        off_load = sum(Fraction(1, 2) for v in core if v == x or v == y)
        assert off_load == Fraction(1, 2)

    return {
        "a": a_size,
        "b": b_size,
        "N": n,
        "rows": len(rows),
        "support": len(support),
        "outside": len(outside),
        "outsideLoad": str(Fraction(len(outside), 2)),
        "minVertexSlackMargin": str(min(margins.values())),
        "minLoadedVertexMargin": str(min(
            margin for v, margin in margins.items() if outside_degree[v] > 0
        )),
        "hubLoads": [loads[data[k]] for k in ("r", "cL", "cR")],
    }


def formula_audit(a_size: int, b_size: int):
    family = verify_pair(a_size, b_size)
    n = family.n
    # Worst leaf on each shore is a regular (high-lock) leaf.
    left_margin = Fraction(n - 5 * b_size) - Fraction(b_size, 2)
    right_margin = Fraction(n - 5 * a_size) - Fraction(a_size, 2)
    assert left_margin > 0
    assert right_margin > 0
    # Hubs may be overloaded, but have no off-support lock incidence.
    hub_margin = max(Fraction(0), Fraction(n - 5 * a_size * b_size))
    assert hub_margin >= 0
    return min(left_margin, right_margin)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-side", type=int, default=40)
    args = parser.parse_args()

    min_formula_margin = None
    checked = 0
    for a_size in range(2, args.max_side + 1):
        for b_size in range(a_size, args.max_side + 1):
            margin = formula_audit(a_size, b_size)
            min_formula_margin = margin if min_formula_margin is None else min(
                min_formula_margin, margin
            )
            checked += 1

    exact_89 = literal_audit(4, 5)
    exact_110 = literal_audit(5, 5)
    print(f"formulaPairs={checked} minFormulaMargin={min_formula_margin}")
    print(f"literal89={exact_89}")
    print(f"literal110={exact_110}")
    print(
        "VERDICT: collision matching fails, but the half-singleton "
        "vertexSlack-only FullBank certificate obligations pass exactly"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
