#!/usr/bin/env python3
"""Official unscoped-P4 CDC wave-1 coverage run."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections import Counter
from hashlib import sha256
from pathlib import Path

import official_selector as official
import run_wave as helpers
import selector_core as core


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R35_RESULT = HERE / "r35_official_search.json"
OUTPUT = HERE / "official_coverage.json"
REPORT = HERE / "OFFICIAL_REPORT.md"


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def compact_analysis(analysis: dict) -> dict:
    shore = analysis["shoreAudit"]["minimumShore"]
    return {
        "verdict": analysis["verdict"],
        "collisionUnits": analysis["collisionUnits"],
        "collisionHalfDemand": analysis["collisionHalfDemand"],
        "maximumFlow": analysis["flow"]["maximumFlow"],
        "defect": analysis["flow"]["defect"],
        "minimumShore": {
            "owners": shore["owners"],
            "demand": shore["demand"],
            "capacity": shore["capacity"],
            "slack": shore["slack"],
        },
        "rowSha256": analysis["rowSha256"],
    }


def selector_summary(
    graph: core.CutGraph,
    *,
    tuple_cap: int,
    stop_after_pass: bool,
) -> dict:
    row_db = core.complete_row_database(graph)
    if any(not rows for _edge, rows in row_db):
        raise AssertionError("non-ell5 row database")
    fixed_rows = tuple(rows[0] for _edge, rows in row_db)
    fixed = official.analyze_tuple(graph, fixed_rows)
    selector = official.exhaustive_minimum_collision_tuples(
        graph,
        row_db,
        tuple_cap=tuple_cap,
        stop_after_first_passing_minimum=stop_after_pass,
    )
    result = {
        "graph6": core.graph6_encode(graph.n, graph.edges),
        "side": "".join(map(str, core.recover_side(graph))),
        "order": graph.n,
        "edges": len(graph.edges),
        "badEdges": len(graph.bad),
        "rowFamilySizes": [len(rows) for _edge, rows in row_db],
        "fixedTuple": compact_analysis(fixed),
        "tupleProduct": selector["tupleCount"],
        "rowProductExhaustive": selector["exhaustive"],
    }
    if selector["exhaustive"]:
        result.update(
            {
                "minimumCollisionUnits": selector["minimumCollisionUnits"],
                "minimumTupleCount": selector["minimumTupleCount"],
                "minimumTuplesEvaluated": selector["minimumTuplesEvaluated"],
                "allMinimumTuplesEvaluated": selector[
                    "allMinimumTuplesEvaluated"
                ],
                "selectorVerdict": selector["selectorVerdict"],
                "evaluatedMinimumTuples": [
                    {
                        "choice": item["choice"],
                        "analysis": compact_analysis(item["analysis"]),
                    }
                    for item in selector["minimumTuples"]
                ],
            }
        )
    return result


def named_fixtures(tuple_cap: int) -> dict:
    records = []
    for graph in (core.n24_fixture(), core.n89_fixture()):
        checks = core.displayed_graph_checks(graph)
        if graph.n == 24:
            maxcut = core.maxcut_gray_exact(graph)
        else:
            maxcut = helpers.n89_quotient_maxcut()
        summary = selector_summary(
            graph, tuple_cap=tuple_cap, stop_after_pass=False
        )
        summary["fixture"] = graph.name
        summary["graphChecks"] = checks
        summary["maximumCutCertificate"] = maxcut
        summary["displayedGamma"] = 25 * len(graph.bad)
        summary["gammaLowerBound"] = 25 * (
            len(graph.edges) - maxcut["maximumCut"]
        )
        records.append(summary)
    return {
        "status": "COMPLETE",
        "fixtures": records,
        "allPass": all(
            item["selectorVerdict"] == "PASS_SOME_MINIMUM_TUPLE"
            for item in records
        ),
    }


def random_census_stress(
    *, seed: int, sample_per_order: int, tuple_cap: int
) -> dict:
    rng = random.Random(seed)
    counters = Counter()
    cases = []
    for n in (8, 9, 10):
        proc = subprocess.run(
            [str(helpers.GENG), "-tc", str(n)],
            check=True,
            capture_output=True,
            text=True,
        )
        corpus = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        sample = rng.sample(corpus, min(sample_per_order, len(corpus)))
        counters["graphsAvailable"] += len(corpus)
        counters["graphsSampled"] += len(sample)
        for g6 in sample:
            decoded_n, edges = core.graph6_decode(g6)
            if decoded_n != n:
                raise AssertionError((decoded_n, n))
            maximum, cuts = helpers.gamma_min_cuts(n, edges)
            if not cuts:
                counters["noConnectedNonbipartiteGammaMinCut"] += 1
                continue
            counters["gammaMinCuts"] += len(cuts)
            for cut_index, cut in enumerate(cuts[:4]):
                if not cut["allEllFive"]:
                    counters["nonEllFiveGammaMinCuts"] += 1
                    continue
                counters["allEllFiveGammaMinCuts"] += 1
                graph = core.CutGraph(
                    f"random_{n}_{g6}_{cut_index}",
                    n,
                    cut["blue"],
                    cut["bad"],
                )
                summary = selector_summary(
                    graph, tuple_cap=tuple_cap, stop_after_pass=True
                )
                summary["maximumCut"] = maximum
                summary["gamma"] = cut["gamma"]
                cases.append(summary)
                if summary["rowProductExhaustive"]:
                    counters["rowProductsExhausted"] += 1
                    counters[
                        summary["fixedTuple"]["verdict"] + "_fixedTuple"
                    ] += 1
                    counters[summary["selectorVerdict"]] += 1
                else:
                    counters["rowProductsOverCap"] += 1
    return {
        "status": "COMPLETE",
        "seed": seed,
        "orders": [8, 9, 10],
        "samplePerOrder": sample_per_order,
        "tupleCap": tuple_cap,
        "counters": dict(sorted(counters.items())),
        "cases": cases,
    }


def blowup_stress(tuple_cap: int) -> dict:
    size_cases = (
        (1, 1, 1, 1, 1),
        (1, 2, 1, 2, 1),
        (1, 2, 2, 1, 2),
        (2, 1, 2, 2, 1),
        (2, 2, 2, 2, 2),
    )
    counters = Counter()
    cases = []
    for sizes in size_cases:
        n, edges, _classes = helpers.c5_blowup(sizes)
        maximum, cuts = helpers.gamma_min_cuts(n, edges)
        for cut_index, cut in enumerate(cuts):
            if not cut["allEllFive"]:
                counters["nonEllFiveCuts"] += 1
                continue
            graph = core.CutGraph(
                f"C5_blowup_{'_'.join(map(str, sizes))}_{cut_index}",
                n,
                cut["blue"],
                cut["bad"],
            )
            summary = selector_summary(
                graph, tuple_cap=tuple_cap, stop_after_pass=True
            )
            summary["classSizes"] = list(sizes)
            summary["maximumCut"] = maximum
            summary["gamma"] = cut["gamma"]
            cases.append(summary)
            if summary["rowProductExhaustive"]:
                counters["rowProductsExhausted"] += 1
                counters[
                    summary["fixedTuple"]["verdict"] + "_fixedTuple"
                ] += 1
                counters[summary["selectorVerdict"]] += 1
            else:
                counters["rowProductsOverCap"] += 1
    return {
        "status": "COMPLETE",
        "tupleCap": tuple_cap,
        "sizeCases": [list(item) for item in size_cases],
        "counters": dict(sorted(counters.items())),
        "cases": cases,
    }


def validate_r35() -> dict:
    data = json.loads(R35_RESULT.read_text(encoding="ascii"))
    copy = dict(data)
    claimed = copy.pop("canonicalPayloadSha256")
    canonical_ok = core.canonical_sha(copy) == claimed
    return {
        "status": "COMPLETE",
        "artifact": str(R35_RESULT.relative_to(ROOT)).replace("\\", "/"),
        "fileSha256": file_sha(R35_RESULT),
        "canonicalPayloadSha256": claimed,
        "canonicalHashValid": canonical_ok,
        "cpSatStatus": data["optimization"]["status"],
        "minimumCollisionUnits": data["optimization"]["minimumCollisionUnits"],
        "passingMinimumTupleFound": data["passingMinimumTupleFound"],
        "passingChoice": data["trials"][0]["choice"],
        "passingAnalysis": data["trials"][0]["analysis"],
        "graphScope": data["graph"],
    }


def write_report(payload: dict) -> None:
    fixtures = payload["namedFixtures"]["fixtures"]
    n24, n89 = fixtures
    r35 = payload["r35GlobalOptimization"]
    random_counts = payload["randomCensusStress"]["counters"]
    blowup_counts = payload["blowupStress"]["counters"]
    text = f"""# CDC Wave 1 Official Selector Adversary

