#!/usr/bin/env python3
"""Construct and exactly verify a C79 dual from a C65 path packing.

The input is a feasible certificate emitted by ``C84_deadline_pack.py``.
Every unary path edge uses one subadditivity row.  Its generated-factor load,
and every grounded terminal load, are recursively pushed to the seeds through
a fixed grounded derivation.  This is the global update that lets old closure
multipliers, including ``subadd_5_2_3``, grow with the cutoff.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C84 = load("c84_flow_base", "C84_global_dual_coarea.py")
PACK = load("c84_pack_verify", "C84_deadline_pack.py")


def selected_grounding_pair(data, n: int) -> tuple[int, int]:
    for a, b in data.pairs[n]:
        if a in data.generated and b in data.generated:
            return a, b
    raise RuntimeError(f"generated value {n} has no grounded witness")


def construct(certificate: dict) -> dict:
    pack_summary = PACK.verify(certificate)
    if not pack_summary.get("verified_feasible"):
        raise RuntimeError("input is not a feasible path packing")
    limit = int(certificate["limit"])
    data = C84.arithmetic(limit)
    hard_shapes = {
        n for n in data.values if C84.hard_shape(n, list(data.pairs[n]))
    }
    generated_hard = hard_shapes & data.generated

    hard_start = Counter()
    splitless_start = Counter()
    unary_flow = Counter()
    seed_flow = Counter()
    path_ground_load = Counter()

    for record in certificate["paths"]:
        for step in record["steps"]:
            kind = step["kind"]
            u, v = int(step["from"]), int(step["to"])
            if kind == "hard_source":
                hard_start[v] += 1
            elif kind == "splitless_source":
                splitless_start[v] += 1
            elif kind == "unary":
                witness = int(step["witness"])
                unary_flow[(u, v, witness)] += 1
                path_ground_load[witness] += 1
            elif kind == "seed":
                seed_flow[(u, v)] += 1
            elif kind == "seed_to_ground":
                child = int(step["witness"])
                seed_flow[(u, child)] += 1
                path_ground_load[child] += 1
            else:
                raise RuntimeError(f"unknown path step {kind}")

    if any(value > 1 for value in hard_start.values()):
        raise RuntimeError("hard-source capacity exceeded")
    if any(value > 1 for value in seed_flow.values()):
        raise RuntimeError("seed capacity exceeded")

    # alpha indexes subadditivity rows (output, smaller factor, larger factor).
    alpha = Counter()
    for (n, target, witness), amount in unary_flow.items():
        a, b = sorted((target, witness))
        if (a, b) not in data.pairs[n]:
            raise RuntimeError("unary flow has no matching subadditivity row")
        alpha[(n, a, b)] += amount

    # Push all generated loads globally to the fixed seeds.  Factors are
    # strictly smaller than their output, so descending order is exact.
    # C79 charges every hard shape, including generated hard values.  Their
    # potentials vanish by grounded induction, so each contributes one more
    # grounding request in the exact dual identity.
    propagated = Counter(path_ground_load)
    propagated.update(generated_hard)
    for n in sorted(data.generated, reverse=True):
        if n in (2, 3):
            continue
        amount = propagated[n]
        if not amount:
            continue
        a, b = selected_grounding_pair(data, n)
        alpha[(n, a, b)] += amount
        propagated[a] += amount
        propagated[b] += amount
        propagated[n] = 0
    if any(propagated[n] for n in data.generated if n not in (2, 3)):
        raise RuntimeError("ground load did not reach the seeds")

    beta = Counter({child: amount for (_parent, child), amount in seed_flow.items()})
    if any(amount > 1 for amount in beta.values()):
        raise RuntimeError("boundary multiplier exceeds q capacity")

    # Verify the exact slack identity after substituting fixed values:
    # u_2=u_3=0 and u_e=1 for structural splitless e.
    #
    # sum q - sum_{hard holes} u_h
    # = sum alpha(u_a+u_b-u_n)
    # + sum beta(q_c+u_c-u_p)
    # + sum_h(1-a_h)(1-u_h)
    # + sum_c(1-beta_c)q_c.
    lhs_constant = 0
    lhs_u = Counter({h: -1 for h in hard_shapes})
    lhs_q = Counter({2 * p - 1: 1 for p in data.values if 2 * p - 1 <= limit})

    rhs_constant = 0
    rhs_u = Counter()
    rhs_q = Counter()
    for (n, a, b), amount in alpha.items():
        rhs_u[a] += amount
        rhs_u[b] += amount
        rhs_u[n] -= amount
    for child, amount in beta.items():
        parent = (child + 1) // 2
        rhs_q[child] += amount
        rhs_u[child] += amount
        rhs_u[parent] -= amount
    for h in data.hard:
        amount = 1 - hard_start[h]
        rhs_constant += amount
        rhs_u[h] -= amount
    for child in lhs_q:
        rhs_q[child] += 1 - beta[child]

    fixed = {2: 0, 3: 0}
    fixed.update({n: 1 for n in data.splitless})
    for n, value in fixed.items():
        lhs_constant += lhs_u.pop(n, 0) * value
        rhs_constant += rhs_u.pop(n, 0) * value
    lhs_u += Counter()  # drop zero entries below
    rhs_u += Counter()
    lhs_q += Counter()
    rhs_q += Counter()
    if lhs_constant != rhs_constant:
        raise RuntimeError(f"constant mismatch {lhs_constant} != {rhs_constant}")
    if lhs_u != rhs_u:
        differing = sorted(set(lhs_u) | set(rhs_u))
        witness = [(n, lhs_u[n], rhs_u[n]) for n in differing if lhs_u[n] != rhs_u[n]][:20]
        raise RuntimeError(f"u stationarity mismatch: {witness}")
    if lhs_q != rhs_q:
        differing = sorted(set(lhs_q) | set(rhs_q))
        witness = [(n, lhs_q[n], rhs_q[n]) for n in differing if lhs_q[n] != rhs_q[n]][:20]
        raise RuntimeError(f"q stationarity mismatch: {witness}")

    alpha_rows = [
        {"output": n, "left": a, "right": b, "multiplier": amount}
        for (n, a, b), amount in sorted(alpha.items())
        if amount
    ]
    return {
        "schema_version": 1,
        "limit": limit,
        "hard_shapes": len(hard_shapes),
        "hard_holes": len(data.hard),
        "generated_hard_shapes": len(generated_hard),
        "paths": len(certificate["paths"]),
        "hard_source_paths": sum(hard_start.values()),
        "splitless_source_paths": sum(splitless_start.values()),
        "unary_flow_units": sum(unary_flow.values()),
        "used_seed_edges": sum(seed_flow.values()),
        "path_ground_load_units": sum(path_ground_load.values()),
        "objective_ground_load_units": len(generated_hard),
        "total_ground_load_units": sum(path_ground_load.values()) + len(generated_hard),
        "base_multiplier_alpha_5": alpha[(5, 2, 3)],
        "maximum_alpha": max(alpha.values(), default=0),
        "nonzero_alpha_rows": len(alpha_rows),
        "nonzero_beta_rows": sum(value != 0 for value in beta.values()),
        "seed_terminal_load_2": propagated[2],
        "seed_terminal_load_3": propagated[3],
        "identity_constant": lhs_constant,
        "stationarity_exact": True,
        "dual_signs_exact": True,
        "alpha_rows": alpha_rows,
        "beta_rows": [
            {"child": child, "multiplier": amount}
            for child, amount in sorted(beta.items())
            if amount
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    certificate = json.loads(args.packing.read_text(encoding="utf-8"))
    result = construct(certificate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print({key: value for key, value in result.items() if key not in ("alpha_rows", "beta_rows")})


if __name__ == "__main__":
    main()
