#!/usr/bin/env python3
"""Decode a CaDiCaL witness for the frozen cycle-19 CNF to verifier JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Sequence


EDGE_NAME = re.compile(r"edge\((\d+),(\d+)\)\Z")


def parse_solution(path: Path) -> dict[int, bool]:
    status: str | None = None
    assignment: dict[int, bool] = {}
    saw_model_line = False
    for line_number, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        fields = line.split()
        if fields[0] == "s":
            if len(fields) != 2 or status is not None:
                raise ValueError(f"invalid status line {line_number}: {raw!r}")
            status = fields[1]
            continue
        if fields[0] != "v":
            raise ValueError(f"unexpected solution line {line_number}: {raw!r}")
        saw_model_line = True
        for token in fields[1:]:
            literal = int(token)
            if literal == 0:
                continue
            variable = abs(literal)
            value = literal > 0
            if variable in assignment and assignment[variable] != value:
                raise ValueError(f"conflicting assignments for variable {variable}")
            assignment[variable] = value
    if status != "SATISFIABLE":
        raise ValueError(f"solution status is {status!r}, expected 'SATISFIABLE'")
    if not saw_model_line:
        raise ValueError("SAT solution has no model line")
    return assignment


def decode(manifest: dict[str, object], assignment: dict[int, bool]) -> dict[str, object]:
    if manifest.get("schema") != "ssnc-fixed-cycle19-cnf-v1":
        raise ValueError("unexpected manifest schema")
    n = manifest.get("n")
    if type(n) is not int or n != 19:
        raise ValueError(f"unexpected order: {n!r}")
    variable_map = manifest.get("variable_map")
    if not isinstance(variable_map, dict):
        raise ValueError("manifest variable_map is not an object")

    adjacency = [[False] * n for _ in range(n)]
    seen_edges: set[tuple[int, int]] = set()
    for identifier, name in variable_map.items():
        if not isinstance(identifier, str) or not isinstance(name, str):
            raise ValueError("invalid variable_map entry")
        match = EDGE_NAME.fullmatch(name)
        if match is None:
            continue
        variable = int(identifier)
        if variable not in assignment:
            raise ValueError(f"orientation variable {variable} is unassigned")
        a, b = map(int, match.groups())
        if not (0 <= a < b < n) or (a, b) in seen_edges:
            raise ValueError(f"invalid or duplicate edge name: {name}")
        seen_edges.add((a, b))
        tail, head = (a, b) if assignment[variable] else (b, a)
        adjacency[tail][head] = True

    missing_raw = manifest.get("missing_edges")
    if not isinstance(missing_raw, list):
        raise ValueError("manifest missing_edges is not an array")
    missing = {tuple(edge) for edge in missing_raw if isinstance(edge, list)}
    if len(missing) != 19:
        raise ValueError(f"expected 19 missing edges, found {len(missing)}")
    if len(seen_edges) != 152:
        raise ValueError(f"expected 152 orientation variables, found {len(seen_edges)}")

    for a in range(n):
        if adjacency[a][a]:
            raise ValueError(f"decoded loop at {a}")
        for b in range(a + 1, n):
            count = int(adjacency[a][b]) + int(adjacency[b][a])
            expected = 0 if (a, b) in missing else 1
            if count != expected:
                raise ValueError(f"support mismatch at pair {(a, b)}")
    if not adjacency[0][2]:
        raise ValueError("decoded model violates the declared symmetry unit 0->2")

    out_neighbors = [
        [u for u in range(n) if adjacency[v][u]]
        for v in range(n)
    ]
    if any(len(row) != 8 for row in out_neighbors):
        raise ValueError("decoded model violates exact outdegree 8")

    unreachable_columns = [0] * n
    for v in range(n):
        two_step = {
            w
            for u in out_neighbors[v]
            for w in out_neighbors[u]
        }
        unreachable = [
            w
            for w in range(n)
            if w != v and not adjacency[v][w] and w not in two_step
        ]
        if len(unreachable) != 3:
            raise ValueError(
                f"decoded model has {len(unreachable)} unreachable targets at {v}"
            )
        for w in unreachable:
            unreachable_columns[w] += 1
    if unreachable_columns != [3] * n:
        raise ValueError(f"decoded model violates target ledger: {unreachable_columns}")

    return {"n": n, "out_neighbors": out_neighbors}


def canonical_sha256(value: dict[str, object]) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest().upper()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    assignment = parse_solution(args.solution)
    certificate = decode(manifest, assignment)
    data = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    args.output.write_text(data, encoding="ascii")
    print(
        json.dumps(
            {
                "status": "DECODED_UNVERIFIED",
                "output": str(args.output),
                "certificate_sha256": canonical_sha256(certificate),
                "orientation_variables": 152,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
