#!/usr/bin/env python3
"""C70: exact red-team of C66-RANK on arbitrary admissible source shores.

For each cutoff and root prefix, CP-SAT minimizes

    (# nonhard exiting seed chains with root <= R)
      - (# hard truncated seed chains with root <= R)

over every Boolean shore that contains all splitless holes and is closed under
all infinite unary selector arcs.  A negative optimum is an exact falsifier to
the proposed extension of C66-RANK from canonical minimum shores to arbitrary
admissible shores.  The returned assignment is independently replayed with
plain Python integers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ortools.sat.python import cp_model


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def precompute(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    splitless = {n for n in holes if not pairs[n]}

    def hard_shape(n: int) -> bool:
        if n % 2 or not pairs[n]:
            return False
        if (n + 1) % 3:
            return True
        q = (n + 1) // 3
        return not (q != 3 and allowed(q))

    hard = {n for n in holes if hard_shape(n)}
    selectors: set[tuple[int, int]] = set()
    for n in holes:
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                parent = b if a in generated else a
                assert parent in holes
                selectors.add((n, parent))

    predecessor = {
        child: parent
        for parent in holes
        for child in [2 * parent - 1]
        if child <= limit and child in holes
    }
    roots = sorted(holes - set(predecessor))
    chains = []
    covered: set[int] = set()
    for root in roots:
        nodes = []
        node = root
        while True:
            assert node not in covered
            covered.add(node)
            nodes.append(node)
            child = 2 * node - 1
            if child > limit:
                terminal = "cutoff"
                break
            if child in holes:
                node = child
                continue
            assert child in generated
            terminal = "generated"
            break
        assert sum(n in hard for n in nodes) <= 1
        chains.append(
            {
                "root": root,
                "last": nodes[-1],
                "nodes": nodes,
                "hard": any(n in hard for n in nodes),
                "terminal": terminal,
            }
        )
    assert covered == holes
    return {
        "limit": limit,
        "values": values,
        "pairs": pairs,
        "generated": generated,
        "holes": holes,
        "splitless": splitless,
        "hard": hard,
        "selectors": selectors,
        "chains": chains,
    }


def coefficients(data: dict, root_bound: int) -> dict[int, int]:
    coeff = {n: 0 for n in data["holes"]}
    for chain in data["chains"]:
        if chain["root"] > root_bound:
            continue
        root = chain["root"]
        last = chain["last"]
        if chain["hard"]:
            if chain["terminal"] == "cutoff":
                coeff[last] -= 1
        else:
            coeff[root] += 1
            if chain["terminal"] == "cutoff":
                coeff[last] -= 1
    return {n: c for n, c in coeff.items() if c}


def replay(data: dict, shore: set[int], root_bound: int) -> dict:
    holes = data["holes"]
    assert shore <= holes
    assert data["splitless"] <= shore
    assert all(n not in shore or parent in shore for n, parent in data["selectors"])

    hard_truncated = []
    nonhard_exiting = []
    for chain in data["chains"]:
        inside = [n for n in chain["nodes"] if n in shore]
        if not inside:
            continue
        assert inside == chain["nodes"][: len(inside)]
        full = len(inside) == len(chain["nodes"])
        truncated = full and chain["terminal"] == "cutoff"
        exiting = not truncated
        if chain["hard"] and truncated:
            hard_truncated.append(chain["root"])
        if not chain["hard"] and exiting:
            nonhard_exiting.append(chain["root"])

    h_prefix = sorted(r for r in hard_truncated if r <= root_bound)
    e_prefix = sorted(r for r in nonhard_exiting if r <= root_bound)
    objective = len(e_prefix) - len(h_prefix)
    coeff = coefficients(data, root_bound)
    linear = sum(c for n, c in coeff.items() if n in shore)
    assert objective == linear
    return {
        "objective": objective,
        "hard_truncated_prefix": h_prefix,
        "nonhard_exiting_prefix": e_prefix,
        "hard_truncated_total": len(hard_truncated),
        "nonhard_exiting_total": len(nonhard_exiting),
    }


def solve_prefix(data: dict, root_bound: int, time_limit: float) -> dict:
    model = cp_model.CpModel()
    z = {n: model.new_bool_var(f"z_{n}") for n in sorted(data["holes"])}
    for n in data["splitless"]:
        model.add(z[n] == 1)
    for n, parent in data["selectors"]:
        model.add(z[n] <= z[parent])
    coeff = coefficients(data, root_bound)
    model.minimize(sum(c * z[n] for n, c in coeff.items()))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": solver.status_name(status)}
    shore = {n for n in data["holes"] if solver.value(z[n])}
    replayed = replay(data, shore, root_bound)
    assert replayed["objective"] == round(solver.objective_value)
    return {
        "status": solver.status_name(status),
        "objective": replayed["objective"],
        "root_bound": root_bound,
        "shore": sorted(shore),
        "replay": replayed,
    }


def scan(cutoffs: list[int], time_limit: float) -> dict:
    rows = []
    first_falsifier = None
    for limit in cutoffs:
        data = precompute(limit)
        root_bounds = sorted({chain["root"] for chain in data["chains"]})
        minimum = None
        minimum_row = None
        for root_bound in root_bounds:
            row = solve_prefix(data, root_bound, time_limit)
            if row["status"] != "OPTIMAL":
                raise RuntimeError((limit, root_bound, row["status"]))
            if minimum is None or row["objective"] < minimum:
                minimum = row["objective"]
                minimum_row = row
            if row["objective"] < 0:
                first_falsifier = {"limit": limit, **row}
                break
        rows.append(
            {
                "limit": limit,
                "holes": len(data["holes"]),
                "chains": len(data["chains"]),
                "root_prefixes_checked": (
                    1 + root_bounds.index(first_falsifier["root_bound"])
                    if first_falsifier and first_falsifier["limit"] == limit
                    else len(root_bounds)
                ),
                "minimum_objective": minimum,
                "minimum_root_bound": minimum_row["root_bound"],
            }
        )
        if first_falsifier:
            # Recompute and retain an exact compact witness.
            witness = replay(data, set(first_falsifier["shore"]), first_falsifier["root_bound"])
            assert witness["objective"] < 0
            first_falsifier["replay"] = witness
            break
    return {
        "cutoffs": cutoffs,
        "rows": rows,
        "first_falsifier": first_falsifier,
        "verdict": "C66-RANK false for arbitrary shores" if first_falsifier else "no falsifier",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoffs", default="54,74,100,200,362,500,1000,2000")
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("C70_arbitrary_shore_rank.json"),
    )
    args = parser.parse_args()
    cutoffs = [int(x) for x in args.cutoffs.split(",") if x]
    result = scan(cutoffs, args.time_limit)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

