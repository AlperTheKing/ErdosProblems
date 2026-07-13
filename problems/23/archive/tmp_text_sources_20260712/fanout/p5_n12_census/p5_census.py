"""Exact all-tuple / exact global-minimum-representative P5 census.

The graph/cut/row universe is the pinned canonical one used by the existing
N=12 gates.  ``--mode all`` checks every coherent row tuple in the requested
bands.  ``--mode representative`` chooses the lexicographically first global
minimum of ``collision + 25*HitNeed``; a zero-demand tuple permits exact early
termination because the score is a natural number.
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
sys.path.insert(0, str(WRITEUP))
sys.path.insert(0, str(PHT))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from p5_core import analyze_rows, make_graph_context  # noqa: E402


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
    "zeroDemandTuples",
    "positiveDemandTuples",
    "p5NonemptyTuples",
    "p5Keys",
    "p5OwnerArcs",
    "p5NewGlobalKeys",
    "p5ExtendedKeys",
    "p5NewOwnerArcs",
    "p5CheckedSwitches",
    "p5NegativeSwitches",
    "p5ReservedCandidates",
    "oneClaudeBeforeFailures",
    "oneClaudeAfterFailures",
    "oneClaudeRepairs",
    "oneBeforeP5Failures",
    "oneFiveFailures",
    "oneRepairs",
    "microBeforeP5Failures",
    "microFiveFailures",
    "microRepairs",
    "microFiveTightPositiveTuples",
    "representativeGraphs",
    "representativeZeroDemand",
    "representativePositiveDemand",
    "representativeMicroFailures",
    "representativeOneFailures",
    "representativeTightPositive",
)

HIST_KEYS = (
    "p5KeyHistogram",
    "oneClaudeBeforeDefectHistogram",
    "oneClaudeAfterDefectHistogram",
    "oneBeforeDefectHistogram",
    "oneFiveDefectHistogram",
    "microBeforeDefectHistogram",
    "microFiveDefectHistogram",
    "microFiveMarginHistogram",
    "representativeDemandHistogram",
    "representativeMarginHistogram",
)

FIRST_KEYS = (
    "firstP5Nonempty",
    "firstOneClaudeRepair",
    "firstOneRepair",
    "firstOneFalsifier",
    "firstMicroRepair",
    "firstMicroFalsifier",
    "firstRepresentativeFalsifier",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


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
        "blue": [list(e) for e in sorted(info["Bset"])],
        "bad": [list(e) for e in sorted(info["Mset"])],
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
        "oneDemand": analysis["oneDemand"],
        "microDemand": analysis["microDemand"],
        "collisionDemand": analysis["collisionDemand"],
        "hitNeedSlots": analysis["hitNeedSlots"],
        "owners": analysis["owners"],
        "activeVertices": analysis["activeVertices"],
        "p5Stats": analysis["p5Stats"],
        "oneClaudeBefore": analysis["oneClaudeBefore"],
        "oneClaudeAfter": analysis["oneClaudeAfter"],
        "oneBeforeP5": analysis["oneBeforeP5"],
        "oneFive": analysis["oneFive"],
        "microBeforeP5": analysis["microBeforeP5"],
        "microFive": analysis["microFive"],
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def analyze_graph(task: tuple) -> dict:
    (
        order,
        graph_ordinal,
        g6,
        mode,
        band_selection,
    ) = task
    n, graph_edges = dec(g6)
    assert n == order
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

    choices = itertools.product(*(range(size) for size in sizes))
    for tuple_index, choice in enumerate(choices):
        rows = rows_for_choice(families, choice)
        analysis = analyze_rows(ctx, rows)
        counts["examinedTuples"] += 1
        if analysis["microDemand"] == 0:
            counts["zeroDemandTuples"] += 1
        else:
            counts["positiveDemandTuples"] += 1

        p5 = analysis["p5Stats"]
        counts["p5NonemptyTuples"] += int(p5["keys"] > 0)
        counts["p5Keys"] += p5["keys"]
        counts["p5OwnerArcs"] += p5["ownerArcs"]
        counts["p5NewGlobalKeys"] += p5["newGlobalKeysVsP1P4"]
        counts["p5ExtendedKeys"] += p5["extendedKeysVsP1P4"]
        counts["p5NewOwnerArcs"] += p5["newOwnerArcsVsP1P4"]
        counts["p5CheckedSwitches"] += analysis["p5Audit"]["checkedSwitches"]
        counts["p5NegativeSwitches"] += analysis["p5Audit"]["negativeSwitches"]
        counts["p5ReservedCandidates"] += analysis["p5Audit"]["reservedCandidates"]
        hist["p5KeyHistogram"][p5["keys"]] += 1

        checks = {
            "oneClaudeBefore": analysis["oneClaudeBefore"],
            "oneClaudeAfter": analysis["oneClaudeAfter"],
            "oneBeforeP5": analysis["oneBeforeP5"],
            "oneFive": analysis["oneFive"],
            "microBeforeP5": analysis["microBeforeP5"],
            "microFive": analysis["microFive"],
        }
        for name, check in checks.items():
            if name == "oneClaudeBefore":
                hist["oneClaudeBeforeDefectHistogram"][check["maximumDefect"]] += 1
            elif name == "oneClaudeAfter":
                hist["oneClaudeAfterDefectHistogram"][check["maximumDefect"]] += 1
            elif name == "oneBeforeP5":
                hist["oneBeforeDefectHistogram"][check["maximumDefect"]] += 1
            elif name == "oneFive":
                hist["oneFiveDefectHistogram"][check["maximumDefect"]] += 1
            elif name == "microBeforeP5":
                hist["microBeforeDefectHistogram"][check["maximumDefect"]] += 1
            else:
                hist["microFiveDefectHistogram"][check["maximumDefect"]] += 1
                hist["microFiveMarginHistogram"][check["minimumMargin"]] += 1

        counts["oneClaudeBeforeFailures"] += int(not checks["oneClaudeBefore"]["full"])
        counts["oneClaudeAfterFailures"] += int(not checks["oneClaudeAfter"]["full"])
        counts["oneClaudeRepairs"] += int(
            not checks["oneClaudeBefore"]["full"] and checks["oneClaudeAfter"]["full"]
        )
        counts["oneBeforeP5Failures"] += int(not checks["oneBeforeP5"]["full"])
        counts["oneFiveFailures"] += int(not checks["oneFive"]["full"])
        counts["oneRepairs"] += int(
            not checks["oneBeforeP5"]["full"] and checks["oneFive"]["full"]
        )
        counts["microBeforeP5Failures"] += int(not checks["microBeforeP5"]["full"])
        counts["microFiveFailures"] += int(not checks["microFive"]["full"])
        counts["microRepairs"] += int(
            not checks["microBeforeP5"]["full"] and checks["microFive"]["full"]
        )
        counts["microFiveTightPositiveTuples"] += int(
            analysis["microDemand"] > 0 and checks["microFive"]["minimumMargin"] == 0
        )

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

        if p5["keys"] and bucket["first"]["firstP5Nonempty"] is None:
            bucket["first"]["firstP5Nonempty"] = make_record()
        if (
            not checks["oneClaudeBefore"]["full"]
            and checks["oneClaudeAfter"]["full"]
            and bucket["first"]["firstOneClaudeRepair"] is None
        ):
            bucket["first"]["firstOneClaudeRepair"] = make_record()
        if (
            not checks["oneBeforeP5"]["full"]
            and checks["oneFive"]["full"]
            and bucket["first"]["firstOneRepair"] is None
        ):
            bucket["first"]["firstOneRepair"] = make_record()
        if not checks["oneFive"]["full"] and bucket["first"]["firstOneFalsifier"] is None:
            bucket["first"]["firstOneFalsifier"] = make_record()
        if (
            not checks["microBeforeP5"]["full"]
            and checks["microFive"]["full"]
            and bucket["first"]["firstMicroRepair"] is None
        ):
            bucket["first"]["firstMicroRepair"] = make_record()
        if not checks["microFive"]["full"] and bucket["first"]["firstMicroFalsifier"] is None:
            bucket["first"]["firstMicroFalsifier"] = make_record()

        candidate = (analysis["microDemand"], tuple_index, choice, analysis)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
        if mode == "representative" and analysis["microDemand"] == 0:
            break

    assert best is not None
    best_demand, best_index, best_choice, best_analysis = best
    counts["representativeGraphs"] = 1
    counts["representativeZeroDemand"] = int(best_demand == 0)
    counts["representativePositiveDemand"] = int(best_demand > 0)
    counts["representativeMicroFailures"] = int(not best_analysis["microFive"]["full"])
    counts["representativeOneFailures"] = int(not best_analysis["oneFive"]["full"])
    counts["representativeTightPositive"] = int(
        best_demand > 0 and best_analysis["microFive"]["minimumMargin"] == 0
    )
    hist["representativeDemandHistogram"][best_demand] += 1
    hist["representativeMarginHistogram"][best_analysis["microFive"]["minimumMargin"]] += 1
    if not best_analysis["microFive"]["full"]:
        bucket["first"]["firstRepresentativeFalsifier"] = summary_record(
            order=order,
            graph_ordinal=graph_ordinal,
            g6=g6,
            tuple_index=best_index,
            choice=best_choice,
            sizes=sizes,
            info=info,
            analysis=best_analysis,
        )
    return {
        "status": "eligibleTested",
        "order": order,
        "band": band,
        "bucket": bucket,
    }


def analyze_chunk(task: tuple) -> dict:
    mode, band_selection, graph_tasks = task
    status: dict[int, Counter] = {}
    bands: dict[str, dict] = {}
    total = empty_bucket()
    for order, graph_ordinal, g6 in graph_tasks:
        result = analyze_graph((order, graph_ordinal, g6, mode, band_selection))
        order_status = status.setdefault(order, Counter())
        order_status[result["status"]] += 1
        if result["status"].startswith("eligible"):
            order_status["eligible"] += 1
            order_status["availableTuples"] += result.get(
                "availableTuples",
                result.get("bucket", {}).get("counts", {}).get("availableTuples", 0),
            )
            band = result["band"]
            order_status[f"{band}Graphs"] += 1
            order_status[f"{band}Tuples"] += result.get(
                "availableTuples",
                result.get("bucket", {}).get("counts", {}).get("availableTuples", 0),
            )
        if result["status"] != "eligibleTested":
            continue
        merge_bucket(total, result["bucket"])
        band_bucket = bands.setdefault(result["band"], empty_bucket())
        merge_bucket(band_bucket, result["bucket"])
    return {"status": status, "bands": bands, "total": total}


def serializable_bucket(bucket: dict) -> dict:
    counts = {key: bucket["counts"].get(key, 0) for key in COUNT_KEYS}
    return {
        "counts": counts,
        "histograms": {
            key: {str(k): v for k, v in sorted(bucket["histograms"][key].items())}
            for key in HIST_KEYS
        },
        "first": bucket["first"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--mode", choices=("all", "representative"), default="all")
    parser.add_argument(
        "--band",
        choices=("all", "light", "medium", "heavy", "medium-heavy"),
        default="all",
    )
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--graph6", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 12:
        parser.error("--workers must be in 1..12")
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
        assert {n: len(v) for n, v in graphs_by_order.items()} == generated

    graph_tasks: list[tuple[int, int, str]] = []
    stream_sha: dict[str, str] = {}
    generated_by_order: dict[str, int] = {}
    for order in sorted(graphs_by_order):
        graphs = graphs_by_order[order]
        if args.limit_graphs is not None:
            graphs = graphs[:args.limit_graphs]
        generated_by_order[str(order)] = len(graphs)
        stream = "".join(f"{g6}\n" for g6 in graphs).encode("ascii")
        stream_sha[str(order)] = hashlib.sha256(stream).hexdigest()
        graph_tasks.extend((order, index, g6) for index, g6 in enumerate(graphs))

    chunks = [
        (args.mode, args.band, graph_tasks[i:i + args.chunk_size])
        for i in range(0, len(graph_tasks), args.chunk_size)
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
                    json.dumps({
                        "chunks": chunk_index,
                        "of": len(chunks),
                        "examinedTuples": total["counts"]["examinedTuples"],
                        "microFiveFailures": total["counts"]["microFiveFailures"],
                    }, sort_keys=True),
                    flush=True,
                )

    full_unfiltered_n12 = (
        not args.graph6
        and args.limit_graphs is None
        and args.n_min <= 12 <= args.n_max
    )
    if full_unfiltered_n12:
        n12_status = status[12]
        actual = {
            "generated": generated_by_order["12"],
            "eligible": n12_status["eligible"],
            "lightGraphs": n12_status["lightGraphs"],
            "lightTuples": n12_status["lightTuples"],
            "mediumGraphs": n12_status["mediumGraphs"],
            "mediumTuples": n12_status["mediumTuples"],
            "heavyGraphs": n12_status["heavyGraphs"],
            "heavyTuples": n12_status["heavyTuples"],
        }
        if actual != N12_EXPECTED:
            raise AssertionError({"expected": N12_EXPECTED, "actual": actual})

    if args.mode == "all":
        expected_examined = sum(
            source["counts"]["availableTuples"] for source in bands.values()
        )
        if total["counts"]["examinedTuples"] != expected_examined:
            raise AssertionError("all-tuple mode did not examine every selected tuple")
    if total["counts"]["p5NegativeSwitches"] != 0:
        raise AssertionError("negative P5 switch reached aggregate")
    if total["counts"]["p5ReservedCandidates"] != 0:
        raise AssertionError("reserved P5 source reached aggregate")

    source_paths = [
        HERE / "p5_core.py",
        Path(__file__),
        HERE / "audit_inputs.py",
        HERE / "input_audit.json",
        WRITEUP / "_h.py",
        WRITEUP / "_codex_r19_global_base_census.py",
        WRITEUP / "_codex_r20_two_row_exchange_gate.py",
        WRITEUP / "_codex_r23_heavy_alltuple_descent_gate.py",
        WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py",
        WRITEUP / "_claude_r29_pattern5_gate.py",
    ]
    payload = {
        "schema": "P5_N_LE_12_CENSUS_V1",
        "arithmetic": "Python integers only",
        "workers": args.workers,
        "mode": args.mode,
        "bandSelection": args.band,
        "representativeRule": (
            "lexicographically first global minimum of collision+25*HitNeed; "
            "zero permits exact early stop"
        ),
        "relation": {
            "P1": "sameFirst",
            "P2": "corrected common-blue: blue to owner and sigma({x,y})>=2",
            "P3": "rowCompanion with sigma({x,y})>=0",
            "P4": "strict selected-complement attachment with active-component equality",
            "P5": "quiescent B[V\\A] component attachment with active-component equality",
            "reservation": "only half zero on demanded active off-support edges",
            "claudeChecksum": "P1/P3 before versus P1/P3/P5 after",
            "oneDemand": "collision + HitNeed",
            "microDemand": "collision + 25*HitNeed",
        },
        "coverage": {
            "generatedByOrder": generated_by_order,
            "graphStreamSha256ByOrder": stream_sha,
            "statusByOrder": {
                str(order): dict(sorted(values.items()))
                for order, values in sorted(status.items())
            },
            "n12ExpectedValidated": full_unfiltered_n12,
        },
        "bands": {name: serializable_bucket(bucket) for name, bucket in bands.items()},
        "total": serializable_bucket(total),
        "elapsedSeconds": int(time.time() - started),
        "sourceSha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in source_paths
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = args.output or HERE / f"census_{args.mode}_{args.band}.json"
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    for key, filename in (
        ("firstMicroFalsifier", "first_micro_falsifier.json"),
        ("firstOneFalsifier", "first_one_falsifier.json"),
        ("firstMicroRepair", "first_micro_repair.json"),
        ("firstRepresentativeFalsifier", "first_representative_falsifier.json"),
    ):
        record = payload["total"]["first"][key]
        if record is not None:
            (HERE / filename).write_text(
                json.dumps(record, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
    print(json.dumps({
        "output": str(output),
        "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
        "counts": payload["total"]["counts"],
        "firstMicroFalsifier": payload["total"]["first"]["firstMicroFalsifier"],
        "firstOneFalsifier": payload["total"]["first"]["firstOneFalsifier"],
        "elapsedSeconds": payload["elapsedSeconds"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
