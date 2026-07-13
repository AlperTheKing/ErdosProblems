"""Exact order-12 stress gate for the compiled common-blue terminal.

Coverage matches the accepted N12 medium/heavy direct gate: 18,961,358 row
tuples.  The old relation is evaluated first; only its Hall failures are
re-evaluated after adding CheckedC5BaseTransfer.Valid owner arcs.
"""

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


def make_common_blue_flow():
    """Inject one explicit relation block into the pinned production gate."""
    source = inspect.getsource(flow_base.full_owner_flow)
    marker = "        # Outside-component attachment sources.  These cells are never active.\n"
    assert source.count(marker) == 1
    addition = """        # Compiled CheckedC5BaseTransfer.TerminalData.Valid relation:
        # source vertices are distinct free blue neighbors of the owner and
        # dB({x,y}) - dM({x,y}) >= 2.
        for x in blue_adj[owner]:
            for y in blue_adj[owner]:
                if x != y and counts.get((x, y), 0) == 0 and loss({x, y}) >= 2:
                    owner_cell_arcs.add((owner_index, get_cell(x, y)))

"""
    patched = source.replace(marker, addition + marker)
    namespace = dict(vars(flow_base))
    exec(compile(patched, "<common_blue_full_owner_flow>", "exec"), namespace)
    return namespace["full_owner_flow"], hashlib.sha256(
        patched.encode("utf-8")
    ).hexdigest()


COMMON_BLUE_FLOW, PATCHED_FLOW_SHA = make_common_blue_flow()


def analyze_graph(task: tuple[str, str]) -> dict:
    g6, band = task
    n_vertices, edges = n12.dec(g6)
    info = n12.loads(n_vertices, edges)
    assert info is not None and all(length == 5 for length in info["ell"].values())
    families = n12.shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    tuple_count = math.prod(sizes)

    old_failures = 0
    repaired = 0
    remaining = 0
    old_defect_hist = Counter()
    new_defect_hist = Counter()
    first_remaining = None
    first_repaired = None
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = n12.rows_for_choice(families, choice)
        score = n12.scoped_score(n_vertices, info, rows)
        if score == 0:
            continue
        old = flow_base.full_owner_flow(
            n_vertices, set(info["Bset"]), set(info["Mset"]), rows, g6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        if old["full"]:
            continue
        old_failures += 1
        old_defect_hist[old["deficiency"]] += 1
        new = COMMON_BLUE_FLOW(
            n_vertices, set(info["Bset"]), set(info["Mset"]), rows, g6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        record = {
            "g6": g6,
            "band": band,
            "tupleIndex": tuple_index,
            "choice": list(choice),
            "familySizes": list(sizes),
            "oldDefect": old["deficiency"],
            "newDefect": new["deficiency"],
            "oldOwners": old["deficientOwners"],
            "newOwners": new["deficientOwners"],
        }
        if new["full"]:
            repaired += 1
            if first_repaired is None:
                first_repaired = record
        else:
            remaining += 1
            new_defect_hist[new["deficiency"]] += 1
            if first_remaining is None:
                first_remaining = record
    assert old_failures == repaired + remaining
    return {
        "g6": g6,
        "band": band,
        "tuples": tuple_count,
        "oldFailures": old_failures,
        "repaired": repaired,
        "remaining": remaining,
        "oldDefectHistogram": dict(sorted(old_defect_hist.items())),
        "newDefectHistogram": dict(sorted(new_defect_hist.items())),
        "firstRepaired": first_repaired,
        "firstRemaining": first_remaining,
    }


def main() -> None:
    workers = min(32, os.cpu_count() or 1)
    graph6, generated_by_order = n12.graph6_for_orders(12, 12)
    assert len(graph6) == n12.EXPECTED["generated"]
    tasks, preflight = n12.candidate_census(graph6, workers)
    assert preflight["bands"]["medium"]["tuples"] == n12.EXPECTED["mediumTuples"]
    assert preflight["bands"]["heavy"]["tuples"] == n12.EXPECTED["heavyTuples"]

    totals = {
        "graphs": 0,
        "tuples": 0,
        "oldFailures": 0,
        "repaired": 0,
        "remaining": 0,
    }
    old_hist = Counter()
    new_hist = Counter()
    first_repaired = None
    first_remaining = None
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(analyze_graph, tasks, chunksize=1):
            totals["graphs"] += 1
            totals["tuples"] += result["tuples"]
            totals["oldFailures"] += result["oldFailures"]
            totals["repaired"] += result["repaired"]
            totals["remaining"] += result["remaining"]
            old_hist.update({int(k): v for k, v in result["oldDefectHistogram"].items()})
            new_hist.update({int(k): v for k, v in result["newDefectHistogram"].items()})
            if first_repaired is None and result["firstRepaired"] is not None:
                first_repaired = result["firstRepaired"]
            if first_remaining is None and result["firstRemaining"] is not None:
                first_remaining = result["firstRemaining"]

    assert totals["tuples"] == (
        n12.EXPECTED["mediumTuples"] + n12.EXPECTED["heavyTuples"]
    )
    assert totals["oldFailures"] == (
        n12.EXPECTED["mediumFailures"] + n12.EXPECTED["heavyFailures"]
    )
    assert totals["oldFailures"] == totals["repaired"] + totals["remaining"]
    stream_sha = hashlib.sha256(
        "".join(f"{g}\n" for g in graph6).encode("ascii")
    ).hexdigest()
    result = {
        "schema": "N12_COMMON_BLUE_REPAIR_V1",
        "workers": workers,
        "coverage": {
            "generatedGraphs": len(graph6),
            "generatedByOrder": generated_by_order,
            "mediumHeavyGraphs": len(tasks),
            "mediumHeavyTuples": totals["tuples"],
            "oldFailuresExpected": totals["oldFailures"],
            "oldPassingTuplesRemainPassingByRelationMonotonicity": True,
        },
        "totals": totals,
        "oldDefectHistogram": dict(sorted(old_hist.items())),
        "remainingDefectHistogram": dict(sorted(new_hist.items())),
        "firstRepaired": first_repaired,
        "firstRemaining": first_remaining,
        "verdict": "PASS_ALL_OLD_FAILURES_REPAIRED" if totals["remaining"] == 0 else "REMAINING_FAILURES",
        "sha256": {
            "graph6Stream": stream_sha,
            "pinnedN12Gate": sha256(PHT_DIR / "n12_pht.py"),
            "pinnedOwnerFlow": sha256(WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py"),
            "patchedFlowSource": PATCHED_FLOW_SHA,
            "checkedC5BaseTransferLean": sha256(ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean"),
        },
    }
    out = HERE / "n12_common_blue_gate.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
