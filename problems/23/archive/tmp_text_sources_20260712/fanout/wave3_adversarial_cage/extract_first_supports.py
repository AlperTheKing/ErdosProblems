#!/usr/bin/env python3
"""Reconstruct deterministic first rooted t=5 supports for the n=17 splits."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRIVER = ROOT / "tmp" / "fanout" / "r42_graph_specific_exclusion" / "rooted_t5_support_cp_sat.py"
SOURCE_DIR = ROOT / "tmp" / "fanout" / "r42_graph_specific_exclusion"
SPLITS = ((9, 8), (10, 7), (11, 6))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def load_driver():
    spec = importlib.util.spec_from_file_location("rooted_t5_driver", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {DRIVER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def connected(graph: nx.Graph) -> bool:
    return graph.number_of_nodes() > 0 and nx.is_connected(graph)


def support_record(driver, left: int, right: int) -> dict:
    model, edge_vars = driver.build_rooted_support_model(left, right, False, False)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 1
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"support {left}+{right}: {solver.status_name(status)}")

    graph = driver.graph_from_solution(solver, edge_vars, left, right)
    atoms = driver.distance_four_atoms(graph, left, right)
    local_edges = [
        [u, v - left] if u < left else [v, u - left]
        for u, v in sorted(graph.edges())
    ]
    owner_d4 = {
        str(owner): sum(owner in (atom["u"], atom["v"]) for atom in atoms)
        for owner in (0, 1)
    }
    mandatory_rows = {
        (2, left, 0, left + 1, 3),
        (2, left, 1, left + 1, 3),
    }
    all_rows = {tuple(row) for atom in atoms for row in atom["rows"]}
    record = {
        "left": left,
        "right": right,
        "solver": "OR-Tools CP-SAT deterministic one-worker",
        "status": solver.status_name(status),
        "supportEdgesGlobal": [list(e) for e in sorted(graph.edges())],
        "supportEdgesLocal": local_edges,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode("ascii").strip(),
        "edgeCount": graph.number_of_edges(),
        "connected": connected(graph),
        "ownerDegrees": {"0": graph.degree[0], "1": graph.degree[1]},
        "distanceFourAtomCount": len(atoms),
        "ownerDistanceFourDegrees": owner_d4,
        "mandatoryRowsPresent": mandatory_rows <= all_rows,
        "supportSha256": canonical_sha([list(e) for e in sorted(graph.edges())]),
    }
    if record["edgeCount"] != 24 or not record["connected"]:
        raise AssertionError(record)
    if record["ownerDegrees"] != {"0": 5, "1": 5}:
        raise AssertionError(record)
    if len(atoms) < 25 or min(owner_d4.values()) < 5:
        raise AssertionError(record)
    if not record["mandatoryRowsPresent"]:
        raise AssertionError(record)
    return record


def main() -> None:
    driver = load_driver()
    sources = {}
    for left, right in SPLITS:
        artifact = SOURCE_DIR / f"t5_solo_l{left}_r{right}_3000.json"
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        sources[f"{left}+{right}"] = {
            "path": str(artifact.relative_to(ROOT)).replace("\\", "/"),
            "fileSha256": sha256_file(artifact),
            "storedCanonicalSha256": payload["canonicalSha256"],
            "verdict": payload["verdict"],
            "supportsSolved": payload["supportsSolved"],
        }
    result = {
        "schema": "wave3-first-rooted-t5-supports-v1",
        "driver": {
            "path": str(DRIVER.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(DRIVER),
        },
        "sourceArtifacts": sources,
        "supports": [support_record(driver, left, right) for left, right in SPLITS],
        "scope": "one deterministic feasible support per split; not a catalogue claim",
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "first_supports.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
