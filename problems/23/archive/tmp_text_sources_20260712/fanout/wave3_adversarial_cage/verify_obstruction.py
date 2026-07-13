#!/usr/bin/env python3
"""Independent replay for the first-support production obstruction."""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
from collections import deque
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LRAT_TRIM = ROOT / "tmp" / "fanout" / "r51_independent_t5_verifier" / "lrat-trim.exe"
CADICAL = ROOT / "tmp" / "fanout" / "r51_independent_t5_verifier" / "cadical.exe"
V, M, A, B = 0, 1, 2, 3


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def support_sha(edges) -> str:
    return canonical_sha(sorted([list(edge) for edge in edges]))


def reconstruct_atoms(record: dict):
    left, right = record["left"], record["right"]
    n = left + right
    edges = [tuple(edge) for edge in record["supportEdgesGlobal"]]
    if len(edges) != 24 or len(set(edges)) != 24:
        raise AssertionError("support edge count")
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        if not (u < left <= v < n):
            raise AssertionError("support not bipartite in displayed shores")
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
    if any(value < 0 for value in distances[0]):
        raise AssertionError("support disconnected")
    atoms = []
    for shore, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v in itertools.combinations(vertices, 2):
            if distances[u][v] == 4:
                atoms.append((shore, u, v))
    return atoms


def triangles(atoms, left: int, n: int):
    atom_set = set(atoms)
    out = []
    for shore, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v, w in itertools.combinations(vertices, 3):
            triangle = ((shore, u, v), (shore, u, w), (shore, v, w))
            if all(atom in atom_set for atom in triangle):
                out.append(frozenset(triangle))
    return out


def semantic_exhaustion(record: dict, certificate: dict) -> dict:
    left, right = record["left"], record["right"]
    atoms = reconstruct_atoms(record)
    if support_sha(tuple(tuple(edge) for edge in record["supportEdgesGlobal"])) != record["supportSha256"]:
        raise AssertionError("support hash")
    atom_set = set(atoms)
    atom_triangles = triangles(atoms, left, left + right)
    root = ("L", A, B)
    candidates = 0
    triangle_free = 0
    for chosen_tuple in itertools.combinations(atoms, 25):
        chosen = frozenset(chosen_tuple)
        if root not in chosen:
            continue
        if any(sum(owner in atom[1:] for atom in chosen) != 5 for owner in (V, M)):
            continue
        candidates += 1
        if not any(triangle <= chosen for triangle in atom_triangles):
            triangle_free += 1
    if triangle_free != 0:
        raise AssertionError("semantic survivor")

    if certificate["distanceFourAtomCount"] != len(atoms):
        raise AssertionError("certificate atom count")
    if certificate["omissionBudget"] != len(atoms) - 25:
        raise AssertionError("certificate omission budget")
    if certificate["kind"] == "TWIN_OWNER_COMPLETER_PIGEONHOLE":
        neighbours = {}
        for owner in (V, M):
            neighbours[owner] = sorted(
                atom[2] if atom[1] == owner else atom[1]
                for atom in atoms
                if atom[0] == "L" and owner in atom[1:]
            )
        common = certificate["commonOwnerNeighbourSet"]
        if neighbours[V] != common or neighbours[M] != common or len(common) != 5:
            raise AssertionError("twin owner class")
        completers = {
            ("L", min(u, v), max(u, v))
            for u, v in itertools.combinations(common, 2)
            if ("L", min(u, v), max(u, v)) in atom_set
        }
        serialized = {tuple(atom) for atom in certificate["triangleCompleters"]}
        if completers != serialized or len(completers) <= len(atoms) - 25:
            raise AssertionError("completer pigeonhole")
    elif certificate["kind"] == "ZERO_OMISSION_TRIANGLE":
        triangle = frozenset(tuple(atom) for atom in certificate["triangle"])
        if len(atoms) != 25 or triangle not in atom_triangles:
            raise AssertionError("zero omission triangle")
    else:
        raise AssertionError("unknown certificate class")
    return {
        "split": [left, right],
        "atomCount": len(atoms),
        "rootedDegreeFiveSelectionsExhausted": candidates,
        "triangleFreeSurvivors": triangle_free,
        "certificateKind": certificate["kind"],
        "verdict": "PASS",
    }


def verify_cnf(instance: dict) -> dict:
    cnf_path = HERE / instance["path"]
    lrat_path = cnf_path.with_suffix(".lrat")
    if sha256_file(cnf_path) != instance["sha256"]:
        raise AssertionError("CNF hash")
    cnf = CNF(from_file=str(cnf_path))
    statuses = {}
    for solver_name in ("cadical195", "glucose4", "lingeling"):
        with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
            statuses[solver_name] = "SAT" if solver.solve() else "UNSAT"
    if set(statuses.values()) != {"UNSAT"}:
        raise AssertionError(statuses)
    checked = subprocess.run(
        [str(LRAT_TRIM), str(cnf_path), str(lrat_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    checker_output = checked.stdout + checked.stderr
    if "s VERIFIED" not in checker_output:
        raise AssertionError(checker_output)
    return {
        "split": instance["split"],
        "cnfSha256": sha256_file(cnf_path),
        "lratSha256": sha256_file(lrat_path),
        "solverStatuses": statuses,
        "lratTrimReturnCode": checked.returncode,
        "lratTrimVerdict": "VERIFIED",
    }


def main() -> None:
    supports_path = HERE / "first_supports.json"
    certificate_path = HERE / "omission_budget_certificate.json"
    cnf_manifest_path = HERE / "small_cnf_manifest.json"
    supports = json.loads(supports_path.read_text(encoding="utf-8"))
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    cnf_manifest = json.loads(cnf_manifest_path.read_text(encoding="utf-8"))
    cert_by_split = {
        tuple(item["split"]): item for item in certificate["certificates"]
    }
    result = {
        "schema": "wave3-production-obstruction-independent-replay-v1",
        "semanticChecks": [
            semantic_exhaustion(record, cert_by_split[(record["left"], record["right"])])
            for record in supports["supports"]
        ],
        "cnfChecks": [verify_cnf(instance) for instance in cnf_manifest["instances"]],
        "tools": {
            "cadical.exe": sha256_file(CADICAL),
            "lrat-trim.exe": sha256_file(LRAT_TRIM),
        },
        "inputs": {
            supports_path.name: sha256_file(supports_path),
            certificate_path.name: sha256_file(certificate_path),
            cnf_manifest_path.name: sha256_file(cnf_manifest_path),
        },
        "verdict": "PASS_ALL_THREE_SUPPORTS_EXCLUDED_BY_STRICT_RELAXATION",
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "verification.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
