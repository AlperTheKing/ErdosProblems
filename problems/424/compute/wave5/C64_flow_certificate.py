#!/usr/bin/env python3
"""Verify C56 certificates through their exact token-flow interpretation.

This checker deliberately ignores the stored LP bound multipliers.  It parses
only closure and seed-2 rows and verifies the sufficient flow inequalities
from the C64 lemma with Python integers.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c56_image", HERE / "C56_image_lp_dual.py")
if not SPEC or not SPEC.loader:
    raise RuntimeError("cannot load C56_image_lp_dual.py")
C56 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C56
SPEC.loader.exec_module(C56)

CLOSURE = re.compile(r"^closure_(\d+)_(\d+)_(\d+)$")
BOUNDARY = re.compile(r"^q_ge_difference_(\d+)$")


def load_certificates(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else [value]


def verify_flow(cert: dict) -> dict:
    limit = int(cert["limit"])
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    value_set = set(values)
    pairs = {n: C56.admissible_pairs(n) for n in values}
    hard = {n for n in values if C56.hard_shape(n, pairs[n])}
    splitless = {n for n in values if n not in (2, 3) and not pairs[n]}

    produced: Counter[int] = Counter()
    consumed: Counter[int] = Counter()
    selected_by_output: defaultdict[int, set[tuple[int, int]]] = defaultdict(set)
    beta: dict[int, int] = {}
    split_mass = 0

    for name, raw_value in cert["row"]:
        value = int(raw_value)
        if value >= 0:
            raise RuntimeError(f"{limit}: nonnegative selected row {name}={value}")
        amount = -value
        closure = CLOSURE.fullmatch(name)
        if closure:
            n, a, b = map(int, closure.groups())
            if n not in value_set or (a, b) not in pairs[n]:
                raise RuntimeError(f"{limit}: invalid closure row {name}")
            produced[n] += amount
            consumed[a] += amount
            consumed[b] += amount
            selected_by_output[n].add((a, b))
            split_mass += amount
            continue
        boundary = BOUNDARY.fullmatch(name)
        if boundary:
            child = int(boundary.group(1))
            parent = (child + 1) // 2
            if child % 2 != 1 or child > limit or parent not in value_set:
                raise RuntimeError(f"{limit}: invalid boundary row {name}")
            if child in beta:
                raise RuntimeError(f"{limit}: duplicate boundary row {name}")
            if amount > 1:
                raise RuntimeError(f"{limit}: boundary capacity exceeded at {child}")
            beta[child] = amount
            continue
        raise RuntimeError(f"{limit}: unsupported selected row {name}")

    divergence: dict[int, int] = {}
    residual: dict[int, int] = {}
    overflow: dict[int, int] = {}
    for vertex in values:
        boundary_out = beta.get(2 * vertex - 1, 0)
        boundary_in = beta.get(vertex, 0)
        div = produced[vertex] - consumed[vertex] + boundary_out - boundary_in
        divergence[vertex] = div
        if vertex not in (2, 3) and vertex not in splitless:
            room = int(vertex in hard) - div
            residual[vertex] = room
            overflow[vertex] = max(-room, 0)

    seed_arrival = -divergence[2] - divergence[3]
    overflow_penalty = sum(overflow.values())
    credit = seed_arrival - split_mass - overflow_penalty
    if credit < len(hard):
        raise RuntimeError(
            f"{limit}: flow credit {credit} is below hard count {len(hard)}"
        )

    multiple_outputs = {
        n: sorted([list(pair) for pair in choices])
        for n, choices in selected_by_output.items()
        if len(choices) > 1
    }
    return {
        "limit": limit,
        "hard_count": len(hard),
        "selected_closure_rows": sum(len(v) for v in selected_by_output.values()),
        "selected_closure_outputs": len(selected_by_output),
        "outputs_with_multiple_selected_pairs": multiple_outputs,
        "selected_boundary_rows": len(beta),
        "max_boundary_multiplier": max(beta.values(), default=0),
        "max_closure_multiplier": max(produced.values(), default=0),
        "split_mass": split_mass,
        "seed_arrival": seed_arrival,
        "overflow_vertices": sum(value > 0 for value in overflow.values()),
        "overflow_penalty": overflow_penalty,
        "flow_credit": credit,
        "flow_margin": credit - len(hard),
        "positive_free_residual": sum(value > 0 for value in residual.values()),
        "max_free_residual": max(residual.values(), default=0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificates", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summaries = []
    for path in args.certificates:
        summaries.extend(verify_flow(cert) for cert in load_certificates(path))
    text = json.dumps(summaries, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
