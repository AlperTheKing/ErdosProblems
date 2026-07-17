#!/usr/bin/env python3
"""Independent CaDiCaL replay of fixed-circuit active-scope infeasibility."""

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


def add_and(cnf, pool, terms, name):
    out = pool.id(name)
    for term in terms:
        cnf.append([-out, term])
    cnf.append([out] + [-term for term in terms])
    return out


def add_or_equiv(cnf, pool, terms, name):
    out = pool.id(name)
    for term in terms:
        cnf.append([-term, out])
    cnf.append([-out] + list(terms))
    return out


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
    vertex_count = source["left"] + source["right"]
    neighbours = sorted(v for edge in support_edges for v in edge if owner in edge and v != owner)

    pool = IDPool()
    cnf = CNF()
    row_vars = {}
    for i, atom in enumerate(atoms):
        variables = [pool.id(("row", i, j)) for j in range(len(atom["rows"]))]
        row_vars[i] = variables
        cnf.extend(
            CardEnc.equals(
                variables,
                bound=1,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    def rows_where(predicate):
        return [
            row_vars[i][j]
            for i, atom in enumerate(atoms)
            for j, row in enumerate(atom["rows"])
            if predicate(tuple(row))
        ]

    cnf.extend(
        CardEnc.equals(
            rows_where(lambda row: owner in row),
            bound=5,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )

    active_owner_edge = norm(owner, active)
    for variable in rows_where(
        lambda row: active_owner_edge
        in {norm(row[k], row[k + 1]) for k in range(4)}
    ):
        cnf.append([-variable])
    for neighbour in neighbours:
        if neighbour == active:
            continue
        edge = norm(owner, neighbour)
        cnf.append(
            rows_where(
                lambda row, e=edge: e
                in {norm(row[k], row[k + 1]) for k in range(4)}
            )
        )
        cnf.append(rows_where(lambda row, y=neighbour: active in row and y in row))
    cnf.append(rows_where(lambda row: active in row))

    active_edge = {}
    for edge in support_edges:
        variable = pool.id(("active", edge))
        uses = rows_where(
            lambda row, e=edge: e
            in {norm(row[k], row[k + 1]) for k in range(4)}
        )
        for use in uses:
            cnf.append([-variable, -use])
        cnf.append([variable] + uses)
        active_edge[edge] = variable

    reach = {(0, v): pool.id(("reach", 0, v)) for v in range(vertex_count)}
    for v in range(vertex_count):
        cnf.append([reach[0, v] if v == owner else -reach[0, v]])
    adjacency = {v: [] for v in range(vertex_count)}
    for edge in support_edges:
        u, v = edge
        adjacency[u].append((v, active_edge[edge]))
        adjacency[v].append((u, active_edge[edge]))

    for depth in range(vertex_count - 1):
        for v in range(vertex_count):
            terms = [reach[depth, v]]
            for u, edge_var in adjacency[v]:
                terms.append(
                    add_and(
                        cnf,
                        pool,
                        [reach[depth, u], edge_var],
                        ("step", depth, u, v),
                    )
                )
            reach[depth + 1, v] = add_or_equiv(
                cnf, pool, terms, ("reach", depth + 1, v)
            )

    final_depth = vertex_count - 1
    scope_terms = []
    for i, atom in enumerate(atoms):
        scope_terms.append(
            add_and(
                cnf,
                pool,
                [reach[final_depth, atom["u"]], reach[final_depth, atom["v"]]],
                ("scope", i),
            )
        )
    cnf.append(scope_terms)

    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
        satisfiable = solver.solve()
    assert not satisfiable
    result = {
        "schema": "t5-active-scope-cadical-replay-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "solver": "CaDiCaL195",
        "satisfiable": satisfiable,
        "verdict": "PASS_FIXED_CIRCUIT_ACTIVE_SCOPE_UNSAT",
    }
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
