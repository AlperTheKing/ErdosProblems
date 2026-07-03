#!/usr/bin/env python3
"""ChartSOS Gram sparsity analyzer for CERT-2 charted equality certificates.

Search helper only: builds degree-6 monomial compatibility graphs and reports
component/block sizes before a real chordal/SOS solve is attempted. No proof claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos


def add_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def monomials_leq_degree(num_vars: int, max_degree: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def rec(pos: int, remaining: int, cur: list[int]) -> None:
        if pos == num_vars - 1:
            for x in range(remaining + 1):
                out.append(tuple(cur + [x]))
            return
        for x in range(remaining + 1):
            cur.append(x)
            rec(pos + 1, remaining - x, cur)
            cur.pop()

    rec(0, max_degree, [])
    return sorted(out)


def monomials_exact_degree(num_vars: int, degree: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def rec(pos: int, remaining: int, cur: list[int]) -> None:
        if pos == num_vars - 1:
            out.append(tuple(cur + [remaining]))
            return
        for x in range(remaining + 1):
            cur.append(x)
            rec(pos + 1, remaining - x, cur)
            cur.pop()

    rec(0, degree, [])
    return sorted(out)


def rows_from_seed(seed_path: str | None, target12: dict[tuple[int, ...], Fraction]) -> set[tuple[int, ...]]:
    if seed_path is None:
        return {exp for exp, coeff in target12.items() if coeff < 0}
    data = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    rows = data.get("active_rows", data.get("rows", []))
    return {tuple(int(x) for x in row) for row in rows}


def sparse_basis_for_rows(rows: set[tuple[int, ...]]) -> list[tuple[int, ...]]:
    basis: set[tuple[int, ...]] = set()
    for row in rows:
        halves = []
        for x in row:
            lo = x // 2
            halves.append((lo, x - lo))
        for mask in range(1 << len(row)):
            beta = tuple(halves[i][(mask >> i) & 1] for i in range(len(row)))
            gamma = tuple(row[i] - beta[i] for i in range(len(row)))
            basis.add(beta)
            basis.add(gamma)
    return sorted(basis)


def build_pair_graph(basis: list[tuple[int, ...]], rows: set[tuple[int, ...]]):
    by_exp = {exp: i for i, exp in enumerate(basis)}
    by_sum: dict[tuple[int, ...], list[tuple[int, int]]] = defaultdict(list)
    adj = [set() for _ in basis]
    active_pair_count = 0
    represented_rows: set[tuple[int, ...]] = set()
    diag_rows: set[tuple[int, ...]] = set()
    for i, a in enumerate(basis):
        doubled = tuple(2 * x for x in a)
        if doubled in rows:
            adj[i].add(i)
            by_sum[doubled].append((i, i))
            active_pair_count += 1
            represented_rows.add(doubled)
            diag_rows.add(doubled)
        for j in range(i + 1, len(basis)):
            s = add_exp(a, basis[j])
            if s in rows:
                adj[i].add(j)
                adj[j].add(i)
                by_sum[s].append((i, j))
                active_pair_count += 1
                represented_rows.add(s)
    return adj, by_sum, active_pair_count, represented_rows, diag_rows


def components(adj: list[set[int]]) -> list[list[int]]:
    seen = [False] * len(adj)
    comps: list[list[int]] = []
    for start in range(len(adj)):
        if seen[start]:
            continue
        q = deque([start])
        seen[start] = True
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def component_row_stats(comps: list[list[int]], basis: list[tuple[int, ...]], rows: set[tuple[int, ...]]):
    comp_id = {}
    for idx, comp in enumerate(comps):
        for v in comp:
            comp_id[v] = idx
    comp_rows: list[set[tuple[int, ...]]] = [set() for _ in comps]
    cross_rows: set[tuple[int, ...]] = set()
    row_pair_mult = Counter()
    for i, a in enumerate(basis):
        for j in range(i, len(basis)):
            s = add_exp(a, basis[j])
            if s not in rows:
                continue
            ci = comp_id[i]
            cj = comp_id[j]
            if ci == cj:
                comp_rows[ci].add(s)
            else:
                cross_rows.add(s)
                row_pair_mult[s] += 1
    return comp_rows, cross_rows, row_pair_mult


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--basis", choices=["dense-leq", "dense-exact", "sparse"], default="sparse")
    ap.add_argument("--seed-rows", default="")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_sos_sparsity_v1.json")
    args = ap.parse_args()

    target11, generators, meta = lp.build_chart(args.chart)
    target12 = sos.mul_linear(target11)
    rows = rows_from_seed(args.seed_rows or None, target12)
    num_vars = len(next(iter(target12)))
    if args.basis == "dense-leq":
        basis = monomials_leq_degree(num_vars, 6)
        seed = (6,) + (0,) * (num_vars - 1)
        basis = [b for b in basis if b != seed]
    elif args.basis == "dense-exact":
        basis = monomials_exact_degree(num_vars, 6)
        seed = (6,) + (0,) * (num_vars - 1)
        basis = [b for b in basis if b != seed]
    else:
        basis = sparse_basis_for_rows(rows)

    adj, by_sum, pair_count, represented, diag_rows = build_pair_graph(basis, rows)
    comps = components(adj)
    comp_rows, cross_rows, row_pair_mult = component_row_stats(comps, basis, rows)
    comp_degrees = [sum(len(adj[v]) for v in comp) // 2 for comp in comps]
    out = {
        "schema": "eq_cert2_chart_sos_sparsity_v1",
        "chart": args.chart,
        "basis_mode": args.basis,
        "seed_rows": args.seed_rows or None,
        "basis_size": len(basis),
        "row_count": len(rows),
        "target12_terms": len(target12),
        "target12_negative_terms": sum(1 for c in target12.values() if c < 0),
        "active_pair_count": pair_count,
        "represented_row_count": len(represented),
        "unrepresented_row_count": len(rows - represented),
        "diag_row_count": len(diag_rows),
        "component_count": len(comps),
        "component_sizes_top20": [len(c) for c in comps[:20]],
        "component_edges_top20": comp_degrees[:20],
        "component_rows_top20": [len(x) for x in comp_rows[:20]],
        "cross_component_row_count": len(cross_rows),
        "cross_component_pair_multiplicity_top10": row_pair_mult.most_common(10),
        "isolated_vertices": sum(1 for c in comps if len(c) == 1 and len(adj[c[0]]) == 0),
        "meta": meta,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    printable = dict(out)
    printable.pop("meta", None)
    print(json.dumps(printable, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
