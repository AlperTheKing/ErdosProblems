#!/usr/bin/env python3
"""Independent exact verifier for P31's indexed-star lemma and falsifier."""

from __future__ import annotations

import itertools
from collections import Counter

from audit_indexed_phase import ROWS, audit_row, interval_residue_capacity
from search_indexed_twins import is_sidon, labels


W_MAX = 14
G_MAX = 15
P_MAX = 6


def support_profile(z: tuple[int, ...], gap: int, modulus: int) -> tuple[int, ...]:
    differences, stars = labels(z, gap)
    return (
        len({value % modulus for value in differences}),
        *(len({value % modulus for value in star}) for star in stars),
    )


def intersection_profile(
    z: tuple[int, ...], gap: int, modulus: int
) -> tuple[int, ...]:
    differences, stars = labels(z, gap)
    d_support = {value % modulus for value in differences}
    return tuple(
        len(d_support.intersection(value % modulus for value in star))
        for star in stars
    )


def triple_sums(e: tuple[int, ...]) -> set[int]:
    return {
        e[i] + e[j] + e[k]
        for i in range(len(e))
        for j in range(i, len(e))
        for k in range(j, len(e))
    }


def verify_twin() -> None:
    good = (0, 3, 19, 20)
    bad = (0, 1, 17, 20)
    gap = 2
    p = 4
    assert bad == tuple(sorted(good[-1] - value for value in good))
    assert is_sidon(good) and is_sidon(bad)

    good_d, good_stars = labels(good, gap)
    bad_d, bad_stars = labels(bad, gap)
    expected_d = {1, 3, 16, 17, 19, 20}
    assert set(good_d) == set(bad_d) == expected_d
    assert good_stars == (
        (2, 5, 21, 22),
        (8, 24, 25),
        (40, 41),
        (42,),
    )
    assert bad_stars == (
        (2, 3, 19, 22),
        (4, 20, 23),
        (36, 39),
        (42,),
    )
    good_c = {value for star in good_stars for value in star}
    bad_c = {value for star in bad_stars for value in star}
    assert not expected_d.intersection(good_c)
    assert expected_d.intersection(bad_c) == {3, 19, 20}
    assert gap + 2 * good[-1] == 42 < 3 * p * p

    good_e = tuple(gap + 2 * value for value in good)
    bad_e = tuple(gap + 2 * value for value in bad)
    assert not set(good_e).intersection(triple_sums(good_e))
    assert set(bad_e).intersection(triple_sums(bad_e)) == {42}

    expected_profiles = (
        (3, 2, 2, 2, 1),
        (5, 3, 3, 2, 1),
        (5, 4, 3, 2, 1),
        (5, 4, 3, 2, 1),
        (4, 3, 2, 2, 1),
        (5, 4, 3, 2, 1),
        (6, 3, 3, 2, 1),
        (6, 4, 3, 2, 1),
        (6, 4, 3, 2, 1),
        (5, 4, 3, 2, 1),
        (5, 4, 3, 2, 1),
        (5, 4, 3, 2, 1),
        (4, 3, 2, 2, 1),
    )
    for modulus, expected in zip(range(4, 17), expected_profiles):
        assert support_profile(good, gap, modulus) == expected
        assert support_profile(bad, gap, modulus) == expected

    assert intersection_profile(good, gap, 6) == (4, 2, 2, 0)
    assert intersection_profile(bad, gap, 6) == (4, 3, 1, 0)


def verify_lemma_exhaustively() -> tuple[int, int]:
    valid = 0
    star_modulus_checks = 0

    for width in range(1, W_MAX + 1):
        for p in range(2, min(P_MAX, width + 1) + 1):
            for interior in itertools.combinations(range(1, width), p - 2):
                z = (0, *interior, width)
                if not is_sidon(z):
                    continue
                differences, _ = labels(z, 1)
                assert len(differences) == len(set(differences))
                for gap in range(1, G_MAX + 1):
                    differences, stars = labels(z, gap)
                    all_sums = {value for star in stars for value in star}
                    if set(differences).intersection(all_sums):
                        continue
                    valid += 1
                    for modulus in range(p, p * p + 1):
                        dcounts = Counter(value % modulus for value in differences)
                        d_support = set(dcounts)
                        for star in stars:
                            ccounts = Counter(value % modulus for value in star)
                            c_support = set(ccounts)
                            lower = max(
                                0,
                                len(d_support) + len(c_support) - modulus,
                            )
                            relative = len(d_support.intersection(c_support))
                            cross = sum(
                                dcounts[residue] * count
                                for residue, count in ccounts.items()
                            )
                            capacity = sum(
                                interval_residue_capacity(value, modulus, width)
                                for value in star
                            )
                            assert lower <= relative <= cross <= capacity
                            star_modulus_checks += 1

    assert valid == 2861
    return valid, star_modulus_checks


def verify_stored_audits() -> None:
    by_p = {p: audit_row(p, x, span) for p, x, span in ROWS}
    expected = {
        5: (72, 178, 223, 267),
        9: (706, 2092, 3332, 4448),
        11: (1558, 4783, 8101, 12276),
    }
    for p, values in expected.items():
        stats = by_p[p]
        actual = (
            stats["sum_lower"],
            stats["sum_intersection"],
            stats["sum_actual"],
            stats["sum_capacity"],
        )
        assert actual == values


def main() -> None:
    verify_twin()
    valid, checks = verify_lemma_exhaustively()
    verify_stored_audits()
    print("PASS: P31 indexed-star phase verifier")
    print(f"valid signed rulers: {valid}")
    print(f"star-modulus inequalities: {checks}")
    print("support twin: p=4, G=2, W=20, L=42")
    print("bad overlap: {3, 19, 20}")
    print("relative phase at m=6: (4,2,2,0) != (4,3,1,0)")


if __name__ == "__main__":
    main()
