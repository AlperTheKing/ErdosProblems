#!/usr/bin/env python3
"""Run the exact CDC wave-1 selector adversary and emit replay artifacts."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections import Counter, deque
from hashlib import sha256
from pathlib import Path

import selector_core as core


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def n89_quotient_maxcut() -> dict:
    graph = core.n89_fixture()
    locks = (0, 0, 0, 4, 6, 4, 5, 5, 3, 3, 3, 5)
    core_edges = [edge for edge in graph.edges if edge[0] < 12 and edge[1] < 12]
    anchor_side = 1
    best = -1
    count = 0
    first = None
    for mask in range(1 << 12):
        side = [(mask >> vertex) & 1 for vertex in range(12)]
        value = sum(side[x] != side[y] for x, y in core_edges)
        value += sum(
            locks[vertex] * (2 + (side[vertex] != anchor_side))
            for vertex in range(12)
        )
        if value > best:
            best = value
            count = 1
            first = side
        elif value == best:
            count += 1
    return {
        "method": (
            "4096 core assignments with anchor fixed; each private length-3 "
            "lock path contributes exactly 3 for opposite endpoints and 2 otherwise"
        ),
        "coreAssignmentsChecked": 1 << 12,
        "maximumCut": best,
        "maximizingCoreAssignmentCount": count,
        "firstMaximumCoreSide": "".join(map(str, first)),
    }


def fixture_certificate(graph: core.CutGraph, maxcut: dict) -> dict:
    checks = core.displayed_graph_checks(graph)
    row_db = core.complete_row_database(graph)
    selector = core.exhaustive_minimum_collision_tuples(graph, row_db)
    maxcut_value = maxcut["maximumCut"]
    bad_at_maxcut = len(graph.edges) - maxcut_value
    displayed_gamma = 25 * len(graph.bad)
    gamma_lower = 25 * bad_at_maxcut
    hypotheses = {
        "connectedGraph": checks["graphConnected"],
        "triangleFree": checks["triangleCount"] == 0,
        "displayedCutIsMaximum": checks["cutValue"] == maxcut_value,
        "blueConnected": checks["blueConnected"],
        "allBadDistanceFour": checks["allBadDistanceFour"],
        "gammaMinimal": displayed_gamma == gamma_lower,
        "completeShortestRowDatabase": all(checks["rowFamilySizes"]),
    }
    if not all(hypotheses.values()):
        raise AssertionError((graph.name, hypotheses))
    if selector["selectorVerdict"] != "FAIL_ALL_MINIMUM_TUPLES":
        raise AssertionError((graph.name, selector["selectorVerdict"]))
    result = {
        "schema": "CDC_WAVE1_SELECTOR_COUNTEREXAMPLE_V1",
        "fixture": graph.name,
        "model": {
            "demand": "every global CollisionHalf",
            "sinks": "actual FreeHalf(sourceX,sourceY,half)",
            "relations": list(core.FAMILIES),
            "p4Semantics": (
                "frozen strict R23/R37 relation: each outside-component "
                "attachment companion is in the owner's active component"
            ),
            "unscopedP4Included": False,
            "literalKeyCapacity": 1,
            "activeUndirectedEdgeAggregateCapacity": 2,
            "arithmetic": "Python integers only; integral max flow and exact Hall shores",
        },
        "graph": checks,
        "maximumCutCertificate": maxcut,
        "gammaCertificate": {
            "badEdgesAtEveryMaximumCut": bad_at_maxcut,
            "triangleFreeConnectedBLowerBoundPerBadEdge": 25,
            "gammaLowerBound": gamma_lower,
            "displayedGamma": displayed_gamma,
            "equalityProvesGammaMinimal": displayed_gamma == gamma_lower,
        },
        "hypotheses": hypotheses,
        "rowSelection": selector,
        "fixedVersusAllMinimum": {
            "fixedTupleFails": selector["minimumTuples"][0]["verdict"] == "FAIL",
            "rowDatabaseSingleton": selector["tupleCount"] == 1,
            "allMinimumTuplesExhausted": selector["allMinimumTuplesEvaluated"],
            "allMinimumTuplesFail": selector["selectorVerdict"]
            == "FAIL_ALL_MINIMUM_TUPLES",
        },
        "sourceSha256": {
            "selector_core.py": file_sha(HERE / "selector_core.py"),
            "run_wave.py": file_sha(Path(__file__)),
        },
    }
    result["canonicalPayloadSha256"] = core.canonical_sha(result)
    return result


def all_distances(n: int, edges: frozenset[core.Edge], source: int) -> list[int]:
    adj = core.adjacency(n, edges)
    distance = [-1] * n
    distance[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if distance[y] < 0:
                distance[y] = distance[x] + 1
                queue.append(y)
    return distance


def gamma_min_cuts(n: int, edges: frozenset[core.Edge]) -> tuple[int, list[dict]]:
    candidates = []
    maximum = -1
    for mask in range(1 << max(0, n - 1)):
        side = (0,) + tuple((mask >> (vertex - 1)) & 1 for vertex in range(1, n))
        value = sum(side[x] != side[y] for x, y in edges)
        if value > maximum:
            maximum = value
            candidates = [side]
        elif value == maximum:
            candidates.append(side)
    connected = []
    for side in candidates:
        blue = frozenset(edge for edge in edges if side[edge[0]] != side[edge[1]])
        bad = frozenset(edges - blue)
        if not bad or not core.is_connected(n, blue):
            continue
        distance_cache = {x: all_distances(n, blue, x) for x, _y in bad}
        if any(distance_cache[x][y] < 0 for x, y in bad):
            continue
        gamma = sum((distance_cache[x][y] + 1) ** 2 for x, y in bad)
        connected.append(
            {
                "side": side,
                "blue": blue,
                "bad": bad,
                "gamma": gamma,
                "allEllFive": all(distance_cache[x][y] == 4 for x, y in bad),
            }
        )
    if not connected:
        return maximum, []
    minimum_gamma = min(item["gamma"] for item in connected)
    return maximum, [item for item in connected if item["gamma"] == minimum_gamma]


def selector_summary(
    graph: core.CutGraph,
    *,
    tuple_cap: int,
    stop_after_pass: bool,
) -> dict:
    row_db = core.complete_row_database(graph)
    fixed_rows = tuple(rows[0] for _edge, rows in row_db)
    fixed = core.analyze_tuple(graph, fixed_rows)
    selector = core.exhaustive_minimum_collision_tuples(
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
        "fixedTupleDefect": fixed["flow"]["defect"],
        "fixedTupleVerdict": fixed["verdict"],
        "tupleProduct": selector["tupleCount"],
        "rowProductExhaustive": selector["exhaustive"],
    }
    if selector["exhaustive"]:
        result.update(
            {
                "minimumCollisionUnits": selector["minimumCollisionUnits"],
                "minimumTupleCount": selector["minimumTupleCount"],
                "minimumTuplesEvaluated": selector["minimumTuplesEvaluated"],
                "selectorVerdict": selector["selectorVerdict"],
                "minimumTupleDefectsEvaluated": [
                    item["defect"] for item in selector["minimumTuples"]
                ],
            }
        )
        failure = next(
            (
                item
                for item in selector["minimumTuples"]
                if item["verdict"] == "FAIL"
            ),
            None,
        )
        passing = next(
            (
                item
                for item in selector["minimumTuples"]
                if item["verdict"] == "PASS"
            ),
            None,
        )
        if failure is not None:
            result["firstEvaluatedFailure"] = {
                "choice": failure["choice"],
                "shore": failure["analysis"]["shoreAudit"]["minimumShore"],
            }
        if passing is not None:
            result["firstPassingMinimumChoice"] = passing["choice"]
    return result


def run_random_census_sample(
    *, seed: int, sample_per_order: int, tuple_cap: int
) -> dict:
    if not GENG.exists():
        return {"status": "SKIPPED_GENG_MISSING", "path": str(GENG)}
    rng = random.Random(seed)
    cases = []
    counters = Counter()
    for n in (8, 9, 10):
        proc = subprocess.run(
            [str(GENG), "-tc", str(n)],
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
                raise AssertionError((g6, decoded_n, n))
            maximum, cuts = gamma_min_cuts(n, edges)
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
                if not summary["rowProductExhaustive"]:
                    counters["rowProductsOverCap"] += 1
                else:
                    counters["rowProductsExhausted"] += 1
                    counters[summary["fixedTupleVerdict"] + "_fixedTuple"] += 1
                    counters[summary["selectorVerdict"]] += 1
    return {
        "status": "COMPLETE",
        "seed": seed,
        "orders": [8, 9, 10],
        "samplePerOrder": sample_per_order,
        "tupleCap": tuple_cap,
        "counters": dict(sorted(counters.items())),
        "cases": cases,
    }


def c5_blowup(sizes: tuple[int, int, int, int, int]) -> tuple[int, frozenset[core.Edge], tuple[tuple[int, ...], ...]]:
    classes = []
    nxt = 0
    for size in sizes:
        classes.append(tuple(range(nxt, nxt + size)))
        nxt += size
    edges = set()
    for index in range(5):
        left = classes[index]
        right = classes[(index + 1) % 5]
        edges.update(core.norm_edge(x, y) for x in left for y in right)
    return nxt, frozenset(edges), tuple(classes)


def run_blowup_stress(*, tuple_cap: int) -> dict:
    size_cases = (
        (1, 1, 1, 1, 1),
        (1, 2, 1, 2, 1),
        (1, 2, 2, 1, 2),
        (2, 1, 2, 2, 1),
        (2, 2, 2, 2, 2),
    )
    cases = []
    counters = Counter()
    for sizes in size_cases:
        n, edges, _classes = c5_blowup(sizes)
        maximum, cuts = gamma_min_cuts(n, edges)
        if not cuts:
            raise AssertionError(sizes)
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
            summary["maxCutProof"] = (
                "the class-count objective is multi-affine, so a maximizing "
                "split has a class-extreme maximizer; all 16 class patterns modulo complement checked"
            )
            cases.append(summary)
            if summary["rowProductExhaustive"]:
                counters["rowProductsExhausted"] += 1
                counters[summary["fixedTupleVerdict"] + "_fixedTuple"] += 1
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


def p4_scope_fork_audit() -> dict:
    path = (
        ROOT
        / "tmp"
        / "fanout"
        / "r53_global_softcap_gate"
        / "n89_unscoped_p4_alternate.json"
    )
    if not path.exists():
        return {"status": "SKIPPED_MISSING", "path": str(path)}
    data = json.loads(path.read_text(encoding="ascii"))
    diagnostics = data["namedDiagnostics"]
    return {
        "status": "COMPLETE",
        "scope": (
            "separate alternate model: P4 drops the owner/attachment "
            "active-component equality"
        ),
        "sourcePath": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sourceFileSha256": file_sha(path),
        "n24UnscopedP4Defect": diagnostics["n24_r1_fixed_rows"]["defect"],
        "n89UnscopedP4Defect": diagnostics["n89_singleton_row_database"]["defect"],
        "strictP4DefectsFromThisWave": {"N24": 102, "N89": 2},
        "conclusion": (
            "strict and unscoped P4 are different selector statements; "
            "the counterexamples here target the frozen strict relation"
        ),
    }


def compact_counterexample(certificate: dict) -> dict:
    minimum = certificate["rowSelection"]["minimumTuples"][0]
    analysis = minimum["analysis"]
    return {
        "fixture": certificate["fixture"],
        "graph6": certificate["graph"]["graph6"],
        "side": certificate["graph"]["side"],
        "rows": analysis["rows"],
        "rowFamilySizes": certificate["graph"]["rowFamilySizes"],
        "minimumCollisionUnits": certificate["rowSelection"]["minimumCollisionUnits"],
        "minimumTupleCount": certificate["rowSelection"]["minimumTupleCount"],
        "allMinimumTuplesFail": certificate["fixedVersusAllMinimum"]["allMinimumTuplesFail"],
        "maximumFlow": analysis["flow"]["maximumFlow"],
        "totalDemand": analysis["flow"]["totalDemand"],
        "defect": analysis["flow"]["defect"],
        "shore": analysis["shoreAudit"]["minimumShore"],
        "hypotheses": certificate["hypotheses"],
        "maximumCutCertificate": certificate["maximumCutCertificate"],
        "gammaCertificate": certificate["gammaCertificate"],
        "certificateCanonicalPayloadSha256": certificate["canonicalPayloadSha256"],
    }


def write_report(n24: dict, n89: dict, coverage: dict) -> None:
    c24 = compact_counterexample(n24)
    c89 = compact_counterexample(n89)
    random_counts = coverage["randomCensusStress"].get("counters", {})
    blowup_counts = coverage["blowupStress"].get("counters", {})
    text = f"""# CDC Wave 1 Adversary: Exact Selector Counterexamples

