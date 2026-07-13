"""Exact Pattern-5 completeness gate on the canonical R29 2943 cage.

This checks two selector tuples on the same graph:
  * baseline: every quiescent component boundary misses the deficient shore's
    55-vertex companion set, so Pattern 5 contributes no source;
  * all-anchor: the existing independent gate supplies 28 new, unreserved
    keys and closes the old four-pattern defect exactly.

Only integer/set arithmetic is used.  The script writes a compact JSON
certificate beside itself and fails on any mismatch with the stated values.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
LEAD_PATH = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
P5_PATH = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"
MAXCUT_CERT = ROOT / "tmp/fanout/r29_gate/d03/retry2/certificate.json"
GAMMA_RESULT = ROOT / "tmp/fanout/r29_gate/d04/retry2/run_stdout.json"
OWNERS = (0, 1, 2)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ints(values) -> str:
    payload = json.dumps(sorted(values), separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def quiet_components(state: dict) -> list[dict]:
    active = state["av"]
    quiet = set(range(state["n"])) - active
    adjacency = defaultdict(set)
    for u, v in state["blue"]:
        if u in quiet and v in quiet:
            adjacency[u].add(v)
            adjacency[v].add(u)

    components = []
    seen = set()
    for root in sorted(quiet):
        if root in seen:
            continue
        vertices = {root}
        seen.add(root)
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in seen:
                    seen.add(v)
                    vertices.add(v)
                    queue.append(v)
        boundary = {
            a
            for z in vertices
            for a in active
            if (min(z, a), max(z, a)) in state["blue"]
        }
        components.append(
            {
                "root": root,
                "vertices": vertices,
                "boundary": boundary,
            }
        )
    return components


def pattern5_masks(state: dict, components: list[dict]) -> dict:
    """Enumerate P5 owner masks for every ordered quiet FreeHalf key.

    Eligibility is exactly R30's attachment condition.  An owner must have a
    row companion in each component boundary, in its active component.
    """
    component_of = {}
    eligible = []
    for index, component in enumerate(components):
        for x in component["vertices"]:
            component_of[x] = index
        owners = set()
        for owner in OWNERS:
            if any(
                state["pair"][owner, a] > 0
                and state["comp"].get(a) == state["comp"].get(owner)
                for a in component["boundary"]
            ):
                owners.add(owner)
        eligible.append(owners)

    quiet = sorted(component_of)
    masks = {}
    for x in quiet:
        for y in quiet:
            if x == y or state["pair"][x, y] != 0:
                continue
            owner_set = eligible[component_of[x]] & eligible[component_of[y]]
            mask = sum(1 << owner for owner in owner_set)
            if not mask:
                continue
            for half in (0, 1):
                reserved = (
                    half == 0
                    and (min(x, y), max(x, y)) in state["active_edges"]
                    and x in state["av"]
                )
                if not reserved:
                    masks[x, y, half] = mask
    return masks


def main() -> None:
    lead = load("r29_lead_pattern5_falsifier", LEAD_PATH)
    p5 = load("r29_pattern5_gate_falsifier", P5_PATH)
    data = lead.build()

    # The canonical cage is graph-realizable and already has exact independent
    # MaxCut/Gamma certificates.  Recheck its inexpensive structural invariants
    # and bind this result to those certificate files by SHA-256.
    graph = set(data["graph"])
    adjacency = defaultdict(set)
    for u, v in graph:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert data["n"] == 2943
    assert len(data["blue"]) == 7039 and len(data["bad"]) == 1383
    assert all(not (adjacency[u] & adjacency[v]) for u, v in graph)
    maxcut = json.loads(MAXCUT_CERT.read_text())
    gamma = json.loads(GAMMA_RESULT.read_text())
    assert maxcut["maxcut"] == 7039
    assert maxcut["traffic_quotient"]["cases"] == 11664
    assert sum(maxcut["attaining_class_counts"].values()) == 7039
    assert gamma["gamma"] == 34575
    assert gamma["distance_histogram"] == {"4": 1383}

    baseline_rows = tuple(tuple(row) for row in data["rows"])
    baseline = p5.full_state(data, baseline_rows)
    components = quiet_components(baseline)

    companion_by_owner = {
        owner: {x for x in range(data["n"]) if baseline["pair"][owner, x] > 0}
        for owner in OWNERS
    }
    shore_companions = set().union(*companion_by_owner.values())
    assert shore_companions == set(range(55))
    assert len(baseline["selected"]) == 2803
    assert len(baseline["av"]) == 2775
    assert data["n"] - len(baseline["av"]) == 168
    assert sorted(len(c["vertices"]) for c in components) == [1, 1, 4, 4, 4, 5, 44, 50, 55]
    assert all(c["boundary"] for c in components)
    assert all(not (c["boundary"] & shore_companions) for c in components)

    p5_masks = pattern5_masks(baseline, components)
    p5_reach = sum(1 for mask in p5_masks.values() if mask & 7)
    old_reach = sum(1 for mask in baseline["masks"].values() if mask & 7)
    old_histogram = Counter(baseline["masks"].values())
    demand = sum(baseline["demand"].values())
    assert baseline["demand"] == {0: 6651, 1: 6651, 2: 6651}
    assert demand == 19953 and old_reach == 19925
    assert p5_reach == 0 and demand - old_reach - p5_reach == 28

    component_records = []
    for component in sorted(components, key=lambda c: (len(c["vertices"]), c["root"])):
        boundary = component["boundary"]
        component_records.append(
            {
                "root": component["root"],
                "size": len(component["vertices"]),
                "vertex_sha256": digest_ints(component["vertices"]),
                "boundary_size": len(boundary),
                "boundary_sha256": digest_ints(boundary),
                "companion_hits": sorted(boundary & shore_companions),
            }
        )

    anchor_rows = list(baseline_rows)
    for index, meta in enumerate(data["selectorMeta"]):
        anchor_rows[data["selectorStart"] + index] = tuple(meta["anchorRow"])
    anchor = p5.p5_at(data, tuple(anchor_rows), verbose=False)
    assert not anchor["leaf_active"]
    assert anchor["K"] == 1379 and anchor["boundary"] == [1, 55]
    assert anchor["xs_ok"] and anchor["free_ok"]
    assert all(anchor["elig"].values())
    assert anchor["disjoint"] and anchor["unreserved"]
    assert anchor["loss"] == 26 and anchor["full_gap"] == 0
    assert all(gap <= 0 for _, _, _, gap in anchor["all_cuts"])

    result = {
        "arithmetic": "integer-only",
        "verdict": {
            "arbitrary_tuple_pattern5_completeness": "FALSIFIED",
            "selection_sensitive_existential": "NOT_FALSIFIED",
        },
        "graph_certificate": {
            "n": data["n"],
            "edges": len(graph),
            "blue": len(data["blue"]),
            "bad": len(data["bad"]),
            "triangle_free": True,
            "maxcut": maxcut["maxcut"],
            "maxcut_certificate_sha256": sha256(MAXCUT_CERT),
            "gamma": gamma["gamma"],
            "gamma_result_sha256": sha256(GAMMA_RESULT),
        },
        "baseline": {
            "selected": len(baseline["selected"]),
            "active": len(baseline["av"]),
            "quiescent": data["n"] - len(baseline["av"]),
            "quiescent_component_count": len(components),
            "shore_companions": sorted(shore_companions),
            "shore_companion_sha256": digest_ints(shore_companions),
            "components": component_records,
            "all_boundaries_companion_starved": True,
            "old_mask_histogram": {str(k): v for k, v in sorted(old_histogram.items())},
            "old_reach": old_reach,
            "pattern5_reach": p5_reach,
            "demand": demand,
            "five_pattern_defect": demand - old_reach - p5_reach,
        },
        "all_anchor": {
            "component_size": anchor["K"],
            "boundary": anchor["boundary"],
            "new_keys": 28,
            "unreserved": anchor["unreserved"],
            "disjoint_from_old": anchor["disjoint"],
            "switch_loss": anchor["loss"],
            "full_shore_gap": anchor["full_gap"],
        },
    }
    output = HERE / "result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "result": str(output),
        "result_sha256": sha256(output),
        "baseline_defect": result["baseline"]["five_pattern_defect"],
        "all_anchor_gap": result["all_anchor"]["full_shore_gap"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
