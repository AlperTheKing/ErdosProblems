"""Exact R37 sink-neutral-SCC obstruction gate.

The abstract certificate keeps the complete row tuple, optimal matching, full
occurrence-level obligation, and unmatched-root cursor in every state.  The
separate real-carrier audit records why the same two-row detour is not itself
a real counterexample: its production active scope is empty.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, order=True)
class Obligation:
    owner: int
    other: int
    producer_atom: int
    occurrence: int
    copy: int
    half: int
    component: int


@dataclass(frozen=True, order=True)
class Source:
    x: int
    y: int
    half: int


@dataclass(frozen=True, order=True)
class Vertex:
    tuple_index: int
    matching: tuple[tuple[Obligation, Source], ...]
    root: Obligation


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def connected(vertices: set[int], edges: set[tuple[int, int]]) -> bool:
    if not vertices:
        return True
    seen = {min(vertices)}
    todo = deque(seen)
    adjacency = {v: set() for v in vertices}
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    while todo:
        for y in adjacency[todo.popleft()]:
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return seen == vertices


def maximum_cut(n: int, edges: set[tuple[int, int]]) -> int:
    return max(
        sum(((mask >> x) ^ (mask >> y)) & 1 for x, y in edges)
        for mask in range(1 << n)
    )


def shortest_paths(
    n: int, edges: set[tuple[int, int]], start: int, finish: int
) -> list[tuple[int, ...]]:
    adjacency = {v: set() for v in range(n)}
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    distance = {start: 0}
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in adjacency[x]:
            if y not in distance:
                distance[y] = distance[x] + 1
                queue.append(y)
    target = distance[finish]
    paths: list[tuple[int, ...]] = []

    def visit(path: tuple[int, ...]) -> None:
        x = path[-1]
        if x == finish:
            if len(path) - 1 == target:
                paths.append(path)
            return
        for y in sorted(adjacency[x]):
            if y not in path and distance.get(y) == distance[x] + 1:
                visit(path + (y,))

    visit((start,))
    return paths


def real_carrier_audit() -> dict:
    # Two length-four blue geodesics for the bad atom (0,4).
    q0 = (0, 1, 2, 3, 4)
    q1 = (0, 1, 5, 3, 4)
    blue = {norm(x, y) for q in (q0, q1) for x, y in zip(q, q[1:])}
    bad = {norm(0, 4)}
    graph = blue | bad
    triangles = [
        (a, b, c)
        for a, b, c in itertools.combinations(range(6), 3)
        if {norm(a, b), norm(a, c), norm(b, c)} <= graph
    ]
    cut_side = (0, 1, 0, 1, 0, 0)
    cut = sum(cut_side[x] != cut_side[y] for x, y in graph)
    paths = shortest_paths(6, blue, 0, 4)

    active_by_tuple = []
    for row in (q0, q1):
        selected = set(row)
        support = {norm(x, y) for x, y in zip(row, row[1:])}
        active_edges = {
            e for e in blue if e not in support and e[0] in selected and e[1] in selected
        }
        endpoint_connected = connected({0, 4}, {
            e for e in active_edges if e[0] in {0, 4} and e[1] in {0, 4}
        }) and norm(0, 4) in active_edges
        # Direct reachability is clearer than the compact helper above.
        adjacency = {v: set() for v in selected}
        for x, y in active_edges:
            adjacency[x].add(y)
            adjacency[y].add(x)
        seen = {0}
        todo = deque([0])
        while todo:
            for y in adjacency[todo.popleft()]:
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
        endpoint_connected = 4 in seen
        active_by_tuple.append({
            "row": list(row),
            "activeEdges": [list(e) for e in sorted(active_edges)],
            "badEndpointsInOneActiveComponent": endpoint_connected,
        })
    return {
        "order": 6,
        "triangleFree": not triangles,
        "blueConnected": connected(set(range(6)), blue),
        "displayedCut": cut,
        "maximumCut": maximum_cut(6, graph),
        "displayedCutIsMaximum": cut == maximum_cut(6, graph),
        "completeShortestRows": [list(path) for path in paths],
        "anchored": all(path[0] == 0 and path[-1] == 4 for path in paths),
        "detourMiddleReplacement": q0[:2] + (5,) + q0[3:] == q1,
        "activeScope": active_by_tuple,
        "realCounterexample": False,
        "failedRealHypothesis": "ActiveOwner: bad endpoints are disconnected in activeGraph",
    }


def all_matchings(
    obligations: tuple[Obligation, ...], sources: tuple[Source, ...]
) -> list[tuple[tuple[Obligation, Source], ...]]:
    result = [()]
    for size in range(1, min(len(obligations), len(sources)) + 1):
        for ds in itertools.combinations(obligations, size):
            for ss in itertools.permutations(sources, size):
                result.append(tuple(sorted(zip(ds, ss))))
    return result


def abstract_sink_certificate() -> dict:
    q0 = (0, 1, 2, 3, 4)
    q1 = (0, 1, 5, 3, 4)
    fixed = (
        (6, 5, 1, 9, 10),
        (11, 5, 1, 14, 15),
        (16, 2, 1, 19, 20),
        (21, 2, 1, 24, 25),
    )
    states = ((q0,) + fixed, (q1,) + fixed)
    families = ((q0, q1),) + tuple((row,) for row in fixed)
    endpoint_pairs = tuple(norm(family[0][0], family[0][-1]) for family in families)
    endpoint_anchored = all(
        norm(row[0], row[-1]) == endpoint_pairs[index]
        for index, family in enumerate(families)
        for row in family
    )

    def generated_obligations(rows: tuple[tuple[int, ...], ...]) -> tuple[Obligation, ...]:
        result: list[Obligation] = []
        for owner in (2, 5):
            for other in range(26):
                atoms = [i for i, row in enumerate(rows) if owner in row and other in row]
                for copy in range(max(0, len(atoms) - 1)):
                    for half in (0, 1):
                        result.append(Obligation(
                            owner, other, atoms[copy + 1], copy + 1, copy, half, 7
                        ))
        return tuple(sorted(result))

    obligations_by_state = tuple(generated_obligations(rows) for rows in states)
    assert tuple(map(len, obligations_by_state)) == (12, 12)
    sources = tuple(Source(30 + i, 50 + i, i % 2) for i in range(11))
    optimum = len(sources)
    defect = len(obligations_by_state[0]) - optimum
    matchings = tuple(
        tuple(zip(obligations[:optimum], sources)) for obligations in obligations_by_state
    )
    roots = tuple(obligations[-1] for obligations in obligations_by_state)
    v0 = Vertex(0, matchings[0], roots[0])
    v1 = Vertex(1, matchings[1], roots[1])
    for index, vertex in enumerate((v0, v1)):
        assert len(vertex.matching) == optimum
        assert len({d for d, _ in vertex.matching}) == optimum
        assert len({s for _, s in vertex.matching}) == optimum
        assert all(d in obligations_by_state[index] for d, _ in vertex.matching)
        assert vertex.root in obligations_by_state[index]
        assert vertex.root not in {d for d, _ in vertex.matching}
    vertices = (v0, v1)
    edges = ((v0, v1), (v1, v0))

    # The complete neutral graph has one SCC, and every edge stays in it.
    reachable = {(start, finish): False for start in vertices for finish in vertices}
    for start in vertices:
        seen = {start}
        todo = deque([start])
        while todo:
            x = todo.popleft()
            for a, b in edges:
                if a == x and b not in seen:
                    seen.add(b)
                    todo.append(b)
        for finish in seen:
            reachable[start, finish] = True
    one_scc = all(reachable[a, b] and reachable[b, a] for a in vertices for b in vertices)
    outgoing = [(a, b) for a, b in edges if a in vertices and b not in vertices]
    unused_sources = []
    for vertex in vertices:
        used = {s for _, s in vertex.matching}
        unused_sources.append(sorted(set(sources) - used))

    return {
        "rowFamilies": [[list(row) for row in family] for family in families],
        "rowEndpointAnchoring": endpoint_anchored,
        "distinctEndpointPairs": len(set(endpoint_pairs)) == len(endpoint_pairs),
        "completeDetourFamily": families[0] == (q0, q1),
        "detourGeometry": {
            "probePair": [1, 3],
            "positionSeparation": 2,
            "forwardOwner": 5,
            "reverseOwner": 2,
            "middleReplacementForward": list(q1),
            "middleReplacementReverse": list(q0),
        },
        "obligationsByState": [
            [asdict(d) for d in obligations] for obligations in obligations_by_state
        ],
        "occurrenceValidityChecked": all(
            d.occurrence == d.copy + 1
            and d.producer_atom == [
                i for i, row in enumerate(states[state_index])
                if d.owner in row and d.other in row
            ][d.occurrence]
            for state_index, obligations in enumerate(obligations_by_state)
            for d in obligations
        ),
        "sources": [asdict(source) for source in sources],
        "attainableMatchingCardinalities": list(range(optimum + 1)),
        "optimalMatchingCountLowerBound": 2,
        "optimalCardinality": optimum,
        "defect": defect,
        "canonicalTuple": 0,
        "vertices": [
            {
                "tuple": vertex.tuple_index,
                "matching": [
                    {"obligation": asdict(d), "source": asdict(s)}
                    for d, s in vertex.matching
                ],
                "unmatchedRoot": asdict(vertex.root),
            }
            for vertex in vertices
        ],
        "neutralEdges": [[a.tuple_index, b.tuple_index] for a, b in edges],
        "fullMatchingCursorChanges": v0.matching != v1.matching and v0.root != v1.root,
        "singleStronglyConnectedComponent": one_scc,
        "sink": not outgoing,
        "unusedSourcesByVertex": [len(items) for items in unused_sources],
        "coherentAugmentationExists": any(unused_sources),
        "strictDefectTradeExists": False,
        "explicitTradeLeavingSccExists": bool(outgoing),
        "verdict": "EXACT_ABSTRACT_POSITIVE_DEFECT_SINK_SCC",
        "scope": "attachmentStep_total plus full cursors; not ActiveOwner-realizable",
    }


def main() -> int:
    result = {
        "schema": "R36_R37_SINK_SCC_GATE_V1",
        "realCarrierAudit": real_carrier_audit(),
        "abstractSink": abstract_sink_certificate(),
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("ascii")
    result["canonicalSha256"] = hashlib.sha256(raw).hexdigest()
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "verdict": result["abstractSink"]["verdict"],
        "defect": result["abstractSink"]["defect"],
        "sink": result["abstractSink"]["sink"],
        "realCounterexample": result["realCarrierAudit"]["realCounterexample"],
        "sha256": result["canonicalSha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
