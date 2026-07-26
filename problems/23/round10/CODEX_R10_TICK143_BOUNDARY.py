"""Exact boundary test for Claude TICK-143's proposed non-colourable gap.

The support S is one of the minimal non-C5-colourable supports in Gamma_11.
Five vertices C induce a C5.  Give every vertex of C weight M and every
vertex of S-C weight 1.  Exact cut enumeration, performed symbolically in M,
proves

    bip(Gamma_11[a(M)]) = M^2 + 1

for every integer M >= 1.  Consequently

    25*bip / (sum a)^2 = 25(M^2+1)/(5M+3)^2 -> 1.

Thus the full-support non-C5-colourable region has no uniform gap below the
1/25 frontier.  This does not refute the desired inequality.
"""

from __future__ import annotations

from collections import Counter
from itertools import product


N = 11
S = frozenset((0, 1, 2, 4, 5, 6, 8, 9))
C = frozenset((0, 1, 4, 5, 8))
R = S - C


def gamma_11_edges() -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(N)
        for v in range(u + 1, N)
        if min((v - u) % N, (u - v) % N) >= 4
    ]


def is_c5_colourable(vertices: tuple[int, ...], edges: list[tuple[int, int]]) -> bool:
    relevant = [(u, v) for u, v in edges if u in S and v in S]
    for colours in product(range(5), repeat=len(vertices)):
        assignment = dict(zip(vertices, colours))
        if all((assignment[u] - assignment[v]) % 5 in (1, 4) for u, v in relevant):
            return True
    return False


def cut_polynomial_histogram(
    edges: list[tuple[int, int]],
) -> Counter[tuple[int, int, int]]:
    """Return counts of A*M^2+B*M+C over every labelled cut."""
    relevant = [(u, v) for u, v in edges if u in S and v in S]
    histogram: Counter[tuple[int, int, int]] = Counter()
    for mask in range(1 << N):
        coefficients = [0, 0, 0]
        for u, v in relevant:
            if ((mask >> u) & 1) != ((mask >> v) & 1):
                continue
            number_in_cycle = int(u in C) + int(v in C)
            coefficients[2 - number_in_cycle] += 1
        histogram[tuple(coefficients)] += 1
    return histogram


def main() -> None:
    edges = gamma_11_edges()
    assert len(edges) == 22
    cycle_edges = [(u, v) for u, v in edges if u in C and v in C]
    assert len(cycle_edges) == 5
    assert all(sum(vertex in edge for edge in cycle_edges) == 2 for vertex in C)
    assert not is_c5_colourable(tuple(sorted(S)), edges)

    histogram = cut_polynomial_histogram(edges)
    assert sum(histogram.values()) == 1 << N
    assert all(leading in (1, 3, 5) for leading, _linear, _constant in histogram)
    assert min(
        constant
        for leading, linear, constant in histogram
        if leading == 1 and linear == 0
    ) == 1
    assert histogram[(1, 0, 1)] == 32

    # The preceding exact facts prove every cut costs at least M^2+1 for
    # integer M>=1, and the displayed cut type attains it.
    for mass in (1, 2, 5, 10, 20, 50, 100, 1000):
        total = 5 * mass + 3
        optimum = min(
            leading * mass * mass + linear * mass + constant
            for leading, linear, constant in histogram
        )
        assert optimum == mass * mass + 1
        print(
            f"M={mass} q={total} bip={optimum} "
            f"ratio=25*{optimum}/{total * total}"
        )

    print(
        "EXACT: bip=M^2+1 for every integer M>=1; "
        "25*bip/(5M+3)^2 tends to 1"
    )
    print("CONCLUSION: no uniform gap on the non-C5-colourable full-support region")


if __name__ == "__main__":
    main()
