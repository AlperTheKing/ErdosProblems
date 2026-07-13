"""Independent exact verifier for the load-bearing P16 identities and twins."""

from __future__ import annotations

import json
from collections import Counter
from itertools import product


WITNESSES = [
    (5, 30, [0, 1, 3, 8, 12]),
    (9, 116, [0, 1, 3, 11, 15, 20, 36, 43, 49]),
    (10, 152, [0, 1, 6, 10, 23, 26, 34, 41, 53, 55]),
    (11, 191, [0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84]),
    (12, 238, [0, 2, 6, 18, 21, 28, 29, 60, 69, 74, 94, 107]),
]


def labels(z: list[int], gap: int) -> tuple[list[int], list[int]]:
    p = len(z)
    return (
        [z[j] - z[i] for i in range(p) for j in range(i + 1, p)],
        [gap + z[i] + z[j] for i in range(p) for j in range(i, p)],
    )


def sidon(z: list[int]) -> bool:
    sums = [z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))]
    return len(sums) == len(set(sums))


def histogram(values: list[int], modulus: int) -> Counter[int]:
    return Counter(x % modulus for x in values)


def q_moments(d: list[int], c: list[int], modulus: int, degree: int) -> tuple[int, ...]:
    return tuple(
        sum(
            ((x - y) // modulus) ** j
            for x in d
            for y in c
            if (x - y) % modulus == 0
        )
        for j in range(degree + 1)
    )


def cross_count(d: list[int], c: list[int], modulus: int) -> int:
    dh = histogram(d, modulus)
    ch = histogram(c, modulus)
    return sum(dh[r] * ch[r] for r in dh)


def audit_witness(p: int, theta: int, lower: list[int]) -> dict[str, int]:
    width = lower[-1]
    z = sorted(width - x for x in lower)
    gap = theta - 2 * width
    d, c = labels(z, gap)
    assert sidon(z)
    assert len(d) == len(set(d)) == p * (p - 1) // 2
    assert len(c) == len(set(c)) == p * (p + 1) // 2
    assert set(d).isdisjoint(c)

    cross_sum = 0
    self_sum = 0
    for modulus in range(p, p * p + 1):
        nh = histogram(z, modulus)
        dh = histogram(d, modulus)
        ch = histogram(c, modulus)
        for residue in range(modulus):
            ordered_sum = sum(nh[a] * nh[(residue - a) % modulus] for a in range(modulus))
            diagonal = sum(1 for x in z if 2 * x % modulus == residue)
            assert 2 * ch[(gap + residue) % modulus] == ordered_sum + diagonal
            correlation = sum(nh[a] * nh[(a + residue) % modulus] for a in range(modulus))
            if residue == 0:
                correlation -= p
            assert dh[residue] + dh[-residue % modulus] == correlation

        point_collisions = sum(v * (v - 1) // 2 for v in nh.values())
        assert point_collisions <= width // modulus
        xmod = cross_count(d, c, modulus)
        assert xmod == sum(1 for x in d for y in c if (x - y) % modulus == 0)
        assert all(x != y for x in d for y in c)
        cross_sum += xmod
        self_sum += sum(
            p - 1 - i
            for i, value in enumerate(z[:-1])
            if (gap + 2 * value) % modulus == 0
        )

    divisor_sum = sum(
        sum(1 for modulus in range(p, p * p + 1) if abs(x - y) % modulus == 0)
        for x in d
        for y in c
    )
    assert cross_sum == divisor_sum

    center_layers: Counter[int] = Counter()
    for a, b, c0, d0 in product(lower, repeat=4):
        value = a + b + c0 - d0
        if value % theta == 0:
            center_layers[value // theta] += 1
    assert set(center_layers) <= {0}
    return {"p": p, "cross_sum": cross_sum, "self_sum": self_sum, "center_zero": center_layers[0]}


def verify_phase_twin() -> dict[str, object]:
    p, gap, modulus = 5, 3, 9
    good = [0, 2, 8, 18, 22]
    bad = [0, 2, 8, 9, 22]
    gd, gc = labels(good, gap)
    bd, bc = labels(bad, gap)
    assert sidon(good) and sidon(bad)
    assert set(gd).isdisjoint(gc)
    assert sorted(set(bd).intersection(bc)) == [7, 13, 14, 20]
    assert histogram(good, modulus) == histogram(bad, modulus)
    assert histogram(gd, modulus) == histogram(bd, modulus)
    assert histogram(gc, modulus) == histogram(bc, modulus)
    assert q_moments(gd, gc, modulus, 3) == (16, -20, 72, -236)
    assert q_moments(bd, bc, modulus, 3) == (16, -20, 72, -236)
    assert gap + 2 * good[-1] == 47 < 3 * p * p
    return {"length": 47, "moments": [16, -20, 72, -236]}


def verify_average_twin() -> dict[str, object]:
    p, gap = 5, 6
    good = [0, 14, 24, 25, 27]
    bad = [0, 4, 5, 13, 27]
    gd, gc = labels(good, gap)
    bd, bc = labels(bad, gap)
    assert sidon(good) and sidon(bad)
    assert set(gd).isdisjoint(gc)
    assert sorted(set(bd).intersection(bc)) == [14, 23]
    good_vector = [cross_count(gd, gc, m) for m in range(p, p * p + 1)]
    bad_vector = [cross_count(bd, bc, m) for m in range(p, p * p + 1)]
    good_moments = tuple(sum(m**j * x for m, x in zip(range(p, p * p + 1), good_vector)) for j in range(3))
    bad_moments = tuple(sum(m**j * x for m, x in zip(range(p, p * p + 1), bad_vector)) for j in range(3))
    assert good_moments == bad_moments == (232, 2718, 39570)
    assert gap + 2 * good[-1] == 60 < 3 * p * p
    return {"length": 60, "modulus_moments": list(good_moments)}


def verify_prouhet(max_degree: int = 10) -> None:
    for degree in range(max_degree + 1):
        even = [n for n in range(2 ** (degree + 1)) if n.bit_count() % 2 == 0]
        odd = [n for n in range(2 ** (degree + 1)) if n.bit_count() % 2 == 1]
        assert 0 in even and 0 not in odd
        for j in range(degree + 1):
            assert sum(n**j for n in even) == sum(n**j for n in odd)


def main() -> None:
    witness_records = [audit_witness(*w) for w in WITNESSES]
    phase = verify_phase_twin()
    average = verify_average_twin()
    verify_prouhet()
    print(json.dumps({"witnesses": witness_records, "phase_twin": phase, "average_twin": average, "prouhet_through": 10}, sort_keys=True))


if __name__ == "__main__":
    main()
