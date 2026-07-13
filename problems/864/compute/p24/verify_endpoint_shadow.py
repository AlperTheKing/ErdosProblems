"""Exact audit for P24's ordered endpoint-shadow inequalities."""

from bisect import bisect_right
from itertools import combinations, combinations_with_replacement


W_MAX = 14
G_MAX = 15
Q_MAX = 6


def choose2(n):
    return n * (n - 1) // 2


def choose2_with_diagonal(n):
    return n * (n + 1) // 2


def unordered_pair_sums(values):
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def is_sidon(values):
    sums = unordered_pair_sums(values)
    return len(sums) == len(set(sums))


def triple_shadow(values, cutoff):
    return {
        a + b + c
        for a, b, c in combinations_with_replacement(values, 3)
        if a + b + c <= cutoff
    }


def assert_valid_e(values):
    assert values == tuple(sorted(values))
    assert values[0] > 0
    assert len({value % 2 for value in values}) == 1
    assert is_sidon(values)
    triples = {
        a + b + c
        for a, b, c in combinations_with_replacement(values, 3)
    }
    assert set(values).isdisjoint(triples)


def assert_signed_ruler(z, g):
    assert z == tuple(sorted(z))
    assert z[0] == 0
    assert g > 0
    assert is_sidon(z)
    differences = {
        z[j] - z[i]
        for i in range(len(z))
        for j in range(i + 1, len(z))
    }
    shifted_sums = {g + value for value in unordered_pair_sums(z)}
    assert differences.isdisjoint(shifted_sums)
    e = tuple(g + 2 * value for value in z)
    assert_valid_e(e)
    return e