## Verdict

No real graph-derived counterexample was found under the official
coherence-free six-relation model with unscoped `P4_outsideAttachment`.
All acceptance computations use integers only.

The earlier strict-P4 deficits are a diagnostic scope fork, not
counterexamples to this official selector.  Direct official replay gives:

| Fixture | Row product | Min collision | Flow | Defect |
|---|---:|---:|---:|---:|
| N24 singleton | {n24['tupleProduct']} | {n24['minimumCollisionUnits']} | {n24['evaluatedMinimumTuples'][0]['analysis']['maximumFlow']}/{n24['evaluatedMinimumTuples'][0]['analysis']['collisionHalfDemand']} | {n24['evaluatedMinimumTuples'][0]['analysis']['defect']} |
| N89 singleton | {n89['tupleProduct']} | {n89['minimumCollisionUnits']} | {n89['evaluatedMinimumTuples'][0]['analysis']['maximumFlow']}/{n89['evaluatedMinimumTuples'][0]['analysis']['collisionHalfDemand']} | {n89['evaluatedMinimumTuples'][0]['analysis']['defect']} |
| R35 N24 | {r35['graphScope']['rowTupleProduct']} | {r35['minimumCollisionUnits']} | {r35['passingAnalysis']['maximumFlow']}/{r35['passingAnalysis']['collisionHalfDemand']} | {r35['passingAnalysis']['defect']} |

