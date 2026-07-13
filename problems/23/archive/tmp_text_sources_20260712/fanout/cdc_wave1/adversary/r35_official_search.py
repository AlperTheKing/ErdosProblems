#!/usr/bin/env python3
"""Optimize R35 N24 row choices, then test official grouped-cap Hall."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

from ortools.sat.python import cp_model

import official_selector as official
import selector_core as core


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R35_PATH = ROOT / "tmp" / "fanout" / "r35_24_trade" / "evaluate_trade.py"
OUTPUT = HERE / "r35_official_search.json"


def load_r35():
    spec = importlib.util.spec_from_file_location("cdc_wave1_r35", R35_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(R35_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_model(r35, *, optimum: int | None = None, tie_seed: int | None = None):
    model = cp_model.CpModel()
    selected = []
    for atom, family in enumerate(r35.ROW_FAMILIES):
        row_vars = [
            model.NewBoolVar(f"row_{atom}_{choice}")
            for choice in range(len(family))
        ]
        model.AddExactlyOne(row_vars)
        selected.append(row_vars)

    weighted_excess = []
    for x in range(r35.N):
        for y in range(x, r35.N):
            terms = []
            for atom, family in enumerate(r35.ROW_FAMILIES):
                for choice, row in enumerate(family):
                    if x in row and y in row:
                        terms.append(selected[atom][choice])
            count = model.NewIntVar(0, len(r35.BADS), f"count_{x}_{y}")
            model.Add(count == sum(terms))
            excess = model.NewIntVar(0, len(r35.BADS) - 1, f"excess_{x}_{y}")
            model.Add(excess >= count - 1)
            weight = 1 if x == y else 2
            weighted_excess.append(weight * excess)
    collision = sum(weighted_excess)
    if optimum is None:
        model.Minimize(collision)
    else:
        model.Add(collision == optimum)
        if tie_seed is not None:
            rng = random.Random(tie_seed)
            tie_terms = []
            for atom, row_vars in enumerate(selected):
                for choice, var in enumerate(row_vars):
                    tie_terms.append(rng.randrange(1, 1_000_001) * var)
            model.Minimize(sum(tie_terms))
    return model, selected, collision


def solve_choice(r35, *, optimum: int | None = None, tie_seed: int | None = None, workers: int = 16):
    model, selected, collision = build_model(
        r35, optimum=optimum, tie_seed=tie_seed
    )
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053 if tie_seed is None else tie_seed
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise RuntimeError(f"CP-SAT status {solver.StatusName(status)}")
    choice = tuple(
        next(index for index, var in enumerate(row_vars) if solver.Value(var))
        for row_vars in selected
    )
    rows = tuple(r35.ROW_FAMILIES[atom][item] for atom, item in enumerate(choice))
    state = core.reconstruct_state(
        core.CutGraph(
            "R35_N24", r35.N, frozenset(r35.BLUE), frozenset(r35.BAD)
        ),
        rows,
    )
    exact_collision = core.collision_units(state)
    model_collision = solver.Value(collision)
    if exact_collision != model_collision:
        raise AssertionError((exact_collision, model_collision))
    if optimum is not None and exact_collision != optimum:
        raise AssertionError((exact_collision, optimum))
    return {
        "status": solver.StatusName(status),
        "choice": choice,
        "rows": rows,
        "collisionUnits": exact_collision,
        "workers": workers,
        "tieSeed": tie_seed,
    }


def compact_analysis(result: dict) -> dict:
    shore = result["shoreAudit"]["minimumShore"]
    return {
        "verdict": result["verdict"],
        "collisionUnits": result["collisionUnits"],
        "collisionHalfDemand": result["collisionHalfDemand"],
        "maximumFlow": result["flow"]["maximumFlow"],
        "defect": result["flow"]["defect"],
        "activeEdges": len(result["activeEdges"]),
        "minimumShore": {
            "owners": shore["owners"],
            "demand": shore["demand"],
            "capacity": shore["capacity"],
            "slack": shore["slack"],
        },
        "rowSha256": result["rowSha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tie-trials", type=int, default=64)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    r35 = load_r35()
    graph = core.CutGraph(
        "R35_N24", r35.N, frozenset(r35.BLUE), frozenset(r35.BAD)
    )
    graph_checks = core.displayed_graph_checks(graph)
    maxcut = core.maxcut_gray_exact(graph)
    gamma_lower = 25 * (len(graph.edges) - maxcut["maximumCut"])
    displayed_gamma = 25 * len(graph.bad)
    if not (
        graph_checks["triangleCount"] == 0
        and graph_checks["blueConnected"]
        and graph_checks["allBadDistanceFour"]
        and graph_checks["cutValue"] == maxcut["maximumCut"]
        and displayed_gamma == gamma_lower
    ):
        raise AssertionError((graph_checks, maxcut, displayed_gamma, gamma_lower))

    optimum_solution = solve_choice(r35, workers=args.workers)
    optimum = optimum_solution["collisionUnits"]
    seen = set()
    trials = []

    def evaluate_solution(solution: dict) -> bool:
        choice = solution["choice"]
        if choice in seen:
            return False
        seen.add(choice)
        analysis = official.analyze_tuple(graph, solution["rows"])
        trials.append(
            {
                "choice": list(choice),
                "cpSatStatus": solution["status"],
                "tieSeed": solution["tieSeed"],
                "analysis": compact_analysis(analysis),
            }
        )
        return analysis["verdict"] == "PASS"

    passing = evaluate_solution(optimum_solution)
    for seed in range(args.tie_trials):
        if passing:
            break
        solution = solve_choice(
            r35,
            optimum=optimum,
            tie_seed=230053 + seed,
            workers=args.workers,
        )
        passing = evaluate_solution(solution)

    payload = {
        "schema": "CDC_WAVE1_R35_OFFICIAL_MIN_COLLISION_SEARCH_V1",
        "model": {
            "selector": "official coherence-free P4_outsideAttachment",
            "minimumObjective": "global collisionUnits over all row tuples",
            "cpSatArithmetic": "integer constraints and objective only",
            "hallArithmetic": "integer Dinic plus direct grouped-shore enumeration",
        },
        "graph": {
            "order": r35.N,
            "graph6": core.graph6_encode(r35.N, r35.EDGES),
            "blueEdges": len(r35.BLUE),
            "badEdges": len(r35.BAD),
            "rowFamilySizes": list(r35.RADICES),
            "rowTupleProduct": __import__("math").prod(r35.RADICES),
            "side": graph_checks["side"],
            "triangleFree": graph_checks["triangleCount"] == 0,
            "blueConnected": graph_checks["blueConnected"],
            "maximumCutCertificate": maxcut,
            "displayedGamma": displayed_gamma,
            "gammaLowerBoundAtMaximumCut": gamma_lower,
            "gammaMinimal": displayed_gamma == gamma_lower,
        },
        "optimization": {
            "status": optimum_solution["status"],
            "minimumCollisionUnits": optimum,
            "workers": args.workers,
            "tieTrialsRequested": args.tie_trials,
            "distinctOptimalTuplesEvaluated": len(trials),
        },
        "trials": trials,
        "passingMinimumTupleFound": passing,
        "selectorVerdict": (
            "PASS_SOME_MINIMUM_TUPLE"
            if passing
            else "NO_PASS_IN_BOUNDED_OPTIMAL_FACE_SEARCH"
        ),
        "sourceSha256": {
            "official_selector.py": file_sha(HERE / "official_selector.py"),
            "selector_core.py": file_sha(HERE / "selector_core.py"),
            "r35_official_search.py": file_sha(Path(__file__)),
            str(R35_PATH.relative_to(ROOT)).replace("\\", "/"): file_sha(R35_PATH),
        },
    }
    payload["canonicalPayloadSha256"] = core.canonical_sha(payload)
    OUTPUT.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    print(
        json.dumps(
            {
                "minimumCollisionUnits": optimum,
                "distinctOptimalTuplesEvaluated": len(trials),
                "passingMinimumTupleFound": passing,
                "firstDefect": trials[0]["analysis"]["defect"],
                "payloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if passing else 2


if __name__ == "__main__":
    raise SystemExit(main())