def audit_e(values):
    """Check every P24 formula for one valid set E using integer arithmetic."""
    assert_valid_e(values)
    q = len(values)
    m = values[-1]
    parity = m % 2
    slots = set(range(1 if parity else 2, m + 1, 2))
    holes = slots.difference(values)
    pair_sums = tuple(sorted(unordered_pair_sums(values)))
    shadow = triple_shadow(values, m)
    rank = lambda cutoff: bisect_right(values, cutoff)

    seen_differences = set()
    per_pair = []
    q_value = 0
    represented_shadow_edges = 0
    represented_hole_edges = 0

    for i, x in enumerate(values):
        for j in range(i + 1, q):
            y = values[j]
            d = y - x
            assert d not in seen_differences
            seen_differences.add(d)

            source = bisect_right(pair_sums, m - y)
            shadow_edges = sum(1 for u in shadow if u + d in shadow)
            hole_edges = sum(1 for u in holes if u + d in holes)

            slot_count = (m + parity) // 2
            exact_hole_formula = (
                slot_count
                - d // 2
                - rank(m - d)
                - q
                + rank(d)
                + 1
            )
            assert hole_edges == exact_hole_formula
            assert source <= shadow_edges <= hole_edges

            per_pair.append((i, j, source, hole_edges))
            q_value += source
            represented_shadow_edges += shadow_edges
            represented_hole_edges += hole_edges

    assert q_value == sum(j * bisect_right(pair_sums, m - values[j]) for j in range(1, q))
    assert q_value <= represented_shadow_edges
    assert represented_shadow_edges <= represented_hole_edges
    assert represented_shadow_edges <= choose2(len(shadow))
    assert represented_hole_edges <= choose2(len(holes))

    # Audit the interval-slice corollary at every integer cutoff.
    for cutoff in range(m + 1):
        prefix_pairs = choose2(rank(m - cutoff))
        restricted_capacity = sum(
            hole_edges
            for _, j, _, hole_edges in per_pair
            if values[j] <= m - cutoff
        )
        exact_slice_lhs = prefix_pairs * bisect_right(pair_sums, cutoff)
        prefix = rank(cutoff // 2)
        coarse_slice_lhs = prefix_pairs * choose2_with_diagonal(prefix)
        assert coarse_slice_lhs <= exact_slice_lhs <= restricted_capacity

    return {
        "q": q,
        "m": m,
        "q_value": q_value,
        "shadow": shadow,
        "shadow_edges": represented_shadow_edges,
        "holes": holes,
        "hole_edges": represented_hole_edges,
        "pair_checks": choose2(q),
        "slice_checks": m + 1,
    }


def exhaustive_small_audit():
    valid = 0
    pair_checks = 0
    slice_checks = 0
    equality = None

    for w in range(1, W_MAX + 1):
        for q in range(2, min(Q_MAX, w + 1) + 1):
            for interior in combinations(range(1, w), q - 2):
                z = (0, *interior, w)
                if not is_sidon(z):
                    continue
                differences = {
                    z[j] - z[i]
                    for i in range(q)
                    for j in range(i + 1, q)
                }
                sums = set(unordered_pair_sums(z))
                for g in range(1, G_MAX + 1):
                    if differences.intersection(g + value for value in sums):
                        continue
                    e = assert_signed_ruler(z, g)
                    stats = audit_e(e)
                    valid += 1
                    pair_checks += stats["pair_checks"]
                    slice_checks += stats["slice_checks"]
                    if e == (2, 4, 14):
                        equality = stats

    assert valid == 2861
    assert pair_checks == 14405
    assert equality is not None
    assert equality["q_value"] == equality["hole_edges"] == 3
    assert equality["shadow"] == {6, 8, 10, 12}
    return valid, pair_checks, slice_checks, equality


def audit_known_rulers():
    # Rows are (q, lower representatives X, signed-ruler span M).
    rows = (
        (2, (0, 1), 4),
        (3, (0, 1, 3), 10),
        (4, (0, 2, 5, 6), 19),
        (5, (0, 1, 3, 8, 12), 30),
        (6, (0, 1, 3, 8, 14, 18), 48),
        (7, (0, 5, 8, 9, 15, 26, 28), 68),
        (8, (0, 2, 3, 10, 16, 28, 33, 37), 85),
        (9, (0, 1, 3, 11, 15, 20, 36, 43, 49), 116),
        (10, (0, 1, 3, 8, 14, 26, 30, 47, 62, 71), 152),
        (11, (0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84), 191),
        (12, (0, 1, 4, 6, 14, 29, 36, 53, 69, 87, 96, 107), 240),
    )
    audited = []
    for q, x, m in rows:
        w = x[-1]
        z = tuple(sorted(w - value for value in x))
        g = m - 2 * w
        assert len(z) == q
        e = assert_signed_ruler(z, g)
        stats = audit_e(e)
        assert stats["m"] == m
        audited.append(q)
    return tuple(audited)


def audit_boundary_examples():
    equality_e = (2, 4, 14)
    assert_valid_e(equality_e)

    collision_e = (1, 7, 11)
    assert_valid_e(collision_e)
    block_2 = {value + 2 for value in collision_e if value + 2 <= 11}
    block_8 = {value + 8 for value in collision_e if value + 8 <= 11}
    assert block_2 == {3, 9}
    assert block_8 == {9}
    assert block_2.intersection(block_8) == {9}

    repeated_shadow_e = (1, 7, 19, 23)
    assert_valid_e(repeated_shadow_e)
    assert 1 + 1 + 19 == 7 + 7 + 7 == 21
    return block_2, block_8


def main():
    valid, pair_checks, slice_checks, equality = exhaustive_small_audit()
    known = audit_known_rulers()
    block_2, block_8 = audit_boundary_examples()
    print("PASS: ordered endpoint-shadow audit")
    print(f"small signed rulers: {valid}")
    print(f"represented differences: {pair_checks}")
    print(f"integer interval slices: {slice_checks}")
    print(
        "equality: E=(2, 4, 14), "
        f"Q={equality['q_value']}, hole-edge capacity={equality['hole_edges']}"
    )
    print(f"translate collision: {sorted(block_2)} intersect {sorted(block_8)} = [9]")
    print("repeated shadow: 21 = 1+1+19 = 7+7+7")
    print(f"known signed-ruler witnesses: q={known[0]}..{known[-1]}")


if __name__ == "__main__":
    main()
