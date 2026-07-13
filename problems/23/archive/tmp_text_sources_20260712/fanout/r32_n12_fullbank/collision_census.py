"""Exhaustive N<=12 no-common collision Hall census.

Universe: connected triangle-free graph6 stream, pinned connected Gamma-minimum
maximum cut, all bad edges of length five, and every coherent shortest-row
tuple.  Demand is collision halves only.  Sources are the deduplicated union
P1/P3 + strict P4 + P5; common-blue is absent.
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
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
P5_DIR = HERE.parent / "p5_n12_census"
sys.path.insert(0, str(WRITEUP))
sys.path.insert(0, str(PHT))
sys.path.insert(0, str(P5_DIR))
sys.path.insert(0, str(HERE))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402
from p5_core import make_graph_context  # noqa: E402


N12_EXPECTED = {
    "generated": 1_144_061,
    "eligible": 921_910,
    "lightGraphs": 899_619,
    "lightTuples": 20_181_461,
    "mediumGraphs": 21_841,
    "mediumTuples": 14_160_291,
    "heavyGraphs": 450,
    "heavyTuples": 4_801_067,
}

COUNT_KEYS = (
    "testedGraphs",
    "availableTuples",
    "examinedTuples",
    "zeroCollisionTuples",
    "positiveCollisionTuples",
    "collisionPassingTuples",
    "collisionFailingTuples",
    "p4NonemptyTuples",
    "p5NonemptyTuples",
    "p4Keys",
    "p5Keys",
    "p4CheckedSwitches",
    "p4NegativeSwitchesRejected",
    "p5CheckedSwitches",
    "p5NegativeSwitches",
    "p5ReservedCandidates",
    "coherenceAutomaticTuples",
    "coherenceSearchTuples",
    "coherenceSearchNodes",
    "hitNeedPositiveTuplesSeparate",
    "hitNeedSlotsSeparate",
    "defectMinimizerGraphs",
    "defectMinimizerPassingGraphs",
    "defectMinimizerFailingGraphs",
    "allTuplePassingGraphs",
    "someTupleFailingGraphs",
    "allTupleFailingGraphs",
)

HIST_KEYS = (
    "collisionDemandHistogram",
    "collisionDefectHistogram",
    "defectMinimumHistogram",
    "minimizerDemandHistogram",
    "minimizerHitNeedHistogramSeparate",
)

FIRST_KEYS = (
    "firstPositiveCollision",
    "firstTupleFalsifier",
    "firstDefectMinimizerFalsifier",
    "firstAllTupleFalsifier",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def band_of(tuple_count: int) -> str:
    if tuple_count <= 256:
        return "light"
    if tuple_count <= 4096:
        return "medium"
    return "heavy"


def band_selected(band: str, selection: str) -> bool:
    return (
        selection == "all"
        or band == selection
        or selection == "medium-heavy" and band in {"medium", "heavy"}
    )


def empty_bucket() -> dict:
    return {
        "counts": Counter(),
        "histograms": {key: Counter() for key in HIST_KEYS},
        "first": {key: None for key in FIRST_KEYS},
    }


def record_key(record: dict) -> tuple[int, int, int]:
    return record["order"], record["graphOrdinal"], record["tupleIndex"]


def merge_bucket(target: dict, source: dict) -> None:
    target["counts"].update(source["counts"])
    for key in HIST_KEYS:
        target["histograms"][key].update(source["histograms"][key])
    for key in FIRST_KEYS:
        candidate = source["first"][key]
        current = target["first"][key]
        if candidate is not None and (
            current is None or record_key(candidate) < record_key(current)
        ):
            target["first"][key] = candidate


def summary_record(
    *,
    order: int,
    graph_ordinal: int,
    g6: str,
    tuple_index: int,
    choice: tuple[int, ...],
    sizes: tuple[int, ...],
    info,
    analysis: dict,
) -> dict:
    cut_payload = {
        "side": info["side"],
        "blue": [list(edge) for edge in sorted(info["Bset"])],
        "bad": [list(edge) for edge in sorted(info["Mset"])],
    }
    record = {
        "order": order,
        "graphOrdinal": graph_ordinal,
        "g6": g6,
        "tupleIndex": tuple_index,
        "choice": list(choice),
        "familySizes": list(sizes),
        "tupleCount": math.prod(sizes),
        "gamma": info["G"],
        "cutPayloadSha256": canonical_sha(cut_payload),
        "collisionDemand": analysis["collisionDemand"],
        "collisionMatched": analysis["collisionMatched"],
        "collisionDefect": analysis["collisionDefect"],
        "hitNeedSlotsSeparate": analysis["hitNeedSlotsSeparate"],
        "owners": analysis["owners"],
        "sourceKeys": analysis["sourceKeys"],
        "p4Keys": analysis["p4Keys"],
        "p5Keys": analysis["p5Keys"],
        "coherenceAutomatic": analysis["coherenceAutomatic"],
        "coherenceLabels": analysis["coherenceLabels"],
        "searchNodes": analysis["searchNodes"],
        "commonBlueCandidates": 0,
        "commonBlueUsed": 0,
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def analyze_graph(task: tuple) -> dict:
    order, graph_ordinal, g6, band_selection = task
    n, graph_edges = dec(g6)
    if n != order:
        raise AssertionError((n, order, g6))
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": order}
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    tuple_count = math.prod(sizes)
    band = band_of(tuple_count)
    if not band_selected(band, band_selection):
        return {
            "status": "eligibleUntested",
            "order": order,
            "band": band,
            "availableTuples": tuple_count,
        }

    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    bucket = empty_bucket()
    counts = bucket["counts"]
    hist = bucket["histograms"]
    counts["testedGraphs"] = 1
    counts["availableTuples"] = tuple_count
    best: tuple[int, int, tuple[int, ...], dict] | None = None
    graph_failures = 0

    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = rows_for_choice(families, choice)
        analysis = analyze_collision_only(ctx, rows)
        counts["examinedTuples"] += 1
        demand = analysis["collisionDemand"]
        defect = analysis["collisionDefect"]
        counts["zeroCollisionTuples"] += int(demand == 0)
        counts["positiveCollisionTuples"] += int(demand > 0)
        counts["collisionPassingTuples"] += int(defect == 0)
        counts["collisionFailingTuples"] += int(defect > 0)
        graph_failures += int(defect > 0)
        counts["p4NonemptyTuples"] += int(analysis["p4Keys"] > 0)
        counts["p5NonemptyTuples"] += int(analysis["p5Keys"] > 0)
        counts["p4Keys"] += analysis["p4Keys"]
        counts["p5Keys"] += analysis["p5Keys"]
        counts["p4CheckedSwitches"] += analysis["p4CheckedSwitches"]
        counts["p4NegativeSwitchesRejected"] += analysis[
            "p4NegativeSwitchesRejected"
        ]
        counts["p5CheckedSwitches"] += analysis["p5CheckedSwitches"]
        counts["p5NegativeSwitches"] += analysis["p5NegativeSwitches"]
        counts["p5ReservedCandidates"] += analysis["p5ReservedCandidates"]
        counts["coherenceAutomaticTuples"] += int(
            analysis["coherenceAutomatic"]
        )
        counts["coherenceSearchTuples"] += int(
            not analysis["coherenceAutomatic"]
        )
        counts["coherenceSearchNodes"] += analysis["searchNodes"]
        hit_slots = analysis["hitNeedSlotsSeparate"]
        counts["hitNeedPositiveTuplesSeparate"] += int(hit_slots > 0)
        counts["hitNeedSlotsSeparate"] += hit_slots
        hist["collisionDemandHistogram"][demand] += 1
        hist["collisionDefectHistogram"][defect] += 1

        def make_record() -> dict:
            return summary_record(
                order=order,
                graph_ordinal=graph_ordinal,
                g6=g6,
                tuple_index=tuple_index,
                choice=choice,
                sizes=sizes,
                info=info,
                analysis=analysis,
            )

        if demand > 0 and bucket["first"]["firstPositiveCollision"] is None:
            bucket["first"]["firstPositiveCollision"] = make_record()
        if defect > 0 and bucket["first"]["firstTupleFalsifier"] is None:
            bucket["first"]["firstTupleFalsifier"] = make_record()

        candidate = (defect, tuple_index, choice, analysis)
        if best is None or candidate[:2] < best[:2]:
            best = candidate

    if best is None:
        raise AssertionError("eligible graph has no row tuple")
    best_defect, best_index, best_choice, best_analysis = best
    counts["defectMinimizerGraphs"] = 1
    counts["defectMinimizerPassingGraphs"] = int(best_defect == 0)
    counts["defectMinimizerFailingGraphs"] = int(best_defect > 0)
    counts["allTuplePassingGraphs"] = int(graph_failures == 0)
    counts["someTupleFailingGraphs"] = int(graph_failures > 0)
    counts["allTupleFailingGraphs"] = int(graph_failures == tuple_count)
    hist["defectMinimumHistogram"][best_defect] += 1
    hist["minimizerDemandHistogram"][best_analysis["collisionDemand"]] += 1
    hist["minimizerHitNeedHistogramSeparate"][
        best_analysis["hitNeedSlotsSeparate"]
    ] += 1
    if best_defect > 0:
        record = summary_record(
            order=order,
            graph_ordinal=graph_ordinal,
            g6=g6,
            tuple_index=best_index,
            choice=best_choice,
            sizes=sizes,
            info=info,
            analysis=best_analysis,
        )
        bucket["first"]["firstDefectMinimizerFalsifier"] = record
        bucket["first"]["firstAllTupleFalsifier"] = record
    return {
        "status": "eligibleTested",
        "order": order,
        "band": band,
        "bucket": bucket,
    }


def analyze_chunk(task: tuple) -> dict:
    band_selection, graph_tasks = task
    status: dict[int, Counter] = {}
    bands: dict[str, dict] = {}
    total = empty_bucket()
    for order, graph_ordinal, g6 in graph_tasks:
        result = analyze_graph((order, graph_ordinal, g6, band_selection))
        order_status = status.setdefault(order, Counter())
        order_status[result["status"]] += 1
        if result["status"].startswith("eligible"):
            order_status["eligible"] += 1
            available = result.get(
                "availableTuples",
                result.get("bucket", {}).get("counts", {}).get(
                    "availableTuples", 0
                ),
            )
            order_status["availableTuples"] += available
            band = result["band"]
            order_status[f"{band}Graphs"] += 1
            order_status[f"{band}Tuples"] += available
        if result["status"] != "eligibleTested":
            continue
        merge_bucket(total, result["bucket"])
        merge_bucket(bands.setdefault(result["band"], empty_bucket()), result["bucket"])
    return {"status": status, "bands": bands, "total": total}


def serializable_bucket(bucket: dict) -> dict:
    return {
        "counts": {key: bucket["counts"].get(key, 0) for key in COUNT_KEYS},
        "histograms": {
            key: {
                str(value): count
                for value, count in sorted(bucket["histograms"][key].items())
            }
            for key in HIST_KEYS
        },
        "first": bucket["first"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(20, os.cpu_count() or 1))
    parser.add_argument(
        "--band",
        choices=("all", "light", "medium", "heavy", "medium-heavy"),
        default="all",
    )
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--graph6", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 20:
        parser.error("--workers must be in 1..20")
    if not 1 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 1 <= n-min <= n-max <= 12")
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be positive")
    if args.limit_graphs is not None and args.limit_graphs <= 0:
        parser.error("--limit-graphs must be positive")
    return args


def main() -> int:
    args = parse_args()
    started = time.time()
    if args.graph6:
        graphs_by_order: dict[int, list[str]] = {}
        for g6 in args.graph6:
            graphs_by_order.setdefault(dec(g6)[0], []).append(g6)
    else:
        graph6, generated = graph6_for_orders(args.n_min, args.n_max)
        graphs_by_order = {n: [] for n in range(args.n_min, args.n_max + 1)}
        for g6 in graph6:
            graphs_by_order[dec(g6)[0]].append(g6)
        if {n: len(v) for n, v in graphs_by_order.items()} != generated:
            raise AssertionError("generated graph counts changed")

    graph_tasks: list[tuple[int, int, str]] = []
    stream_sha: dict[str, str] = {}
    generated_by_order: dict[str, int] = {}
    for order in sorted(graphs_by_order):
        graphs = graphs_by_order[order]
        if args.limit_graphs is not None:
            graphs = graphs[: args.limit_graphs]
        generated_by_order[str(order)] = len(graphs)
        stream = "".join(f"{g6}\n" for g6 in graphs).encode("ascii")
        stream_sha[str(order)] = hashlib.sha256(stream).hexdigest()
        graph_tasks.extend((order, index, g6) for index, g6 in enumerate(graphs))

    chunks = [
        (args.band, graph_tasks[index : index + args.chunk_size])
        for index in range(0, len(graph_tasks), args.chunk_size)
    ]
    status: dict[int, Counter] = {}
    bands = {name: empty_bucket() for name in ("light", "medium", "heavy")}
    total = empty_bucket()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for chunk_index, result in enumerate(
            pool.map(analyze_chunk, chunks, chunksize=1), start=1
        ):
            for order, source in result["status"].items():
                status.setdefault(order, Counter()).update(source)
            for band, source in result["bands"].items():
                merge_bucket(bands[band], source)
            merge_bucket(total, result["total"])
            if args.progress_every and chunk_index % args.progress_every == 0:
                print(
                    "chunks=%d/%d graphs=%d tuples=%d failures=%d elapsed=%.1fs"
                    % (
                        chunk_index,
                        len(chunks),
                        total["counts"]["testedGraphs"],
                        total["counts"]["examinedTuples"],
                        total["counts"]["collisionFailingTuples"],
                        time.time() - started,
                    ),
                    flush=True,
                )

    status_payload = {
        str(order): {key: value for key, value in sorted(values.items())}
        for order, values in sorted(status.items())
    }
    preflight = None
    if not args.graph6 and args.n_min == args.n_max == 12 and args.limit_graphs is None:
        n12 = status[12]
        preflight = {
            "generated": generated_by_order["12"],
            "eligible": n12["eligible"],
            "lightGraphs": n12["lightGraphs"],
            "lightTuples": n12["lightTuples"],
            "mediumGraphs": n12["mediumGraphs"],
            "mediumTuples": n12["mediumTuples"],
            "heavyGraphs": n12["heavyGraphs"],
            "heavyTuples": n12["heavyTuples"],
        }
        if preflight != N12_EXPECTED:
            raise AssertionError((preflight, N12_EXPECTED))

    payload = {
        "schema": "R32_NO_COMMON_COLLISION_CENSUS_V1",
        "relation": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "P5"],
        "commonBlue": False,
        "hallDemand": "active-scoped collision halves only",
        "hitNeed": "excluded; recorded separately as bank-funded metadata",
        "integerOnly": True,
        "orders": [args.n_min, args.n_max],
        "band": args.band,
        "workers": args.workers,
        "elapsedSeconds": round(time.time() - started, 6),
        "generatedByOrder": generated_by_order,
        "graphStreamSha256": stream_sha,
        "statusByOrder": status_payload,
        "n12Preflight": preflight,
        "bands": {name: serializable_bucket(bucket) for name, bucket in bands.items()},
        "total": serializable_bucket(total),
        "sha256": {
            "collisionCore": sha256(HERE / "collision_only_core.py"),
            "fullbankCore": sha256(HERE / "fullbank_core.py"),
            "p5Core": sha256(P5_DIR / "p5_core.py"),
            "driver": sha256(Path(__file__)),
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "testedGraphs": total["counts"]["testedGraphs"],
                "examinedTuples": total["counts"]["examinedTuples"],
                "collisionFailures": total["counts"]["collisionFailingTuples"],
                "minimizerFailures": total["counts"]["defectMinimizerFailingGraphs"],
                "allTupleFailingGraphs": total["counts"]["allTupleFailingGraphs"],
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

