#!/usr/bin/env python3
"""Adversarial computational audit of the n=18 SSNC counting obstruction.

This is not a counterexample search.  It tests the proposed local inequality

    r_u <= 2 (e_u + mu_u) - 1   whenever r_u > 0,

where r_u counts degree-8 roots for which u is outside both the closed first
out-neighborhood and the new second out-neighborhood.  The implementation is
independent of the production search model and uses integer bitsets for direct
graph evaluation.  Optional CP-SAT checks search specifically for a violation
of the local inequality and for feasibility of the claimed global incidence
constraints.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

from ortools.sat.python import cp_model


N = 18
FULL = (1 << N) - 1


def iter_bits(mask: int) -> Iterable[int]:
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def validate_rows(rows: Sequence[int], require_minimum_eight: bool = True) -> None:
    if len(rows) != N:
        raise ValueError("expected exactly 18 adjacency rows")
    for v, row in enumerate(rows):
        if row < 0 or row & ~FULL:
            raise ValueError(f"row {v} is not an 18-bit mask")
        if row & (1 << v):
            raise ValueError(f"loop at vertex {v}")
    for v in range(N):
        for w in iter_bits(rows[v]):
            if rows[w] & (1 << v):
                raise ValueError(f"digon on {v},{w}")
    if require_minimum_eight and min(row.bit_count() for row in rows) < 8:
        raise ValueError("minimum out-degree is below 8")


@dataclass(frozen=True)
class AuditMetrics:
    degrees: tuple[int, ...]
    missing_degrees: tuple[int, ...]
    excess_missing: tuple[int, ...]
    second: tuple[int, ...]
    unreachable: tuple[int, ...]
    incidence_counts: tuple[int, ...]
    local_gaps: tuple[int | None, ...]
    candidate: bool
    pair_cover_slacks: tuple[int | None, ...]


def evaluate(rows: Sequence[int]) -> AuditMetrics:
    """Compute all quantities directly, then assert each proof transition."""
    validate_rows(rows)
    degrees = tuple(row.bit_count() for row in rows)
    incoming = [0] * N
    for v, row in enumerate(rows):
        for w in iter_bits(row):
            incoming[w] |= 1 << v
    missing = tuple(
        (FULL & ~(rows[v] | incoming[v] | (1 << v))).bit_count()
        for v in range(N)
    )
    t_values = tuple(degrees[v] - 8 + missing[v] for v in range(N))

    second_masks: list[int] = []
    unreachable_masks: list[int] = []
    for v in range(N):
        raw_two = 0
        for x in iter_bits(rows[v]):
            raw_two |= rows[x]
        second = raw_two & ~rows[v] & ~(1 << v) & FULL
        closed_first = rows[v] | (1 << v)
        unreachable = FULL & ~(closed_first | second)
        second_masks.append(second)
        unreachable_masks.append(unreachable)

    roots = [v for v in range(N) if degrees[v] == 8]
    r_values = tuple(
        sum(1 for v in roots if unreachable_masks[v] & (1 << u))
        for u in range(N)
    )

    gaps: list[int | None] = []
    cover_slacks: list[int | None] = []
    for u in range(N):
        r_u = r_values[u]
        t_u = t_values[u]
        if r_u == 0:
            gaps.append(None)
            cover_slacks.append(None)
            continue
        if t_u < 1:
            raise AssertionError(f"positive r_{u} with t_{u}=0")

        # U_u = V \ ({u} union N-(u)).  Every C_v for v in R_u must fit.
        universe_u = FULL & ~(incoming[u] | (1 << u))
        root_list = [v for v in roots if unreachable_masks[v] & (1 << u)]
        exclusion_sum = 0
        for v in root_list:
            closed_v = rows[v] | (1 << v)
            if closed_v & ~universe_u:
                raise AssertionError(f"C_{v} is not contained in U_{u}")
            complement_v = universe_u & ~closed_v
            if complement_v.bit_count() != t_u - 1:
                raise AssertionError(
                    f"|B_{v}| mismatch for target {u}: "
                    f"{complement_v.bit_count()} != {t_u - 1}"
                )
            exclusion_sum += sum(
                1 for w in root_list if complement_v & (1 << w)
            )
        pair_count = math.comb(r_u, 2)
        if pair_count > exclusion_sum:
            raise AssertionError(
                f"pair-cover failure at {u}: {pair_count}>{exclusion_sum}"
            )
        upper_exclusions = r_u * (t_u - 1)
        if exclusion_sum > upper_exclusions:
            raise AssertionError("exclusion sum exceeds r(t-1)")
        if r_u > 2 * t_u - 1:
            raise AssertionError(
                f"local bound violated at {u}: r={r_u}, t={t_u}"
            )
        gaps.append(r_u - (2 * t_u - 1))
        cover_slacks.append(exclusion_sum - pair_count)

    candidate = all(second_masks[v].bit_count() < degrees[v] for v in range(N))
    return AuditMetrics(
        degrees=degrees,
        missing_degrees=missing,
        excess_missing=t_values,
        second=tuple(second_masks),
        unreachable=tuple(unreachable_masks),
        incidence_counts=r_values,
        local_gaps=tuple(gaps),
        candidate=candidate,
        pair_cover_slacks=tuple(cover_slacks),
    )


def cyclic_base() -> list[int]:
    rows = [0] * N
    for v in range(N):
        for step in range(1, 9):
            rows[v] |= 1 << ((v + step) % N)
    validate_rows(rows)
    return rows


def exhaustive_antipodal_family() -> dict[str, object]:
    """Exhaust all 3^9 states of the antipodal nonedges of a cyclic base."""
    base = cyclic_base()
    checked = 0
    candidates = 0
    saturation_count = 0
    best_gap = -10**9
    h_histogram = [0] * 10
    for code in range(3**9):
        rows = base.copy()
        value = code
        h = 0
        for i in range(9):
            state = value % 3
            value //= 3
            j = i + 9
            if state == 0:
                h += 1
            elif state == 1:
                rows[i] |= 1 << j
            else:
                rows[j] |= 1 << i
        metrics = evaluate(rows)
        checked += 1
        h_histogram[h] += 1
        candidates += int(metrics.candidate)
        for gap in metrics.local_gaps:
            if gap is not None:
                best_gap = max(best_gap, gap)
                saturation_count += int(gap == 0)
    return {
        "graphs": checked,
        "candidate_graphs": candidates,
        "maximum_local_gap": best_gap,
        "saturated_incidences": saturation_count,
        "missing_edge_histogram": h_histogram,
    }


def _pair_state(rows: Sequence[int], i: int, j: int) -> int:
    if rows[i] & (1 << j):
        return 1
    if rows[j] & (1 << i):
        return 2
    return 0


def _set_pair_state(rows: list[int], i: int, j: int, state: int) -> None:
    rows[i] &= ~(1 << j)
    rows[j] &= ~(1 << i)
    if state == 1:
        rows[i] |= 1 << j
    elif state == 2:
        rows[j] |= 1 << i
    elif state != 0:
        raise ValueError("pair state must be 0, 1, or 2")


def sampled_degree_preserving_walk(
    samples: int, steps_between: int, seed: int
) -> dict[str, object]:
    """Audit states from a deterministic walk that never lets d+ fall below 8."""
    rng = random.Random(seed)
    rows = cyclic_base()
    accepted_mutations = 0
    attempted_mutations = 0
    candidates = 0
    saturation_count = 0
    best_gap = -10**9
    distinct_signatures: set[tuple[int, ...]] = set()

    while len(distinct_signatures) < samples:
        for _ in range(steps_between):
            attempted_mutations += 1
            i, j = sorted(rng.sample(range(N), 2))
            old = _pair_state(rows, i, j)
            new = rng.randrange(3)
            if new == old:
                continue
            degrees = [row.bit_count() for row in rows]
            losing_tail: int | None = None
            if old == 1 and new != 1:
                losing_tail = i
            elif old == 2 and new != 2:
                losing_tail = j
            if losing_tail is not None and degrees[losing_tail] == 8:
                continue
            _set_pair_state(rows, i, j, new)
            accepted_mutations += 1

        signature = tuple(rows)
        if signature in distinct_signatures:
            continue
        distinct_signatures.add(signature)
        metrics = evaluate(rows)
        candidates += int(metrics.candidate)
        for gap in metrics.local_gaps:
            if gap is not None:
                best_gap = max(best_gap, gap)
                saturation_count += int(gap == 0)

    return {
        "graphs": len(distinct_signatures),
        "seed": seed,
        "steps_between": steps_between,
        "attempted_mutations": attempted_mutations,
        "accepted_mutations": accepted_mutations,
        "candidate_graphs": candidates,
        "maximum_local_gap": best_gap,
        "saturated_incidences": saturation_count,
    }


@dataclass(frozen=True)
class LocalViolationModel:
    model: cp_model.CpModel
    r_total: cp_model.IntVar
    t_target: cp_model.IntVar


def build_local_violation_model(target: int = 0) -> LocalViolationModel:
    """Build an independent graph model whose only goal is a local violation."""
    model = cp_model.CpModel()
    arc: dict[tuple[int, int], cp_model.IntVar] = {}
    for v in range(N):
        for w in range(N):
            if v != w:
                arc[v, w] = model.NewBoolVar(f"a_{v}_{w}")
    for v in range(N):
        for w in range(v + 1, N):
            model.Add(arc[v, w] + arc[w, v] <= 1)

    degree: list[cp_model.IntVar] = []
    is_degree_eight: list[cp_model.IntVar] = []
    for v in range(N):
        d_v = model.NewIntVar(8, 17, f"d_{v}")
        model.Add(d_v == sum(arc[v, w] for w in range(N) if w != v))
        degree.append(d_v)
        at_eight = model.NewBoolVar(f"degree8_{v}")
        model.Add(d_v == 8).OnlyEnforceIf(at_eight)
        model.Add(d_v >= 9).OnlyEnforceIf(at_eight.Not())
        is_degree_eight.append(at_eight)

    missing_terms: list[cp_model.IntVar] = []
    for w in range(N):
        if w == target:
            continue
        missing = model.NewBoolVar(f"missing_{target}_{w}")
        model.Add(missing + arc[target, w] + arc[w, target] == 1)
        missing_terms.append(missing)
    mu_target = model.NewIntVar(0, 17, "mu_target")
    model.Add(mu_target == sum(missing_terms))
    t_target = model.NewIntVar(0, 9, "t_target")
    model.Add(t_target == degree[target] - 8 + mu_target)

    incidence: list[cp_model.IntVar] = []
    for v in range(N):
        if v == target:
            continue
        path_terms: list[cp_model.IntVar] = []
        for x in range(N):
            if x == v or x == target:
                continue
            path = model.NewBoolVar(f"path_{v}_{x}_{target}")
            model.Add(path <= arc[v, x])
            model.Add(path <= arc[x, target])
            model.Add(path >= arc[v, x] + arc[x, target] - 1)
            path_terms.append(path)
        reachable = model.NewBoolVar(f"reachable_{v}_{target}")
        for path in path_terms:
            model.Add(reachable >= path)
        model.Add(reachable <= sum(path_terms))

        unreachable = model.NewBoolVar(f"unreachable_{v}_{target}")
        model.Add(unreachable + arc[v, target] <= 1)
        model.Add(unreachable + reachable <= 1)
        model.Add(unreachable >= 1 - arc[v, target] - reachable)

        counted = model.NewBoolVar(f"incidence_{v}_{target}")
        model.Add(counted <= is_degree_eight[v])
        model.Add(counted <= unreachable)
        model.Add(counted >= is_degree_eight[v] + unreachable - 1)
        incidence.append(counted)

    r_total = model.NewIntVar(0, 17, "r_target")
    model.Add(r_total == sum(incidence))
    # An integer violation of r <= 2t-1 is r >= 2t.  Require r>0 so the
    # t=0 branch is not misread as a violation of a bound stated for r>0.
    model.Add(r_total >= 1)
    model.Add(r_total >= 2 * t_target)
    validation_error = model.Validate()
    if validation_error:
        raise RuntimeError(validation_error)
    return LocalViolationModel(model=model, r_total=r_total, t_target=t_target)


def cp_sat_local_violation(seconds: float, workers: int) -> dict[str, object]:
    artifacts = build_local_violation_model()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 20260721
    status = solver.Solve(artifacts.model)
    result: dict[str, object] = {
        "status": solver.StatusName(status),
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result["violation"] = {
            "r": solver.Value(artifacts.r_total),
            "t": solver.Value(artifacts.t_target),
        }
    else:
        result["violation"] = None
    return result


def pure_integer_global_audit(seconds: float) -> list[dict[str, object]]:
    """Test a relaxation containing only the claimed incidence inequalities."""
    results: list[dict[str, object]] = []
    for q in range(10):
        model = cp_model.CpModel()
        t = [model.NewIntVar(0, 9, f"t_{u}") for u in range(N)]
        active = [model.NewBoolVar(f"active_{u}") for u in range(N)]
        r = [model.NewIntVar(0, 17, f"r_{u}") for u in range(N)]
        model.Add(sum(t) == 9 + q)
        for u in range(N):
            model.Add(t[u] >= 1).OnlyEnforceIf(active[u])
            model.Add(t[u] == 0).OnlyEnforceIf(active[u].Not())
            model.Add(r[u] == 0).OnlyEnforceIf(active[u].Not())
            model.Add(r[u] <= 2 * t[u] - 1).OnlyEnforceIf(active[u])
        z = model.NewIntVar(9 + q, N, "degree8_count")
        model.Add(sum(r) >= 2 * z)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = seconds
        solver.parameters.num_search_workers = 1
        status = solver.Solve(model)
        results.append(
            {
                "q": q,
                "status": solver.StatusName(status),
                "wall_time_seconds": solver.WallTime(),
            }
        )
    return results


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=20_000)
    parser.add_argument("--steps-between", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument("--cp-seconds", type=float, default=30.0)
    parser.add_argument("--cp-workers", type=int, default=4)
    parser.add_argument("--skip-cp", action="store_true")
    args = parser.parse_args(argv)
    if args.samples < 1:
        parser.error("--samples must be positive")
    if args.steps_between < 1:
        parser.error("--steps-between must be positive")
    if not 1 <= args.cp_workers <= 64:
        parser.error("--cp-workers must lie in [1,64]")
    if args.cp_seconds <= 0:
        parser.error("--cp-seconds must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result: dict[str, object] = {
        "exhaustive_antipodal_family": exhaustive_antipodal_family(),
        "sampled_walk": sampled_degree_preserving_walk(
            args.samples, args.steps_between, args.seed
        ),
    }
    if not args.skip_cp:
        result["cp_sat_local_violation"] = cp_sat_local_violation(
            args.cp_seconds, args.cp_workers
        )
        result["pure_integer_global"] = pure_integer_global_audit(
            args.cp_seconds
        )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
