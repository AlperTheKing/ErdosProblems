#!/usr/bin/env python3
"""Exact graph-level minimum-defect census for the corrected global model."""

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
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
for path in (HERE, WRITEUP, PHT):
    sys.path.insert(0, str(path))

import global_softcap as soft  # noqa: E402
from _codex_r19_global_base_census import (  # noqa: E402
    dec,
    graph6_for_orders,
    loads,
)
from _codex_r20_two_row_exchange_gate import (  # noqa: E402
    shortest_row_families,
)
from _codex_r23_heavy_alltuple_descent_gate import (  # noqa: E402
    rows_for_choice,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def failure_record(
    order: int,
    ordinal: int,
    g6: str,
    sizes: tuple[int, ...],
    tuple_count: int,
    tuple_index: int,
    choice: tuple[int, ...],
    summary: dict,
) -> dict:
    stage = summary["stages"][-1]
    record = {
        "order": order,
        "graphOrdinal": ordinal,
        "g6": g6,
        "familySizes": list(sizes),
        "tupleCount": tuple_count,
        "minimumTupleIndex": tuple_index,
        "minimumChoice": list(choice),
        "minimumDefect": summary["minimumDefect"],
        "globalDemand": summary["state"]["globalCollisionHalfDemand"],
        "maximumFlow": summary["maximumFlow"],
        "shoreOwners": summary["minCutSourceOwners"],
        "shoreDemand": stage["minCutSourceOwnerDemand"],
        "shoreCapacity": stage["minCutShoreCapacity"],
        "shoreDirectCapacity": stage["minCutShoreDirectCapacity"],
        "shoreActiveCapacity": stage["minCutShoreActiveCapacity"],
        "state": summary["state"],
        "familyStats": summary["familyStats"],
        "stages": summary["stages"],
        "evaluatedFamilies": summary["evaluatedFamilies"],
        "notEnumeratedFamilies": summary["notEnumeratedFamilies"],
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def analyze_graph(task) -> dict:
    order, ordinal, g6, max_tuples = task
    n, graph_edges = dec(g6)
    if n != order:
        raise AssertionError((n, order))
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": order}
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    tuple_count = math.prod(sizes)
    if max_tuples is not None and tuple_count > max_tuples:
        return {
            "status": "skipTupleLimit",
            "order": order,
            "availableTuples": tuple_count,
        }

    ctx = soft.make_graph_context(n, info["Bset"], info["Mset"])
    best = None
    examined = 0
    positive_tuple_failures = 0
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = rows_for_choice(families, choice)
        summary, _ = soft.analyze_global(ctx, rows)
        examined += 1
        defect = summary["minimumDefect"]
        positive_tuple_failures += int(defect > 0)
        candidate = (defect, tuple_index, choice, summary)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
        if defect == 0:
            break
    if best is None:
        raise AssertionError("empty row-choice product")
    defect, tuple_index, choice, summary = best
    result = {
        "status": "tested",
        "order": order,
        "availableTuples": tuple_count,
        "examinedTuples": examined,
        "positiveTupleFailuresBeforeStop": positive_tuple_failures,
        "minimumDefect": defect,
        "zeroFound": defect == 0,
        "exhaustedAllTuples": examined == tuple_count,
    }
    if defect:
        if examined != tuple_count:
            raise AssertionError("nonzero minimum without exhaustion")
        result["failure"] = failure_record(
            order,
            ordinal,
            g6,
            sizes,
            tuple_count,
            tuple_index,
            choice,
            summary,
        )
    return result


def analyze_chunk(task) -> dict:
    graph_tasks, max_tuples = task
    counts_by_order: dict[int, Counter] = {}
    failures = []
    for order, ordinal, g6 in graph_tasks:
        result = analyze_graph((order, ordinal, g6, max_tuples))
        counts = counts_by_order.setdefault(order, Counter())
        counts[result["status"]] += 1
        counts["availableTuples"] += result.get("availableTuples", 0)
        if result["status"] != "tested":
            continue
        counts["examinedTuples"] += result["examinedTuples"]
        counts["positiveTupleFailuresBeforeStop"] += result[
            "positiveTupleFailuresBeforeStop"
        ]
        counts["zeroMinimumGraphs"] += int(result["zeroFound"])
        counts["failedGraphs"] += int(not result["zeroFound"])
        counts["fullyExhaustedGraphs"] += int(result["exhaustedAllTuples"])
        if "failure" in result:
            failures.append(result["failure"])
    return {"countsByOrder": counts_by_order, "failures": failures}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument(
        "--workers", type=int, default=min(16, os.cpu_count() or 1)
    )
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument("--limit-graphs-per-order", type=int)
    parser.add_argument("--max-tuples-per-graph", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 1 <= n-min <= n-max <= 12")
    if not 1 <= args.workers <= 61:
        parser.error("workers must be in 1..61 on Windows")
    if args.chunk_size <= 0:
        parser.error("chunk-size must be positive")
    if (
        args.limit_graphs_per_order is not None
        and args.limit_graphs_per_order <= 0
    ):
        parser.error("limit-graphs-per-order must be positive")
    if args.max_tuples_per_graph is not None and args.max_tuples_per_graph <= 0:
        parser.error("max-tuples-per-graph must be positive")
    return args


def main() -> int:
    args = parse_args()
    graph6, generated = graph6_for_orders(args.n_min, args.n_max)
    by_order: dict[int, list[str]] = {
        order: [] for order in range(args.n_min, args.n_max + 1)
    }
    for g6 in graph6:
        by_order[dec(g6)[0]].append(g6)
    if {order: len(items) for order, items in by_order.items()} != generated:
        raise AssertionError("graph stream count mismatch")

    selected_by_order = {}
    stream_sha = {}
    tasks = []
    for order, items in sorted(by_order.items()):
        if args.limit_graphs_per_order is not None:
            items = items[: args.limit_graphs_per_order]
        selected_by_order[str(order)] = len(items)
        stream_sha[str(order)] = hashlib.sha256(
            "".join(f"{item}\n" for item in items).encode("ascii")
        ).hexdigest()
        tasks.extend((order, ordinal, g6) for ordinal, g6 in enumerate(items))

    chunks = [
        (tasks[index : index + args.chunk_size], args.max_tuples_per_graph)
        for index in range(0, len(tasks), args.chunk_size)
    ]
    counts_by_order: dict[int, Counter] = {}
    failures = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(analyze_chunk, chunks, chunksize=1):
            for order, source in result["countsByOrder"].items():
                counts_by_order.setdefault(order, Counter()).update(source)
            failures.extend(result["failures"])
    failures.sort(key=lambda item: (item["order"], item["graphOrdinal"]))

    coverage_complete = (
        args.limit_graphs_per_order is None
        and args.max_tuples_per_graph is None
    )
    payload = {
        "schema": "R53_GLOBAL_FREEHALF_SOFTCAP_CENSUS_V1",
        "arithmetic": "Python integers only; exact integral max flow",
        "range": [args.n_min, args.n_max],
        "workers": args.workers,
        "selection": (
            "enumerate row tuples until exact defect zero; if none, exhaust all "
            "tuples and report the exact graph minimum"
        ),
        "coverage": {
            "generatedByOrder": {str(k): v for k, v in generated.items()},
            "selectedByOrder": selected_by_order,
            "graphStreamSha256ByOrder": stream_sha,
            "limitGraphsPerOrder": args.limit_graphs_per_order,
            "maxTuplesPerGraph": args.max_tuples_per_graph,
            "completeForSelectedOrders": coverage_complete,
            "countsByOrder": {
                str(order): dict(sorted(counts.items()))
                for order, counts in sorted(counts_by_order.items())
            },
        },
        "failedGraphCount": len(failures),
        "failures": failures,
        "relationProvenance": soft.RELATION_PROVENANCE,
        "sourceSha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (
                HERE / "global_softcap.py",
                Path(__file__),
                WRITEUP / "_codex_r19_global_base_census.py",
                WRITEUP / "_codex_r20_two_row_exchange_gate.py",
                WRITEUP / "_codex_r23_heavy_alltuple_descent_gate.py",
            )
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = (
        args.output.resolve()
        if args.output is not None
        else HERE / f"census_n{args.n_min}_n{args.n_max}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)).replace("\\", "/"),
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
                "failedGraphCount": len(failures),
                "countsByOrder": payload["coverage"]["countsByOrder"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
