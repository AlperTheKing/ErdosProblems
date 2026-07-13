"""Find a real all-weak active cage with no alternative shortest row.

The quantifier is literal: every active owner, active neighbor, and distinct
selected-support neighbor is tested.  Restricting to singleton complete row
families makes the proposed trade conclusion impossible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
for path in (WRITEUP, R32, P5, PHT):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from p5_core import edge, make_graph_context, reconstruct_state  # noqa: E402


def probe_audit(ctx, state):
    support_adj = [set() for _ in range(ctx.n)]
    active_adj = [set() for _ in range(ctx.n)]
    for x, y in state.support:
        support_adj[x].add(y)
        support_adj[y].add(x)
    for x, y in state.demanded_active_edges:
        active_adj[x].add(y)
        active_adj[y].add(x)

    probes = []
    for owner in sorted(state.active_vertices):
        for x in sorted(active_adj[owner]):
            for y in sorted(support_adj[owner]):
                if x == y:
                    continue
                probes.append({
                    "owner": owner,
                    "activeNeighbor": x,
                    "supportNeighbor": y,
                    "pairCount": state.pair[x][y],
                    "sigma": ctx.sigma_pair[x][y],
                })
    all_weak = bool(probes) and all(
        p["pairCount"] == 0 and p["sigma"] in (0, 1) for p in probes
    )
    return probes, all_weak


def analyze(task):
    order, ordinal, g6 = task
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return "noCut", None
    if not info["Mset"] or any(length != 5 for length in info["ell"].values()):
        return "notAllFive", None
    families = shortest_row_families(info)
    if any(len(family) != 1 for family in families):
        return "notSingleton", None
    rows = rows_for_choice(families, (0,) * len(families))
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    state = reconstruct_state(ctx, rows)
    if not state.active_vertices:
        return "inactive", None
    probes, all_weak = probe_audit(ctx, state)
    if not all_weak:
        return "hasNonweakProbe", None
    selected_atoms_in_scope = [
        list(e) for e in sorted(ctx.bad)
        if e[0] in state.active_vertices and e[1] in state.active_vertices
        and state.selected_comp[e[0]] == state.selected_comp[e[1]]
    ]
    record = {
        "order": order,
        "ordinal": ordinal,
        "g6": g6,
        "edges": [list(e) for e in sorted(set(ctx.blue) | set(ctx.bad))],
        "blue": [list(e) for e in sorted(ctx.blue)],
        "bad": [list(e) for e in sorted(ctx.bad)],
        "gamma": info["G"],
        "rowFamilies": [[list(row) for row in family] for family in families],
        "activeEdges": [list(e) for e in sorted(state.demanded_active_edges)],
        "activeVertices": sorted(state.active_vertices),
        "selectedAtomsInScope": selected_atoms_in_scope,
        "probes": probes,
        "allProbesWeakFree": True,
        "allRowFamiliesSingleton": True,
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    record["sha256"] = hashlib.sha256(canonical.encode("ascii")).hexdigest()
    return "witness", record


def chunk_run(chunk):
    counts = Counter()
    witness = None
    for task in chunk:
        status, record = analyze(task)
        counts[status] += 1
        if witness is None and record is not None:
            witness = record
    return counts, witness


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--chunk-size", type=int, default=64)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--output", type=Path, default=HERE / "witness.json")
    args = parser.parse_args()
    graphs, _ = graph6_for_orders(args.n_min, args.n_max)
    by_order = {n: [] for n in range(args.n_min, args.n_max + 1)}
    for g6 in graphs:
        by_order[dec(g6)[0]].append(g6)
    tasks = []
    for order, values in by_order.items():
        if args.limit_graphs is not None:
            values = values[:args.limit_graphs]
        tasks.extend((order, i, g6) for i, g6 in enumerate(values))
    chunks = [tasks[i:i + args.chunk_size] for i in range(0, len(tasks), args.chunk_size)]
    counts = Counter()
    witness = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for local_counts, local_witness in pool.map(chunk_run, chunks):
            counts.update(local_counts)
            if witness is None and local_witness is not None:
                witness = local_witness
                pool.shutdown(wait=False, cancel_futures=True)
                break
    payload = {"counts": dict(sorted(counts.items())), "witness": witness}
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"counts": payload["counts"], "witness": witness and witness["sha256"]}, sort_keys=True))
    return 0 if witness else 2


if __name__ == "__main__":
    raise SystemExit(main())
