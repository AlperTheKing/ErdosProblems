#!/usr/bin/env python3
"""Independent SAT replay that every non-owner edge at live x is selected."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def norm(u, v):
    return (u, v) if u < v else (v, u)


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    hit = source["hit"]
    owner = 0
    active = hit["selectionMeta"]["localClassifiers"]["0"]["activeNeighbour"]
    atoms = hit["selectedAtoms"]
    support_edges = sorted(norm(*edge) for edge in hit["supportEdges"])
    owner_neighbours = sorted(
        v for edge in support_edges for v in edge if owner in edge and v != owner
    )
    active_neighbours = sorted(
        v for edge in support_edges for v in edge if active in edge and v != active
    )

    pool = IDPool()
    base = CNF()
    row_vars = {}
    for i, atom in enumerate(atoms):
        variables = [pool.id(("row", i, j)) for j in range(len(atom["rows"]))]
        row_vars[i] = variables
        base.extend(
            CardEnc.equals(
                variables, 1, vpool=pool, encoding=EncType.seqcounter
            ).clauses
        )

    def rows_where(predicate):
        return [
            row_vars[i][j]
            for i, atom in enumerate(atoms)
            for j, row in enumerate(atom["rows"])
            if predicate(tuple(row))
        ]

    base.extend(
        CardEnc.equals(
            rows_where(lambda row: owner in row),
            5,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    owner_active_edge = norm(owner, active)
    for variable in rows_where(
        lambda row: owner_active_edge
        in {norm(row[k], row[k + 1]) for k in range(4)}
    ):
        base.append([-variable])
    for neighbour in owner_neighbours:
        if neighbour == active:
            continue
        edge = norm(owner, neighbour)
        base.append(
            rows_where(
                lambda row, e=edge: e
                in {norm(row[k], row[k + 1]) for k in range(4)}
            )
        )
        base.append(
            rows_where(lambda row, y=neighbour: active in row and y in row)
        )
    base.append(rows_where(lambda row: active in row))

    tests = []
    for neighbour in active_neighbours:
        if neighbour == owner:
            continue
        edge = norm(active, neighbour)
        cnf = CNF(from_clauses=base.clauses)
        uses = rows_where(
            lambda row, e=edge: e
            in {norm(row[k], row[k + 1]) for k in range(4)}
        )
        for variable in uses:
            cnf.append([-variable])
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
            satisfiable = solver.solve()
        assert not satisfiable
        tests.append(
            {
                "edge": list(edge),
                "satisfiableWhenAbsent": satisfiable,
                "variables": pool.top,
                "clauses": len(cnf.clauses),
            }
        )

    result = {
        "schema": "t5-live-tail-blanket-cadical-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "owner": owner,
        "activeNeighbour": active,
        "activeNeighbourhood": active_neighbours,
        "tests": tests,
        "solver": "CaDiCaL195",
        "verdict": "PASS_ALL_NONOWNER_TAIL_EDGES_FORCED_SELECTED",
    }
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
