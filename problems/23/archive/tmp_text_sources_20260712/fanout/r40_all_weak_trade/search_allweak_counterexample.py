"""Exact universal-weak probe and all one-row replacement gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for path in (
    ROOT / "problems" / "23" / "writeup",
    ROOT / "tmp" / "fanout" / "r32_n12_fullbank",
    ROOT / "tmp" / "fanout" / "p5_n12_census",
    ROOT / "tmp" / "fanout" / "pht_n12_direct",
):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import analyze_collision_only  # noqa: E402
from p5_core import make_graph_context, reconstruct_state  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "singleton_gate", HERE / "search_singleton_counterexample.py"
)
singleton_gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(singleton_gate)


def analyze(task):
    order, ordinal, g6 = task
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or not info["Mset"]:
        return "noCut", None
    if any(length != 5 for length in info["ell"].values()):
        return "notAllFive", None
    families = shortest_row_families(info)
    choice = (0,) * len(families)
    rows = rows_for_choice(families, choice)
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    state = reconstruct_state(ctx, rows)
    if not state.active_vertices:
        return "inactive", None
    probes, all_weak = singleton_gate.probe_audit(ctx, state)
    if not all_weak:
        return "nonweak", None

    old = analyze_collision_only(ctx, rows)["collisionDefect"]
    scoped_atoms = [
        i for i, (x, y) in enumerate(sorted(ctx.bad))
        if x in state.active_vertices and y in state.active_vertices
        and state.selected_comp[x] == state.selected_comp[y]
    ]
    replacements = []
    conclusion = False
    for atom in scoped_atoms:
        for replacement in range(1, len(families[atom])):
            new_choice = list(choice)
            new_choice[atom] = replacement
            new_rows = rows_for_choice(families, tuple(new_choice))
            new_state = reconstruct_state(ctx, new_rows)
            new_defect = analyze_collision_only(ctx, new_rows)["collisionDefect"]
            vacates = not new_state.active_vertices
            lowers = new_defect < old
            replacements.append({
                "atom": atom,
                "oldRow": list(families[atom][0]),
                "newRow": list(families[atom][replacement]),
                "newDefect": new_defect,
                "lowers": lowers,
                "vacatesScope": vacates,
            })
            conclusion |= lowers or vacates
    if conclusion:
        return "conclusionHolds", None
    record = {
        "order": order, "ordinal": ordinal, "g6": g6,
        "blue": [list(e) for e in sorted(ctx.blue)],
        "bad": [list(e) for e in sorted(ctx.bad)],
        "gamma": info["G"],
        "choice": list(choice),
        "families": [[list(row) for row in family] for family in families],
        "activeEdges": [list(e) for e in sorted(state.demanded_active_edges)],
        "activeVertices": sorted(state.active_vertices),
        "probes": probes,
        "oldDefect": old,
        "scopedAtoms": scoped_atoms,
        "replacements": replacements,
    }
    return "counterexample", record


def chunk_run(chunk):
    counts = Counter()
    witness = None
    for task in chunk:
        status, record = analyze(task)
        counts[status] += 1
        if witness is None and record is not None:
            witness = record
            break
    return counts, witness


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--chunk-size", type=int, default=128)
    parser.add_argument("--output", type=Path, default=HERE / "allweak_witness.json")
    args = parser.parse_args()
    graphs, _ = graph6_for_orders(args.n_min, args.n_max)
    by_order = {n: [] for n in range(args.n_min, args.n_max + 1)}
    for g6 in graphs:
        by_order[dec(g6)[0]].append(g6)
    tasks = [(n, i, g) for n, gs in by_order.items() for i, g in enumerate(gs)]
    chunks = [tasks[i:i + args.chunk_size] for i in range(0, len(tasks), args.chunk_size)]
    counts = Counter()
    witness = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for local_counts, candidate in pool.map(chunk_run, chunks):
            counts.update(local_counts)
            if candidate is not None:
                witness = candidate
                pool.shutdown(wait=False, cancel_futures=True)
                break
    payload = {"counts": dict(sorted(counts.items())), "witness": witness}
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"counts": payload["counts"], "witness": witness and witness["g6"]}, sort_keys=True))
    return 0 if witness else 2


if __name__ == "__main__":
    raise SystemExit(main())
