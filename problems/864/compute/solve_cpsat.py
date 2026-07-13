#!/usr/bin/env python3
'''Exact CP-SAT discovery solver for Erdos Problem #864.'''
from __future__ import annotations
import argparse, json, math, time
from collections import Counter
from pathlib import Path
from ortools.sat.python import cp_model

def representation_counts(values):
    a = sorted(values)
    c = Counter()
    for i, x in enumerate(a):
        for y in a[i:]:
            c[x + y] += 1
    return c

def analyze_set(n, values):
    a = sorted(values)
    if len(a) != len(set(a)):
        raise ValueError('duplicate elements')
    if any(x < 1 or x > n for x in a):
        raise ValueError('element outside [1,N]')
    c = representation_counts(a)
    repeated = sorted((s, r) for s, r in c.items() if r >= 2)
    exceptional = repeated[0][0] if repeated else None
    aset = set(a)
    reflected = 0 if exceptional is None else sum(
        1 for x in a if x <= exceptional - x and exceptional - x in aset)
    return {
        'N': n, 'A': a, 'size': len(a),
        'admissible': len(repeated) <= 1,
        'repeated_sums': repeated,
        'exceptional_sum': exceptional,
        'exceptional_multiplicity': repeated[0][1] if repeated else 0,
        'reflected_pairs_at_exception': reflected,
        'exception_midpoint_present': (exceptional is not None and
            exceptional % 2 == 0 and exceptional // 2 in aset),
        'min': a[0] if a else None, 'max': a[-1] if a else None,
        'span': a[-1] - a[0] if a else 0,
        'sum_values': len(c),
        'unordered_pairs': len(a) * (len(a) + 1) // 2,
    }

def build_model(n):
    if n < 1:
        raise ValueError('N must be positive')
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f'x_{i}') for i in range(n + 1)]
    model.Add(x[0] == 0)
    # Any nonempty candidate can be translated left to have minimum 1.
    model.Add(x[1] == 1)
    by_sum = {s: [] for s in range(2, 2 * n + 1)}
    for a in range(1, n + 1):
        by_sum[2 * a].append(x[a])
        for b in range(a + 1, n + 1):
            y = model.NewBoolVar(f'p_{a}_{b}')
            model.Add(y <= x[a])
            model.Add(y <= x[b])
            model.Add(y >= x[a] + x[b] - 1)
            by_sum[a + b].append(y)
    flags = []
    for s, terms in by_sum.items():
        if len(terms) <= 1:
            continue
        z = model.NewBoolVar(f'repeat_{s}')
        r = cp_model.LinearExpr.sum(terms)
        model.Add(r <= 1 + (len(terms) - 1) * z)
        model.Add(r >= 2 * z)
        flags.append(z)
    model.Add(cp_model.LinearExpr.sum(flags) <= 1)
    model.Maximize(cp_model.LinearExpr.sum(x[1:]))
    return model, x

def solve_one(n, workers, time_limit, log_search=False):
    model, x = build_model(n)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 864
    solver.parameters.log_search_progress = log_search
    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start
    result = {
        'N': n, 'status': solver.StatusName(status), 'workers': workers,
        'time_limit_seconds': time_limit, 'wall_seconds': elapsed,
        'conflicts': solver.NumConflicts(), 'branches': solver.NumBranches(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result.update(analyze_set(n, [i for i in range(1, n + 1)
                                      if solver.Value(x[i])]))
        if not result['admissible']:
            raise AssertionError('non-admissible solver output')
        result['objective'] = int(round(solver.ObjectiveValue()))
        if result['objective'] != result['size']:
            raise AssertionError('objective mismatch')
    # Diagnostic only: exact acceptance requires status OPTIMAL.
    if status != cp_model.UNKNOWN:
        bound = solver.BestObjectiveBound()
        if math.isfinite(bound):
            result['diagnostic_best_bound'] = bound
    result['finite_optimum_certified'] = status == cp_model.OPTIMAL
    return result

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--n', type=int)
    g.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'))
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--time-limit', type=float, default=3600.0)
    p.add_argument('--output', type=Path)
    p.add_argument('--log-search', action='store_true')
    args = p.parse_args()
    if not 1 <= args.workers <= 64:
        raise SystemExit('--workers must be in [1,64]')
    if args.time_limit <= 0:
        raise SystemExit('--time-limit must be positive')
    if args.n is not None:
        ns = [args.n]
    else:
        start, end = args.range
        if start < 1 or end < start:
            raise SystemExit('invalid --range')
        ns = list(range(start, end + 1))
    out = args.output.open('a', encoding='utf-8') if args.output else None
    try:
        for n in ns:
            result = solve_one(n, args.workers, args.time_limit, args.log_search)
            line = json.dumps(result, sort_keys=True, separators=(',', ':'))
            print(line, flush=True)
            if out:
                out.write(line + '\n')
                out.flush()
    finally:
        if out:
            out.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
