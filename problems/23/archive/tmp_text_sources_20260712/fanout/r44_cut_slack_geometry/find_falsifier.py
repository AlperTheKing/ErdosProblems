"""Find a live detour whose two endpoint common-blue sources are both weak.

The search is exact and uses the same connected Gamma-minimum maximum cut,
complete length-five row families, active-owner semantics, and collision-only
production matching defect as the R40 strong-probe census.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R40 = ROOT / "tmp" / "fanout" / "r40_strong_probe_census"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
WRITEUP = ROOT / "problems" / "23" / "writeup"
for path in (R40, R32, P5, PHT, WRITEUP):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice
from collision_only_core import canonical_sha
from strong_probe_census import (
    active_adjacency,
    matching_analysis,
    row_edges,
    singleton_sigma,
    support_adjacency,
)
import p5_core as p5


SCHEMA = "R44_LIVE_DETOUR_ENDPOINT_SLACK_FALSIFIER_V1"


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def exact_maxcut(n: int, edges: set[tuple[int, int]]) -> tuple[int, int]:
    best = -1
    multiplicity = 0
    for mask in range(1 << n):
        cut = sum(((mask >> x) & 1) != ((mask >> y) & 1) for x, y in edges)
        if cut > best:
            best = cut
            multiplicity = 1
        elif cut == best:
            multiplicity += 1
    return best, multiplicity


def triangle_free(n: int, edges: set[tuple[int, int]]) -> bool:
    adjacency = [set() for _ in range(n)]
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    return all(not (adjacency[x] & adjacency[y]) for x, y in edges)


def live_weak_detours(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    families: tuple[tuple[tuple[int, ...], ...], ...],
    choice: tuple[int, ...],
    *,
    require_collision: bool,
) -> list[dict]:
    out: list[dict] = []
    active_adj = active_adjacency(state)
    support_adj = support_adjacency(state)
    owners = state.owners if require_collision else tuple(sorted(state.active_vertices))
    for owner in owners:
        if require_collision and state.collision[owner] == 0:
            continue
        for x in active_adj[owner]:
            for y in support_adj[owner]:
                if x == y or state.pair[x][y] == 0:
                    continue
                for atom, row in enumerate(state.rows):
                    if x not in row or y not in row:
                        continue
                    ix, iy = row.index(x), row.index(y)
                    if abs(ix - iy) != 2:
                        continue
                    left = min(ix, iy)
                    replacement = list(row)
                    middle = replacement[left + 1]
                    replacement[left + 1] = owner
                    replacement = tuple(replacement)
                    if replacement == row or replacement not in families[atom]:
                        continue
                    a, b = row[0], row[-1]
                    sigma_ma = ctx.sigma_pair[middle][a]
                    sigma_mb = ctx.sigma_pair[middle][b]
                    if sigma_ma >= 2 or sigma_mb >= 2:
                        continue
                    out.append({
                        "owner": owner,
                        "ownerCollision": state.collision[owner],
                        "ownerHitNeed": state.hit_need[owner],
                        "activeNeighbor": x,
                        "supportNeighbor": y,
                        "atom": atom,
                        "selectedRowIndex": choice[atom],
                        "Q": list(row),
                        "Qprime": list(replacement),
                        "a": a,
                        "m": middle,
                        "b": b,
                        "singletonSigma": {
                            str(vertex): singleton_sigma(ctx, vertex)
                            for vertex in (middle, a, b)
                        },
                        "sigmaMA": sigma_ma,
                        "sigmaMB": sigma_mb,
                        "activeEdge": list(edge(owner, x)),
                        "supportEdge": list(edge(owner, y)),
                        "activeEdgeAbsentSupport": edge(owner, x) not in state.support,
                        "supportEdgePresent": edge(owner, y) in state.support,
                    })
    return out


def analyze_graph(
    order: int, ordinal: int, g6: str, *, require_collision: bool
) -> dict | None:
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])

    minimum: int | None = None
    minimizers: list[tuple[int, tuple[int, ...], p5.TupleState, dict]] = []
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        state = p5.reconstruct_state(ctx, rows_for_choice(families, choice))
        matching = matching_analysis(ctx, state)
        defect = matching["defect"]
        if minimum is None or defect < minimum:
            minimum = defect
            minimizers = [(tuple_index, choice, state, matching)]
        elif defect == minimum:
            minimizers.append((tuple_index, choice, state, matching))

    for tuple_index, choice, state, matching in minimizers:
        candidates = live_weak_detours(
            ctx, state, families, choice, require_collision=require_collision
        )
        if not candidates:
            continue
        candidate = candidates[0]
        graph_edge_set = {edge(x, y) for x, y in graph_edges}
        best_cut, maxcut_multiplicity = exact_maxcut(n, graph_edge_set)
        displayed_cut = len(info["Bset"])
        record = {
            "schema": SCHEMA,
            "order": order,
            "graphOrdinal": ordinal,
            "g6": g6,
            "triangleFree": triangle_free(n, graph_edge_set),
            "edges": [list(item) for item in sorted(graph_edge_set)],
            "blue": [list(item) for item in sorted(info["Bset"])],
            "bad": [list(item) for item in sorted(info["Mset"])],
            "displayedCutSize": displayed_cut,
            "exactMaximumCutSize": best_cut,
            "maximumCutMultiplicity": maxcut_multiplicity,
            "gamma": sum(length * length for length in info["ell"].values()),
            "allBadLengths": [info["ell"][item] for item in info["M"]],
            "familySizes": list(sizes),
            "completeRowDB": [[list(row) for row in family] for family in families],
            "rowTupleCount": math.prod(sizes),
            "minimumProductionDefect": minimum,
            "minimumTupleCount": len(minimizers),
            "tupleIndex": tuple_index,
            "choice": list(choice),
            "selectedRows": [list(row) for row in state.rows],
            "matching": matching,
            "activeVertices": sorted(state.active_vertices),
            "demandOwners": list(state.owners),
            "support": [list(item) for item in sorted(state.support)],
            "demandedActiveEdges": [
                list(item) for item in sorted(state.demanded_active_edges)
            ],
            "candidate": candidate,
        }
        record["recordSha256"] = canonical_sha(record)
        return record
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--allow-noncollision-owner", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, _ = graph6_for_orders(args.n_min, args.n_max)
    ordinal_by_order: dict[int, int] = {}
    seen = 0
    for g6 in rows:
        order = dec(g6)[0]
        ordinal = ordinal_by_order.get(order, 0)
        ordinal_by_order[order] = ordinal + 1
        if args.limit_graphs is not None and seen >= args.limit_graphs:
            break
        seen += 1
        result = analyze_graph(
            order, ordinal, g6,
            require_collision=not args.allow_noncollision_owner,
        )
        if result is None:
            continue
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "status": "FOUND",
            "graphsScanned": seen,
            "order": order,
            "g6": g6,
            "recordSha256": result["recordSha256"],
        }, sort_keys=True))
        return 0
    print(json.dumps({"status": "NO_HIT", "graphsScanned": seen}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


