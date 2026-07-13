"""Exact N=12 medium/heavy gate for bank-scale common-blue matching."""

from __future__ import annotations

import hashlib
import inspect
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
PHT_DIR = ROOT / "tmp/fanout/pht_n12_direct"
WRITEUP = ROOT / "problems/23/writeup"
sys.path.insert(0, str(PHT_DIR))
sys.path.insert(0, str(WRITEUP))

import n12_pht as n12
import _codex_r23_outside_attachment_full_obligation_gate as flow_base


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_micro_common_blue_flow():
    source = inspect.getsource(flow_base.full_owner_flow)
    demand_old = "v: collision[v] + hitneed[v]"
    demand_new = "v: collision[v] + 25 * hitneed[v]"
    assert source.count(demand_old) == 1
    source = source.replace(demand_old, demand_new)
    marker = "        # Outside-component attachment sources.  These cells are never active.\n"
    assert source.count(marker) == 1
    addition = """        # Corrected common-blue terminal: literal Valid predicate.
        for x in blue_adj[owner]:
            for y in blue_adj[owner]:
                if x != y and counts.get((x, y), 0) == 0 and loss({x, y}) >= 2:
                    owner_cell_arcs.add((owner_index, get_cell(x, y)))

"""
    source = source.replace(marker, addition + marker)
    namespace = dict(vars(flow_base))
    exec(compile(source, "<micro_common_blue_flow>", "exec"), namespace)
    return namespace["full_owner_flow"], hashlib.sha256(source.encode()).hexdigest()


MICRO_FLOW, PATCHED_FLOW_SHA = make_micro_common_blue_flow()


def analyze_graph(task: tuple[str, str]) -> dict:
    g6, band = task
    n_vertices, edges = n12.dec(g6)
    info = n12.loads(n_vertices, edges)
    assert info is not None and all(length == 5 for length in info["ell"].values())
    families = n12.shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    tuple_count = math.prod(sizes)
    tested = 0
    positive_hitneed = 0
    failures = 0
    defect_hist = Counter()
    first_failure = None
    max_hitneed = 0
    max_demand = 0
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = n12.rows_for_choice(families, choice)
        if n12.scoped_score(n_vertices, info, rows) == 0:
            continue
        tested += 1
        flow = MICRO_FLOW(
            n_vertices,
            set(info["Bset"]),
            set(info["Mset"]),
            rows,
            g6,
            require_full=False,
            quiet=True,
            scope="active",
            include_outside=False,
        )
        max_hitneed = max(max_hitneed, flow["hitNeed"])
        max_demand = max(max_demand, flow["totalDemand"])
        if flow["hitNeed"] > 0:
            positive_hitneed += 1
        if flow["full"]:
            continue
        failures += 1
        defect_hist[flow["deficiency"]] += 1
        if first_failure is None:
            first_failure = {
                "g6": g6,
                "band": band,
                "tupleIndex": tuple_index,
                "choice": list(choice),
                "familySizes": list(sizes),
                "defect": flow["deficiency"],
                "owners": flow["deficientOwners"],
                "collisionDemand": flow["collisionDemand"],
                "hitNeedSlots": flow["hitNeed"],
                "microDemand": flow["totalDemand"],
                "maxFlow": flow["maxFlow"],
            }
    return {
        "g6": g6,
        "band": band,
        "tuples": tuple_count,
        "tested": tested,
        "positiveHitNeed": positive_hitneed,
        "failures": failures,
        "defectHistogram": dict(sorted(defect_hist.items())),
        "firstFailure": first_failure,
        "maxHitNeedSlots": max_hitneed,
        "maxMicroDemand": max_demand,
    }


def main() -> None:
    # Python's Windows ProcessPoolExecutor hard-caps workers at 61.
    workers = min(61, os.cpu_count() or 1)
    graph6, generated_by_order = n12.graph6_for_orders(12, 12)
    assert len(graph6) == n12.EXPECTED["generated"]
    tasks, preflight = n12.candidate_census(graph6, workers)
    expected_tuples = n12.EXPECTED["mediumTuples"] + n12.EXPECTED["heavyTuples"]
    assert sum(preflight["bands"][band]["tuples"] for band in ("medium", "heavy")) == expected_tuples

    totals = Counter()
    defects = Counter()
    first_failure = None
    max_hitneed = 0
    max_demand = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(analyze_graph, tasks, chunksize=1):
            totals["graphs"] += 1
            for key in ("tuples", "tested", "positiveHitNeed", "failures"):
                totals[key] += result[key]
            defects.update({int(k): v for k, v in result["defectHistogram"].items()})
            max_hitneed = max(max_hitneed, result["maxHitNeedSlots"])
            max_demand = max(max_demand, result["maxMicroDemand"])
            if first_failure is None and result["firstFailure"] is not None:
                first_failure = result["firstFailure"]
    assert totals["graphs"] == len(tasks)
    assert totals["tuples"] == expected_tuples

    result = {
        "schema": "N12_COMMON_BLUE_MICRO_MEDIUM_HEAVY_V1",
        "workers": workers,
        "coverage": {
            "generatedGraphs": len(graph6),
            "generatedByOrder": generated_by_order,
            "mediumHeavyGraphs": len(tasks),
            "mediumHeavyTuples": expected_tuples,
        },
        "totals": dict(totals),
        "defectHistogram": dict(sorted(defects.items())),
        "firstFailure": first_failure,
        "maxHitNeedSlots": max_hitneed,
        "maxMicroDemand": max_demand,
        "verdict": "PASS_ZERO_FAILURES" if totals["failures"] == 0 else "FAILURES_FOUND",
        "sha256": {
            "graph6Stream": hashlib.sha256(
                "".join(f"{g}\n" for g in graph6).encode()
            ).hexdigest(),
            "pinnedN12Gate": sha256(PHT_DIR / "n12_pht.py"),
            "pinnedOwnerFlow": sha256(
                WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py"
            ),
            "patchedFlowSource": PATCHED_FLOW_SHA,
            "checkedC5BaseTransferLean": sha256(
                ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean"
            ),
        },
    }
    out = HERE / "n12_common_blue_micro_result.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
