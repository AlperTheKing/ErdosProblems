"""Exact PHT census on the available order-12 medium and heavy scopes."""

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
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice, scoped_score
from _codex_r23_order12_preflight import inspect
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow


EXPECTED = {
    "generated": 1_144_061,
    "eligible": 921_910,
    "lightGraphs": 899_619,
    "lightTuples": 20_181_461,
    "mediumGraphs": 21_841,
    "mediumTuples": 14_160_291,
    "heavyGraphs": 450,
    "heavyTuples": 4_801_067,
    "mediumFailures": 1_080,
    "heavyFailures": 7_144,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_pair(value: Fraction | None) -> list[int] | None:
    if value is None:
        return None
    return [value.numerator, value.denominator]


def record_key(record: dict) -> tuple:
    return (
        record["tuples"], record["g6"], record["tupleIndex"],
        tuple(record["choice"]), tuple(record["owners"]),
    )


def analyze_graph(task: tuple[str, str]) -> dict:
    g6, band = task
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        raise AssertionError(f"preflight mismatch for {g6}")
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    choices = itertools.product(*(range(size) for size in sizes))
    scores = []
    for choice in choices:
        scores.append(scoped_score(n, info, rows_for_choice(families, choice)))
    count = math.prod(sizes)
    if len(scores) != count:
        raise AssertionError("row-product count mismatch")
    score_sum = sum(scores)

    failures = 0
    pht_failures = 0
    min_normalized = None
    min_normalized_record = None
    min_raw = None
    min_raw_record = None
    first_falsifier = None
    for tuple_index, (choice, score) in enumerate(zip(
        itertools.product(*(range(size) for size in sizes)), scores
    )):
        if score == 0:
            continue
        rows = rows_for_choice(families, choice)
        flow = full_owner_flow(
            n, set(info["Bset"]), set(info["Mset"]), rows, g6,
            require_full=False, quiet=True, scope="active",
            include_outside=False,
        )
        if flow["full"]:
            continue
        failures += 1
        defect = flow["deficiency"]
        residual = count * (score - defect) - score_sum
        normalized = Fraction(residual, count)
        record = {
            "band": band,
            "g6": g6,
            "tuples": count,
            "familySizes": list(sizes),
            "tupleIndex": tuple_index,
            "choice": list(choice),
            "score": score,
            "scoreSum": score_sum,
            "defect": defect,
            "owners": flow["deficientOwners"],
            "residualNumerator": residual,
            "residualDenominator": count,
            "residualReduced": fraction_pair(normalized),
        }
        if min_normalized is None or normalized < min_normalized or (
            normalized == min_normalized
            and record_key(record) < record_key(min_normalized_record)
        ):
            min_normalized = normalized
            min_normalized_record = record
        if min_raw is None or residual < min_raw or (
            residual == min_raw and record_key(record) < record_key(min_raw_record)
        ):
            min_raw = residual
            min_raw_record = record
        if residual < 0:
            pht_failures += 1
            if first_falsifier is None or record_key(record) < record_key(first_falsifier):
                first_falsifier = record
    return {
        "band": band,
        "g6": g6,
        "tuples": count,
        "scoreSum": score_sum,
        "failures": failures,
        "phtFailures": pht_failures,
        "minNormalized": fraction_pair(min_normalized),
        "minNormalizedRecord": min_normalized_record,
        "minRaw": min_raw,
        "minRawRecord": min_raw_record,
        "firstFalsifier": first_falsifier,
    }


def candidate_census(graph6: list[str], workers: int) -> tuple[list[tuple[str, str]], dict]:
    status = Counter()
    bands = {
        "light": {"graphs": 0, "tuples": 0},
        "medium": {"graphs": 0, "tuples": 0},
        "heavy": {"graphs": 0, "tuples": 0},
    }
    tasks = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for kind, g6, count, sizes, bads in pool.map(inspect, graph6, chunksize=64):
            status[kind] += 1
            if kind != "eligible":
                continue
            if count <= 256:
                band = "light"
            elif count <= 4096:
                band = "medium"
            else:
                band = "heavy"
            bands[band]["graphs"] += 1
            bands[band]["tuples"] += count
            if band != "light":
                tasks.append((g6, band))
    tasks.sort(key=lambda task: (0 if task[1] == "medium" else 1, task[0]))
    return tasks, {"status": dict(sorted(status.items())), "bands": bands}


def empty_band() -> dict:
    return {
        "graphs": 0,
        "tuples": 0,
        "failures": 0,
        "phtFailures": 0,
        "minNormalized": None,
        "minNormalizedRecord": None,
        "minRaw": None,
        "minRawRecord": None,
        "firstFalsifier": None,
    }


def merge_result(target: dict, result: dict) -> None:
    target["graphs"] += 1
    target["tuples"] += result["tuples"]
    target["failures"] += result["failures"]
    target["phtFailures"] += result["phtFailures"]
    record = result["minNormalizedRecord"]
    if record is not None:
        value = Fraction(*result["minNormalized"])
        current = target["minNormalizedRecord"]
        if current is None or value < Fraction(*target["minNormalized"]) or (
            value == Fraction(*target["minNormalized"])
            and record_key(record) < record_key(current)
        ):
            target["minNormalized"] = result["minNormalized"]
            target["minNormalizedRecord"] = record
    record = result["minRawRecord"]
    if record is not None:
        current = target["minRawRecord"]
        if current is None or result["minRaw"] < target["minRaw"] or (
            result["minRaw"] == target["minRaw"]
            and record_key(record) < record_key(current)
        ):
            target["minRaw"] = result["minRaw"]
            target["minRawRecord"] = record
    record = result["firstFalsifier"]
    if record is not None and (
        target["firstFalsifier"] is None
        or record_key(record) < record_key(target["firstFalsifier"])
    ):
        target["firstFalsifier"] = record


def validate_expected(preflight: dict, bands: dict) -> None:
    actual = {
        "eligible": preflight["status"].get("eligible", 0),
        "lightGraphs": preflight["bands"]["light"]["graphs"],
        "lightTuples": preflight["bands"]["light"]["tuples"],
        "mediumGraphs": bands["medium"]["graphs"],
        "mediumTuples": bands["medium"]["tuples"],
        "heavyGraphs": bands["heavy"]["graphs"],
        "heavyTuples": bands["heavy"]["tuples"],
        "mediumFailures": bands["medium"]["failures"],
        "heavyFailures": bands["heavy"]["failures"],
    }
    for key, expected in EXPECTED.items():
        if key == "generated":
            continue
        if actual[key] != expected:
            raise AssertionError(f"expected {key}={expected}, got {actual[key]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--no-expected-counts", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        parser.error("--workers must be in 1..32")

    graph6, generated_by_order = graph6_for_orders(12, 12)
    if not args.no_expected_counts and len(graph6) != EXPECTED["generated"]:
        raise AssertionError(
            f"expected {EXPECTED['generated']} generated graphs, got {len(graph6)}"
        )
    graph_stream = "".join(f"{g6}\n" for g6 in graph6).encode("ascii")
    tasks, preflight = candidate_census(graph6, args.workers)

    bands = {"medium": empty_band(), "heavy": empty_band()}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, tasks, chunksize=1):
            merge_result(bands[result["band"]], result)
    if not args.no_expected_counts:
        validate_expected(preflight, bands)

    all_results = empty_band()
    for band in ("medium", "heavy"):
        source = bands[band]
        all_results["graphs"] += source["graphs"]
        all_results["tuples"] += source["tuples"]
        all_results["failures"] += source["failures"]
        all_results["phtFailures"] += source["phtFailures"]
        synthetic = {
            "tuples": 0,
            "failures": 0,
            "phtFailures": 0,
            "minNormalized": source["minNormalized"],
            "minNormalizedRecord": source["minNormalizedRecord"],
            "minRaw": source["minRaw"],
            "minRawRecord": source["minRawRecord"],
            "firstFalsifier": source["firstFalsifier"],
        }
        merge_result(all_results, synthetic)
        all_results["graphs"] -= 1

    machinery = [
        WRITEUP / "_h.py",
        WRITEUP / "_codex_r19_global_base_census.py",
        WRITEUP / "_codex_r20_two_row_exchange_gate.py",
        WRITEUP / "_codex_r23_heavy_alltuple_descent_gate.py",
        WRITEUP / "_codex_r23_order12_preflight.py",
        WRITEUP / "_codex_r23_outside_attachment_full_obligation_gate.py",
        ROOT / "tmp" / "fanout" / "transport_dual" / "lead" / "full_heatbath_gate.py",
        ROOT / "tmp" / "fanout" / "transport_dual" / "SYNTHESIS.md",
    ]
    payload = {
        "format": "pht-n12-direct-v1",
        "arithmetic": "Python integers; Fraction only for reduced residuals",
        "workers": args.workers,
        "order": 12,
        "generatedByOrder": generated_by_order,
        "graphStreamSha256": hashlib.sha256(graph_stream).hexdigest(),
        "preflight": preflight,
        "testedBands": bands,
        "combined": all_results,
        "lightScope": {
            **preflight["bands"]["light"],
            "phtTests": 0,
            "reason": "the available light census has zero scoped Hall failures",
        },
        "quantifiers": {
            "omegaSpace": "Omega_G = product_{i=0}^{m-1} {0,...,|R_i|-1}",
            "tested": (
                "for every omega in Omega_G with scoped owner-Hall failure, "
                "and hence for every deficient owner shore A subseteq O(omega)"
            ),
            "defect": "defect_omega(A)=Demand_omega(A)-Source_omega(A)>0",
            "inequality": (
                "sum_{eta in Omega_G} S(eta) <= |Omega_G|*"
                "(S(omega)-defect_omega(A))"
            ),
            "maxDefectReduction": (
                "the residual min-cut returns Delta=max_A defect_omega(A); "
                "testing Delta is strongest and implies the inequality for every "
                "deficient A"
            ),
        },
        "sourceSha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in machinery
        },
        "scriptSha256": sha256(Path(__file__)),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["resultSha256"] = hashlib.sha256(encoded).hexdigest()
    output = HERE / "n12_result.json"
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "output": str(output),
        "combined": all_results,
        "resultSha256": payload["resultSha256"],
    }, sort_keys=True, separators=(",", ":")))
    return int(all_results["phtFailures"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
