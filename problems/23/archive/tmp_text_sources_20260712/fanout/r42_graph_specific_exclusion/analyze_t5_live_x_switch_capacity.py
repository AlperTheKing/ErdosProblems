#!/usr/bin/env python3
"""Exact SAT capacity audit for the live-x ambient max-cut obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def canonical_sha(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonicalSha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def exact_max_cardinality(
    clauses: list[list[int]], lits: list[int], top_id: int
) -> tuple[int, dict]:
    """Return max sum(lits), with exact SAT witnesses at k and UNSAT at k+1."""
    low, high = 0, len(lits)
    calls = []
    while low < high:
        mid = (low + high + 1) // 2
        enc = CardEnc.atleast(
            lits=lits, bound=mid, top_id=top_id, encoding=EncType.totalizer
        )
        with Solver(name="cadical195", bootstrap_with=clauses + enc.clauses) as solver:
            sat = solver.solve()
        calls.append({"bound": mid, "sat": sat})
        if sat:
            low = mid
        else:
            high = mid - 1

    enc = CardEnc.atleast(
        lits=lits, bound=low, top_id=top_id, encoding=EncType.totalizer
    )
    with Solver(name="cadical195", bootstrap_with=clauses + enc.clauses) as solver:
        sat_at_max = solver.solve()
    if not sat_at_max:
        raise AssertionError("reported maximum is not feasible")

    if low < len(lits):
        enc = CardEnc.atleast(
            lits=lits, bound=low + 1, top_id=top_id, encoding=EncType.totalizer
        )
        with Solver(name="cadical195", bootstrap_with=clauses + enc.clauses) as solver:
            sat_above = solver.solve()
        if sat_above:
            raise AssertionError("reported maximum is not maximal")
    else:
        sat_above = False

    return low, {
        "binarySearchCalls": calls,
        "satAtMaximum": sat_at_max,
        "satAboveMaximum": sat_above,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("extension", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    extension = json.loads(args.extension.read_text(encoding="utf-8"))
    if canonical_sha(source) != source["canonicalSha256"]:
        raise SystemExit("source hash mismatch")
    if canonical_sha(extension) != extension["canonicalSha256"]:
        raise SystemExit("extension hash mismatch")
    if not extension["allowExistingExtraBlue"]:
        raise SystemExit("capacity audit requires unrestricted blue-edge domain")

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

    rows = []
    for split in extension["splits"]:
        new_left = set(all_new[: split["newLeft"]])
        new_right = set(all_new[split["newLeft"] :])
        left = existing_left | new_left
        right = existing_right | new_right
        potential = sorted(
            norm(u, v)
            for u in left
            for v in right
            if norm(u, v) not in fixed_blue
        )
        var = {edge: index + 1 for index, edge in enumerate(potential)}
        clauses: list[list[int]] = []

        def edge_value(u: int, v: int):
            edge = norm(u, v)
            if edge in fixed_blue:
                return True
            if edge in var:
                return var[edge]
            return False

        for u, v in bad_edges:
            opposite = right if u in left else left
            for z in opposite:
                a = edge_value(u, z)
                b = edge_value(v, z)
                if a is True and b is True:
                    raise AssertionError("fixed support already forms a triangle")
                if a is True and isinstance(b, int):
                    clauses.append([-b])
                elif b is True and isinstance(a, int):
                    clauses.append([-a])
                elif isinstance(a, int) and isinstance(b, int):
                    clauses.append([-a, -b])

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
            if set(variable_edges) != {edge for edge in path_edges if edge not in fixed_blue}:
                raise AssertionError("path witness variable projection is wrong")
            if set(path_edges) <= footprints[bad]:
                raise AssertionError("path witness was already in the original footprint")
            clauses.append([-var[edge] for edge in variable_edges])

        separator_lits = []
        separator_rows = []
        for separator in split["separators"]:
            switch = set(separator["switch"])
            fixed_cross = sum((u in switch) ^ (v in switch) for u, v in fixed_blue)
            bad_cross = sum((u in switch) ^ (v in switch) for u, v in bad_edges)
            lits = [
                var[edge]
                for edge in potential
                if (edge[0] in switch) ^ (edge[1] in switch)
            ]
            required = bad_cross - fixed_cross
            if (
                fixed_cross != separator["fixedBlueCross"]
                or bad_cross != separator["badCross"]
                or required != separator["requiredVariableBlueCross"]
            ):
                raise AssertionError("separator arithmetic mismatch")
            maximum, proof = exact_max_cardinality(clauses, lits, len(var))
            separator_lits.append(lits)
            separator_rows.append(
                {
                    "switch": sorted(switch),
                    "fixedBlueCross": fixed_cross,
                    "badCross": bad_cross,
                    "requiredAddedBlueCross": required,
                    "safeCapacity": maximum,
                    "capacityProof": proof,
                }
            )

        joint = None
        if len(separator_lits) > 1:
            # Replace each occurrence by an equivalent fresh literal so a
            # cardinality encoding measures the exact weighted sum.
            joint_clauses = [list(clause) for clause in clauses]
            copies = []
            next_var = len(var)
            for lits in separator_lits:
                for lit in lits:
                    next_var += 1
                    copy = next_var
                    copies.append(copy)
                    joint_clauses.extend([[-copy, lit], [copy, -lit]])
            maximum, proof = exact_max_cardinality(joint_clauses, copies, next_var)
            joint = {
                "requiredSum": sum(
                    item["requiredAddedBlueCross"] for item in separator_rows
                ),
                "safeCapacitySum": maximum,
                "capacityProof": proof,
            }

        rows.append(
            {
                "newLeft": split["newLeft"],
                "newRight": split["newRight"],
                "potentialBlueVariables": len(var),
                "triangleAndPathClauses": len(clauses),
                "separators": separator_rows,
                "jointSeparatorCapacity": joint,
            }
        )

    result = {
        "schema": "rooted-t5-live-x-switch-capacity-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "extensionCanonicalSha256": extension["canonicalSha256"],
        "splits": rows,
    }
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
