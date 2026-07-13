#!/usr/bin/env python3
"""Exact literal-hole subset repair of archived C84 countermodels.

For every archived endpoint Sidon ruler with T_F > C_S, and for b=1,2:

1. maximize the size of an endpoint-retaining literal-hole subset;
2. if positive defect remains possible, maximize T_F-C_S over all such
   subsets, encoding every inherited fold and loose triangle exactly.

Every CP-SAT worker is single-threaded.  Independent jobs are parallelized
at the process level, with a hard cap of 16 workers.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Sequence

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
P86_PATH = ROOT / "problems/864/compute/p86/dense_loose_search.py"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p88/c84_subset_repair.json"


def load_p86():
    spec = importlib.util.spec_from_file_location("p86_for_p88_repair", P86_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(P86_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def loose_triangle_supports(
    values: Sequence[int], edges: Sequence[tuple[int, int, int, int]]
) -> list[frozenset[int]]:
    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(edges)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(edges)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(edges)}
    out = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or len(set(ids)) != 3:
                continue
            out.append(frozenset(q for index in ids for q in edges[index]))
    return out


def hole_supports(values: Sequence[int], b: int) -> list[frozenset[int]]:
    support = set(values)
    out: set[frozenset[int]] = set()
    for i, x in enumerate(values):
        for j in range(i, len(values)):
            y = values[j]
            for k in range(j, len(values)):
                z = values[k]
                w = x + y + z + b
                if w > values[-1]:
                    break
                if w in support:
                    out.add(frozenset((x, y, z, w)))
    return sorted(out, key=lambda row: (len(row), tuple(sorted(row))))


def positive_defect_min_order(h: int) -> int:
    p = 1
    while (3 * p * p - p + 2) // 2 <= h:
        p += 1
    return p


def add_hole_constraints(model, selected, holes) -> None:
    for support in holes:
        model.Add(sum(selected[v] for v in support) <= len(support) - 1)


def add_and_indicator(model, selected, support, name: str):
    indicator = model.NewBoolVar(name)
    for value in support:
        model.Add(indicator <= selected[value])
    model.Add(
        indicator >= sum(selected[value] for value in support) - len(support) + 1
    )
    return indicator


def solve_job(job: dict[str, object]) -> dict[str, object]:
    p86 = load_p86()
    values = tuple(int(x) for x in job["B"])
    b = int(job["b"])
    h = values[-1] + 1
    edges, _sums = p86.fold_edges(values, h)
    triangles = loose_triangle_supports(values, edges)
    holes = hole_supports(values, b)
    p_min = positive_defect_min_order(h)

    cardinality_model = cp_model.CpModel()
    selected = {v: cardinality_model.NewBoolVar(f"x{v}") for v in values}
    cardinality_model.Add(selected[values[-1]] == 1)
    add_hole_constraints(cardinality_model, selected, holes)
    cardinality_model.Maximize(sum(selected.values()))
    cardinality_solver = cp_model.CpSolver()
    cardinality_solver.parameters.max_time_in_seconds = int(job["cardinality_seconds"])
    cardinality_solver.parameters.num_search_workers = 1
    cardinality_status = cardinality_solver.Solve(cardinality_model)
    max_cardinality = (
        int(round(cardinality_solver.ObjectiveValue()))
        if cardinality_status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
    )
    result: dict[str, object] = {
        "parent_id": job["parent_id"],
        "b": b,
        "parent_p": len(values),
        "h": h,
        "parent_delta": (3 * len(values) ** 2 - len(values) + 2) // 2 - h,
        "parent_C_S": len(edges),
        "parent_T_F": len(triangles),
        "hole_obstruction_count": len(holes),
        "positive_defect_min_p": p_min,
        "max_hole_subset_status": cardinality_solver.StatusName(cardinality_status),
        "max_hole_subset_bound": cardinality_solver.BestObjectiveBound(),
        "max_hole_subset_p": max_cardinality,
    }
    if (
        cardinality_status == cp_model.OPTIMAL
        and max_cardinality is not None
        and max_cardinality < p_min
    ):
        result["repair_status"] = "positive_defect_infeasible"
        return result

    model = cp_model.CpModel()
    selected = {v: model.NewBoolVar(f"x{v}") for v in values}
    model.Add(selected[values[-1]] == 1)
    model.Add(sum(selected.values()) >= p_min)
    add_hole_constraints(model, selected, holes)
    fold_vars = [
        add_and_indicator(model, selected, frozenset(edge), f"f{index}")
        for index, edge in enumerate(edges)
    ]
    triangle_vars = [
        add_and_indicator(model, selected, support, f"t{index}")
        for index, support in enumerate(triangles)
    ]
    model.Maximize(sum(triangle_vars) - sum(fold_vars))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = int(job["margin_seconds"])
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    result.update({
        "repair_status": solver.StatusName(status),
        "margin_bound": solver.BestObjectiveBound(),
        "margin": (
            int(round(solver.ObjectiveValue()))
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
        ),
    })
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result
    subset = tuple(v for v in values if solver.Value(selected[v]))
    audit = p86.audit_candidate(subset, h, b, "p88", "induced subset", 0)
    if int(audit["T_F"]) - int(audit["C_S"]) != result["margin"]:
        raise AssertionError((audit, result))
    result.update({
        "subset_B": list(subset),
        "subset_p": int(audit["p"]),
        "subset_delta": int(audit["delta"]),
        "subset_C_S": int(audit["C_S"]),
        "subset_T_F": int(audit["T_F"]),
    })
    return result


def find_parent_jobs(
    cardinality_seconds: int, margin_seconds: int
) -> tuple[list[dict[str, object]], dict[str, int]]:
    p86 = load_p86()
    bases, _manifests = p86.load_archives()
    parents = []
    folded = 0
    for index, base in enumerate(bases):
        values = base.values
        h = values[-1] + 1
        edges, _sums = p86.fold_edges(values, h)
        if not edges:
            continue
        folded += 1
        triangles, _witnesses = p86.loose_triangle_data(edges, 0)
        delta = (3 * len(values) ** 2 - len(values) + 2) // 2 - h
        if triangles <= len(edges) or delta <= 0:
            continue
        parents.append({
            "parent_id": f"archive-{index}",
            "B": list(values),
            "p": len(values),
            "h": h,
            "delta": delta,
            "C_S": len(edges),
            "T_F": triangles,
            "source": base.sources[0],
        })
    parents.sort(key=lambda row: (int(row["p"]), int(row["h"]), str(row["parent_id"])))
    jobs = [
        {
            "parent_id": parent["parent_id"], "B": parent["B"], "b": b,
            "cardinality_seconds": cardinality_seconds,
            "margin_seconds": margin_seconds,
        }
        for parent in parents for b in (1, 2)
    ]
    return jobs, {
        "archive_bases": len(bases),
        "raw_endpoint_systems_with_folds": folded,
        "positive_defect_raw_C84_violations": len(parents),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--cardinality-seconds", type=int, default=5)
    parser.add_argument("--margin-seconds", type=int, default=30)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    jobs, summary = find_parent_jobs(
        max(1, int(args.cardinality_seconds)), max(1, int(args.margin_seconds))
    )
    workers = max(1, min(16, int(args.workers)))
    if workers == 1:
        rows = [solve_job(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(solve_job, jobs, chunksize=1))
    witnesses = [
        row for row in rows
        if row.get("repair_status") in {"OPTIMAL", "FEASIBLE"}
        and int(row.get("margin", -1)) > 0
    ]
    witnesses.sort(key=lambda row: (int(row["subset_p"]), int(row["h"]), int(row["b"])))
    payload = {
        "schema_version": 1,
        "arithmetic": "exact integer enumeration and CP-SAT",
        "worker_cap": workers,
        **summary,
        "jobs": len(jobs),
        "certified_positive_margin_witnesses": len(witnesses),
        "smallest_witness": witnesses[0] if witnesses else None,
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(args.output)


if __name__ == "__main__":
    main()
