"""Graph-realizable falsifier to local Pattern-5 component uniqueness.

Take two exact R29 2943 cages, complement the certified cut on the second,
and join their quiescent leaf-3 vertices by one blue bridge.  The same static
Pattern-5 base key in the first copy is then eligible for owners in two
different active components.

The script checks triangle-freeness, blue connectivity, exact MaxCut by an
additive upper/attaining certificate, every bad edge's blue distance four,
Gamma, selected rows, active scope, quiescent boundary, freeness, reservation,
switch loss, and the two-component eligibility claim using integers only.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
P5 = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"
BASE_MAXCUT_CERT = ROOT / "tmp/fanout/r29_gate/d03/retry2/certificate.json"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def shifted(items, offset: int) -> set[tuple[int, int]]:
    return {(x + offset, y + offset) for x, y in items}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bfs_distance(adjacency: list[set[int]], source: int, target: int) -> int | None:
    distance = [-1] * len(adjacency)
    distance[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        if x == target:
            return distance[x]
        for y in adjacency[x]:
            if distance[y] < 0:
                distance[y] = distance[x] + 1
                queue.append(y)
    return None


def main() -> None:
    lead = load("p5_double_lead", LEAD)
    p5 = load("p5_double_gate", P5)
    base = lead.build()
    offset = base["n"]
    n = 2 * offset
    bridge = edge(3, offset + 3)
    blue = set(base["blue"]) | shifted(base["blue"], offset) | {bridge}
    bad = set(base["bad"]) | shifted(base["bad"], offset)
    graph = blue | bad

    # Exact structural certificate.
    assert n == 5886
    assert len(blue) == 14079 and len(bad) == 2766 and len(graph) == 16845
    adjacency = [set() for _ in range(n)]
    blue_adjacency = [set() for _ in range(n)]
    for x, y in graph:
        adjacency[x].add(y)
        adjacency[y].add(x)
    for x, y in blue:
        blue_adjacency[x].add(y)
        blue_adjacency[y].add(x)
    assert all(not (adjacency[x] & adjacency[y]) for x, y in graph)
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in blue_adjacency[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    assert len(seen) == n

    # One bridge cannot create a shorter path internal to either copy; replay
    # all distances anyway as an executable Gamma certificate.
    distance_histogram = defaultdict(int)
    for x, y in sorted(bad):
        distance_histogram[bfs_distance(blue_adjacency, x, y)] += 1
    assert dict(distance_histogram) == {4: 2766}
    gamma = 25 * len(bad)
    assert gamma == 69150

    # Each internal copy has exact MaxCut 7039.  Any cut gains at most one on
    # the bridge, while the displayed cut attains all three terms.
    base_cert = json.loads(BASE_MAXCUT_CERT.read_text())
    assert base_cert["maxcut"] == 7039
    side = list(base["side"]) + [not bit for bit in base["side"]]
    cut_blue = sum(side[x] != side[y] for x, y in blue)
    maxcut_upper = 7039 + 7039 + 1
    assert cut_blue == maxcut_upper == 14079
    assert all(side[x] == side[y] for x, y in bad)

    anchor_rows = [tuple(row) for row in base["rows"]]
    for index, meta in enumerate(base["selectorMeta"]):
        anchor_rows[base["selectorStart"] + index] = tuple(meta["anchorRow"])
    rows = tuple(anchor_rows) + tuple(
        tuple(x + offset for x in row) for row in anchor_rows
    )
    combined = {"n": n, "blue": blue, "bad": bad}
    state = p5.full_state(combined, rows)
    assert len(state["av"]) == 38
    owner_roots = {
        owner: state["comp"][owner]
        for owner in (0, 1, 2, offset, offset + 1, offset + 2)
    }
    assert len({owner_roots[o] for o in (0, 1, 2)}) == 1
    assert len({owner_roots[o] for o in (offset, offset + 1, offset + 2)}) == 1
    assert owner_roots[0] != owner_roots[offset]

    # Build Q = B[V minus active scope] and certify the merged K(3).
    quiet = set(range(n)) - state["av"]
    qadj = defaultdict(set)
    for x, y in blue:
        if x in quiet and y in quiet:
            qadj[x].add(y)
            qadj[y].add(x)
    K = {3}
    queue = deque([3])
    while queue:
        x = queue.popleft()
        for y in qadj[x]:
            if y not in K:
                K.add(y)
                queue.append(y)
    boundary = {
        a for z in K for a in state["av"] if edge(z, a) in blue
    }
    assert len(K) == 2758
    assert boundary == {1, 55, offset + 1, offset + 55}

    source_x, source_y = 3, 56
    assert source_x in K and source_y in K
    assert state["pair"][source_x, source_y] == 0
    assert source_x not in state["av"] and source_y not in state["av"]
    # ScopedReserved additionally requires ActiveOwner(sourceX), so half zero
    # is free even when this selected off-support edge exists.
    switch_loss = (
        sum((x in K) != (y in K) for x, y in blue)
        - sum((x in K) != (y in K) for x, y in bad)
    )
    assert switch_loss == 52

    eligible_owners = []
    for owner in owner_roots:
        if any(
            state["pair"][owner, a] > 0
            and state["comp"].get(a) == state["comp"].get(owner)
            for a in boundary
        ):
            eligible_owners.append(owner)
    assert eligible_owners == [0, 1, 2, offset, offset + 1, offset + 2]
    eligible_roots = {owner_roots[owner] for owner in eligible_owners}
    assert len(eligible_roots) == 2

    # The two full half keys are injective but can be assigned across the two
    # roots; no single base-key component label can satisfy both assignments.
    split_assignment = {
        "half0Owner": 0,
        "half1Owner": offset,
        "half0Root": owner_roots[0],
        "half1Root": owner_roots[offset],
    }
    assert split_assignment["half0Root"] != split_assignment["half1Root"]

    result = {
        "schema": "DOUBLED_R29_PATTERN5_COMPONENT_UNIQUENESS_FALSIFIER_V1",
        "arithmetic": "integer-only",
        "graph": {
            "n": n,
            "edges": len(graph),
            "blue": len(blue),
            "bad": len(bad),
            "bridge": list(bridge),
            "triangleFree": True,
            "blueConnected": True,
            "maxCutUpper": maxcut_upper,
            "attainingCut": cut_blue,
            "baseMaxCutCertificateSHA256": sha256(BASE_MAXCUT_CERT),
            "badBlueDistanceHistogram": {str(k): v for k, v in distance_histogram.items()},
            "gamma": gamma,
        },
        "selectedState": {
            "rows": len(rows),
            "activeVertices": len(state["av"]),
            "activeOwnerRoots": sorted(eligible_roots),
        },
        "pattern5": {
            "sourceBaseKey": [source_x, source_y],
            "free": True,
            "bothHalvesUnreserved": True,
            "quiescentComponentSize": len(K),
            "boundary": sorted(boundary),
            "switchLoss": switch_loss,
            "eligibleOwners": eligible_owners,
            "eligibleDestinationRoots": sorted(eligible_roots),
        },
        "splitHalfAssignment": split_assignment,
        "verdict": "RELATION_BASE_COMPONENT_UNIQUE_FALSIFIED",
        "scope": (
            "Local Pattern-5 eligibility does not determine one destination component. "
            "A chosen matching must impose base-key coherence globally."
        ),
    }
    output = HERE / "doubled_cage_result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"resultSHA256": sha256(output), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
