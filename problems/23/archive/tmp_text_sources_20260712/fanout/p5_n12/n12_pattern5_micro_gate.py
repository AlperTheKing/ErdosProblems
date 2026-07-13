"""Exact N=12 medium/heavy gate for the reservation-free five-pattern relation."""

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


def make_micro_pattern5_flow():
    source = inspect.getsource(flow_base.full_owner_flow)
    demand_old = "v: collision[v] + hitneed[v]"
    demand_new = "v: collision[v] + 25 * hitneed[v]"
    assert source.count(demand_old) == 1
    source = source.replace(demand_old, demand_new)

    setup_marker = "    def loss(vertices):\n"
    assert source.count(setup_marker) == 1
    setup = '''    # Pattern 5: blue components outside the ACTIVE scope, not outside
    # the selected-row union.  Each component records its active boundary.
    quiet_component_id = [-1] * n_vertices
    quiet_components = []
    quiet_attachments = []
    for root in range(n_vertices):
        if root in active_vertices or quiet_component_id[root] >= 0:
            continue
        cid = len(quiet_components)
        vertices = set()
        attachment = set()
        quiet_component_id[root] = cid
        queue = deque([root])
        while queue:
            x = queue.popleft()
            vertices.add(x)
            for y in blue_adj[x]:
                if y in active_vertices:
                    attachment.add(y)
                elif quiet_component_id[y] < 0:
                    quiet_component_id[y] = cid
                    queue.append(y)
        quiet_components.append(vertices)
        quiet_attachments.append(attachment)

    eligible_quiet = {}
    for owner in owners:
        eligible = set()
        owner_root = find(owner)
        for cid, component in enumerate(quiet_components):
            if any(
                counts.get((owner, a), 0) > 0 and find(a) == owner_root
                for a in quiet_attachments[cid]
            ):
                eligible.update(component)
        eligible_quiet[owner] = eligible

'''
    source = source.replace(setup_marker, setup + setup_marker)

    source_marker = "        # Outside-component attachment sources.  These cells are never active.\n"
    assert source.count(source_marker) == 1
    source_block = '''        # Pattern 5: pair-free ordered sources in quiescent components whose
        # active boundaries both attach to selected companions of the owner.
        quiet = sorted(eligible_quiet[owner])
        quiet_loss_cache = {}
        for x in quiet:
            for y in quiet:
                if x == y or counts.get((x, y), 0) != 0:
                    continue
                pair = (quiet_component_id[x], quiet_component_id[y])
                if pair not in quiet_loss_cache:
                    quiet_loss_cache[pair] = loss(
                        quiet_components[pair[0]] | quiet_components[pair[1]]
                    ) >= 0
                if quiet_loss_cache[pair]:
                    owner_cell_arcs.add((owner_index, get_cell(x, y)))

'''
    source = source.replace(source_marker, source_block + source_marker)

    record_marker = '        "eligibleOutsideByOwner": {\n'
    assert source.count(record_marker) == 1
    record_block = '''        "eligibleQuiescentByOwner": {
            str(v): len(eligible_quiet[v]) for v in owners
            if eligible_quiet[v]
        },
'''
    source = source.replace(record_marker, record_block + record_marker)

    namespace = dict(vars(flow_base))
    exec(compile(source, "<micro_pattern5_flow>", "exec"), namespace)
    return namespace["full_owner_flow"], hashlib.sha256(source.encode()).hexdigest()


MICRO_FLOW, PATCHED_FLOW_SHA = make_micro_pattern5_flow()


def analyze_graph(task: tuple[str, str]) -> dict:
    g6, band = task
    n_vertices, edges = n12.dec(g6)
    info = n12.loads(n_vertices, edges)
    assert info is not None and all(length == 5 for length in info["ell"].values())
    families = n12.shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    tuple_count = math.prod(sizes)
    tested = failures = positive_hitneed = 0
    defect_hist = Counter()
    first_failure = None
    max_hitneed = max_demand = 0
    for tuple_index, choice in enumerate(itertools.product(*(range(size) for size in sizes))):
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
            include_outside=True,
        )
        max_hitneed = max(max_hitneed, flow["hitNeed"])
        max_demand = max(max_demand, flow["totalDemand"])
        positive_hitneed += flow["hitNeed"] > 0
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
                "eligibleQuiescentByOwner": flow["eligibleQuiescentByOwner"],
                "eligibleOutsideByOwner": flow["eligibleOutsideByOwner"],
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
    workers = min(61, os.cpu_count() or 1)
    graph6, generated_by_order = n12.graph6_for_orders(12, 12)
    assert len(graph6) == n12.EXPECTED["generated"]
    tasks, preflight = n12.candidate_census(graph6, workers)
    expected_tuples = n12.EXPECTED["mediumTuples"] + n12.EXPECTED["heavyTuples"]
    assert sum(preflight["bands"][band]["tuples"] for band in ("medium", "heavy")) == expected_tuples

    totals = Counter()
    defects = Counter()
    first_failure = None
    max_hitneed = max_demand = 0
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

    result = {
        "schema": "N12_PATTERN5_MICRO_MEDIUM_HEAVY_V1",
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
            "graph6Stream": hashlib.sha256("".join(f"{g}\n" for g in graph6).encode()).hexdigest(),
            "pinnedN12Gate": sha256(PHT_DIR / "n12_pht.py"),
            "pinnedOwnerFlow": sha256(WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py"),
            "patchedFlowSource": PATCHED_FLOW_SHA,
            "pattern5FixtureGate": sha256(WRITEUP / "_claude_r29_pattern5_gate.py"),
        },
    }
    out = HERE / "n12_pattern5_micro_result.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
