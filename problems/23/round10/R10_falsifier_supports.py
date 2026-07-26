"""Exact finite support reduction for the Gamma_11 arc-falsifier search.

This script independently rebuilds Gamma_11 and its distinct cyclic-interval
cut forms.  It then enumerates all 2^11-1 nonempty supports.

A support S can have positive ARCBOUND only if every arc form has at least one
monochromatic edge with both endpoints in S.  We enumerate those supports,
their inclusion-minimal members, and their D_22 orbits.  The output is a finite
certificate that the minimal members are exactly the 33 induced C5s, in three
D_22 orbits.  It also verifies the weighted-Mantel upper bound used by the
integer branch-and-bound on every induced subgraph of every arc form.

All checks use integers and finite enumeration.
"""

from itertools import combinations

N = 11


def adjacent(u, v):
    d = abs(u - v)
    d = min(d, N - d)
    return 3 * d > N


EDGES = tuple(
    (u, v) for u in range(N) for v in range(u + 1, N) if adjacent(u, v)
)


def arc_forms():
    forms = set()
    for start in range(N):
        for length in range(N + 1):
            side = {(start + t) % N for t in range(length)}
            mono = tuple(
                (u, v) for (u, v) in EDGES if ((u in side) == (v in side))
            )
            forms.add(mono)
    return tuple(sorted(forms))


ARCS = arc_forms()


def support_hits_every_arc(mask):
    return all(
        any((mask >> u) & 1 and (mask >> v) & 1 for (u, v) in form)
        for form in ARCS
    )


def is_induced_c5(mask):
    if mask.bit_count() != 5:
        return False
    vertices = [v for v in range(N) if (mask >> v) & 1]
    degrees = []
    edge_count = 0
    for u in vertices:
        degree = sum(adjacent(u, v) for v in vertices if u != v)
        degrees.append(degree)
        edge_count += degree
    return edge_count == 10 and degrees == [2] * 5


def image(mask, rotation, reflection):
    out = 0
    for v in range(N):
        if (mask >> v) & 1:
            w = ((-v if reflection else v) + rotation) % N
            out |= 1 << w
    return out


def canonical(mask):
    return min(
        image(mask, rotation, reflection)
        for rotation in range(N)
        for reflection in (False, True)
    )


def triangle_free(mask, form):
    vertices = [v for v in range(N) if (mask >> v) & 1]
    form_set = set(form)
    return not any(
        tuple(sorted((u, v))) in form_set
        and tuple(sorted((u, w))) in form_set
        and tuple(sorted((v, w))) in form_set
        for u, v, w in combinations(vertices, 3)
    )


def vertices(mask):
    return [v for v in range(N) if (mask >> v) & 1]


def main():
    assert len(EDGES) == 22
    assert all(sum(v in edge for edge in EDGES) == 4 for v in range(N))
    assert len(ARCS) == 56

    survivors = [
        mask for mask in range(1, 1 << N) if support_hits_every_arc(mask)
    ]
    minimal = [
        mask
        for mask in survivors
        if not any(
            sub != mask and (sub & mask) == sub
            for sub in survivors
        )
    ]
    induced_c5s = [mask for mask in range(1, 1 << N) if is_induced_c5(mask)]

    assert set(minimal) == set(induced_c5s)
    assert len(minimal) == 33
    reps = sorted({canonical(mask) for mask in minimal})
    assert len(reps) == 3

    survivor_counts = {
        size: sum(mask.bit_count() == size for mask in survivors)
        for size in range(1, N + 1)
    }
    survivor_orbits = {
        size: len(
            {
                canonical(mask)
                for mask in survivors
                if mask.bit_count() == size
            }
        )
        for size in range(1, N + 1)
    }

    # Every induced subgraph of every arc's monochromatic graph is triangle-free.
    # This is the sole graph hypothesis needed for the weighted Mantel r^2/4
    # upper bound in R10_falsifier_bnb.cpp.
    for form in ARCS:
        for mask in range(1 << N):
            assert triangle_free(mask, form)

    print("Gamma_11: vertices=11 edges=22 degree=4")
    print(f"distinct cyclic-interval monochromatic forms: {len(ARCS)}")
    print(f"nonempty supports: {(1 << N) - 1}")
    print(f"supports killed by an empty monochromatic arc: {(1 << N) - 1 - len(survivors)}")
    print(f"supports surviving the positive-ARCBOUND gate: {len(survivors)}")
    print("survivors by support size:", survivor_counts)
    print("D_22 orbits by support size:", survivor_orbits)
    print(f"inclusion-minimal survivors: {len(minimal)}")
    print(f"induced C5 supports: {len(induced_c5s)}")
    print("minimal survivors equal induced C5s: PASS")
    print("three D_22 representatives:")
    for rep in reps:
        print(" ", vertices(rep))
    print("all arc-form induced subgraphs triangle-free: PASS")


if __name__ == "__main__":
    main()
