"""Exact census of same-shore sources created by support-constant detours.

This is a falsifier gate, not a proof.  It inspects the canonical first
defect-zero row state of every available all-ell=5 graph and classifies each
support-constant one-position row replacement by the production common-blue
threshold and target-owner collision activity.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for path in (WRITEUP, P5, PHT, R32):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402
import p5_core as p5  # noqa: E402


def edge(x, y):
    return (x, y) if x < y else (y, x)


def classify_transition(ctx, old, target, row, replacement, atom, choice, new_index):
    diffs = [i for i, (a, b) in enumerate(zip(row, replacement)) if a != b]
    if len(diffs) != 1 or diffs[0] not in (1, 2, 3):
        return None
    j = diffs[0]
    m, v = row[j], replacement[j]
    entering = {edge(row[j - 1], v), edge(v, row[j + 1])}
    leaving = {edge(row[j - 1], m), edge(m, row[j + 1])}
    if not entering.isdisjoint(old.support):
        return None
    disappearing = {e for e in leaving if e not in target.support}
    if target.support != (old.support - disappearing) | entering:
        raise AssertionError("support identity")
    if len(target.support) != len(old.support):
        return None

    probes = []
    p2 = p5.relation_masks(ctx, target)["p2"]
    owner_index = {owner: i for i, owner in enumerate(target.owners)}
    for k in range(5):
        if k == j or (k - j) % 2:
            continue
        z = row[k]
        if old.pair[m][z] != 1 or target.pair[m][z] != 0:
            continue
        step = 1 if k > j else -1
        common_owner = row[j + step]
        sigma = ctx.sigma_pair[m][z]
        collision_loaded = target.collision.get(common_owner, 0) > 0
        active_owner = common_owner in target.active_vertices
        relation_arc = False
        if common_owner in owner_index:
            bit = 1 << owner_index[common_owner]
            relation_arc = all(
                p2.get(p5.source_id(ctx.n, a, b, half), 0) & bit
                for a, b in ((m, z), (z, m))
                for half in (0, 1)
            )
        probes.append({
            "oldMiddle": m,
            "newMiddle": v,
            "retained": z,
            "commonOwner": common_owner,
            "sigma": sigma,
            "activeOwner": active_owner,
            "collisionDemand": target.collision.get(common_owner, 0),
            "collisionLoaded": collision_loaded,
            "productionP2AllFourHalves": bool(relation_arc),
        })
    return {
        "atom": atom,
        "oldChoice": choice[atom],
        "newChoice": new_index,
        "position": j,
        "oldRow": list(row),
        "newRow": list(replacement),
        "probes": probes,
        "outerPairSaturated": not probes,
        "hasStrong": any(p["sigma"] >= 2 for p in probes),
        "hasLoadedStrong": any(
            p["sigma"] >= 2 and p["collisionLoaded"] and p["activeOwner"]
            for p in probes
        ),
        "hasProductionP2": any(p["productionP2AllFourHalves"] for p in probes),
    }


def analyze_graph(task):
    order, ordinal, g6 = task
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return Counter(skip=1), None
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    chosen = None
    for tuple_index, choice in enumerate(itertools.product(*(range(s) for s in sizes))):
        rows = rows_for_choice(families, choice)
        result = analyze_collision_only(ctx, rows)
        if result["collisionDefect"] == 0:
            chosen = (tuple_index, choice, rows)
            break
    if chosen is None:
        return Counter(positive=1), {
            "order": order, "ordinal": ordinal, "g6": g6,
            "kind": "positiveCanonical",
        }
    tuple_index, choice, rows = chosen
    old = p5.reconstruct_state(ctx, rows)
    counts = Counter(graphs=1)
    first = None
    for atom, family in enumerate(families):
        row = rows[atom]
        for new_index, replacement in enumerate(family):
            if new_index == choice[atom]:
                continue
            new_choice = list(choice)
            new_choice[atom] = new_index
            target_rows = rows_for_choice(families, tuple(new_choice))
            target = p5.reconstruct_state(ctx, target_rows)
            record = classify_transition(
                ctx, old, target, row, replacement, atom, choice, new_index
            )
            if record is None:
                continue
            counts["supportConstantDetours"] += 1
            counts["outerPairSaturated"] += record["outerPairSaturated"]
            counts["strong"] += record["hasStrong"]
            counts["loadedStrong"] += record["hasLoadedStrong"]
            counts["productionP2"] += record["hasProductionP2"]
            counts["allWeak"] += not record["hasStrong"]
            counts["strongButUnloaded"] += (
                record["hasStrong"] and not record["hasLoadedStrong"]
            )
            if first is None and (
                not record["hasStrong"] or not record["hasLoadedStrong"]
            ):
                first = {
                    "order": order,
                    "ordinal": ordinal,
                    "g6": g6,
                    "tupleIndex": tuple_index,
                    "choice": list(choice),
                    "familySizes": list(sizes),
                    "transition": record,
                }
    return counts, first


def analyze_chunk(chunk):
    total = Counter()
    first = None
    for task in chunk:
        counts, candidate = analyze_graph(task)
        total.update(counts)
        if first is None and candidate is not None:
            first = candidate
    return total, first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    graphs, _generated = graph6_for_orders(args.n_min, args.n_max)
    tasks = []
    by_order = Counter()
    stream = hashlib.sha256()
    for g6 in graphs:
        order = dec(g6)[0]
        if args.limit_graphs and by_order[order] >= args.limit_graphs:
            continue
        ordinal = by_order[order]
        by_order[order] += 1
        tasks.append((order, ordinal, g6))
        stream.update((g6 + "\n").encode("ascii"))
    chunks = [tasks[i:i + args.chunk_size]
              for i in range(0, len(tasks), args.chunk_size)]
    counts = Counter()
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for partial, candidate in pool.map(analyze_chunk, chunks):
            counts.update(partial)
            if first is None and candidate is not None:
                first = candidate
    payload = {
        "schema": "R42_OUTER_PAIR_EXPOSURE_CENSUS_V1",
        "orders": [args.n_min, args.n_max],
        "workers": args.workers,
        "graphsByOrder": dict(sorted(by_order.items())),
        "graphStreamSha256": stream.hexdigest(),
        "counts": dict(sorted(counts.items())),
        "firstNonLoadedStrong": first,
        "scope": "canonical first defect-zero tuple per available all-ell=5 graph",
        "claim": "bounded falsifier gate only",
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "counts": payload["counts"],
        "first": first,
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
