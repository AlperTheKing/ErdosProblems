#!/usr/bin/env python3
"""Focused zero-trust replay for the V7 unit-column theorem.

This is deliberately not a parameter census.  It checks one asymmetric full
Ehrhart polynomial, one pair whose numerator terms meet both coefficient
chambers and the chamber wall, the generalized-binomial continuation, and a
small homogeneous skew-Kostka/LR replay at dilations 0, 1, and 2.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import math


def generalized_binomial(top: int, bottom: int) -> Fraction:
    """Falling-factorial binomial, including negative integral tops."""
    assert bottom >= 0
    answer = Fraction(1)
    for q in range(bottom):
        answer *= Fraction(top - q, q + 1)
    return answer


def binomial_jet(slope: int, constant: int, bottom: int) -> tuple[Fraction, Fraction]:
    """Value and derivative at zero of binom(slope*n+constant,bottom)."""
    value = generalized_binomial(constant, bottom)
    if bottom == 0:
        return value, Fraction(0)
    derivative = Fraction(0)
    for omitted in range(bottom):
        product = Fraction(slope, math.factorial(bottom))
        for q in range(bottom):
            if q != omitted:
                product *= constant - q
        derivative += product
    return value, derivative


def jet_product(*jets: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    value = Fraction(1)
    derivative = Fraction(0)
    for next_value, next_derivative in jets:
        derivative = derivative * next_value + value * next_derivative
        value *= next_value
    return value, derivative


def direct_K(P: int, Q: int, alpha: int, gamma: int, delta: int) -> int:
    """Direct coefficient of (1-p)^-alpha(1-pt)^-gamma(1-t)^-delta."""
    assert min(P, Q) >= 0
    return sum(
        math.comb(P - c + alpha - 1, alpha - 1)
        * math.comb(c + gamma - 1, gamma - 1)
        * math.comb(Q - c + delta - 1, delta - 1)
        for c in range(min(P, Q) + 1)
    )


def partial_fraction_K(P: int, Q: int, alpha: int, gamma: int, delta: int) -> Fraction:
    """The P<=Q pole decomposition; swap endpoints in the other chamber."""
    if Q < P:
        return partial_fraction_K(Q, P, delta, gamma, alpha)
    first = sum(
        (
            Fraction((-1) ** m * math.comb(gamma + m - 1, m))
            * generalized_binomial(P + alpha - m - 1, alpha - m - 1)
            * generalized_binomial(
                Q + gamma + delta - 1, gamma + delta + m - 1
            )
            for m in range(alpha)
        ),
        Fraction(0),
    )
    second = sum(
        (
            Fraction((-1) ** alpha * math.comb(alpha + m - 1, m))
            * generalized_binomial(P + gamma - m - 1, gamma - m - 1)
            * generalized_binomial(
                Q - P + delta + m - 1, delta + alpha + m - 1
            )
            for m in range(gamma)
        ),
        Fraction(0),
    )
    return first + second


def partial_fraction_K_linear(
    p_slope: int,
    p_constant: int,
    q_slope: int,
    q_constant: int,
    alpha: int,
    gamma: int,
    delta: int,
    p_le_q_eventually: bool,
) -> Fraction:
    """Derivative at zero of the fixed eventual coefficient-chamber polynomial."""
    if not p_le_q_eventually:
        return partial_fraction_K_linear(
            q_slope,
            q_constant,
            p_slope,
            p_constant,
            delta,
            gamma,
            alpha,
            True,
        )

    answer = Fraction(0)
    for m in range(alpha):
        jet = jet_product(
            binomial_jet(
                p_slope, p_constant + alpha - m - 1, alpha - m - 1
            ),
            binomial_jet(
                q_slope,
                q_constant + gamma + delta - 1,
                gamma + delta + m - 1,
            ),
        )
        answer += (-1) ** m * math.comb(gamma + m - 1, m) * jet[1]
    for m in range(gamma):
        jet = jet_product(
            binomial_jet(
                p_slope, p_constant + gamma - m - 1, gamma - m - 1
            ),
            binomial_jet(
                q_slope - p_slope,
                q_constant - p_constant + delta + m - 1,
                delta + alpha + m - 1,
            ),
        )
        answer += (
            (-1) ** alpha * math.comb(alpha + m - 1, m) * jet[1]
        )
    return answer


def derivative_from_values(nodes: list[int], values: list[int]) -> Fraction:
    """Derivative at zero of the unique interpolating polynomial."""
    assert len(nodes) == len(values)
    answer = Fraction(0)
    for index, node in enumerate(nodes):
        polynomial = [Fraction(1)]
        denominator = Fraction(1)
        for other_index, other in enumerate(nodes):
            if other_index == index:
                continue
            updated = [Fraction(0)] * (len(polynomial) + 1)
            for degree, coefficient in enumerate(polynomial):
                updated[degree] -= other * coefficient
                updated[degree + 1] += coefficient
            polynomial = updated
            denominator *= node - other
        answer += Fraction(values[index]) * polynomial[1] / denominator
    return answer


def first_differences(values: list[int]) -> list[int]:
    firsts: list[int] = []
    row = values[:]
    while row:
        firsts.append(row[0])
        row = [right - left for left, right in zip(row, row[1:])]
    return firsts


def newton_linear(firsts: list[int]) -> Fraction:
    return sum(
        (
            Fraction((-1) ** (order - 1) * firsts[order], order)
            for order in range(1, len(firsts))
        ),
        Fraction(0),
    )


def newton_value(firsts: list[int], n: int) -> int:
    return sum(
        firsts[order] * math.comb(n, order) for order in range(len(firsts))
    )


def distribution(k: int, n: int) -> dict[tuple[int, int], int]:
    kernel = [(x, y) for x in range(n + 1) for y in range(n - x + 1)]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_x, old_y), multiplicity in states.items():
            for x, y in kernel:
                updated[(old_x + x, old_y + y)] += multiplicity
        states = dict(updated)
    return states


def projected_count(
    rows: tuple[int, int, int], k: int, n: int, states: dict[tuple[int, int], int]
) -> int:
    return sum(
        multiplicity
        for (x, y), multiplicity in states.items()
        if x <= rows[0] * n
        and y <= rows[1] * n
        and k * n - x - y <= rows[2] * n
    )


def single_count(cap: int, n: int, states: dict[tuple[int, int], int]) -> int:
    return sum(value for (x, _), value in states.items() if x > cap * n)


def pair_count(
    cap1: int, cap2: int, n: int, states: dict[tuple[int, int], int]
) -> int:
    return sum(
        value
        for (x, y), value in states.items()
        if x > cap1 * n and y > cap2 * n
    )


def F(k: int, x: int) -> Fraction:
    if x >= k:
        return Fraction(0)
    return sum(
        (Fraction(q, 2 * (x + q)) for q in range(1, k - x + 1)),
        Fraction(0),
    )


def predicted_linear(rows: tuple[int, int, int], k: int) -> Fraction:
    pairs = (rows[0] + rows[1], rows[0] + rows[2], rows[1] + rows[2])
    return (
        Fraction(3 * k, 2)
        - sum((F(k, row) for row in rows), Fraction(0))
        - sum((F(k, pair) for pair in pairs), Fraction(0))
    )


def is_partition(partition: tuple[int, ...]) -> bool:
    return all(partition[i] >= partition[i + 1] >= 0 for i in range(len(partition) - 1))


def contains(outer: tuple[int, ...], inner: tuple[int, ...]) -> bool:
    padded = inner + (0,) * (len(outer) - len(inner))
    return len(inner) <= len(outer) and all(a >= b for a, b in zip(outer, padded))


def bridge_partitions(
    B: tuple[int, int], weights: tuple[int, ...]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    tails = tuple(sum(weights[index:]) for index in range(len(weights)))
    R = (tails[0] + B[0], tails[0] + B[1], tails[0]) + tails[1:]
    S = (tails[0], tails[0]) + tails[1:]
    return R, S


def skew_cells(outer: tuple[int, ...], inner: tuple[int, ...]) -> list[tuple[int, int]]:
    padded = inner + (0,) * (len(outer) - len(inner))
    return [
        (row, column)
        for row, length in enumerate(outer)
        for column in range(padded[row] + 1, length + 1)
    ]


def tableau_count(
    outer: tuple[int, ...],
    inner: tuple[int, ...],
    content: tuple[int, ...],
    lattice_word: bool,
) -> int:
    """Small independent SSYT/LR enumerator in row-reading order."""
    cells = set(skew_cells(outer, inner))
    order = sorted(cells, key=lambda cell: (cell[0], -cell[1]))
    remaining = list(content)
    prefix = [0] * len(content)
    filling: dict[tuple[int, int], int] = {}

    def recurse(position: int) -> int:
        if position == len(order):
            return int(all(value == 0 for value in remaining))
        row, column = order[position]
        total = 0
        for letter in range(1, len(content) + 1):
            index = letter - 1
            if remaining[index] == 0:
                continue
            right = filling.get((row, column + 1))
            above = filling.get((row - 1, column))
            if right is not None and letter > right:
                continue
            if above is not None and letter <= above:
                continue
            remaining[index] -= 1
            prefix[index] += 1
            if not lattice_word or all(
                prefix[q] >= prefix[q + 1] for q in range(len(prefix) - 1)
            ):
                filling[(row, column)] = letter
                total += recurse(position + 1)
                del filling[(row, column)]
            prefix[index] -= 1
            remaining[index] += 1
        return total

    return recurse(0)


def transportation_count_two_columns(rows: tuple[int, int, int], unit: int) -> int:
    """Margins rows and (sum(rows)-unit,unit)."""
    return sum(
        1
        for x in range(unit + 1)
        for y in range(unit - x + 1)
        if unit - x - y <= rows[2] and x <= rows[0] and y <= rows[1]
    )


def matrix_rank(matrix: list[list[int]]) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    columns = len(rows[0])
    for column in range(columns):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for r in range(len(rows)):
            if r == rank or not rows[r][column]:
                continue
            scale = rows[r][column]
            rows[r] = [a - scale * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
    return rank


def transportation_constraint_rank(k: int) -> tuple[int, int]:
    columns = k + 1
    variable_count = 3 * columns
    matrix: list[list[int]] = []
    for row in range(3):
        matrix.append(
            [int(variable // columns == row) for variable in range(variable_count)]
        )
    for column in range(columns):
        matrix.append(
            [int(variable % columns == column) for variable in range(variable_count)]
        )
    return matrix_rank(matrix), variable_count


def main() -> None:
    # Generalized-binomial simple roots and negative-top continuation.
    generalized_checks = 0
    for slope, constant, bottom in ((3, 0, 4), (-2, 2, 5), (5, -3, 4), (2, -1, 1)):
        value, derivative = binomial_jet(slope, constant, bottom)
        if 0 <= constant < bottom:
            expected = Fraction(
                slope * (-1) ** (bottom - 1 - constant),
                bottom * math.comb(bottom - 1, constant),
            )
            assert value == 0 and derivative == expected
        else:
            expected = value * sum(
                (Fraction(slope, constant - q) for q in range(bottom)),
                Fraction(0),
            )
            assert derivative == expected
        generalized_checks += 1

    # One exact point in each chamber, including P=Q.
    chamber_points = (
        (5, 9, 2, 4, 3, "P<Q"),
        (6, 6, 2, 3, 2, "P=Q"),
        (8, 3, 3, 2, 4, "Q<P"),
    )
    for P, Q, alpha, gamma, delta, _label in chamber_points:
        assert partial_fraction_K(P, Q, alpha, gamma, delta) == direct_K(
            P, Q, alpha, gamma, delta
        )

    # k=4, caps (1,1): surviving numerator terms encounter P<Q, P=Q, Q<P.
    k = 4
    r1 = r2 = 1
    b = k - r1 - r2
    numerator_records: list[dict[str, object]] = []
    pair_linear = Fraction(0)
    for j in range(b):
        for i in range(k - r2 - j):
            alpha = i + j + 1
            gamma = k + 1 - i
            delta = k - j
            p_slope, p_constant = b - j, -2 - 2 * j
            q_slope, q_constant = k - r2 - i - j, -1 - i - j
            if p_slope < q_slope:
                chamber = "P<Q"
                p_le_q = True
            elif p_slope > q_slope:
                chamber = "Q<P"
                p_le_q = False
            elif p_constant <= q_constant:
                chamber = "P=Q" if p_constant == q_constant else "P<Q"
                p_le_q = True
            else:
                chamber = "Q<P"
                p_le_q = False

            start = 1
            while True:
                P = p_slope * start + p_constant
                Q = q_slope * start + q_constant
                relation_ok = P <= Q if p_le_q else Q < P
                if min(P, Q) >= 0 and relation_ok:
                    break
                start += 1
            nodes = list(range(start, start + 2 * k + 1))
            values = [
                direct_K(
                    p_slope * n + p_constant,
                    q_slope * n + q_constant,
                    alpha,
                    gamma,
                    delta,
                )
                for n in nodes
            ]
            raw_derivative = derivative_from_values(nodes, values)
            partial_fraction_derivative = partial_fraction_K_linear(
                p_slope,
                p_constant,
                q_slope,
                q_constant,
                alpha,
                gamma,
                delta,
                p_le_q,
            )
            assert raw_derivative == partial_fraction_derivative
            multiplier = Fraction(
                (-1) ** i * math.factorial(k),
                math.factorial(i)
                * math.factorial(j)
                * math.factorial(k - i - j),
            )
            contribution = multiplier * raw_derivative
            expected = (
                -Fraction(b - j, 2 * (k - j)) if i == 0 else Fraction(0)
            )
            assert contribution == expected
            pair_linear += contribution
            numerator_records.append(
                {
                    "i": i,
                    "j": j,
                    "chamber": chamber,
                    "contribution": str(contribution),
                }
            )
    assert {record["chamber"] for record in numerator_records} == {
        "P<Q",
        "P=Q",
        "Q<P",
    }
    assert pair_linear == -F(k, r1 + r2) == Fraction(-5, 12)

    # Minimal full-polynomial calibration, with two dilations held out.
    rows = (1, 1, 3)
    degree = 2 * k
    states = [distribution(k, n) for n in range(degree + 3)]
    full_values = [projected_count(rows, k, n, states[n]) for n in range(degree + 3)]
    single_values = [single_count(1, n, states[n]) for n in range(degree + 3)]
    pair_values = [pair_count(1, 1, n, states[n]) for n in range(degree + 3)]
    full_firsts = first_differences(full_values[: degree + 1])
    single_firsts = first_differences(single_values[: degree + 1])
    pair_firsts = first_differences(pair_values[: degree + 1])
    assert full_firsts[-1] != 0
    assert newton_linear(full_firsts) == predicted_linear(rows, k) == Fraction(85, 24)
    assert newton_linear(single_firsts) == F(k, 1) == Fraction(23, 24)
    assert newton_linear(pair_firsts) == pair_linear
    for n in (degree + 1, degree + 2):
        assert newton_value(full_firsts, n) == full_values[n]
        assert newton_value(single_firsts, n) == single_values[n]
        assert newton_value(pair_firsts, n) == pair_values[n]

    # The submitted strict step fails here, while the repaired theorem is exact.
    edge_rows = (2, 5, 7)
    assert predicted_linear(edge_rows, 1) == Fraction(3, 2)
    edge_h = sum(edge_rows) - 1
    edge_S = sum(
        max(1 - row, 0) + max(row - edge_h, 0) for row in edge_rows
    )
    assert edge_S == 0

    # Dimension and homogeneous bridge at a genuinely scaled n=2 instance.
    rank, variable_count = transportation_constraint_rank(k)
    assert rank == k + 3 and variable_count - rank == 2 * k

    bridge_rows = (1, 1, 1)
    bridge_k = 1
    N = sum(bridge_rows)
    A = (N, bridge_rows[1] + bridge_rows[2], bridge_rows[2])
    B = (bridge_rows[1] + bridge_rows[2], bridge_rows[2])
    weights = (N - bridge_k,) + (1,) * bridge_k
    R, S = bridge_partitions(B, weights)
    assert is_partition(A) and is_partition(B) and is_partition(weights)
    assert is_partition(R) and is_partition(S)
    assert contains(A, B) and contains(R, S)
    assert sum(A) - sum(B) == sum(weights)
    assert sum(R) == sum(A) + sum(S)
    A_cells = skew_cells(A, B)
    assert [sum(row == q for row, _ in A_cells) for q in range(3)] == list(bridge_rows)
    assert len({column for _, column in A_cells}) == len(A_cells)

    bridge_replays: list[dict[str, int]] = []
    for dilation in (0, 1, 2):
        if dilation == 0:
            transport = kostka = lr = 1
        else:
            nA = tuple(dilation * value for value in A)
            nB = tuple(dilation * value for value in B)
            nw = tuple(dilation * value for value in weights)
            nR = tuple(dilation * value for value in R)
            nS = tuple(dilation * value for value in S)
            rebuilt_R, rebuilt_S = bridge_partitions(nB, nw)
            assert rebuilt_R == nR and rebuilt_S == nS
            transport = transportation_count_two_columns(
                tuple(dilation * value for value in bridge_rows), dilation
            )
            kostka = tableau_count(nA, nB, nw, False)
            lr = tableau_count(nR, nS, nA, True)
        assert transport == kostka == lr
        bridge_replays.append(
            {
                "dilation": dilation,
                "transport": transport,
                "skew_kostka": kostka,
                "lr": lr,
            }
        )

    payload = {
        "verdict": "CONFIRMS_THEOREM_WITH_STRICT_STEP_REPAIR",
        "generalized_binomial_checks": generalized_checks,
        "coefficient_chambers": [point[-1] for point in chamber_points],
        "numerator_records": numerator_records,
        "pair_linear_caps_1_1_k4": str(pair_linear),
        "full_rows": list(rows),
        "full_k": k,
        "full_degree": degree,
        "full_linear": str(newton_linear(full_firsts)),
        "held_out_dilations": [degree + 1, degree + 2],
        "edge_k1_rows": list(edge_rows),
        "edge_linear": str(predicted_linear(edge_rows, 1)),
        "dimension": variable_count - rank,
        "bridge_replays": bridge_replays,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    print("PASS")
    print("verdict=CONFIRMS_THEOREM_WITH_STRICT_STEP_REPAIR")
    print(f"pair_linear_caps_1_1_k4={pair_linear}")
    print(f"full_linear_rows_1_1_3_k4={newton_linear(full_firsts)}")
    print(f"chambers={','.join(point[-1] for point in chamber_points)}")
    print(f"edge_k1_linear={predicted_linear(edge_rows, 1)}")
    print(f"dimension_k4={variable_count - rank}")
    print(f"bridge_replays={bridge_replays}")
    print(f"payload_sha256={digest}")


if __name__ == "__main__":
    main()
