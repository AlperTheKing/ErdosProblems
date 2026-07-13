#!/usr/bin/env python3
"""CNF for the small triangle obstruction, omitting all downstream gates."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
V, M, A, B = 0, 1, 2, 3


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def atoms_for(record: dict):
    left, right = record["left"], record["right"]
    n = left + right
    adjacency = [[] for _ in range(n)]
    for u, v in record["supportEdgesGlobal"]:
        adjacency[u].append(v)
        adjacency[v].append(u)
    distances = []
    for source in range(n):
        distance = [-1] * n
        distance[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if distance[v] < 0:
                    distance[v] = distance[u] + 1
                    queue.append(v)
        distances.append(distance)
    atoms = []
    for shore, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v in itertools.combinations(vertices, 2):
            if distances[u][v] == 4:
                atoms.append((shore, u, v))
    return atoms


def triangles_for(atoms, left: int, n: int):
    index = {atom: i for i, atom in enumerate(atoms)}
    triangles = []
    for shore, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v, w in itertools.combinations(vertices, 3):
            triple = ((shore, u, v), (shore, u, w), (shore, v, w))
            if all(atom in index for atom in triple):
                triangles.append(tuple(index[atom] for atom in triple))
    return index, triangles


def build(record: dict) -> dict:
    left, right = record["left"], record["right"]
    atoms = atoms_for(record)
    index, triangles = triangles_for(atoms, left, left + right)
    pool = IDPool()
    selected = [pool.id(("selected", i)) for i in range(len(atoms))]
    cnf = CNF()
    cnf.extend(CardEnc.equals(
        lits=selected, bound=25, vpool=pool, encoding=EncType.seqcounter
    ).clauses)
    root_index = index[("L", A, B)]
    cnf.append([selected[root_index]])
    for owner in (V, M):
        incident = [
            selected[i] for i, atom in enumerate(atoms) if owner in atom[1:]
        ]
        cnf.extend(CardEnc.equals(
            lits=incident, bound=5, vpool=pool, encoding=EncType.seqcounter
        ).clauses)
    for i, j, k in triangles:
        cnf.append([-selected[i], -selected[j], -selected[k]])

    path = HERE / f"small_obstruction_l{left}_r{right}.cnf"
    cnf.to_file(str(path))
    statuses = {}
    for name in ("cadical195", "glucose4", "lingeling"):
        with Solver(name=name, bootstrap_with=cnf.clauses) as solver:
            statuses[name] = "SAT" if solver.solve() else "UNSAT"
    if set(statuses.values()) != {"UNSAT"}:
        raise AssertionError(statuses)
    return {
        "split": [left, right],
        "supportSha256": record["supportSha256"],
        "atomCount": len(atoms),
        "atoms": [[shore, u, v] for shore, u, v in atoms],
        "triangleCount": len(triangles),
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "path": path.name,
        "sha256": sha256_file(path),
        "solverStatuses": statuses,
    }


def main() -> None:
    source_path = HERE / "first_supports.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = {
        "schema": "wave3-small-triangle-obstruction-cnf-v1",
        "semantics": [
            "choose exactly 25 exact-distance-four atoms",
            "select root atom (2,3)",
            "give owners 0 and 1 bad degree exactly 5",
            "selected atom graph is triangle-free",
        ],
        "omittedProductionGates": [
            "footprint multiplicity and deletion SDR",
            "rows and selected support",
            "ambient extension and maximum cut",
            "active scope and second owner",
            "coherent matching, positive defect, and ledger",
        ],
        "source": {"path": source_path.name, "sha256": sha256_file(source_path)},
        "instances": [build(record) for record in source["supports"]],
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "small_cnf_manifest.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
