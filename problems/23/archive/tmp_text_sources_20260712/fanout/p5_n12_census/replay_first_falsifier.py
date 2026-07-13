"""Exact replay and structural certificate for the first aggregate falsifier."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
AGGREGATE = HERE / "census_all_n5_n12.json"
sys.path.insert(0, str(WRITEUP))
sys.path.insert(0, str(PHT))

from _codex_r19_global_base_census import dec, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from p5_core import (  # noqa: E402
    analyze_rows,
    decode_source,
    make_graph_context,
    reconstruct_state,
    relation_masks,
    sigma_value,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def connected(n: int, edges: set[tuple[int, int]]) -> bool:
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return len(seen) == n


def distance(n: int, edges: set[tuple[int, int]], source: int, target: int) -> int | None:
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    dist = {source: 0}
    queue = deque([source])
    while queue:
        x = queue.popleft()
        if x == target:
            return dist[x]
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    return None


def brute_cut_certificate(n: int, edges: set[tuple[int, int]]) -> dict:
    maximum = -1
    max_masks: list[int] = []
    for mask in range(1 << (n - 1)):
        cut = sum(((mask >> x) ^ (mask >> y)) & 1 for x, y in edges)
        if cut > maximum:
            maximum = cut
            max_masks = [mask]
        elif cut == maximum:
            max_masks.append(mask)

    candidates = []
    for mask in max_masks:
        blue = {e for e in edges if ((mask >> e[0]) ^ (mask >> e[1])) & 1}
        bad = edges - blue
        if not bad or not connected(n, blue):
            continue
        lengths = []
        for x, y in sorted(bad):
            d = distance(n, blue, x, y)
            if d is None:
                break
            lengths.append((x, y, d + 1))
        else:
            candidates.append({
                "mask": mask,
                "gamma": sum(length * length for _, _, length in lengths),
                "lengths": lengths,
                "blue": sorted(blue),
                "bad": sorted(bad),
            })
    minimum_gamma = min(candidate["gamma"] for candidate in candidates)
    minimum = [candidate for candidate in candidates if candidate["gamma"] == minimum_gamma]
    return {
        "maximumCutSize": maximum,
        "maximumCutCountModuloComplement": len(max_masks),
        "connectedNonbipartiteMaximumCuts": len(candidates),
        "minimumGamma": minimum_gamma,
        "minimumGammaCutMasks": [candidate["mask"] for candidate in minimum],
        "firstMinimum": minimum[0],
    }


def quiescent_components(ctx, state) -> list[dict]:
    allowed = set(range(ctx.n)) - state.active_vertices
    seen: set[int] = set()
    out = []
    for root in sorted(allowed):
        if root in seen:
            continue
        component = {root}
        seen.add(root)
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in ctx.blue_adj[x]:
                if y in allowed and y not in seen:
                    seen.add(y)
                    component.add(y)
                    queue.append(y)
        boundary = sorted({
            y for x in component for y in ctx.blue_adj[x]
            if y in state.active_vertices
        })
        mask = sum(1 << x for x in component)
        out.append({
            "vertices": sorted(component),
            "activeBoundary": boundary,
            "switchLoss": sigma_value(ctx, mask),
        })
    return out


def main() -> int:
    aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8"))
    record = aggregate["total"]["first"]["firstMicroFalsifier"]
    assert record is not None
    n, graph_edges_list = dec(record["g6"])
    graph_edges = set(graph_edges_list)
    assert n == record["order"] == 10
    assert connected(n, graph_edges)
    assert all(
        not ({x, y, z} <= set(range(n)) and
             tuple(sorted((x, y))) in graph_edges and
             tuple(sorted((x, z))) in graph_edges and
             tuple(sorted((y, z))) in graph_edges)
        for x, y, z in itertools.combinations(range(n), 3)
    )

    cut = brute_cut_certificate(n, graph_edges)
    info = loads(n, graph_edges_list)
    assert info is not None
    assert cut["minimumGamma"] == info["G"] == record["gamma"]
    assert cut["firstMinimum"]["blue"] == sorted(info["Bset"])
    assert cut["firstMinimum"]["bad"] == sorted(info["Mset"])
    assert all(length == 5 for length in info["ell"].values())

    families = shortest_row_families(info)
    sizes = tuple(map(len, families))
    assert list(sizes) == record["familySizes"]
    indexed_choice = next(
        choice for index, choice in enumerate(itertools.product(*(range(s) for s in sizes)))
        if index == record["tupleIndex"]
    )
    assert indexed_choice == tuple(record["choice"])
    rows = rows_for_choice(families, indexed_choice)
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    state = reconstruct_state(ctx, rows)
    analysis = analyze_rows(ctx, rows, details=True)
    masks = relation_masks(ctx, state)

    for key in (
        "oneDemand", "microDemand", "collisionDemand", "hitNeedSlots",
        "owners", "activeVertices", "p5Stats", "oneClaudeBefore",
        "oneClaudeAfter", "oneBeforeP5", "oneFive", "microBeforeP5",
        "microFive",
    ):
        assert analysis[key] == record[key], key

    demand = [
        state.collision[owner] + 25 * state.hit_need[owner]
        for owner in state.owners
    ]
    shore_rows = []
    for shore in range(1, 1 << len(state.owners)):
        shore_demand = sum(
            amount for index, amount in enumerate(demand) if shore & (1 << index)
        )
        before_reach = sum(bool(mask & shore) for mask in masks["beforeP5"].values())
        five_reach = sum(bool(mask & shore) for mask in masks["five"].values())
        shore_rows.append({
            "shoreMask": shore,
            "owners": [
                owner for index, owner in enumerate(state.owners)
                if shore & (1 << index)
            ],
            "demand": shore_demand,
            "beforeP5Reach": before_reach,
            "fivePatternReach": five_reach,
            "fivePatternDefect": shore_demand - five_reach,
        })
    assert max(row["fivePatternDefect"] for row in shore_rows) == 50

    result = {
        "schema": "P5_FIRST_MICRO_FALSIFIER_REPLAY_V1",
        "verdict": "EXACT_MICRO_FALSIFIER_ONE_COPY_PASSES",
        "g6": record["g6"],
        "order": n,
        "graphEdges": [list(e) for e in sorted(graph_edges)],
        "connected": True,
        "triangleFree": True,
        "cutCertificate": cut,
        "familySizes": list(sizes),
        "tupleIndex": record["tupleIndex"],
        "choice": list(indexed_choice),
        "rows": [list(row) for row in rows],
        "activeVertices": sorted(state.active_vertices),
        "quiescentComponents": quiescent_components(ctx, state),
        "sourceCounts": analysis["sourceCounts"],
        "p5Sources": analysis["p5Sources"],
        "demandByOwner": {
            str(owner): {
                "collision": state.collision[owner],
                "hitNeedSlots": state.hit_need[owner],
                "oneDemand": state.collision[owner] + state.hit_need[owner],
                "microDemand": state.collision[owner] + 25 * state.hit_need[owner],
            }
            for owner in state.owners
        },
        "ownerShoreChecks": shore_rows,
        "oneFive": analysis["oneFive"],
        "microFive": analysis["microFive"],
        "recordSha256": record["recordSha256"],
        "sha256": {
            "aggregate": sha256(AGGREGATE),
            "p5Core": sha256(HERE / "p5_core.py"),
            "p5Census": sha256(HERE / "p5_census.py"),
            "replayScript": sha256(Path(__file__)),
        },
    }
    result["canonicalPayloadSha256"] = canonical_sha(result)
    output = HERE / "first_micro_falsifier_replay.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "verdict": result["verdict"],
        "canonicalPayloadSha256": result["canonicalPayloadSha256"],
        "microFive": result["microFive"],
        "oneFive": result["oneFive"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
