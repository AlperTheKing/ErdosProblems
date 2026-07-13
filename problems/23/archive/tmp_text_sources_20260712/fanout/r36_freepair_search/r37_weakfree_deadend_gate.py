"""Corrected R37 weak-free dead-end falsifier gate.

Production common-blue needs sigma({x,y}) >= 2.  This gate classifies every
attachment probe at the canonical minimum-defect row state as sigma 0,
sigma 1, sigma >= 2, detour, or invalid.  A positive-defect canonical state
with sigma<2 is then tested for other P1/P3/P4/P5 owner arcs, another detour,
and every one-coordinate strict defect trade.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
R36_PROOF = ROOT / "tmp" / "fanout" / "r36_freepair_proof"
for path in (WRITEUP, R32, P5, PHT, R36_PROOF):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402
import p5_core as p5  # noqa: E402
import verify_counterexample as sigma1  # noqa: E402


def edge(x, y):
    return (x, y) if x < y else (y, x)


def cut_sigma(ctx, x, y):
    vertices = {x, y}
    d_blue = sum((a in vertices) != (b in vertices) for a, b in ctx.blue)
    d_bad = sum((a in vertices) != (b in vertices) for a, b in ctx.bad)
    return d_blue, d_bad, d_blue - d_bad


def active_components(ctx, state):
    adjacency = {x: [] for x in state.active_vertices}
    for x, y in state.demanded_active_edges:
        adjacency[x].append(y)
        adjacency[y].append(x)
    return adjacency


def classify_probes(ctx, state, families, choice):
    support_neighbors = {v: set() for v in state.active_vertices}
    for x, y in state.support:
        if x in support_neighbors:
            support_neighbors[x].add(y)
        if y in support_neighbors:
            support_neighbors[y].add(x)
    active_adj = active_components(ctx, state)
    counts = Counter()
    weak = []
    detours = []
    invalid = []
    for owner in sorted(state.active_vertices):
        for x in sorted(active_adj[owner]):
            for y in sorted(support_neighbors[owner]):
                if x == y:
                    continue
                covers = []
                for atom, row in enumerate(state.rows):
                    if x in row and y in row:
                        covers.append((atom, row, abs(row.index(x) - row.index(y))))
                if not covers:
                    d_blue, d_bad, sigma = cut_sigma(ctx, x, y)
                    category = "sigmaGe2" if sigma >= 2 else f"sigma{sigma}"
                    if sigma < 0:
                        category = "sigmaNegative"
                    counts[category] += 1
                    if sigma < 2:
                        weak.append({
                            "owner": owner, "activeNeighbor": x,
                            "supportNeighbor": y, "dB": d_blue,
                            "dM": d_bad, "sigma": sigma,
                        })
                    continue
                atom, row, separation = min(covers)
                if separation == 2:
                    i, j = sorted((row.index(x), row.index(y)))
                    replacement = list(row)
                    replacement[i + 1] = owner
                    replacement = tuple(replacement)
                    members = families[atom]
                    if replacement in members and replacement != row:
                        counts["detour"] += 1
                        detours.append({
                            "owner": owner, "activeNeighbor": x,
                            "supportNeighbor": y, "atom": atom,
                            "oldChoice": choice[atom],
                            "replacementChoice": members.index(replacement),
                        })
                    else:
                        invalid.append({"kind": "missingDetour", "owner": owner,
                                        "x": x, "y": y, "atom": atom,
                                        "row": list(row), "replacement": list(replacement)})
                elif separation == 4:
                    counts["shortcut"] += 1
                else:
                    invalid.append({"kind": "badSeparation", "owner": owner,
                                    "x": x, "y": y, "separation": separation})
    return counts, weak, detours, invalid


def raw_other_source_arcs(ctx, state):
    masks = p5.relation_masks(ctx, state)
    merged = {}
    for name in ("p13", "p4", "p5"):
        for source, mask in masks[name].items():
            merged[source] = merged.get(source, 0) | mask
    owner_arcs = Counter()
    for mask in merged.values():
        for index, owner in enumerate(state.owners):
            if mask & (1 << index):
                owner_arcs[owner] += 1
    return owner_arcs, len(merged)


def strict_one_row_trade(ctx, families, choice, old_defect):
    checked = 0
    for atom, family in enumerate(families):
        for replacement in range(len(family)):
            if replacement == choice[atom]:
                continue
            new_choice = list(choice)
            new_choice[atom] = replacement
            rows = rows_for_choice(families, tuple(new_choice))
            result = analyze_collision_only(ctx, rows)
            checked += 1
            if result["collisionDefect"] < old_defect:
                return {
                    "atom": atom, "oldChoice": choice[atom],
                    "newChoice": replacement, "oldDefect": old_defect,
                    "newDefect": result["collisionDefect"], "checked": checked,
                }
    return None


def analyze_graph(task):
    order, ordinal, g6 = task
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return {"order": order, "status": "skipNoCut"}
    if any(length != 5 for length in info["ell"].values()):
        return {"order": order, "status": "skipNotAll5"}
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    best = None
    examined = 0
    for tuple_index, choice in enumerate(itertools.product(*(range(s) for s in sizes))):
        rows = rows_for_choice(families, choice)
        result = analyze_collision_only(ctx, rows)
        examined += 1
        key = (result["collisionDefect"], tuple_index)
        if best is None or key < best[0]:
            best = (key, choice, rows, result)
        if result["collisionDefect"] == 0:
            break
    assert best is not None
    (defect, tuple_index), choice, rows, result = best
    state = p5.reconstruct_state(ctx, rows)
    probe_counts, weak, detours, invalid = classify_probes(ctx, state, families, choice)
    if invalid:
        return {"order": order, "status": "localLemmaFailure", "g6": g6,
                "choice": list(choice), "invalid": invalid}
    record = {
        "order": order, "graphOrdinal": ordinal, "g6": g6,
        "choice": list(choice), "tupleIndex": tuple_index,
        "familySizes": list(sizes), "tupleCount": math.prod(sizes),
        "examinedUntilCanonical": examined, "collisionDefect": defect,
        "collisionDemand": result["collisionDemand"],
        "probeCounts": dict(sorted(probe_counts.items())),
        "weakFree": weak,
    }
    status = "canonicalZero"
    if defect > 0:
        status = "canonicalPositive"
        owner_arcs, source_keys = raw_other_source_arcs(ctx, state)
        trade = strict_one_row_trade(ctx, families, choice, defect)
        weak_owners = sorted({probe["owner"] for probe in weak})
        fallback = {
            "weakOwners": weak_owners,
            "otherSourceArcsByOwner": {str(o): owner_arcs[o] for o in weak_owners},
            "otherSourceKeys": source_keys,
            "detourCount": len(detours),
            "strictOneRowTrade": trade,
        }
        fallback["deadEndCandidate"] = bool(weak) and all(
            owner_arcs[o] == 0 for o in weak_owners
        ) and not detours and trade is None
        record["fallback"] = fallback
        if fallback["deadEndCandidate"]:
            status = "canonicalDeadEndCandidate"
    record["recordSha256"] = canonical_sha(record)
    return {"order": order, "status": status, "record": record}


def analyze_chunk(chunk):
    counts = Counter()
    probes = Counter()
    first = {}
    examined = 0
    for task in chunk:
        result = analyze_graph(task)
        status = result["status"]
        counts[status] += 1
        record = result.get("record")
        if record:
            probes.update(record["probeCounts"])
            examined += record["examinedUntilCanonical"]
        first.setdefault(status, result)
    return counts, probes, first, examined


def sigma1_replay():
    sigma1.main()
    d_blue, d_bad, sigma = sigma1.sigma([sigma1.X, sigma1.Y])
    return {
        "order": sigma1.N, "edges": len(sigma1.EDGES),
        "rowFamilySizes": [len(sigma1.ROW_DB[e]) for e in sorted(sigma1.BAD)],
        "owner": sigma1.V, "activeNeighbor": sigma1.X,
        "supportNeighbor": sigma1.Y, "dB": d_blue, "dM": d_bad,
        "sigma": sigma, "commonBlueValid": d_bad + 2 <= d_blue,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    started = time.time()
    replay = sigma1_replay()
    graphs, generated = graph6_for_orders(args.n_min, args.n_max)
    by_order = {n: [] for n in range(args.n_min, args.n_max + 1)}
    for g6 in graphs:
        by_order[dec(g6)[0]].append(g6)
    tasks = []
    stream_sha = {}
    generated_used = {}
    for order, rows in by_order.items():
        if args.limit_graphs:
            rows = rows[:args.limit_graphs]
        generated_used[str(order)] = len(rows)
        stream_sha[str(order)] = hashlib.sha256(
            "".join(g + "\n" for g in rows).encode("ascii")
        ).hexdigest()
        tasks.extend((order, i, g) for i, g in enumerate(rows))
    chunks = [tasks[i:i + args.chunk_size] for i in range(0, len(tasks), args.chunk_size)]
    counts = Counter()
    probes = Counter()
    first = {}
    examined = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result_counts, result_probes, result_first, result_examined in pool.map(analyze_chunk, chunks):
            counts.update(result_counts)
            probes.update(result_probes)
            examined += result_examined
            for status, candidate in result_first.items():
                first.setdefault(status, candidate)
    witness = first.get("canonicalDeadEndCandidate") or first.get("localLemmaFailure")
    payload = {
        "schema": "R37_WEAK_FREE_DEADEND_GATE_V1",
        "productionCommonBlueThreshold": "sigma >= 2",
        "sigma1WitnessReplay": replay,
        "orders": [args.n_min, args.n_max], "workers": args.workers,
        "generatedByOrder": generated_used, "graphStreamSha256": stream_sha,
        "counts": dict(sorted(counts.items())),
        "canonicalTuplesExamined": examined,
        "probeCounts": dict(sorted(probes.items())),
        "firstCanonicalPositive": first.get("canonicalPositive"),
        "exactWitness": witness,
        "verdict": "EXACT_CANONICAL_DEADEND_FOUND" if witness else "ZERO_CANONICAL_DEADEND",
        "elapsedSeconds": round(time.time() - started, 6),
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"verdict": payload["verdict"], "counts": payload["counts"],
                      "probes": payload["probeCounts"],
                      "sha256": payload["canonicalPayloadSha256"]}, sort_keys=True))
    return 2 if witness else 0


if __name__ == "__main__":
    raise SystemExit(main())
