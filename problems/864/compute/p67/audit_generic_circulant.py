"""Exact linear-algebra audit of cyclic block cores.

For q blocks on each side, use common cells (i,i), (i,i+1), (i,i+2)
modulo q, delete (0,0), and add one private label on each deficient block.
The quotient by the equal-block-sum equations admits a generic Sidon labeling
iff all diagonal-inclusive pair-sum functionals remain distinct.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path

from sympy import Matrix


OUT = Path(__file__).with_name("generic_circulant_results.json")


def graph_edges(q: int) -> list[tuple[int, int]]:
    edges = sorted({(i, (i + shift) % q) for i in range(q) for shift in (0, 1, 2)})
    edges.remove((0, 0))
    return edges


def audit_q(q: int) -> dict[str, object]:
    edges = graph_edges(q)
    assert len(edges) == 3 * q - 1
    lp, rp = len(edges), len(edges) + 1
    variables = len(edges) + 2

    left_rows: list[list[int]] = []
    right_rows: list[list[int]] = []
    for i in range(q):
        row = [0] * variables
        for k, (u, _) in enumerate(edges):
            if u == i:
                row[k] = 1
        if i == 0:
            row[lp] = 1
        assert sum(row) == 3
        left_rows.append(row)
    for j in range(q):
        row = [0] * variables
        for k, (_, v) in enumerate(edges):
            if v == j:
                row[k] = 1
        if j == 0:
            row[rp] = 1
        assert sum(row) == 3
        right_rows.append(row)

    relations = []
    for i in range(1, q):
        relations.append([a - b for a, b in zip(left_rows[i], left_rows[0])])
    for j in range(1, q):
        relations.append([a - b for a, b in zip(right_rows[j], right_rows[0])])
    matrix = Matrix(relations)
    nullspace = matrix.nullspace()
    assert nullspace

    coordinate_signatures = [
        tuple(vector[index] for vector in nullspace) for index in range(variables)
    ]
    seen: dict[tuple[object, ...], tuple[int, int]] = {}
    duplicate = None
    for i, j in combinations_with_replacement(range(variables), 2):
        signature = tuple(
            coordinate_signatures[i][k] + coordinate_signatures[j][k]
            for k in range(len(nullspace))
        )
        if signature in seen:
            duplicate = {"first": list(seen[signature]), "second": [i, j]}
            break
        seen[signature] = (i, j)

    sum_difference = Matrix([a - b for a, b in zip(right_rows[0], left_rows[0])])
    distinct_column_sums_possible = any(
        (sum_difference.T * vector)[0] != 0 for vector in nullspace
    )
    return {
        "q": q,
        "variables": variables,
        "common_marks": len(edges),
        "relation_rank": matrix.rank(),
        "solution_dimension": len(nullspace),
        "pair_sum_functionals": variables * (variables + 1) // 2,
        "forced_pair_sum_collision": duplicate,
        "generic_sidon_possible": duplicate is None,
        "distinct_column_sums_possible": distinct_column_sums_possible,
        "intersection_excess": (3 * q - 1) - 2 * q,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-q", type=int, default=30)
    args = parser.parse_args()
    rows = [audit_q(q) for q in range(3, args.max_q + 1)]
    payload = {
        "exact_arithmetic": "SymPy rationals",
        "rows": rows,
        "all_generic_sidon": all(row["generic_sidon_possible"] for row in rows),
        "all_distinct_sums": all(
            row["distinct_column_sums_possible"] for row in rows
        ),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
