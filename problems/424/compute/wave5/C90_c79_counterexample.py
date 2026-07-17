#!/usr/bin/env python3
"""Discover and exactly replay the Boolean C79 counterexample at X=2064.

HiGHS is used only to locate an integral optimum.  Acceptance reconstructs
the arithmetic independently and checks the saved 0/1 set, every distinct-
factor subadditivity row, all forced coordinates, and the exact H-Q value.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C90 = load("c90_arithmetic", "C90_ordered_bank.py")
C79 = load("c90_c79_discovery", "C79_fractional_boundary.py")


def discover(limit: int) -> dict:
    model, objective, _hard, _splitless = C79.build(limit)
    matrix = coo_matrix(
        (model.data, (model.rows, model.cols)),
        shape=(len(model.rhs), len(model.names)),
    ).tocsr()
    result = linprog(
        np.asarray(objective, dtype=float),
        A_ub=matrix,
        b_ub=np.asarray(model.rhs, dtype=float),
        bounds=list(zip(model.lower, model.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    integral: list[int] = []
    for name, value in zip(model.names, result.x):
        rounded = int(round(float(value)))
        if rounded not in (0, 1) or abs(float(value) - rounded) > 1e-8:
            raise RuntimeError(f"nonintegral optimum at {name}: {value}")
        integral.append(rounded)
    selected_u = sorted(
        int(name[2:])
        for name, value in zip(model.names, integral)
        if name.startswith("u_") and value == 1
    )
    positive_q = sorted(
        int(name[2:])
        for name, value in zip(model.names, integral)
        if name.startswith("q_") and value == 1
    )
    certificate = {
        "schema_version": 1,
        "limit": limit,
        "selected_u": selected_u,
        "positive_q": positive_q,
    }
    verify(certificate)
    return certificate


def verify(certificate: dict) -> dict:
    limit = int(certificate["limit"])
    data = C90.arithmetic(limit)
    selected = {int(n) for n in certificate["selected_u"]}
    listed_q = {int(n) for n in certificate["positive_q"]}
    if len(selected) != len(certificate["selected_u"]):
        raise RuntimeError("duplicate selected value")
    if len(listed_q) != len(certificate["positive_q"]):
        raise RuntimeError("duplicate q value")
    if not selected <= set(data.values):
        raise RuntimeError("selected value outside the allowed interval")
    if 2 in selected or 3 in selected:
        raise RuntimeError("a seed has u=1")
    if not data.splitless <= selected:
        missing = sorted(data.splitless - selected)[:20]
        raise RuntimeError(f"forced splitless values omitted: {missing}")
    for n in data.values:
        if n not in selected:
            continue
        for a, b in data.pairs[n]:
            if a not in selected and b not in selected:
                raise RuntimeError(f"subadditivity fails at {n}+1={a}*{b}")

    recomputed_q = {
        child
        for parent in data.values
        for child in (2 * parent - 1,)
        if child <= limit and parent in selected and child not in selected
    }
    if listed_q != recomputed_q:
        raise RuntimeError("saved q support differs from the exact boundary")
    hard_shapes = {
        n for n in data.values if C90.hard_shape(n, data.pairs[n])
    }
    hard_selected = hard_shapes & selected
    excess = len(hard_selected) - len(recomputed_q)
    if excess != 1:
        raise RuntimeError(f"counterexample excess is {excess}, expected 1")
    return {
        "limit": limit,
        "selected_u": len(selected),
        "hard_shapes": len(hard_shapes),
        "selected_hard_shapes": len(hard_selected),
        "positive_q": len(recomputed_q),
        "hard_minus_boundary": excess,
        "forced_splitless": len(data.splitless),
        "all_subadditivity_rows_exact": True,
        "exact_replay": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.generate is not None:
        if args.output is None:
            parser.error("--generate requires --output")
        certificate = discover(args.generate)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
        print(verify(certificate))
    else:
        certificate = json.loads(args.verify.read_text(encoding="utf-8"))
        print(verify(certificate))


if __name__ == "__main__":
    main()
