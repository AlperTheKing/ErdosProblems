#!/usr/bin/env python3
"""Exact red-team audits for the P83/P87 loose-triangle frontier.

The abstract lane tests what follows from linearity and the fold role order
alone.  The actual lane applies the P85 q=2 lift to every archived Sidon
ruler loaded by P86, including all endpoint-preserving translations allowed
by positive defect.  All acceptance and counting decisions use integers.
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[4]
P86_PATH = ROOT / "problems/864/compute/p86/dense_loose_search.py"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p88/phase_redteam.json"


def load_p86():
    spec = importlib.util.spec_from_file_location("p86_dense_loose", P86_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {P86_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ordered_modular_edges(p: int, multiplier: int, offset: int) -> list[tuple[int, int, int]]:
    """A dense ordered subgraph of a Latin-square 3-graph.

    The full graph is u = multiplier*a + c + offset (mod p).  Restricting to
    a <= c < u preserves injectivity of all three coordinate projections and
    matches the role inequalities of a canonical fold edge.
    """
    edges = []
    for a in range(p):
        for c in range(a, p):
            u = (multiplier * a + c + offset) % p
            if c < u:
                edges.append((a, c, u))
    return edges


def shadow_triangle_count(edges: Sequence[tuple[int, int, int]]) -> tuple[int, int]:
    ac = {(a, c) for a, c, _u in edges}
    au = {(a, u) for a, _c, u in edges}
    cu = {(c, u) for _a, c, u in edges}
    if len(ac) != len(edges) or len(au) != len(edges) or len(cu) != len(edges):
        raise AssertionError("coordinate projection is not injective")
    au_masks: dict[int, int] = {}
    cu_masks: dict[int, int] = {}
    for a, c, u in edges:
        au_masks[a] = au_masks.get(a, 0) | (1 << u)
        cu_masks[c] = cu_masks.get(c, 0) | (1 << u)
    total = sum(
        (au_masks.get(a, 0) & cu_masks.get(c, 0)).bit_count()
        for a, c in ac
    )
    return total, total - len(edges)


def run_abstract(orders: Iterable[int]) -> list[dict[str, int | str]]:
    rows = []
    for p in orders:
        best = None
        for multiplier in range(1, p):
            for offset in range(p):
                edges = ordered_modular_edges(p, multiplier, offset)
                total, loose = shadow_triangle_count(edges)
                row = {
                    "model": "ordered modular Latin subgraph",
                    "p": p,
                    "multiplier": multiplier,
                    "offset": offset,
                    "edges": len(edges),
                    "all_shadow_triangles": total,
                    "loose_triangles": loose,
                }
                key = (loose, len(edges), -multiplier, -offset)
                if best is None or key > best[0]:
                    best = (key, row)
        assert best is not None
        rows.append(best[1])
    return rows


@dataclass(frozen=True)
class ActualRecord:
    B: list[int]
    p: int
    h: int
    b: int
    delta: int
    C_S: int
    T_F: int
    gamma: int
    source: str


def actual_key(row: ActualRecord) -> tuple[int, int, int, int, int]:
    # Compare T_F/C_S first, then T_F/p^3, without floating point.
    return (row.T_F, -row.C_S, row.T_F, -row.p**3, row.delta)


def better_ratio(left: ActualRecord, right: ActualRecord | None) -> bool:
    if right is None:
        return True
    lhs = left.T_F * right.C_S
    rhs = right.T_F * left.C_S
    if lhs != rhs:
        return lhs > rhs
    lhs = left.T_F * right.p**3
    rhs = right.T_F * left.p**3
    if lhs != rhs:
        return lhs > rhs
    return (left.delta, left.B) > (right.delta, right.B)


def evaluate_seed(p86, values: tuple[int, ...]) -> tuple[int, int]:
    h0 = values[-1] + 1
    try:
        edges, _sums = p86.fold_edges(values, h0)
    except ValueError:
        return -1, -1
    if not edges:
        return 0, 0
    triangles, _witnesses = p86.loose_triangle_data(edges, 0)
    return len(edges), triangles


def local_better(candidate: tuple[int, int], incumbent: tuple[int, int]) -> bool:
    c_s, triangles = candidate
    old_c_s, old_triangles = incumbent
    if triangles * old_c_s != old_triangles * c_s:
        return triangles * old_c_s > old_triangles * c_s
    if triangles - c_s != old_triangles - old_c_s:
        return triangles - c_s > old_triangles - old_c_s
    return (triangles, -c_s) > (old_triangles, -old_c_s)


def reinsert_hill_climb(p86, start: ActualRecord, max_rounds: int = 8) -> dict[str, object]:
    current = tuple((x - 1) // 2 for x in start.B)
    current_score = evaluate_seed(p86, current)
    if current_score != (start.C_S, start.T_F):
        raise AssertionError((current_score, start))
    path = [{"C_S": current_score[0], "T_F": current_score[1], "values": list(current)}]
    evaluations = 0
    for _round in range(max_rounds):
        best_values = current
        best_score = current_score
        width = current[-1]
        for deleted in range(len(current) - 1):
            remainder = current[:deleted] + current[deleted + 1:]
            occupied = set(remainder)
            for x in range(width):
                if x in occupied:
                    continue
                candidate = tuple(sorted(remainder + (x,)))
                evaluations += 1
                score = evaluate_seed(p86, candidate)
                if score[0] <= 0:
                    continue
                if local_better(score, best_score) or (
                    score == best_score and candidate < best_values
                ):
                    best_values, best_score = candidate, score
        if not local_better(best_score, current_score):
            break
        current, current_score = best_values, best_score
        path.append({"C_S": current_score[0], "T_F": current_score[1], "values": list(current)})
    B = [2 * x + 1 for x in current]
    h = 2 * (current[-1] + 1)
    audited = p86.audit_candidate(B, h, 1, "p88 local search", "q=2", 0)
    return {
        "start": asdict(start),
        "evaluations": evaluations,
        "rounds": len(path) - 1,
        "path": path,
        "result": {
            "B": B,
            "p": len(B),
            "h": h,
            "b": 1,
            "delta": int(audited["delta"]),
            "C_S": int(audited["C_S"]),
            "T_F": int(audited["T_F"]),
        },
    }


def enumerate_reinsert_neighbors(p86, values: tuple[int, ...]):
    width = values[-1]
    seen: set[tuple[int, ...]] = set()
    for deleted in range(len(values) - 1):
        remainder = values[:deleted] + values[deleted + 1:]
        occupied = set(remainder)
        for x in range(width):
            if x in occupied:
                continue
            candidate = tuple(sorted(remainder + (x,)))
            if candidate == values or candidate in seen:
                continue
            seen.add(candidate)
            score = evaluate_seed(p86, candidate)
            if score[0] > 0:
                yield candidate, score


def beam_reinsert_search(
    p86, start: ActualRecord, depth: int = 3, beam_width: int = 32
) -> dict[str, object]:
    initial = tuple((x - 1) // 2 for x in start.B)
    initial_score = evaluate_seed(p86, initial)
    beam = [(initial, initial_score)]
    seen = {initial}
    best_values, best_score = initial, initial_score
    layer_sizes = []
    evaluations = 0

    def compare(left, right):
        left_values, left_score = left
        right_values, right_score = right
        if local_better(left_score, right_score):
            return -1
        if local_better(right_score, left_score):
            return 1
        return -1 if left_values < right_values else (1 if left_values > right_values else 0)

    for _level in range(depth):
        candidates = []
        for values, _score in beam:
            for candidate, score in enumerate_reinsert_neighbors(p86, values):
                evaluations += 1
                if candidate in seen:
                    continue
                seen.add(candidate)
                candidates.append((candidate, score))
                if local_better(score, best_score):
                    best_values, best_score = candidate, score
        candidates.sort(key=functools.cmp_to_key(compare))
        layer_sizes.append(len(candidates))
        beam = candidates[:beam_width]
        if not beam or best_score[1] > best_score[0]:
            break

    B = [2 * x + 1 for x in best_values]
    h = 2 * (best_values[-1] + 1)
    audited = p86.audit_candidate(B, h, 1, "p88 beam search", "q=2", 0)
    return {
        "start": asdict(start),
        "depth": depth,
        "beam_width": beam_width,
        "evaluations": evaluations,
        "distinct_states": len(seen),
        "new_states_by_layer": layer_sizes,
        "result": {
            "B": B,
            "p": len(B),
            "h": h,
            "b": 1,
            "delta": int(audited["delta"]),
            "C_S": int(audited["C_S"]),
            "T_F": int(audited["T_F"]),
        },
    }


def pair_reinsert_search(p86, start: ActualRecord) -> dict[str, object]:
    initial = tuple((x - 1) // 2 for x in start.B)
    initial_score = evaluate_seed(p86, initial)
    width = initial[-1]
    best_values, best_score = initial, initial_score
    deletion_pairs = eligible_singletons = insertion_pairs = sidon_pairs = 0
    for first in range(len(initial) - 2):
        for second in range(first + 1, len(initial) - 1):
            deletion_pairs += 1
            remainder = tuple(
                value for index, value in enumerate(initial)
                if index not in (first, second)
            )
            occupied = set(remainder)
            existing_sums = set(p86.unordered_sum_map(remainder))
            eligible = []
            for x in range(width):
                if x in occupied:
                    continue
                if p86.insertion_is_sidon(remainder, existing_sums, x):
                    eligible.append(x)
            eligible_singletons += len(eligible)
            for left_index, x in enumerate(eligible):
                for y in eligible[left_index + 1:]:
                    insertion_pairs += 1
                    candidate = tuple(sorted(remainder + (x, y)))
                    score = evaluate_seed(p86, candidate)
                    if score[0] <= 0:
                        continue
                    sidon_pairs += 1
                    if local_better(score, best_score):
                        best_values, best_score = candidate, score
    B = [2 * x + 1 for x in best_values]
    h = 2 * (best_values[-1] + 1)
    audited = p86.audit_candidate(B, h, 1, "p88 pair search", "q=2", 0)
    return {
        "start": asdict(start),
        "deletion_pairs": deletion_pairs,
        "eligible_singletons": eligible_singletons,
        "insertion_pairs_tested": insertion_pairs,
        "sidon_pairs_with_folds": sidon_pairs,
        "result": {
            "B": B,
            "p": len(B),
            "h": h,
            "b": 1,
            "delta": int(audited["delta"]),
            "C_S": int(audited["C_S"]),
            "T_F": int(audited["T_F"]),
        },
    }


def run_actual() -> dict[str, object]:
    p86 = load_p86()
    bases, _manifests = p86.load_archives()
    tested = folded = 0
    best: ActualRecord | None = None
    violations: list[ActualRecord] = []
    best_by_p: dict[int, ActualRecord] = {}
    all_rows: list[ActualRecord] = []
    for base in bases:
        z = base.values
        p, width = len(z), z[-1]
        threshold = (3 * p * p - p + 2) // 2
        # q=2 lift of C=z+gamma has h=2(width+gamma+1).
        max_gamma = (threshold - 1) // 2 - width - 1
        if max_gamma < 0:
            continue
        source = " | ".join(base.sources[:2])
        for gamma in range(max_gamma + 1):
            tested += 1
            c = tuple(x + gamma for x in z)
            h0 = width + gamma + 1
            edges, _sums = p86.fold_edges(c, h0)
            if not edges:
                continue
            folded += 1
            triangles, _witnesses = p86.loose_triangle_data(edges, 0)
            B = [2 * x + 1 for x in c]
            h = 2 * h0
            audited = p86.audit_candidate(B, h, 1, source, f"q=2 gamma={gamma}", 0)
            if audited["C_S"] != len(edges) or audited["T_F"] != triangles:
                raise AssertionError("q=2 lift did not preserve the fold graph")
            row = ActualRecord(
                B=B, p=p, h=h, b=1,
                delta=int(audited["delta"]), C_S=len(edges), T_F=triangles,
                gamma=gamma, source=source,
            )
            all_rows.append(row)
            if better_ratio(row, best):
                best = row
            if better_ratio(row, best_by_p.get(p)):
                best_by_p[p] = row
            if triangles > len(edges):
                violations.append(row)
    def compare_starts(left: ActualRecord, right: ActualRecord) -> int:
        lhs = left.T_F * right.C_S
        rhs = right.T_F * left.C_S
        if lhs != rhs:
            return -1 if lhs > rhs else 1
        tail_left = (left.T_F - left.C_S, left.T_F, left.p, left.delta)
        tail_right = (right.T_F - right.C_S, right.T_F, right.p, right.delta)
        return -1 if tail_left > tail_right else (1 if tail_left < tail_right else 0)

    unique_rows = {tuple(row.B): row for row in all_rows}
    starts = sorted(
        unique_rows.values(), key=functools.cmp_to_key(compare_starts)
    )[:8]
    local_searches = [reinsert_hill_climb(p86, row) for row in starts]
    beam_searches = [beam_reinsert_search(p86, row) for row in starts[:2]]
    pair_searches = [pair_reinsert_search(p86, row) for row in starts[:3]]
    return {
        "base_count": len(bases),
        "tested_positive_defect_q2_lifts": tested,
        "q2_lifts_with_folds": folded,
        "T_F_gt_C_S_count": len(violations),
        "best_T_F_over_C_S": asdict(best) if best else None,
        "violations": [asdict(row) for row in violations[:20]],
        "best_by_p": [asdict(best_by_p[p]) for p in sorted(best_by_p)],
        "delete_reinsert_searches": local_searches,
        "beam_reinsert_searches": beam_searches,
        "pair_reinsert_searches": pair_searches,
    }


def verify(payload: dict[str, object]) -> None:
    p86 = load_p86()
    actual = payload["actual_q2_archive_scan"]
    assert isinstance(actual, dict)
    rows = []
    best = actual.get("best_T_F_over_C_S")
    if isinstance(best, dict):
        rows.append(best)
    violations = actual.get("violations", [])
    if isinstance(violations, list):
        rows.extend(row for row in violations if isinstance(row, dict))
    searches = actual.get("delete_reinsert_searches", [])
    if isinstance(searches, list):
        rows.extend(
            search["result"] for search in searches
            if isinstance(search, dict) and isinstance(search.get("result"), dict)
        )
    beams = actual.get("beam_reinsert_searches", [])
    if isinstance(beams, list):
        rows.extend(
            search["result"] for search in beams
            if isinstance(search, dict) and isinstance(search.get("result"), dict)
        )
    pairs = actual.get("pair_reinsert_searches", [])
    if isinstance(pairs, list):
        rows.extend(
            search["result"] for search in pairs
            if isinstance(search, dict) and isinstance(search.get("result"), dict)
        )
    for row in rows:
        fresh = p86.audit_candidate(
            row["B"], int(row["h"]), int(row["b"]), "verify", "verify", 0
        )
        for key in ("p", "delta", "C_S", "T_F"):
            if int(fresh[key]) != int(row[key]):
                raise AssertionError((key, fresh[key], row[key]))
    abstract = payload["abstract_ordered_models"]
    assert isinstance(abstract, list)
    for row in abstract:
        assert isinstance(row, dict)
        edges = ordered_modular_edges(
            int(row["p"]), int(row["multiplier"]), int(row["offset"])
        )
        total, loose = shadow_triangle_count(edges)
        if (len(edges), total, loose) != (
            int(row["edges"]), int(row["all_shadow_triangles"]),
            int(row["loose_triangles"]),
        ):
            raise AssertionError(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        payload = json.loads(args.verify.read_text(encoding="ascii"))
        verify(payload)
        print("PASS")
        return
    payload = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "abstract_ordered_models": run_abstract((11, 17, 23, 31, 43, 59)),
        "actual_q2_archive_scan": run_actual(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(args.output)


if __name__ == "__main__":
    main()
