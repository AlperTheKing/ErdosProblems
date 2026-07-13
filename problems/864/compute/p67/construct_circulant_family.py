"""Construct the explicit cyclic two-column obstruction for every q >= 3.

Labels are coefficient vectors in the equal-block-sum quotient.  Evaluation
in base R=4q+2 is a Freiman 2-isomorphism because every coefficient in a
difference of two pair sums has absolute value at most 4q < R-1.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path


OUT = Path(__file__).with_name("circulant_family_results.json")


Vector = tuple[int, ...]


def unit(dim: int, index: int, coefficient: int = 1) -> list[int]:
    vector = [0] * dim
    vector[index] = coefficient
    return vector


def add(*vectors: list[int]) -> list[int]:
    return [sum(entries) for entries in zip(*vectors)]


def scale(coefficient: int, vector: list[int]) -> list[int]:
    return [coefficient * entry for entry in vector]


def evaluate(vector: Vector, base: int) -> int:
    return sum(coefficient * base**index for index, coefficient in enumerate(vector))


def pair_sums(values: tuple[int, ...]) -> set[int]:
    return {a + b for i, a in enumerate(values) for b in values[i:]}


def differences(values: tuple[int, ...]) -> set[int]:
    return {b - a for i, a in enumerate(values) for b in values[i + 1 :]}


def blocks_at(values: tuple[int, ...], target: int, cutoff: int) -> tuple[tuple[int, ...], ...]:
    low = tuple(value for value in values if value <= cutoff)
    return tuple(
        triple
        for triple in combinations_with_replacement(low, 3)
        if sum(triple) == target and len(set(triple)) in (1, 3)
    )


def construct(q: int, enumerate_fibers: bool = True) -> dict[str, object]:
    if q < 3:
        raise ValueError("q must be at least 3")
    # Coordinates are X, B, D, C_0, ..., C_{q-1}.
    dim = q + 3
    X = unit(dim, 0)
    B = unit(dim, 1)
    D = unit(dim, 2)
    C = [unit(dim, 3 + i) for i in range(q)]
    U = add(C[q - 1], C[0])

    c_vectors = [tuple(vector) for vector in C]
    b_vectors: list[Vector] = [tuple(B)]
    a_vectors: dict[int, Vector] = {}
    for j in range(1, q):
        b_j = add(B, U, scale(-1, C[j - 1]), scale(-1, C[j]), scale(-j, D))
        a_j = add(X, scale(-1, B), scale(-1, U), C[j - 1], scale(j, D))
        b_vectors.append(tuple(b_j))
        a_vectors[j] = tuple(a_j)
    left_private_vector = tuple(add(X, scale(-1, B), scale(-1, C[0])))
    right_private_vector = tuple(add(list(left_private_vector), scale(q, D)))

    named_vectors: dict[str, Vector] = {}
    for i, vector in enumerate(c_vectors):
        named_vectors[f"c{i}"] = vector
    for i, vector in enumerate(b_vectors):
        named_vectors[f"b{i}"] = vector
    for i, vector in a_vectors.items():
        named_vectors[f"a{i}"] = vector
    named_vectors["ell"] = left_private_vector
    named_vectors["rho"] = right_private_vector
    assert len(named_vectors) == 3 * q + 1

    # Verify the formal Sidon assertion before projection.
    vector_pair_sums: dict[Vector, tuple[str, str]] = {}
    names = list(named_vectors)
    for i, left_name in enumerate(names):
        for right_name in names[i:]:
            signature = tuple(
                a + b
                for a, b in zip(named_vectors[left_name], named_vectors[right_name])
            )
            assert signature not in vector_pair_sums, (
                q,
                vector_pair_sums.get(signature),
                (left_name, right_name),
            )
            vector_pair_sums[signature] = (left_name, right_name)

    base = 4 * q + 2
    raw = {name: evaluate(vector, base) for name, vector in named_vectors.items()}
    shift = -min(raw.values())
    labels = {name: value + shift for name, value in raw.items()}
    core_values = tuple(sorted(labels.values()))
    assert len(core_values) == len(set(core_values)) == 3 * q + 1
    assert len(pair_sums(core_values)) == (3 * q + 1) * (3 * q + 2) // 2

    left_blocks = [(labels["b0"], labels["c0"], labels["ell"])]
    left_blocks.extend(
        (labels[f"a{i}"], labels[f"b{i}"], labels[f"c{i}"])
        for i in range(1, q)
    )
    right_blocks = [
        (labels[f"b{q - 1}"], labels[f"c{q - 2}"], labels["rho"])
    ]
    right_blocks.extend(
        (
            labels[f"a{j}"],
            labels[f"b{j - 1}"],
            labels[f"c{(j - 2) % q}"],
        )
        for j in range(1, q)
    )
    x_values = {sum(block) for block in left_blocks}
    y_values = {sum(block) for block in right_blocks}
    assert len(x_values) == len(y_values) == 1
    x, y = next(iter(x_values)), next(iter(y_values))
    assert x != y

    core_maximum = max(core_values)
    gap = core_maximum + 1
    cutoff = 3 * core_maximum + 1
    endpoint = 4 * core_maximum + 2
    values = tuple(sorted((*core_values, endpoint)))
    assert len(pair_sums(values)) == len(values) * (len(values) + 1) // 2
    assert differences(values).isdisjoint({gap + s for s in pair_sums(values)})
    assert endpoint - gap == cutoff
    assert max(x, y) <= cutoff < endpoint

    left_support = set().union(*(set(block) for block in left_blocks))
    right_support = set().union(*(set(block) for block in right_blocks))
    assert len(left_support) == len(right_support) == 3 * q
    assert len(left_support & right_support) == 3 * q - 1
    if enumerate_fibers:
        assert set(blocks_at(values, x, cutoff)) == {
            tuple(sorted(block)) for block in left_blocks
        }
        assert set(blocks_at(values, y, cutoff)) == {
            tuple(sorted(block)) for block in right_blocks
        }

    return {
        "q": q,
        "base": base,
        "p": len(values),
        "core_labels": len(core_values),
        "W": endpoint,
        "G": gap,
        "K": cutoff,
        "x": x,
        "y": y,
        "left_blocks": q,
        "right_blocks": q,
        "left_support": 3 * q,
        "right_support": 3 * q,
        "intersection": 3 * q - 1,
        "block_count_sum": 2 * q,
        "intersection_excess": q - 1,
        "pair_sum_count": len(pair_sums(values)),
        "positive_difference_count": len(differences(values)),
        "cross_intersection_size": len(
            differences(values).intersection({gap + s for s in pair_sums(values)})
        ),
        "fiber_enumeration_checked": enumerate_fibers,
        "labels": list(values) if q <= 4 else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-q", type=int, default=20)
    parser.add_argument("--fiber-max-q", type=int, default=12)
    args = parser.parse_args()
    rows = [
        construct(q, enumerate_fibers=q <= args.fiber_max_q)
        for q in range(3, args.max_q + 1)
    ]
    payload = {
        "exact_arithmetic": "integers",
        "construction": "cyclic equal-block-sum quotient, mixed-radix projection",
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
