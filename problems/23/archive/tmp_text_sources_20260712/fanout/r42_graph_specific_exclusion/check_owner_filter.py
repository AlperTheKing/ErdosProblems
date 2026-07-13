"""Exact finite audit of the owner filter on R42 turnover keys.

This does not model the whole graph.  It checks the exact P1/P3 logical core
after graph geometry has ruled out P2/P4/P5 for an active blue-edge base.
"""

from itertools import product


M, X, Y, O = range(4)
SOURCES = ((M, X), (X, M), (M, Y), (Y, M))


def p13(owner, source, companion):
    left, right = source
    return left == owner or (companion[left] and companion[right])


def main():
    universal = []
    for owner in (M, X, Y, O):
        for bits in product((False, True), repeat=3):
            companion = {M: bits[0], X: bits[1], Y: bits[2]}
            # Target turnover freeness: no selected row contains m with x or
            # m with y.  If the owner is one endpoint, the corresponding
            # self/other P3 fallback is therefore impossible.
            if owner == M:
                companion[X] = False
                companion[Y] = False
            elif owner == X:
                companion[M] = False
            elif owner == Y:
                companion[M] = False
            if all(p13(owner, source, companion) for source in SOURCES):
                universal.append((owner, tuple(companion[v] for v in (M, X, Y))))

    assert universal == [(O, (True, True, True))]
    print("verdict=PASS")
    print("universal_owner_cases=1")
    print("case=external owner with companions m,x,y")


if __name__ == "__main__":
    main()
