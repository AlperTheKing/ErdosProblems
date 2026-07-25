#!/usr/bin/env python3
"""Check SMS symmetry witnesses and make a static augmented DIMACS instance.

The current SMS executable writes JSON records of the form
    [[signed edge triples], [witness permutation]]
where a signed triple is [sign, u, v].  This script checks the same
lexicographic witness condition as the bundled sym_clause_checker.py, but
accepts the JSON format emitted by the current C++ implementation.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path


def edge_var(n: int, u: int, v: int) -> int:
    if not 0 <= u < n or not 0 <= v < n or u == v:
        raise ValueError(f"invalid edge ({u},{v})")
    if u > v:
        u, v = v, u
    # Row-major combinations: (0,1),...,(0,n-1),(1,2),...
    return 1 + u * (2 * n - u - 1) // 2 + (v - u - 1)


def normalized_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def check_witness(
    n: int, triples: list[list[int]], permutation: list[int]
) -> list[int]:
    if sorted(permutation) != list(range(n)):
        raise ValueError(f"not a permutation: {permutation}")
    if len(triples) < 2:
        raise ValueError("a symmetry clause must have at least two literals")

    signed_edges: list[tuple[int, tuple[int, int]]] = []
    for triple in triples:
        if len(triple) != 3:
            raise ValueError(f"invalid signed edge triple: {triple}")
        sign, u, v = map(int, triple)
        if sign not in (-1, 1):
            raise ValueError(f"invalid sign: {sign}")
        signed_edges.append((sign, normalized_edge(u, v)))

    remaining = signed_edges[:]
    witnessed = False
    for i, j in combinations(range(n), 2):
        mapped = normalized_edge(permutation[i], permutation[j])
        if (i, j) == mapped:
            continue

        if len(remaining) == 2:
            if remaining[0] != (-1, (i, j)):
                raise ValueError(
                    f"terminal source mismatch: {remaining[0]} vs {-1, (i, j)}"
                )
            if remaining[1] != (1, mapped):
                raise ValueError(
                    f"terminal image mismatch: {remaining[1]} vs {1, mapped}"
                )
            remaining.clear()
            witnessed = True
            break

        if not remaining:
            raise ValueError("clause exhausted before a strict comparison")
        sign, edge = remaining.pop(0)
        expected = (i, j) if sign == -1 else mapped
        if edge != expected:
            raise ValueError(
                f"prefix mismatch at ({i},{j}): literal {(sign, edge)}, "
                f"expected edge {expected}"
            )

    if not witnessed or remaining:
        raise ValueError("witness does not end in a strict lexicographic comparison")

    return [sign * edge_var(n, u, v) for sign, (u, v) in signed_edges]


def parse_dimacs(path: Path) -> tuple[int, list[list[int]], list[str]]:
    comments: list[str] = []
    tokens: list[int] = []
    declared_vars = None
    declared_clauses = None
    for raw in path.read_text(encoding="ascii").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("c"):
            comments.append(raw)
            continue
        if line.startswith("p"):
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError(f"invalid DIMACS header: {raw}")
            declared_vars, declared_clauses = map(int, parts[2:])
            continue
        tokens.extend(map(int, line.split()))
    if declared_vars is None or declared_clauses is None:
        raise ValueError("missing DIMACS header")

    clauses: list[list[int]] = []
    clause: list[int] = []
    for token in tokens:
        if token == 0:
            clauses.append(clause)
            clause = []
        else:
            if abs(token) > declared_vars:
                raise ValueError(f"literal {token} exceeds declared variable count")
            clause.append(token)
    if clause:
        raise ValueError("unterminated DIMACS clause")
    if len(clauses) != declared_clauses:
        raise ValueError(
            f"header declares {declared_clauses} clauses, parsed {len(clauses)}"
        )
    return declared_vars, clauses, comments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertices", type=int, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--sym-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.sym_json.read_text(encoding="utf-8"))
    records = payload.get("sym_clauses")
    if not isinstance(records, list):
        raise ValueError("JSON has no sym_clauses list")

    static_clauses: list[list[int]] = []
    for index, record in enumerate(records):
        if not isinstance(record, list) or len(record) != 2:
            raise ValueError(f"invalid record {index}: {record}")
        triples, permutation = record
        try:
            static_clauses.append(
                check_witness(args.vertices, triples, permutation)
            )
        except ValueError as exc:
            raise ValueError(f"record {index}: {exc}") from exc

    nvars, clauses, comments = parse_dimacs(args.cnf)
    all_clauses = clauses + static_clauses
    with args.output.open("w", encoding="ascii", newline="\n") as out:
        for comment in comments:
            print(comment, file=out)
        print(f"p cnf {nvars} {len(all_clauses)}", file=out)
        for clause in all_clauses:
            print(*clause, 0, file=out)

    print(
        f"VERIFIED records={len(static_clauses)} "
        f"original_clauses={len(clauses)} augmented_clauses={len(all_clauses)}"
    )


if __name__ == "__main__":
    main()
