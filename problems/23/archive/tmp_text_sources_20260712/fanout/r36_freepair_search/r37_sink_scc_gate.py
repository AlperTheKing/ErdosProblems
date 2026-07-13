"""Exact falsifier gate for R37 realSinkNeutralAttachmentClass_hasAugment.

For each real cage, collision defect is a nonnegative integer.  Therefore a
checked row tuple of defect zero proves the global minimum is zero and rules
out every positive-defect sink neutral SCC without enumerating neutral states.
The expensive SCC expansion is required only when exhaustive tuple search
finds a positive global minimum.

The N<=12 universe and collision semantics are imported from the independently
pinned R32 census: connected triangle-free graph6, its exact connected
Gamma-minimum maximum cut, all bad edges of length five, complete shortest-row
families, and P1/P3/strict-P4/P5 coherent FreeHalf matching.  This relation is
a subset of R37's retained relation (which additionally permits common-blue),
so a zero-defect certificate here is also a zero-defect R37 certificate.
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
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402
from p5_core import make_graph_context  # noqa: E402


N12_GENERATED = 1_144_061
N12_ELIGIBLE = 921_910
FIXTURE_RESULT = R32 / "fixture_battery_result.json"
FIXTURE_NAMES = ("2943", "24", "167", "175", "311", "3892", "89")


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_record(order, ordinal, g6, choice, sizes, info, analysis, tuple_index):
    record = {
        "order": order,
        "graphOrdinal": ordinal,
        "g6": g6,
        "choice": list(choice),
        "tupleIndex": tuple_index,
        "familySizes": list(sizes),
        "tupleCount": math.prod(sizes),
        "gamma": info["G"],
        "collisionDemand": analysis["collisionDemand"],
        "collisionMatched": analysis["collisionMatched"],
        "collisionDefect": analysis["collisionDefect"],
        "owners": analysis["owners"],
        "sourceKeys": analysis["sourceKeys"],
        "coherenceAutomatic": analysis["coherenceAutomatic"],
        "coherenceLabels": analysis["coherenceLabels"],
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def analyze_graph(task):
    order, ordinal, g6 = task
    n, edges = dec(g6)
    assert n == order
    info = loads(n, edges)
    if info is None:
        return {"order": order, "status": "skipNoCut"}
    if any(length != 5 for length in info["ell"].values()):
        return {"order": order, "status": "skipNotAll5"}

    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    best = None
    examined = 0
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = rows_for_choice(families, choice)
        analysis = analyze_collision_only(ctx, rows)
        examined += 1
        defect = analysis["collisionDefect"]
        if best is None or defect < best[0]:
            best = (defect, tuple_index, choice, analysis)
        if defect == 0:
            return {
                "order": order,
                "status": "minimumZero",
                "availableTuples": math.prod(sizes),
                "examinedTuples": examined,
                "positiveSinkSccPossible": False,
                "zeroCertificate": zero_record(
                    order, ordinal, g6, choice, sizes, info, analysis, tuple_index
                ),
            }

    assert best is not None
    defect, tuple_index, choice, analysis = best
    assert defect > 0
    # This is the only branch requiring the full R37 occurrence-level neutral
    # graph.  Emit the exact positive-minimum cage immediately; do not silently
    # downgrade it to a zero-failure manifest.
    return {
        "order": order,
        "status": "positiveMinimumRequiresSinkExpansion",
        "availableTuples": math.prod(sizes),
        "examinedTuples": examined,
        "positiveSinkSccPossible": True,
        "positiveMinimum": zero_record(
            order, ordinal, g6, choice, sizes, info, analysis, tuple_index
        ),
    }


def analyze_chunk(chunk):
    counts = Counter()
    examined = 0
    available = 0
    first_positive = None
    first_nonvacuous_zero = None
    for task in chunk:
        result = analyze_graph(task)
        counts[result["status"]] += 1
        examined += result.get("examinedTuples", 0)
        available += result.get("availableTuples", 0)
        if result["status"] == "positiveMinimumRequiresSinkExpansion" and first_positive is None:
            first_positive = result
        cert = result.get("zeroCertificate")
        if cert and cert["collisionDemand"] > 0 and first_nonvacuous_zero is None:
            first_nonvacuous_zero = cert
    return {
        "counts": counts,
        "examinedTuples": examined,
        "availableTuples": available,
        "firstPositiveMinimum": first_positive,
        "firstNonvacuousZero": first_nonvacuous_zero,
    }


def replay_fixtures():
    data = json.loads(FIXTURE_RESULT.read_text(encoding="ascii"))
    by_name = {}
    for result in data["fixtures"]:
        name = result["fixture"]
        if name not in FIXTURE_NAMES or result["scope"] != "active":
            continue
        certificate = result["checked_certificate"]
        demand = certificate["total_demand"]
        matched = certificate["max_flow"]
        if not certificate["full"] or matched != demand:
            raise AssertionError((name, certificate))
        expected_shores = (1 << certificate["owner_count"]) - 1
        if (
            not certificate["all_owner_shores_enumerated"]
            or certificate["owner_shores_checked"] != expected_shores
            or certificate["negative_shore_masks"]
        ):
            raise AssertionError((name, "incomplete Hall certificate"))
        by_name[name] = {
            "collisionDemand": demand,
            "collisionMatched": matched,
            "collisionDefect": demand - matched,
            "owners": result["owners"],
            "scope": result["scope"],
            "ownerShoresChecked": certificate["owner_shores_checked"],
            "shoreTableSha256": certificate["shore_table_sha256"],
            "positiveSinkSccPossible": False,
        }
    if tuple(sorted(by_name)) != tuple(sorted(FIXTURE_NAMES)):
        raise AssertionError((sorted(by_name), FIXTURE_NAMES))
    return {
        "source": str(FIXTURE_RESULT),
        "sourceSha256": file_sha(FIXTURE_RESULT),
        "fixtures": by_name,
        "positiveMinimumFixtures": 0,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    if not 1 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 1 <= n-min <= n-max <= 12")
    if args.chunk_size <= 0:
        parser.error("chunk-size must be positive")
    return args


def main():
    args = parse_args()
    started = time.time()
    fixtures = replay_fixtures()
    generated = {}
    stream_sha = {}
    counts = Counter()
    examined = 0
    available = 0
    first_positive = None
    first_nonvacuous_zero = None

    if not args.fixtures_only:
        graphs, generated_raw = graph6_for_orders(args.n_min, args.n_max)
        by_order = {n: [] for n in range(args.n_min, args.n_max + 1)}
        for g6 in graphs:
            by_order[dec(g6)[0]].append(g6)
        for order, rows in by_order.items():
            if args.limit_graphs is not None:
                rows = rows[: args.limit_graphs]
                by_order[order] = rows
            generated[str(order)] = len(rows)
            stream_sha[str(order)] = hashlib.sha256(
                "".join(g + "\n" for g in rows).encode("ascii")
            ).hexdigest()
        if args.limit_graphs is None:
            assert {n: len(rows) for n, rows in by_order.items()} == generated_raw
        tasks = [
            (order, ordinal, g6)
            for order, rows in sorted(by_order.items())
            for ordinal, g6 in enumerate(rows)
        ]
        chunks = [tasks[i : i + args.chunk_size] for i in range(0, len(tasks), args.chunk_size)]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for index, result in enumerate(pool.map(analyze_chunk, chunks, chunksize=1), 1):
                counts.update(result["counts"])
                examined += result["examinedTuples"]
                available += result["availableTuples"]
                if first_positive is None and result["firstPositiveMinimum"] is not None:
                    first_positive = result["firstPositiveMinimum"]
                candidate = result["firstNonvacuousZero"]
                if first_nonvacuous_zero is None and candidate is not None:
                    first_nonvacuous_zero = candidate
                if args.progress_every and index % args.progress_every == 0:
                    print(json.dumps({
                        "chunks": index,
                        "of": len(chunks),
                        "minimumZero": counts["minimumZero"],
                        "positiveMinimum": counts["positiveMinimumRequiresSinkExpansion"],
                        "examinedTuples": examined,
                        "elapsedSeconds": round(time.time() - started, 1),
                    }, sort_keys=True), flush=True)

    full_n12 = (
        not args.fixtures_only and args.limit_graphs is None
        and args.n_min <= 12 <= args.n_max
    )
    if full_n12:
        if generated["12"] != N12_GENERATED:
            raise AssertionError((generated["12"], N12_GENERATED))
        eligible = counts["minimumZero"] + counts["positiveMinimumRequiresSinkExpansion"]
        if args.n_min == 12 and eligible != N12_ELIGIBLE:
            raise AssertionError((eligible, N12_ELIGIBLE))

    witness = first_positive
    payload = {
        "schema": "R37_SINK_NEUTRAL_SCC_GATE_V1",
        "arithmetic": "Python integers and finite sets only",
        "workers": args.workers,
        "orders": None if args.fixtures_only else [args.n_min, args.n_max],
        "relationSubset": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "P5"],
        "r37AdditionalRelation": "common-blue; omitted subset is harmless for zero-defect certificates",
        "minimumRule": "defect is a natural number; first checked defect-zero tuple proves global minimum zero",
        "neutralExpansionRule": "expand all optimal matchings and occurrence states only if exhaustive minimum is positive",
        "fixtures": fixtures,
        "generatedByOrder": generated,
        "graphStreamSha256": stream_sha,
        "counts": dict(sorted(counts.items())),
        "availableTuples": available,
        "examinedUntilZeroOrExhaustion": examined,
        "firstNonvacuousZero": first_nonvacuous_zero,
        "positiveMinimumWitness": witness,
        "positiveDefectSinkSccWitness": None,
        "sinkSccStatesExamined": 0 if witness is None else None,
        "verdict": (
            "ZERO_FAILURE_MANIFEST_NO_POSITIVE_MINIMUM"
            if witness is None else "POSITIVE_MINIMUM_REQUIRES_SCC_EXPANSION"
        ),
        "elapsedSeconds": round(time.time() - started, 6),
        "inputs": {
            "r37": file_sha(WRITEUP / "WALL_ATTACK_R37_GPTPRO56.md"),
            "collisionCore": file_sha(R32 / "collision_only_core.py"),
            "fullbankCore": file_sha(R32 / "fullbank_core.py"),
            "p5Core": file_sha(P5 / "p5_core.py"),
            "driver": file_sha(Path(__file__)),
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "output": str(args.output),
        "verdict": payload["verdict"],
        "minimumZero": counts["minimumZero"],
        "positiveMinimum": counts["positiveMinimumRequiresSinkExpansion"],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))
    return 0 if witness is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