## Verdict

The frozen strict-P4 selector is false.  Both fixtures below are connected,
triangle-free graphs with a connected Gamma-minimum maximum cut and a complete
singleton shortest-row database.  Consequently their fixed-tuple failures are
also failures of every minimum-collision tuple.

This verdict pins P4 to the R23/R37 strict relation: attachment companions must
lie in the owner's active component.  The separately named unscoped-P4 variant
drops that relation-level equality and repairs both fixtures; it is recorded in
`coverage_report.json` and is not silently conflated with the asked selector.

All acceptance arithmetic is integer.  Max flow is integral Dinic on literal
`CollisionHalf -> FreeHalf` arcs; every owner shore is also enumerated directly.

## N24

Graph6:

~~~text
{c24['graph6']}
~~~

Cut side: `{c24['side']}`.  The exact Gray-code audit checks
{c24['maximumCutCertificate']['cutsChecked']} cuts modulo complement, finds the
unique maximum cut of value {c24['maximumCutCertificate']['maximumCut']}, and
the displayed Gamma is {c24['gammaCertificate']['displayedGamma']}.

The nine row families are singleton.  The unique row tuple is:

~~~json
{json.dumps(c24['rows'], separators=(',', ':'))}
~~~

The Hall shore is owners {c24['shore']['owners']}: demand
{c24['shore']['demand']}, grouped capacity {c24['shore']['capacity']}, defect
{-c24['shore']['slack']}.  Exact max flow is {c24['maximumFlow']} of
{c24['totalDemand']}.

