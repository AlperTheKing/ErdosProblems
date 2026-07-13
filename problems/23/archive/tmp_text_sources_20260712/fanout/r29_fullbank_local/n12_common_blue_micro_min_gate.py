"""Exact N=12 gate for minimum-micro-demand common-blue row choices."""

from __future__ import annotations

import itertools
import json
import math
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import n12_common_blue_micro_gate as base


HERE = Path(__file__).resolve().parent


def analyze_graph(task: tuple[str, str]) -> dict:
    g6, band = task
    n, edges = base.n12.dec(g6)
    info = base.n12.loads(n, edges)
    assert info is not None and all(v == 5 for v in info["ell"].values())
    families = base.n12.shortest_row_families(info)
    sizes = tuple(map(len, families))
    tuple_count = math.prod(sizes)
    blue, bad = set(info["Bset"]), set(info["Mset"])

    minimum = None
    minimum_choices = []
    examined = 0
    zero_witness = None
    for index, choice in enumerate(itertools.product(*(range(s) for s in sizes))):
        examined += 1
        rows = base.n12.rows_for_choice(families, choice)
        collision, hit_need = base.flow_base.active_scoped_obligation_parts(
            n, blue, bad, rows
        )
        score = collision + 25 * hit_need
        if minimum is None or score < minimum:
            minimum = score
            minimum_choices = [(index, choice, collision, hit_need)]
        elif score == minimum:
            minimum_choices.append((index, choice, collision, hit_need))
        if score == 0:
            zero_witness = (index, choice)
            break

    assert minimum is not None
    if minimum == 0:
        assert zero_witness is not None
        return {
            "g6": g6,
            "band": band,
            "tuples": tuple_count,
            "examined": examined,
            "minimum": 0,
            "minimumChoicesChecked": 1,
            "minimumFailures": 0,
            "minimumPasses": 1,
            "allMinimumPass": True,
            "someMinimumPass": True,
            "firstFailure": None,
            "firstPass": {
                "tupleIndex": zero_witness[0],
                "choice": list(zero_witness[1]),
                "zeroDemand": True,
            },
        }

    failures = 0
    passes = 0
    first_failure = None
    first_pass = None
    for index, choice, collision, hit_need in minimum_choices:
        rows = base.n12.rows_for_choice(families, choice)
        flow = base.MICRO_FLOW(
            n, blue, bad, rows, g6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        assert flow["totalDemand"] == minimum
        record = {
            "tupleIndex": index,
            "choice": list(choice),
            "collision": collision,
            "hitNeedSlots": hit_need,
            "demand": minimum,
            "flow": flow["maxFlow"],
            "defect": flow["deficiency"],
            "owners": flow["deficientOwners"],
        }
        if flow["full"]:
            passes += 1
            if first_pass is None:
                first_pass = record
        else:
            failures += 1
            if first_failure is None:
                first_failure = record
    return {
        "g6": g6,
        "band": band,
        "tuples": tuple_count,
        "examined": examined,
        "minimum": minimum,
        "minimumChoicesChecked": len(minimum_choices),
        "minimumFailures": failures,
        "minimumPasses": passes,
        "allMinimumPass": failures == 0,
        "someMinimumPass": passes > 0,
        "firstFailure": first_failure,
        "firstPass": first_pass,
    }


def main() -> None:
    workers = min(61, os.cpu_count() or 1)
    graph6, generated = base.n12.graph6_for_orders(12, 12)
    tasks, preflight = base.n12.candidate_census(graph6, workers)
    totals = Counter()
    minimum_hist = Counter()
    first_no_passing_min = None
    first_failing_min = None
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(analyze_graph, tasks, chunksize=1):
            totals["graphs"] += 1
            totals["tuples"] += result["tuples"]
            totals["examined"] += result["examined"]
            totals["minimumChoicesChecked"] += result["minimumChoicesChecked"]
            totals["minimumFailures"] += result["minimumFailures"]
            totals["minimumPasses"] += result["minimumPasses"]
            totals["graphsWithFailingMinimum"] += int(not result["allMinimumPass"])
            totals["graphsWithoutPassingMinimum"] += int(not result["someMinimumPass"])
            minimum_hist[result["minimum"]] += 1
            if first_failing_min is None and not result["allMinimumPass"]:
                first_failing_min = result
            if first_no_passing_min is None and not result["someMinimumPass"]:
                first_no_passing_min = result
    expected = base.n12.EXPECTED["mediumTuples"] + base.n12.EXPECTED["heavyTuples"]
    assert totals["graphs"] == len(tasks)
    assert totals["tuples"] == expected
    result = {
        "schema": "N12_COMMON_BLUE_MICRO_MINIMUM_V1",
        "workers": workers,
        "coverage": {
            "generatedGraphs": len(graph6),
            "generatedByOrder": generated,
            "mediumHeavyGraphs": len(tasks),
            "mediumHeavyTuples": expected,
            "earlyStopRule": "a zero score proves the exact global minimum and passes vacuously",
        },
        "totals": dict(totals),
        "minimumHistogram": dict(sorted(minimum_hist.items())),
        "firstFailingMinimum": first_failing_min,
        "firstNoPassingMinimum": first_no_passing_min,
        "verdict": (
            "PASS_EVERY_GRAPH_HAS_PASSING_MINIMUM"
            if totals["graphsWithoutPassingMinimum"] == 0
            else "FAIL_GRAPH_WITHOUT_PASSING_MINIMUM"
        ),
    }
    out = HERE / "n12_common_blue_micro_min_result.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
