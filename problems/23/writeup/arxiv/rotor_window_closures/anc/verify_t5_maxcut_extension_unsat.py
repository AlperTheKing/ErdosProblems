#!/usr/bin/env python3
"""Independent exact SAT replay of the t=5 ambient-extension rejection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def canonical_sha_without_marker(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonicalSha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("extension", type=Path)
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    extension = json.loads(args.extension.read_text(encoding="utf-8"))
    if canonical_sha_without_marker(source) != source["canonicalSha256"]:
        raise SystemExit("source hash mismatch")
    if canonical_sha_without_marker(extension) != extension["canonicalSha256"]:
        raise SystemExit("extension hash mismatch")
    if not extension["allowExistingExtraBlue"]:
        raise SystemExit("independent replay requires the unrestricted blue-edge domain")

    hit = source["hit"]
    fixed_blue = {norm(*edge) for edge in hit["supportEdges"]}
    bad_edges = {norm(atom["u"], atom["v"]) for atom in hit["selectedAtoms"]}
    footprints = {
        norm(atom["u"], atom["v"]): {norm(*edge) for edge in atom["footprintEdges"]}
        for atom in hit["selectedAtoms"]
    }
    existing_left = set(range(source["left"]))
    existing_right = set(range(source["left"], source["left"] + source["right"]))
    all_new = list(range(18, 25))

    replay_rows = []
    for split in extension["splits"]:
        new_left = set(all_new[: split["newLeft"]])
        new_right = set(all_new[split["newLeft"] :])
        left = existing_left | new_left
        right = existing_right | new_right
        potential = {
            norm(u, v)
            for u in left
            for v in right
            if norm(u, v) not in fixed_blue
        }
        pool = IDPool()
        var = {edge: pool.id(("edge", edge)) for edge in sorted(potential)}
        cnf = CNF()

        def edge_value(u: int, v: int):
            edge = norm(u, v)
            if edge in fixed_blue:
                return True
            if edge in potential:
                return var[edge]
            return False

        # Exact mixed-triangle exclusions.
        for u, v in bad_edges:
            opposite = right if u in left else left
            for z in opposite:
                a = edge_value(u, z)
                b = edge_value(v, z)
                if a is True and b is True:
                    raise AssertionError("fixed support already forms a triangle")
                if a is True and isinstance(b, int):
                    cnf.append([-b])
                elif b is True and isinstance(a, int):
                    cnf.append([-a])
                elif isinstance(a, int) and isinstance(b, int):
                    cnf.append([-a, -b])

        # Every emitted path clause is independently checked to forbid a real
        # new length-four row of one selected bad atom.
        for witness in split["pathCuts"]:
            bad = norm(*witness["badEdge"])
            if bad not in bad_edges:
                raise AssertionError("path witness uses an unselected bad edge")
            path_edges = [norm(*edge) for edge in witness["pathEdges"]]
            variable_edges = [norm(*edge) for edge in witness["variableEdges"]]
            path_graph = nx.Graph()
            path_graph.add_edges_from(path_edges)
            if path_graph.number_of_edges() != 4 or path_graph.number_of_nodes() != 5:
                raise AssertionError("path witness is not a simple four-edge path")
            endpoints = {v for v, degree in path_graph.degree() if degree == 1}
            if endpoints != set(bad):
                raise AssertionError("path witness endpoints do not match its bad edge")
            if any(edge not in fixed_blue | potential for edge in path_edges):
                raise AssertionError("path witness uses a non-blue-domain edge")
            if set(variable_edges) != {edge for edge in path_edges if edge not in fixed_blue}:
                raise AssertionError("path witness variable-edge projection is wrong")
            if set(path_edges) <= footprints[bad]:
                raise AssertionError("path witness was already in the original footprint")
            cnf.append([-var[edge] for edge in variable_edges])

        separator_requirements = []
        for separator in split["separators"]:
            switch = set(separator["switch"])
            fixed_cross = sum((u in switch) ^ (v in switch) for u, v in fixed_blue)
            bad_cross = sum((u in switch) ^ (v in switch) for u, v in bad_edges)
            crossing_vars = [
                var[edge]
                for edge in sorted(potential)
                if (edge[0] in switch) ^ (edge[1] in switch)
            ]
            required = bad_cross - fixed_cross
            assert fixed_cross == separator["fixedBlueCross"]
            assert bad_cross == separator["badCross"]
            assert required == separator["requiredVariableBlueCross"]
            separator_requirements.append(required)
            cnf.extend(
                CardEnc.atleast(
                    lits=crossing_vars,
                    bound=required,
                    vpool=pool,
                    encoding=EncType.totalizer,
                ).clauses
            )

        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
            satisfiable = solver.solve()
        if satisfiable:
            raise AssertionError("independent SAT replay found an extension")
        replay_rows.append(
            {
                "newLeft": split["newLeft"],
                "newRight": split["newRight"],
                "variables": len(potential),
                "pathClauses": len(split["pathCuts"]),
                "separatorCount": len(split["separators"]),
                "requiredCross": separator_requirements,
                "cnfVariables": pool.top,
                "cnfClauses": len(cnf.clauses),
                "verdict": "UNSAT",
            }
        )

    verification = {
        "schema": "rooted-t5-ambient-extension-independent-sat-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "extensionCanonicalSha256": extension["canonicalSha256"],
        "splits": replay_rows,
        "verdict": "PASS_ALL_EIGHT_SPLITS_UNSAT",
    }
    raw = json.dumps(verification, sort_keys=True, separators=(",", ":")).encode("ascii")
    verification["canonicalSha256"] = hashlib.sha256(raw).hexdigest()
    output = args.extension.with_name(args.extension.stem + "_verification.json")
    output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