## N89

Graph6:

~~~text
{c89['graph6']}
~~~

Cut side: `{c89['side']}`.  The lock-path quotient checks
{c89['maximumCutCertificate']['coreAssignmentsChecked']} core assignments and
finds maximum cut {c89['maximumCutCertificate']['maximumCut']}; triangle-free
odd-cycle length gives Gamma >= {c89['gammaCertificate']['gammaLowerBound']},
attained by the displayed cut.

The twenty row families are singleton.  The unique row tuple is:

~~~json
{json.dumps(c89['rows'], separators=(',', ':'))}
~~~

The Hall shore is owners {c89['shore']['owners']}: demand
{c89['shore']['demand']}, grouped capacity {c89['shore']['capacity']}, defect
{-c89['shore']['slack']}.  Exact max flow is {c89['maximumFlow']} of
{c89['totalDemand']}.

## Stress Coverage

Random census sample counters: `{json.dumps(random_counts, sort_keys=True)}`.

C5 blow-up counters: `{json.dumps(blowup_counts, sort_keys=True)}`.

The complete literal key lists, all rows, shore masks, relation counts, graph
hypothesis checks, and source hashes are in `counterexample_n24.json`,
`counterexample_n89.json`, and `coverage_report.json` beside this report.
"""
    (HERE / "REPORT.md").write_text(text, encoding="ascii", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--sample-per-order", type=int, default=40)
    parser.add_argument("--tuple-cap", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=230053)
    args = parser.parse_args()

    n24 = fixture_certificate(core.n24_fixture(), core.maxcut_gray_exact(core.n24_fixture()))
    n89 = fixture_certificate(core.n89_fixture(), n89_quotient_maxcut())
    write_json(HERE / "counterexample_n24.json", n24)
    write_json(HERE / "counterexample_n89.json", n89)
    (HERE / "n24.g6").write_text(n24["graph"]["graph6"] + "\n", encoding="ascii")
    (HERE / "n89.g6").write_text(n89["graph"]["graph6"] + "\n", encoding="ascii")

    if args.fixtures_only:
        random_stress = {"status": "SKIPPED_BY_FLAG"}
        blowup_stress = {"status": "SKIPPED_BY_FLAG"}
    else:
        random_stress = run_random_census_sample(
            seed=args.seed,
            sample_per_order=args.sample_per_order,
            tuple_cap=args.tuple_cap,
        )
        blowup_stress = run_blowup_stress(tuple_cap=args.tuple_cap)
    coverage = {
        "schema": "CDC_WAVE1_SELECTOR_ADVERSARY_COVERAGE_V1",
        "acceptanceArithmetic": "integers only; no float path",
        "counterexamples": [compact_counterexample(n24), compact_counterexample(n89)],
        "randomCensusStress": random_stress,
        "blowupStress": blowup_stress,
        "p4ScopeFork": p4_scope_fork_audit(),
        "sourceSha256": {
            "selector_core.py": file_sha(HERE / "selector_core.py"),
            "run_wave.py": file_sha(Path(__file__)),
        },
    }
    coverage["canonicalPayloadSha256"] = core.canonical_sha(coverage)
    write_json(HERE / "coverage_report.json", coverage)
    write_report(n24, n89, coverage)
    print(
        json.dumps(
            {
                "n24Defect": compact_counterexample(n24)["defect"],
                "n89Defect": compact_counterexample(n89)["defect"],
                "randomCounters": random_stress.get("counters", {}),
                "blowupCounters": blowup_stress.get("counters", {}),
                "coverageCanonicalPayloadSha256": coverage["canonicalPayloadSha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
