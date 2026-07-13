#!/usr/bin/env python3
"""Exact relaxed-production obstruction for the first n=17 t=5 supports."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
V, M, A, B = 0, 1, 2, 3


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def distance_four_atoms(graph: nx.Graph, left: int) -> list[dict]:
    atoms = []
    shores = (("L", range(left)), ("R", range(left, graph.number_of_nodes())))
    for shore, vertices_iter in shores:
        vertices = list(vertices_iter)
        for i, u in enumerate(vertices):
            for v in vertices[i + 1 :]:
                if nx.shortest_path_length(graph, u, v) != 4:
                    continue
                rows = sorted(tuple(path) for path in nx.all_shortest_paths(graph, u, v))
                footprint = sorted(
                    {norm(row[k], row[k + 1]) for row in rows for k in range(4)}
                )
                atoms.append(
                    {"shore": shore, "u": u, "v": v, "rows": rows, "footprint": footprint}
                )
    return atoms


def triangle_list(atoms: list[dict], left: int, n: int) -> list[tuple[int, int, int]]:
    index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    out = []
    for tag, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v, w in itertools.combinations(vertices, 3):
            keys = ((tag, u, v), (tag, u, w), (tag, v, w))
            if all(key in index for key in keys):
                out.append(tuple(index[key] for key in keys))
    return out


def add_exact(cnf: CNF, pool: IDPool, lits: list[int], bound: int) -> None:
    clauses = CardEnc.equals(
        lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter
    ).clauses
    cnf.extend(clauses)


def add_atleast(cnf: CNF, pool: IDPool, lits: list[int], bound: int) -> None:
    clauses = CardEnc.atleast(
        lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter
    ).clauses
    cnf.extend(clauses)


def build_cnf(atoms: list[dict], support_edges, triangles):
    cnf = CNF()
    pool = IDPool()
    selected = [pool.id(("atom", i)) for i in range(len(atoms))]
    add_exact(cnf, pool, selected, 25)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    cnf.append([selected[atom_index[("L", A, B)]]])
    for owner in (V, M):
        incident = [
            selected[i]
            for i, atom in enumerate(atoms)
            if owner in (atom["u"], atom["v"])
        ]
        add_exact(cnf, pool, incident, 5)
    for support_edge in support_edges:
        covering = [
            selected[i]
            for i, atom in enumerate(atoms)
            if support_edge in atom["footprint"]
        ]
        add_atleast(cnf, pool, covering, 2)
    for i, j, k in triangles:
        cnf.append([-selected[i], -selected[j], -selected[k]])
    return cnf, pool


def check_subset(chosen, atoms, support_edges, triangles, atom_ab):
    if atom_ab not in chosen:
        return "missing_root_atom", atom_ab
    for owner in (V, M):
        degree = sum(owner in (atoms[i]["u"], atoms[i]["v"]) for i in chosen)
        if degree != 5:
            return "owner_degree", [owner, degree]
    for support_edge in support_edges:
        multiplicity = sum(support_edge in atoms[i]["footprint"] for i in chosen)
        if multiplicity < 2:
            return "support_multiplicity", [list(support_edge), multiplicity]
    selected_triangles = [tri for tri in triangles if set(tri) <= chosen]
    if selected_triangles:
        return "bad_triangle", list(selected_triangles[0])
    return "survivor", None


def atom_key(atom: dict) -> list[object]:
    return [atom["shore"], atom["u"], atom["v"]]


def analyze_support(record: dict) -> dict:
    left, right = record["left"], record["right"]
    graph = nx.Graph()
    graph.add_nodes_from(range(left + right))
    graph.add_edges_from(tuple(edge) for edge in record["supportEdgesGlobal"])
    atoms = distance_four_atoms(graph, left)
    support_edges = sorted(norm(*edge) for edge in graph.edges())
    triangles = triangle_list(atoms, left, left + right)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    atom_ab = atom_index[("L", A, B)]

    counts = Counter()
    examples = {}
    upstream = []
    total = 0
    for chosen_tuple in itertools.combinations(range(len(atoms)), 25):
        total += 1
        chosen = frozenset(chosen_tuple)
        reason, detail = check_subset(chosen, atoms, support_edges, triangles, atom_ab)
        counts[reason] += 1
        examples.setdefault(reason, {"chosen": list(chosen_tuple), "detail": detail})
        if reason in ("bad_triangle", "survivor"):
            upstream.append(chosen)
    if counts["survivor"]:
        raise AssertionError("triangle-free relaxed production selection survived")

    common_selected = sorted(set.intersection(*(set(x) for x in upstream))) if upstream else []
    common_triangles = [tri for tri in triangles if all(set(tri) <= x for x in upstream)]
    frequency = Counter(tri for x in upstream for tri in triangles if set(tri) <= x)

    cnf, pool = build_cnf(atoms, support_edges, triangles)
    cnf_path = HERE / f"triangle_obstruction_l{left}_r{right}.cnf"
    cnf.to_file(str(cnf_path))
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
    if sat:
        raise AssertionError("CNF unexpectedly SAT")

    return {
        "split": [left, right],
        "supportSha256": record["supportSha256"],
        "atomCount": len(atoms),
        "atomKeys": [atom_key(atom) for atom in atoms],
        "supportEdges": [list(edge) for edge in support_edges],
        "candidateSubsets": total,
        "rejectionCountsFirstGate": dict(sorted(counts.items())),
        "upstreamSelections": len(upstream),
        "triangleFreeSurvivors": counts["survivor"],
        "commonSelectedAtoms": [atom_key(atoms[i]) for i in common_selected],
        "commonBadTriangles": [
            [atom_key(atoms[i]) for i in tri] for tri in common_triangles
        ],
        "mostFrequentBadTriangles": [
            {
                "atoms": [atom_key(atoms[i]) for i in tri],
                "frequency": count,
                "allUpstreamSelections": count == len(upstream),
            }
            for tri, count in frequency.most_common(12)
        ],
        "exampleRejections": examples,
        "cnf": {
            "path": cnf_path.name,
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "sha256": sha256_file(cnf_path),
            "solver": "PySAT CaDiCaL195",
            "status": "UNSAT",
        },
    }


def main() -> None:
    source_path = HERE / "first_supports.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = {
        "schema": "wave3-first-support-triangle-obstruction-v1",
        "strictRelaxation": {
            "retained": [
                "25 selected exact-distance-four bad atoms",
                "root atom (2,3)",
                "bad degree exactly 5 at owners 0 and 1",
                "every fixed support edge has selected-atom footprint multiplicity at least 2",
                "triangle-free fixed support plus selected bad atoms",
            ],
            "omitted": [
                "deletion SDR",
                "selected rows and local profile",
                "ambient blue extension",
                "maximum cut",
                "active scope and second-owner turnover",
                "coherent matching and transport ledger",
            ],
            "implication": "UNSAT excludes every production completion on the fixed support",
        },
        "source": {"path": source_path.name, "sha256": sha256_file(source_path)},
        "supports": [analyze_support(record) for record in source["supports"]],
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "triangle_obstruction.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "canonicalSha256": result["canonicalSha256"],
        "supports": [
            {
                "split": item["split"],
                "candidateSubsets": item["candidateSubsets"],
                "upstreamSelections": item["upstreamSelections"],
                "triangleFreeSurvivors": item["triangleFreeSurvivors"],
                "commonBadTriangles": item["commonBadTriangles"],
                "cnf": item["cnf"],
            }
            for item in result["supports"]
        ],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
