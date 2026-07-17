#!/usr/bin/env python3
"""Exact chain-root/min-cut probes for the C62 SCB lane.

The max-flow is used only to obtain an extremal closed hole set.  All reported
root identities and category counts are then recomputed directly with integer
arithmetic.  This file does not assert the uniform SCB theorem.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs(n: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < n + 1:
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def hard_shape(n: int, ps: list[tuple[int, int]]) -> bool:
    if n % 2 or not ps:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def least_closure(limit: int, pair_map: dict[int, list[tuple[int, int]]]) -> set[int]:
    generated: set[int] = set()
    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        if n in (2, 3) or any(a in generated and b in generated for a, b in pair_map[n]):
            generated.add(n)
    return generated


def extremal_hole_cut(limit: int) -> tuple[set[int], dict]:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pair_map = {n: pairs(n) for n in values}
    generated = least_closure(limit, pair_map)
    holes = set(values) - generated
    hard = {n for n in values if hard_shape(n, pair_map[n])}
    hard_holes = hard & holes
    splitless = {n for n in holes if n not in (2, 3) and not pair_map[n]}

    source, sink = limit + 1, limit + 2
    infinity = len(hard_holes) + len(splitless) + 2
    capacity: dict[tuple[int, int], int] = {}

    def add(u: int, v: int, c: int) -> None:
        capacity[u, v] = capacity.get((u, v), 0) + c

    for h in hard_holes:
        add(source, h, 1)
    for s in splitless:
        add(source, s, infinity)
    for n in holes:
        for a, b in pair_map[n]:
            if (a in generated) != (b in generated):
                add(n, b if a in generated else a, infinity)
        child = 2 * n - 1
        if child <= limit:
            add(n, sink if child in generated else child, 1)

    rows = np.fromiter((u for u, _ in capacity), dtype=np.int64)
    cols = np.fromiter((v for _, v in capacity), dtype=np.int64)
    data = np.fromiter(capacity.values(), dtype=np.int64)
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(limit + 3, limit + 3), dtype=np.int64
    ).tocsr()
    result = maximum_flow(matrix, source, sink)

    # Reachability in the exact integral residual network gives a minimum cut.
    flow = result.flow.tocsr()
    adjacency: list[list[int]] = [[] for _ in range(limit + 3)]
    for (u, v), cap in capacity.items():
        sent = int(flow[u, v])
        if cap - sent > 0:
            adjacency[u].append(v)
        if sent > 0:
            adjacency[v].append(u)
    reachable = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if v not in reachable:
                reachable.add(v)
                queue.append(v)
    dset = holes & reachable

    # Directly replay the cut and the shell identity on D = A \ T.
    hard_d = hard & dset
    boundaries = {
        n for n in dset if 2 * n - 1 <= limit and 2 * n - 1 not in dset
    }
    if len(boundaries) - len(hard_d) != int(result.flow_value) - len(hard_holes):
        raise RuntimeError("minimum-cut replay mismatch")
    for s in splitless:
        if s not in dset:
            raise RuntimeError("minimum cut omitted a splitless root")
    for n in dset:
        for a, b in pair_map[n]:
            if a in generated and b not in dset:
                raise RuntimeError(("unary closure", n, a, b))
            if b in generated and a not in dset:
                raise RuntimeError(("unary closure", n, b, a))

    y = (limit + 1) // 2
    unhealed_hard: list[int] = []
    healed_splitless: list[int] = []
    healed_seed3: list[int] = []
    healed_details: list[dict] = []
    unhealed_splitless: list[int] = []
    for r in range(2, limit + 1, 2):
        if not allowed(r) or r not in dset:
            continue
        w = r
        while 2 * w - 1 <= limit:
            w = 2 * w - 1
        healed = w not in dset
        first_child = None
        if healed:
            p = r
            while p in dset:
                child = 2 * p - 1
                if child > limit:
                    raise RuntimeError(("healed chain has no boundary", r))
                if child not in dset:
                    first_child = child
                    break
                p = child
            witnesses = []
            if first_child is not None:
                witnesses = [
                    [a, b]
                    for a, b in pair_map[first_child]
                    if a not in dset and b not in dset
                ]
        if r in hard:
            if not healed:
                unhealed_hard.append(r)
        elif not pair_map[r]:
            (healed_splitless if healed else unhealed_splitless).append(r)
            if healed:
                healed_details.append(
                    {"root": r, "kind": "splitless", "child": first_child, "witnesses": witnesses}
                )
        elif healed:
            healed_seed3.append(r)
            healed_details.append(
                {"root": r, "kind": "seed3", "child": first_child, "witnesses": witnesses}
            )

    if len(unhealed_hard) != len(healed_splitless) + len(healed_seed3) - (
        len(boundaries) - len(hard_d)
    ):
        raise RuntimeError("chain-root identity replay mismatch")

    summary = {
        "limit": limit,
        "flow": int(result.flow_value),
        "hard_holes_in_least_closure_complement": len(hard_holes),
        "mincut_hard": len(hard_d),
        "mincut_boundaries": len(boundaries),
        "margin": len(boundaries) - len(hard_d),
        "unhealed_hard_roots": len(unhealed_hard),
        "healed_splitless_roots": len(healed_splitless),
        "healed_seed3_roots": len(healed_seed3),
        "unhealed_splitless_roots": len(unhealed_splitless),
        "samples": {
            "unhealed_hard": unhealed_hard[:30],
            "healed_splitless": healed_splitless[:30],
            "healed_seed3": healed_seed3[:30],
            "unhealed_splitless": unhealed_splitless[:30],
            "healed_details": healed_details[:40],
        },
    }
    return dset, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = []
    for limit in args.limits:
        _, row = extremal_hole_cut(limit)
        payload.append(row)
        print(json.dumps(row, sort_keys=True))
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
