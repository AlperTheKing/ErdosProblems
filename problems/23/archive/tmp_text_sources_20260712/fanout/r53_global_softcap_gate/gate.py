#!/usr/bin/env python3
"""Run the corrected global soft-cap gate on named fixtures."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5_FIXTURES = ROOT / "tmp" / "fanout" / "p5_fixtures" / "gate.py"
N12_PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct" / "n12_pht.py"
N78_FIXTURE = ROOT / "problems" / "23" / "writeup" / "_claude_r40_n78_instance_gate.py"
N89_GUARDRAIL = ROOT / "problems" / "23" / "writeup" / "_claude_r22_89_gate.py"
R35_N24 = ROOT / "tmp" / "fanout" / "r35_24_trade" / "evaluate_trade.py"
R29_CONSTRUCTOR = ROOT / "tmp" / "fanout" / "r29_gate" / "lead" / "r29_lead_gate.py"
N3892_CONSTRUCTOR = ROOT / "problems" / "23" / "writeup" / "_codex_endpointflow_3892_counterexample.py"
CERT_DIR = HERE / "certificates"

sys.path.insert(0, str(HERE))
import global_softcap as soft  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def load_module(name: str, path: Path, *, quiet: bool = False):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    else:
        spec.loader.exec_module(module)
    return module


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )


def compact_summary(summary: dict) -> dict:
    """Keep every verdict-bearing field while avoiding duplicate provenance."""
    return {
        "schema": summary["schema"],
        "model": summary["model"],
        "state": summary["state"],
        "familyStats": summary["familyStats"],
        "stages": summary["stages"],
        "evaluatedFamilies": summary["evaluatedFamilies"],
        "notEnumeratedFamilies": summary["notEnumeratedFamilies"],
        "minimumDefect": summary["minimumDefect"],
        "maximumFlow": summary.get("maximumFlow"),
        "minCutSourceOwners": summary.get("minCutSourceOwners", []),
        "fullUnionExactReason": summary.get("fullUnionExactReason"),
        "verdict": summary["verdict"],
    }


def evaluate_fixed(
    name: str,
    ctx: soft.GraphContext,
    rows,
    *,
    metadata: dict,
    certificate: bool = True,
) -> dict:
    summary, cert = soft.analyze_global(
        ctx, rows, extract_certificate=certificate
    )
    result = compact_summary(summary)
    result["name"] = name
    result["metadata"] = metadata
    result["rowsSha256"] = canonical_sha([list(row) for row in rows])
    if cert is not None:
        cert["fixture"] = name
        cert["rowsSha256"] = result["rowsSha256"]
        cert["canonicalPayloadSha256"] = canonical_sha(cert)
        path = CERT_DIR / f"{name}.json"
        write_json(path, cert)
        artifact_key = (
            "certificate"
            if all(cert["checks"].values())
            else "partialFlowArtifact"
        )
        result[artifact_key] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "canonicalPayloadSha256": cert["canonicalPayloadSha256"],
            "fileSha256": sha256(path),
        }
    result["canonicalPayloadSha256"] = canonical_sha(result)
    return result


def n12_gate(n12) -> tuple[dict, dict]:
    g6 = "K??E@cyjFgWk"
    n, edges = n12.dec(g6)
    info = n12.loads(n, edges)
    if info is None:
        raise AssertionError("N12 fixture has no canonical cut")
    families = n12.shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    if sizes != (6, 5, 8, 10):
        raise AssertionError(sizes)
    ctx = soft.make_graph_context(n, info["Bset"], info["Mset"])
    named_choice = (0, 4, 7, 9)
    named_rows = n12.rows_for_choice(families, named_choice)
    named = evaluate_fixed(
        "n12_common_blue_choice_0_4_7_9",
        ctx,
        named_rows,
        metadata={
            "g6": g6,
            "choice": list(named_choice),
            "tupleIndex": 399,
            "familySizes": list(sizes),
            "historicalStatus": "first common-blue repair in N12_COMMON_BLUE_REPAIR_V1",
        },
        certificate=False,
    )

    histogram: dict[int, int] = {}
    failures = []
    best = None
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = n12.rows_for_choice(families, choice)
        summary, _ = soft.analyze_global(ctx, rows)
        defect = summary["minimumDefect"]
        histogram[defect] = histogram.get(defect, 0) + 1
        candidate = (defect, tuple_index, choice, rows, summary)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
        if defect:
            stage = summary["stages"][-1]
            failures.append(
                {
                    "tupleIndex": tuple_index,
                    "choice": list(choice),
                    "defect": defect,
                    "globalDemand": summary["state"]["globalCollisionHalfDemand"],
                    "maximumFlow": summary["maximumFlow"],
                    "shoreOwners": summary["minCutSourceOwners"],
                    "shoreDemand": stage["minCutSourceOwnerDemand"],
                    "shoreCapacity": stage["minCutShoreCapacity"],
                    "shoreDirectCapacity": stage["minCutShoreDirectCapacity"],
                    "shoreActiveCapacity": stage["minCutShoreActiveCapacity"],
                }
            )
    if best is None:
        raise AssertionError("empty N12 tuple product")
    best_defect, best_index, best_choice, best_rows, _best_summary = best
    best_result = evaluate_fixed(
        "n12_common_blue_graph_minimum",
        ctx,
        best_rows,
        metadata={
            "g6": g6,
            "choice": list(best_choice),
            "tupleIndex": best_index,
            "familySizes": list(sizes),
            "selection": "minimum corrected global defect, then tuple index",
        },
    )
    exhaustive = {
        "schema": "R53_N12_COMMON_BLUE_ALL_TUPLES_V1",
        "g6": g6,
        "familySizes": list(sizes),
        "tuples": sum(histogram.values()),
        "minimumDefect": best_defect,
        "minimumTupleIndex": best_index,
        "minimumChoice": list(best_choice),
        "defectHistogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "failureCount": len(failures),
        "failures": failures,
    }
    exhaustive["canonicalPayloadSha256"] = canonical_sha(exhaustive)
    path = HERE / "n12_common_blue_all_tuples.json"
    write_json(path, exhaustive)
    exhaustive["fileSha256"] = sha256(path)
    return named, {
        "exhaustive": exhaustive,
        "minimum": best_result,
    }


def complete_shortest_family_sizes(fixture) -> list[int]:
    adjacency = [set() for _ in range(fixture.n)]
    for x, y in fixture.blue:
        adjacency[x].add(y)
        adjacency[y].add(x)

    def family(source: int, target: int) -> list[tuple[int, ...]]:
        distance = [-1] * fixture.n
        distance[target] = 0
        queue = [target]
        for x in queue:
            for y in adjacency[x]:
                if distance[y] < 0:
                    distance[y] = distance[x] + 1
                    queue.append(y)
        if distance[source] != 4:
            raise AssertionError((source, target, distance[source]))
        rows = []

        def visit(path: tuple[int, ...]) -> None:
            x = path[-1]
            if len(path) == 5:
                if x == target:
                    rows.append(path)
                return
            for y in sorted(adjacency[x]):
                if y not in path and distance[y] == distance[x] - 1:
                    visit(path + (y,))

        visit((source,))
        return rows

    return [len(family(x, y)) for x, y in fixture.atoms]


def r35_gate(r35) -> tuple[list[dict], dict]:
    ctx = soft.make_graph_context(r35.N, r35.BLUE, r35.BAD)
    displayed = evaluate_fixed(
        "n24_r35_displayed",
        ctx,
        tuple(r35.DISPLAYED_ROWS),
        metadata={
            "state": list(r35.DISPLAYED),
            "scope": "fixed displayed tuple",
            "rowFamilySizes": list(r35.RADICES),
        },
        certificate=False,
    )
    old_trade_state = (0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 31, 44)
    old_trade_rows = tuple(
        r35.ROW_FAMILIES[index][choice]
        for index, choice in enumerate(old_trade_state)
    )
    old_trade = evaluate_fixed(
        "n24_r35_old_one_row_trade",
        ctx,
        old_trade_rows,
        metadata={
            "state": list(old_trade_state),
            "scope": "the prior active-only zero-defect repair",
            "rowFamilySizes": list(r35.RADICES),
        },
        certificate=False,
    )

    states = {tuple(r35.DISPLAYED)}
    for atom, radix in enumerate(r35.RADICES):
        for choice in range(radix):
            state = list(r35.DISPLAYED)
            state[atom] = choice
            states.add(tuple(state))
    records = []
    best = None
    histogram: dict[int, int] = {}
    for state in sorted(states):
        rows = tuple(
            r35.ROW_FAMILIES[index][choice]
            for index, choice in enumerate(state)
        )
        summary, _ = soft.analyze_global(ctx, rows)
        defect = summary["minimumDefect"]
        histogram[defect] = histogram.get(defect, 0) + 1
        record = {
            "state": list(state),
            "hammingDistance": sum(
                left != right for left, right in zip(state, r35.DISPLAYED)
            ),
            "defect": defect,
            "globalDemand": summary["state"]["globalCollisionHalfDemand"],
            "maximumFlow": summary["maximumFlow"],
            "shoreOwners": summary["minCutSourceOwners"],
        }
        records.append(record)
        candidate = (defect, tuple(state), rows)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        raise AssertionError("empty R35 neighborhood")
    best_defect, best_state, best_rows = best
    local_minimum = evaluate_fixed(
        "n24_r35_hamming_le_one_minimum",
        ctx,
        best_rows,
        metadata={
            "state": list(best_state),
            "scope": "all distinct tuples of Hamming distance at most one",
            "statesExhausted": len(states),
            "globalGraphMinimumStatus": "unavailable; full row product not exhausted",
        },
        certificate=False,
    )
    neighborhood = {
        "schema": "R53_R35_N24_HAMMING_LE_ONE_V1",
        "rowFamilySizes": list(r35.RADICES),
        "statesExhausted": len(states),
        "minimumDefect": best_defect,
        "minimumState": list(best_state),
        "defectHistogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "failures": records,
        "globalGraphMinimumStatus": "unavailable; full row product not exhausted",
    }
    neighborhood["canonicalPayloadSha256"] = canonical_sha(neighborhood)
    path = HERE / "r35_n24_hamming_le_one.json"
    write_json(path, neighborhood)
    neighborhood["fileSha256"] = sha256(path)
    return [displayed, old_trade, local_minimum], neighborhood


def main() -> int:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    p5_fixtures = load_module("r53_p5_fixtures", P5_FIXTURES)
    n12 = load_module("r53_n12_pht", N12_PHT)
    n78 = load_module("r53_n78_fixture", N78_FIXTURE, quiet=True)

    named_n12, n12_graph = n12_gate(n12)
    results = [named_n12, n12_graph["minimum"]]

    small_builders = (
        ("n24_r1_fixed_rows", p5_fixtures.build_24),
        ("n167_fixed_rows", lambda: p5_fixtures.build_167_or_175(167)),
        ("n175_fixed_rows", lambda: p5_fixtures.build_167_or_175(175)),
        ("n311_fixed_rows", p5_fixtures.build_311),
        ("n89_singleton_row_database", p5_fixtures.build_89),
    )
    for name, builder in small_builders:
        fixture = builder()
        p5_fixtures.validate_fixture(fixture)
        metadata = dict(fixture.metadata)
        if fixture.n <= 100:
            family_sizes = complete_shortest_family_sizes(fixture)
            metadata["completeShortestRowFamilySizes"] = family_sizes
            metadata["rowDatabaseSingleton"] = all(
                size == 1 for size in family_sizes
            )
        else:
            metadata["completeShortestRowFamilySizes"] = None
            metadata["rowDatabaseStatus"] = (
                "not enumerated by this gate; fixed rows only"
            )
        results.append(
            evaluate_fixed(
                name,
                soft.make_graph_context(fixture.n, fixture.blue, fixture.bad),
                fixture.rows,
                metadata=metadata,
                certificate=True,
            )
        )

    r35 = load_module("r53_r35_n24", R35_N24)
    r35_results, r35_neighborhood = r35_gate(r35)
    results.extend(r35_results)

    fixture_2943 = p5_fixtures.build_2943()
    p5_fixtures.validate_fixture(fixture_2943)
    results.append(
        evaluate_fixed(
            "n2943_all_anchor",
            soft.make_graph_context(
                fixture_2943.n, fixture_2943.blue, fixture_2943.bad
            ),
            fixture_2943.rows,
            metadata=fixture_2943.metadata,
        )
    )

    fixture_3892 = p5_fixtures.build_3892()
    p5_fixtures.validate_fixture(fixture_3892)
    results.append(
        evaluate_fixed(
            "n3892_lex_rows",
            soft.make_graph_context(
                fixture_3892.n, fixture_3892.blue, fixture_3892.bad
            ),
            fixture_3892.rows,
            metadata=fixture_3892.metadata,
        )
    )

    blue78 = {soft.norm_edge(*tuple(item)) for item in n78.blue}
    bad78 = {soft.norm_edge(*tuple(item)) for item in n78.bad}
    ctx78 = soft.make_graph_context(n78.N, blue78, bad78)
    for index, rows in enumerate(n78.states):
        results.append(
            evaluate_fixed(
                f"n78_rotor_state_{index}",
                ctx78,
                tuple(rows),
                metadata={
                    "state": index,
                    "fixture": str(N78_FIXTURE.relative_to(ROOT)).replace(
                        "\\", "/"
                    ),
                },
            )
        )

    failures = [
        {
            "name": result["name"],
            "minimumDefect": result["minimumDefect"],
            "minCutSourceOwners": result["minCutSourceOwners"],
        }
        for result in results
        if result["verdict"] == "FAIL"
    ]
    payload = {
        "schema": "R53_GLOBAL_SOFTCAP_NAMED_GATE_V1",
        "arithmetic": "Python integers only; exact integral max flow",
        "model": results[0]["model"],
        "selfChecks": soft.self_check(),
        "relationProvenance": soft.RELATION_PROVENANCE,
        "fixtures": results,
        "n12AllTuples": n12_graph["exhaustive"],
        "r35N24HammingLeOne": r35_neighborhood,
        "failures": failures,
        "sourceSha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (
                HERE / "global_softcap.py",
                Path(__file__),
                P5_FIXTURES,
                N12_PHT,
                N78_FIXTURE,
                N89_GUARDRAIL,
                R35_N24,
                R29_CONSTRUCTOR,
                N3892_CONSTRUCTOR,
            )
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "named_results.json"
    write_json(output, payload)
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)).replace("\\", "/"),
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
                "fixedFixtureDefects": {
                    result["name"]: result["minimumDefect"] for result in results
                },
                "n12FailureCount": n12_graph["exhaustive"]["failureCount"],
                "n12GraphMinimumDefect": n12_graph["exhaustive"]["minimumDefect"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