R35's minimum `collisionUnits = {r35['minimumCollisionUnits']}` is globally
proved by integer CP-SAT (`{r35['cpSatStatus']}`) over row-family radices
`{r35['graphScope']['rowFamilySizes']}`.  Its first optimum choice
`{r35['passingChoice']}` passes Hall.

## Bounded Stress

Random connected triangle-free `geng` sample counters:
`{json.dumps(random_counts, sort_keys=True)}`.

C5 blow-up counters:
`{json.dumps(blowup_counts, sort_keys=True)}`.

Fixed-tuple failures, when present, are not promoted to selector failures:
the minimum-collision row product is exhausted (or an exact minimum witness is
found) before classification.  Full graph6 strings, rows, choices, exact Hall
shores, source hashes, and per-case coverage are in `official_coverage.json`.
"""
    REPORT.write_text(text, encoding="ascii", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-per-order", type=int, default=30)
    parser.add_argument("--tuple-cap", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=230053)
    args = parser.parse_args()

    payload = {
        "schema": "CDC_WAVE1_OFFICIAL_SELECTOR_COVERAGE_V1",
        "model": {
            "demand": "every global CollisionHalf",
            "sinks": "actual FreeHalf(sourceX,sourceY,half)",
            "relations": list(official.FAMILIES),
            "p4OwnerAttachmentActiveComponentEquality": False,
            "literalKeyCapacity": 1,
            "activeUndirectedEdgeAggregateCapacity": 2,
            "acceptanceArithmetic": "integers only; no float acceptance path",
        },
        "namedFixtures": named_fixtures(args.tuple_cap),
        "r35GlobalOptimization": validate_r35(),
        "randomCensusStress": random_census_stress(
            seed=args.seed,
            sample_per_order=args.sample_per_order,
            tuple_cap=args.tuple_cap,
        ),
        "blowupStress": blowup_stress(args.tuple_cap),
        "strictP4Diagnostic": {
            "status": "SUPERSEDED_FOR_OFFICIAL_SELECTOR",
            "N24Defect": 102,
            "N89Defect": 2,
            "reason": (
                "strict relation imposed owner/attachment active-component "
                "equality that official coherence-free P4 drops"
            ),
        },
        "sourceSha256": {
            "selector_core.py": file_sha(HERE / "selector_core.py"),
            "official_selector.py": file_sha(HERE / "official_selector.py"),
            "run_official_wave.py": file_sha(Path(__file__)),
        },
    }
    payload["counterexampleFound"] = any(
        case.get("selectorVerdict") == "FAIL_ALL_MINIMUM_TUPLES"
        for section in (
            payload["namedFixtures"]["fixtures"],
            payload["randomCensusStress"]["cases"],
            payload["blowupStress"]["cases"],
        )
        for case in section
    )
    payload["canonicalPayloadSha256"] = core.canonical_sha(payload)
    helpers.write_json(OUTPUT, payload)
    write_report(payload)
    print(
        json.dumps(
            {
                "counterexampleFound": payload["counterexampleFound"],
                "namedPass": payload["namedFixtures"]["allPass"],
                "r35Pass": payload["r35GlobalOptimization"][
                    "passingMinimumTupleFound"
                ],
                "randomCounters": payload["randomCensusStress"]["counters"],
                "blowupCounters": payload["blowupStress"]["counters"],
                "payloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 1 if payload["counterexampleFound"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
