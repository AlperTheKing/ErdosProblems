#!/usr/bin/env python3
"""Exact gates for the C84 global flow/coarea dual construction.

The arithmetic network is the C65 network, but this file tests a stricter
ambient-online recursion.  When a new hard root arrives at cutoff ``X``, one
new source-to-sink path must be added using only unused unit seed edges.  Old
paths are never rerouted.  Unary edges and splitless source edges have
unlimited capacity; a hard source edge has capacity one.

All accepted data are integer data.  The verifier replays every path from the
saved certificate and checks allowedness, distinct factors, source capacity,
unary witnesses, seed-edge capacity, and the hard-demand count.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    result: list[tuple[int, int]] = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return result


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


@dataclass(frozen=True)
class Arithmetic:
    limit: int
    values: tuple[int, ...]
    pairs: dict[int, tuple[tuple[int, int], ...]]
    generated: frozenset[int]
    holes: frozenset[int]
    hard: frozenset[int]
    splitless: frozenset[int]
    unary: dict[int, tuple[tuple[int, int], ...]]


def arithmetic(limit: int) -> Arithmetic:
    values = tuple(n for n in range(2, limit + 1) if allowed(n))
    pairs = {n: tuple(factor_pairs(n)) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard = {n for n in holes if hard_shape(n, list(pairs[n]))}
    splitless = {n for n in holes if not pairs[n]}
    unary: dict[int, tuple[tuple[int, int], ...]] = {}
    for n in holes:
        arcs: list[tuple[int, int]] = []
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                arcs.append((b if a in generated else a, a if a in generated else b))
        unary[n] = tuple(sorted(arcs))  # (hole target, generated witness)
    return Arithmetic(
        limit,
        values,
        pairs,
        frozenset(generated),
        frozenset(holes),
        frozenset(hard),
        frozenset(splitless),
        unary,
    )


def find_forward_path(
    data: Arithmetic,
    cutoff: int,
    used_seed: set[tuple[int, int]],
    used_hard_sources: set[int],
) -> dict | None:
    """Return the deterministic shortest forward path at this cutoff."""

    parent: dict[int, tuple[int | None, str, int | None]] = {}
    queue: deque[int] = deque()
    starts = sorted(
        (n for n in data.splitless if n <= cutoff),
    ) + sorted(n for n in data.hard if n <= cutoff and n not in used_hard_sources)
    for n in starts:
        if n in parent:
            continue
        kind = "splitless_source" if n in data.splitless else "hard_source"
        parent[n] = (None, kind, None)
        queue.append(n)

    terminal: int | None = None
    while queue and terminal is None:
        n = queue.popleft()
        for target, witness in data.unary.get(n, ()):
            if target > cutoff or target in parent:
                continue
            parent[target] = (n, "unary", witness)
            queue.append(target)
        child = 2 * n - 1
        edge = (n, child)
        if child <= cutoff and edge not in used_seed:
            if child in data.generated:
                terminal = n
                break
            if child in data.holes and child not in parent:
                parent[child] = (n, "seed", None)
                queue.append(child)

    if terminal is None:
        return None

    nodes = [terminal]
    steps: list[dict] = [
        {"kind": "seed_to_ground", "from": terminal, "to": 2 * terminal - 1}
    ]
    current = terminal
    while parent[current][0] is not None:
        previous, kind, witness = parent[current]
        if previous is None:
            raise RuntimeError("broken predecessor")
        step = {"kind": kind, "from": previous, "to": current}
        if witness is not None:
            step["generated_witness"] = witness
        steps.append(step)
        nodes.append(previous)
        current = previous
    start_kind = parent[current][1]
    nodes.reverse()
    steps.reverse()
    return {
        "cutoff": cutoff,
        "start": current,
        "start_kind": start_kind,
        "nodes": nodes,
        "steps": steps,
    }


def generate(limit: int) -> dict:
    data = arithmetic(limit)
    used_seed: set[tuple[int, int]] = set()
    used_hard_sources: set[int] = set()
    paths: list[dict] = []
    first_failure: dict | None = None
    for hard in sorted(data.hard):
        path = find_forward_path(data, hard, used_seed, used_hard_sources)
        if path is None:
            first_failure = {
                "cutoff": hard,
                "hard_demand": sum(h <= hard for h in data.hard),
                "paths_before_failure": len(paths),
                "used_seed_edges": len(used_seed),
            }
            break
        if path["start_kind"] == "hard_source":
            used_hard_sources.add(int(path["start"]))
        for step in path["steps"]:
            if step["kind"].startswith("seed"):
                edge = (int(step["from"]), int(step["to"]))
                if edge in used_seed:
                    raise RuntimeError(f"reused seed edge {edge}")
                used_seed.add(edge)
        paths.append(path)
    certificate = {
        "schema_version": 1,
        "limit": limit,
        "hard_count": len(data.hard),
        "path_count": len(paths),
        "first_failure": first_failure,
        "paths": paths,
    }
    verify(certificate)
    return certificate


def verify(certificate: dict) -> dict:
    limit = int(certificate["limit"])
    data = arithmetic(limit)
    used_seed: set[tuple[int, int]] = set()
    used_hard_sources: set[int] = set()
    hard_seen = 0
    for path in certificate["paths"]:
        cutoff = int(path["cutoff"])
        hard_seen += 1
        if cutoff not in data.hard:
            raise RuntimeError(f"path cutoff {cutoff} is not hard")
        if hard_seen != sum(h <= cutoff for h in data.hard):
            raise RuntimeError("hard paths are not in exact arrival order")
        start = int(path["start"])
        kind = path["start_kind"]
        if kind == "splitless_source":
            if start not in data.splitless or start > cutoff:
                raise RuntimeError("invalid splitless source")
        elif kind == "hard_source":
            if start not in data.hard or start > cutoff or start in used_hard_sources:
                raise RuntimeError("invalid hard source")
            used_hard_sources.add(start)
        else:
            raise RuntimeError(f"invalid source kind {kind}")

        current = start
        for step in path["steps"]:
            if int(step["from"]) != current:
                raise RuntimeError("noncontiguous path")
            target = int(step["to"])
            if target > cutoff:
                raise RuntimeError("path uses a future vertex")
            kind = step["kind"]
            if kind == "unary":
                witness = int(step["generated_witness"])
                if (target, witness) not in data.unary.get(current, ()):
                    raise RuntimeError("invalid unary witness")
                if current + 1 != target * witness or target == witness:
                    raise RuntimeError("invalid distinct-factor unary arithmetic")
                current = target
            elif kind in ("seed", "seed_to_ground"):
                if target != 2 * current - 1:
                    raise RuntimeError("invalid seed arithmetic")
                edge = (current, target)
                if edge in used_seed:
                    raise RuntimeError("unit seed edge reused")
                used_seed.add(edge)
                if kind == "seed":
                    if target not in data.holes:
                        raise RuntimeError("internal seed target is not a hole")
                    current = target
                else:
                    if target not in data.generated:
                        raise RuntimeError("terminal seed target is not grounded")
            else:
                raise RuntimeError(f"invalid step kind {kind}")

    failure = certificate["first_failure"]
    if failure is None:
        if len(certificate["paths"]) != len(data.hard):
            raise RuntimeError("missing paths without a recorded failure")
    else:
        cutoff = int(failure["cutoff"])
        replay = find_forward_path(data, cutoff, used_seed, used_hard_sources)
        if replay is not None:
            raise RuntimeError("recorded greedy failure has an available forward path")
    return {
        "limit": limit,
        "hard_count": len(data.hard),
        "path_count": len(certificate["paths"]),
        "first_failure": failure,
        "used_seed_edges": len(used_seed),
        "verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.generate is not None:
        certificate = generate(args.generate)
        if args.output is None:
            parser.error("--generate requires --output")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
        print(verify(certificate))
    else:
        certificate = json.loads(args.verify.read_text(encoding="utf-8"))
        print(verify(certificate))


if __name__ == "__main__":
    main()
