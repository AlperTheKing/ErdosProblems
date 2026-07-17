#!/usr/bin/env python3
"""C60: exact structural analysis of the C56 integer duals.

The C56 LP has a much smaller integral max-flow model after the least
generated set is contracted.  This script builds that network incrementally,
checks every cutoff, and compares it with independently regenerated C56 duals
on a configurable dense sample.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COMPUTE = ROOT / "problems" / "424" / "compute" / "wave5"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C56_BASE = load_module("c60_c56_base", COMPUTE / "C56_image_lp_dual.py")
C56_DUAL = load_module("c60_c56_dual", COMPUTE / "C56_dual_cert.py")


@dataclass
class Edge:
    to: int
    rev: int
    cap: int
    initial: int
    kind: str
    born: int


class IncrementalFlow:
    """Deterministic unit-augmenting max flow with auditable rerouting paths."""

    def __init__(self, vertex_count: int, source: int, sink: int) -> None:
        self.adj: list[list[Edge]] = [[] for _ in range(vertex_count)]
        self.source = source
        self.sink = sink
        self.value = 0

    def add_edge(self, u: int, v: int, cap: int, kind: str, born: int) -> None:
        fwd = Edge(v, len(self.adj[v]), cap, cap, kind, born)
        rev = Edge(u, len(self.adj[u]), 0, 0, "reverse:" + kind, born)
        self.adj[u].append(fwd)
        self.adj[v].append(rev)

    def augment_all(self) -> list[dict]:
        paths: list[dict] = []
        while True:
            parent: list[tuple[int, int] | None] = [None] * len(self.adj)
            parent[self.source] = (-1, -1)
            queue = deque([self.source])
            while queue and parent[self.sink] is None:
                u = queue.popleft()
                for i, edge in enumerate(self.adj[u]):
                    if edge.cap <= 0 or parent[edge.to] is not None:
                        continue
                    parent[edge.to] = (u, i)
                    queue.append(edge.to)
                    if edge.to == self.sink:
                        break
            if parent[self.sink] is None:
                return paths

            bottleneck = 10**18
            vertices = [self.sink]
            edge_data: list[tuple[int, int, Edge]] = []
            v = self.sink
            while v != self.source:
                item = parent[v]
                if item is None:
                    raise RuntimeError("broken augmenting path")
                u, i = item
                edge = self.adj[u][i]
                bottleneck = min(bottleneck, edge.cap)
                edge_data.append((u, i, edge))
                vertices.append(u)
                v = u
            # Every finite sink route contains a unit seed edge.
            if bottleneck != 1:
                raise RuntimeError(f"unexpected non-unit augmentation {bottleneck}")
            for u, i, edge in edge_data:
                edge.cap -= bottleneck
                self.adj[edge.to][edge.rev].cap += bottleneck
            self.value += bottleneck
            edge_data.reverse()
            vertices.reverse()
            paths.append(
                {
                    "length": len(edge_data),
                    "vertices": vertices,
                    "kinds": [edge.kind for _, _, edge in edge_data],
                    "reverse_edges": sum(edge.initial == 0 for _, _, edge in edge_data),
                    "oldest_edge": min(edge.born for _, _, edge in edge_data),
                }
            )

    def reachable(self) -> set[int]:
        seen = {self.source}
        queue = deque([self.source])
        while queue:
            u = queue.popleft()
            for edge in self.adj[u]:
                if edge.cap > 0 and edge.to not in seen:
                    seen.add(edge.to)
                    queue.append(edge.to)
        return seen


def precompute(max_limit: int):
    values = [n for n in range(2, max_limit + 1) if C56_BASE.allowed(n)]
    pairs = {n: C56_BASE.admissible_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    hard = {n for n in values if C56_BASE.hard_shape(n, pairs[n])}
    splitless = {n for n in values if n not in (2, 3) and not pairs[n]}
    holes = set(values) - generated
    return values, pairs, generated, hard, splitless, holes


def run_incremental(max_limit: int) -> tuple[list[dict], list[dict], dict]:
    values, pairs, generated, hard, splitless, holes = precompute(max_limit)
    source, sink = max_limit + 1, max_limit + 2
    flow = IncrementalFlow(max_limit + 3, source, sink)
    finite_arc_bound = len(hard & holes) + sum(
        2 * n - 1 <= max_limit for n in holes
    )
    infinity = finite_arc_bound + 1
    rows: list[dict] = []
    augmentations: list[dict] = []
    hard_holes = 0
    generated_hard = 0
    splitless_seen = 0

    for cutoff in range(2, max_limit + 1):
        network_changed = False
        if C56_BASE.allowed(cutoff):
            n = cutoff
            if n in hard:
                if n in generated:
                    generated_hard += 1
                else:
                    hard_holes += 1
                    flow.add_edge(source, n, 1, f"hard:{n}", n)
                    network_changed = True
            if n in holes:
                if n in splitless:
                    splitless_seen += 1
                    flow.add_edge(source, n, infinity, f"splitless:{n}", n)
                    network_changed = True
                for a, b in pairs[n]:
                    if (a in generated) != (b in generated):
                        parent = b if a in generated else a
                        flow.add_edge(n, parent, infinity, f"unary:{n}->{parent}", n)
                        network_changed = True
            if n % 2 == 1:
                parent = (n + 1) // 2
                if parent in holes:
                    target = sink if n in generated else n
                    flow.add_edge(parent, target, 1, f"seed:{parent}->{n}", n)
                    network_changed = True

        new_paths = flow.augment_all() if network_changed else []
        for path in new_paths:
            path["cutoff"] = cutoff
            augmentations.append(path)
        reachable = flow.reachable() if network_changed or cutoff == max_limit else set()
        rows.append(
            {
                "cutoff": cutoff,
                "hard_holes": hard_holes,
                "generated_hard": generated_hard,
                "splitless": splitless_seen,
                "flow": flow.value,
                "reserve": flow.value - hard_holes,
                "new_flow": len(new_paths),
                "new_reverse_paths": sum(path["reverse_edges"] > 0 for path in new_paths),
                "mincut_hole_side": (
                    len((reachable - {source}) & holes) if reachable else None
                ),
            }
        )

    summary = {
        "max_limit": max_limit,
        "all_cutoffs": len(rows),
        "minimum_reserve": min(row["reserve"] for row in rows),
        "zero_reserve_cutoffs": [row["cutoff"] for row in rows if row["reserve"] == 0],
        "first_positive_hard": next(
            (row["cutoff"] for row in rows if row["hard_holes"]), None
        ),
        "final": rows[-1],
        "augmentations": len(augmentations),
        "rerouting_augmentations": sum(path["reverse_edges"] > 0 for path in augmentations),
        "first_rerouting": next(
            (path for path in augmentations if path["reverse_edges"] > 0), None
        ),
        "maximum_path_length": max((path["length"] for path in augmentations), default=0),
        "longest_path_first": max(augmentations, key=lambda path: path["length"], default=None),
        "maximum_reverse_edges": max(
            (path["reverse_edges"] for path in augmentations), default=0
        ),
    }
    return rows, augmentations, summary


def parse_closure(name: str) -> tuple[int, int, int]:
    _, n, a, b = name.split("_")
    return int(n), int(a), int(b)


def cert_features(cert: dict) -> dict:
    limit = int(cert["limit"])
    _, pairs, generated, hard, _, holes = precompute(limit)
    closure = [(name, -int(value)) for name, value in cert["row"] if name.startswith("closure_")]
    boundary = [(name, -int(value)) for name, value in cert["row"] if name.startswith("q_ge_difference_")]
    outputs: dict[int, int] = {}
    bad_active_rows: list[str] = []
    for name, weight in closure:
        n, a, b = parse_closure(name)
        outputs[n] = outputs.get(n, 0) + 1
        if n in holes:
            if (a in generated) == (b in generated):
                bad_active_rows.append(name)
        elif not (a in generated and b in generated):
            bad_active_rows.append(name)
    verified = C56_DUAL.verify_one(cert)
    canonical = json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()
    return {
        "limit": limit,
        "hard_count": len(hard),
        "hard_holes": len(hard & holes),
        "generated_hard": len(hard & generated),
        "objective": verified["exact_dual_objective"],
        "margin": verified["exact_margin"],
        "closure_rows": len(closure),
        "boundary_rows": len(boundary),
        "max_closure_weight": max((weight for _, weight in closure), default=0),
        "all_boundary_weights_one": all(weight == 1 for _, weight in boundary),
        "one_closure_per_output": all(count == 1 for count in outputs.values()),
        "complementary_closure_types": not bad_active_rows,
        "bad_active_rows": bad_active_rows[:10],
        "sha256": hashlib.sha256(canonical).hexdigest(),
        "row_map": {name: -int(value) for name, value in cert["row"]},
        "lower_map": {name: int(value) for name, value in cert["lower"]},
        "upper_map": {name: -int(value) for name, value in cert["upper"]},
    }


def generate_feature(limit: int) -> dict:
    return cert_features(C56_DUAL.generate(limit, 1e-7))


def numeric_floor(name: str) -> int:
    values = [int(piece) for piece in name.split("_") if piece.isdigit()]
    return min(values, default=10**18)


def recurrence_analysis(features: list[dict]) -> dict:
    features.sort(key=lambda row: row["limit"])
    first_nonidentical = None
    first_decrease = None
    first_q_removal = None
    first_selector_switch = None
    maximum_backreach = None
    previous = None
    for current in features:
        if previous is None or current["limit"] != previous["limit"] + 1:
            previous = current
            continue
        changed: list[str] = []
        decreased: list[tuple[str, int, int]] = []
        for key in ("row_map", "lower_map", "upper_map"):
            old, new = previous[key], current[key]
            for name in old.keys() | new.keys():
                a, b = old.get(name, 0), new.get(name, 0)
                if a != b:
                    changed.append(name)
                if b < a:
                    decreased.append((name, a, b))
        if changed and first_nonidentical is None:
            first_nonidentical = {
                "from": previous["limit"], "to": current["limit"], "changed": changed[:20]
            }
        if decreased and first_decrease is None:
            first_decrease = {
                "from": previous["limit"], "to": current["limit"], "decreased": decreased[:20]
            }
        old_q = {name for name in previous["row_map"] if name.startswith("q_ge_difference_")}
        new_q = {name for name in current["row_map"] if name.startswith("q_ge_difference_")}
        if old_q - new_q and first_q_removal is None:
            first_q_removal = {
                "from": previous["limit"], "to": current["limit"], "removed": sorted(old_q-new_q)
            }
        def selectors(row):
            out = {}
            for name in row["row_map"]:
                if name.startswith("closure_"):
                    n, a, b = parse_closure(name)
                    out[n] = (a, b)
            return out
        old_s, new_s = selectors(previous), selectors(current)
        switches = [(n, old_s[n], new_s[n]) for n in old_s.keys() & new_s.keys() if old_s[n] != new_s[n]]
        if switches and first_selector_switch is None:
            first_selector_switch = {
                "from": previous["limit"], "to": current["limit"], "switches": switches[:20]
            }
        if changed:
            floor = min(numeric_floor(name) for name in changed)
            item = {
                "from": previous["limit"],
                "to": current["limit"],
                "oldest_label": floor,
                "backreach": current["limit"] - floor,
                "changed_count": len(changed),
            }
            if maximum_backreach is None or item["backreach"] > maximum_backreach["backreach"]:
                maximum_backreach = item
        previous = current
    return {
        "sample_size": len(features),
        "first_nonidentical_adjacent_dual": first_nonidentical,
        "first_componentwise_decrease": first_decrease,
        "first_boundary_row_removal": first_q_removal,
        "first_closure_selector_switch": first_selector_switch,
        "maximum_observed_backreach": maximum_backreach,
        "all_boundary_weights_one": all(row["all_boundary_weights_one"] for row in features),
        "one_closure_per_output": all(row["one_closure_per_output"] for row in features),
        "complementary_closure_types": all(row["complementary_closure_types"] for row in features),
        "maximum_closure_weight": max(
            features, key=lambda row: row["max_closure_weight"], default=None
        ),
    }


def strip_maps(row: dict) -> dict:
    return {key: value for key, value in row.items() if not key.endswith("_map")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-limit", type=int, default=2000)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--all-lp", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must lie in [1,64]")

    cutoffs, augmentations, flow_summary = run_incremental(args.max_limit)
    if flow_summary["minimum_reserve"] < 0:
        raise RuntimeError("SCB max-flow certificate failed")

    if args.all_lp:
        sample = list(range(2, args.max_limit + 1))
    else:
        sample = set(range(2, min(args.max_limit, 500) + 1))
        for row in cutoffs:
            if row["new_flow"] or row["reserve"] == 0 or row["cutoff"] % 25 == 0:
                sample.add(row["cutoff"])
            if row["cutoff"] > 2 and row["hard_holes"] != cutoffs[row["cutoff"] - 3]["hard_holes"]:
                sample.add(row["cutoff"])
        sample = sorted(sample)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        features = list(pool.map(generate_feature, sample, chunksize=1))

    by_limit = {row["cutoff"]: row for row in cutoffs}
    mismatches = []
    for feature in features:
        flow_row = by_limit[feature["limit"]]
        predicted = flow_row["flow"] + flow_row["generated_hard"]
        if feature["objective"] != predicted:
            mismatches.append(
                {"limit": feature["limit"], "dual": feature["objective"], "flow": predicted}
            )
    if mismatches:
        raise RuntimeError(f"flow/dual mismatch: {mismatches[:5]}")

    payload = {
        "flow_summary": flow_summary,
        "flow_cutoffs": cutoffs,
        "augmentations": augmentations,
        "lp_sample_limits": sample,
        "lp_recurrence": recurrence_analysis(features),
        "lp_features": [strip_maps(row) for row in features],
        "flow_dual_mismatches": mismatches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "flow_summary": flow_summary,
        "lp_sample_size": len(features),
        "lp_recurrence": payload["lp_recurrence"],
        "flow_dual_mismatches": mismatches,
    }, indent=2))


if __name__ == "__main__":
    main()
