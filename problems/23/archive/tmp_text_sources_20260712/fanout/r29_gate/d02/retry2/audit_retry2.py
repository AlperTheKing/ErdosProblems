"""Independent exact audit of incidence emitted by the untrusted lead candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEAD = HERE.parent.parent / "lead" / "r29_lead_gate.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def acquire_candidate() -> dict:
    spec = importlib.util.spec_from_file_location("untrusted_r29_lead", LEAD)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw = module.build()
    return {
        "n": raw["n"],
        "blue": [list(e) for e in sorted(raw["blue"])],
        "bad": [list(e) for e in sorted(raw["bad"])],
    }


def parse_edges(n: int, rows: list[list[int]], label: str) -> tuple[set[tuple[int, int]], list[dict]]:
    edges: set[tuple[int, int]] = set()
    errors: list[dict] = []
    for index, row in enumerate(rows):
        if len(row) != 2 or not all(type(x) is int for x in row):
            errors.append({"kind": "malformed_edge", "label": label, "index": index, "value": row})
            continue
        u, v = row
        if not (0 <= u < n and 0 <= v < n):
            errors.append({"kind": "endpoint_out_of_range", "label": label, "index": index, "edge": row})
        elif u >= v:
            errors.append({"kind": "noncanonical_or_loop", "label": label, "index": index, "edge": row})
        elif (u, v) in edges:
            errors.append({"kind": "duplicate_edge", "label": label, "index": index, "edge": row})
        else:
            edges.add((u, v))
    return edges, errors


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def first_triangle(adj: list[set[int]]) -> list[int] | None:
    for u in range(len(adj)):
        for v in sorted(x for x in adj[u] if x > u):
            common = adj[u].intersection(adj[v])
            eligible = [w for w in common if w > v]
            if eligible:
                return [u, v, min(eligible)]
    return None


def components(adj: list[set[int]]) -> list[list[int]]:
    unseen = set(range(len(adj)))
    result: list[list[int]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        comp = [root]
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in sorted(adj[u]):
                if v in unseen:
                    unseen.remove(v)
                    comp.append(v)
                    queue.append(v)
        result.append(sorted(comp))
    return result


def audit(candidate: dict) -> dict:
    n = candidate["n"]
    blue, blue_errors = parse_edges(n, candidate["blue"], "blue")
    bad, bad_errors = parse_edges(n, candidate["bad"], "bad")
    overlap = sorted(blue.intersection(bad))
    graph = blue.union(bad)
    graph_adj = adjacency(n, graph)
    blue_adj = adjacency(n, blue)
    triangle = first_triangle(graph_adj)
    comps = components(blue_adj)
    reached = len(comps[0]) if comps else 0
    disconnected_witness = None
    if len(comps) != 1:
        disconnected_witness = {
            "component_count": len(comps),
            "component_representatives": [c[0] for c in comps],
            "component_sizes": [len(c) for c in comps],
            "source": 0,
            "first_unreachable": min(v for c in comps[1:] for v in c),
        }
    return {
        "claims": {
            "simple_valid_incidence": not blue_errors and not bad_errors and not overlap,
            "graph_triangle_free": triangle is None,
            "blue_connected": len(comps) == 1,
        },
        "counts": {"n": n, "blue_edges": len(blue), "bad_edges": len(bad), "graph_edges": len(graph)},
        "exact_gaps": {
            "incidence_error_count": len(blue_errors) + len(bad_errors) + len(overlap),
            "triangle_count_acceptance_gap": 0 if triangle is None else 1,
            "blue_unreached_from_0": n - reached,
            "blue_components_minus_one": len(comps) - 1,
        },
        "failure_witnesses": {
            "incidence_errors": blue_errors + bad_errors,
            "blue_bad_overlap_first": list(overlap[0]) if overlap else None,
            "triangle_vertices": triangle,
            "blue_disconnection": disconnected_witness,
        },
    }


def self_test() -> dict:
    triangle_case = {"n": 3, "blue": [[0, 1], [1, 2]], "bad": [[0, 2]]}
    disconnected_case = {"n": 4, "blue": [[0, 1], [2, 3]], "bad": []}
    t = audit(triangle_case)
    d = audit(disconnected_case)
    assert t["failure_witnesses"]["triangle_vertices"] == [0, 1, 2]
    assert d["failure_witnesses"]["blue_disconnection"]["first_unreachable"] == 2
    assert d["exact_gaps"]["blue_unreached_from_0"] == 2
    return {"triangle_witness": [0, 1, 2], "disconnected_witness": [0, 2]}


def main() -> None:
    candidate = acquire_candidate()
    candidate_bytes = canonical(candidate) + b"\n"
    (HERE / "candidate_incidence.json").write_bytes(candidate_bytes)
    result = audit(json.loads(candidate_bytes))
    result["self_test"] = self_test()
    result["input_sha256"] = {
        "lead_source": sha256(LEAD.read_bytes()),
        "candidate_incidence": sha256(candidate_bytes),
    }
    result_bytes = canonical(result) + b"\n"
    (HERE / "audit_result.json").write_bytes(result_bytes)
    manifest = {
        "inputs": result["input_sha256"],
        "outputs": {"audit_result.json": sha256(result_bytes)},
    }
    (HERE / "sha256.json").write_bytes(canonical(manifest) + b"\n")
    print(result_bytes.decode("ascii"), end="")


if __name__ == "__main__":
    main()
