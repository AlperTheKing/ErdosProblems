#!/usr/bin/env python3
"""Independent trial-division replay for the C38 splitless-bank artifacts."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.setrecursionlimit(20_000)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    return [
        (a, product // a)
        for a in range(2, math.isqrt(product) + 1)
        if product % a == 0
        and a < product // a
        and allowed(a)
        and allowed(product // a)
    ]


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


@dataclass(frozen=True)
class Source:
    value: int
    rank: int
    roots: frozenset[int]


@dataclass(frozen=True)
class Target:
    kind: str
    coordinate: int
    value: int
    rank: int
    roots: frozenset[int]


def reconstruct(limit: int) -> dict:
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    rank = [-1] * (limit + 1)
    roots: list[frozenset[int]] = [frozenset() for _ in range(limit + 1)]
    sources: list[Source] = []
    targets: list[Target] = []
    pairs_by_n: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    generated = 2
    holes = splitless = 0

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = factor_pairs(n)
        pairs_by_n[n] = pairs
        if any(member[a] and member[b] for a, b in pairs):
            member[n] = 1
            generated += 1
            if n % 2:
                parent = (n + 1) // 2
                if not member[parent]:
                    targets.append(Target(
                        "Q", n, parent, rank[parent], roots[parent]
                    ))
            continue

        holes += 1
        if not pairs:
            rank[n] = 0
            roots[n] = frozenset((n,))
            targets.append(Target("E", n, n, 0, roots[n]))
            splitless += 1
        else:
            pair_blocks = [
                min(rank[q] for q in (a, b) if not member[q])
                for a, b in pairs
            ]
            rank[n] = 1 + max(pair_blocks)
            lower = {
                q
                for a, b in pairs
                for q in (a, b)
                if not member[q] and rank[q] < rank[n]
            }
            roots[n] = frozenset().union(*(roots[q] for q in lower))
            assert roots[n]
        if hard_shape(n, pairs):
            sources.append(Source(n, rank[n], roots[n]))

    return {
        "member": member,
        "rank": rank,
        "roots": roots,
        "pairs": pairs_by_n,
        "sources": sources,
        "targets": targets,
        "counts": {
            "generated": generated,
            "holes": holes,
            "splitless": splitless,
            "hard": len(sources),
            "healed": sum(target.kind == "Q" for target in targets),
            "maximum_rank": max(rank),
        },
    }


def check_literal_stages(data: dict, limit: int) -> int:
    current = bytearray(limit + 1)
    for n in range(2, limit + 1):
        current[n] = int(allowed(n))
    death = [-1] * (limit + 1)
    stage = 0
    while True:
        stage += 1
        following = bytearray(limit + 1)
        following[2] = following[3] = 1
        for n in range(4, limit + 1):
            if not allowed(n):
                continue
            following[n] = int(any(
                current[a] and current[b]
                for a, b in data["pairs"][n]
            ))
        changed = False
        for n in range(2, limit + 1):
            if current[n] and not following[n]:
                death[n] = stage
                changed = True
        current = following
        if not changed:
            break
        if stage > 100:
            raise AssertionError("stage replay did not stabilize")

    for n in range(2, limit + 1):
        if not allowed(n) or data["member"][n]:
            continue
        assert death[n] == data["rank"][n] + 1, (n, death[n], data["rank"][n])
    return stage - 1


def prefix_audits(data: dict) -> dict:
    sources: list[Source] = data["sources"]
    targets: list[Target] = data["targets"]
    hard_exact = [0] * 32
    healed_exact = [0] * 32
    target_cursor = 0
    e_count = q_count = h_count = 0
    maximum_rank_excess = 0
    maximum_rank_bank_excess = 0
    maximum_scalar_bank_excess = 0
    maximum_h_minus_e = 0
    for source in sources:
        while target_cursor < len(targets) and targets[target_cursor].coordinate <= source.value:
            target = targets[target_cursor]
            if target.kind == "E":
                e_count += 1
            else:
                q_count += 1
                healed_exact[target.rank] += 1
            target_cursor += 1
        h_count += 1
        hard_exact[source.rank] += 1
        h_running = q_running = 0
        for depth in range(32):
            h_running += hard_exact[depth]
            q_running += healed_exact[depth]
            maximum_rank_excess = max(maximum_rank_excess, h_running - q_running)
            maximum_rank_bank_excess = max(
                maximum_rank_bank_excess, h_running - q_running - e_count
            )
        maximum_scalar_bank_excess = max(
            maximum_scalar_bank_excess, h_count - q_count - e_count
        )
        maximum_h_minus_e = max(maximum_h_minus_e, h_count - e_count)
    return {
        "rank_H_minus_Q": maximum_rank_excess,
        "rank_H_minus_Q_minus_E": maximum_rank_bank_excess,
        "H_minus_Q_minus_E": maximum_scalar_bank_excess,
        "H_minus_E": maximum_h_minus_e,
    }


def first_matching_failure(data: dict, bank_capacity: int) -> int | None:
    sources: list[Source] = data["sources"]
    targets: list[Target] = data["targets"]
    slots: list[int] = []
    for target_id, target in enumerate(targets):
        slots.extend([target_id] * (bank_capacity if target.kind == "E" else 1))
    owner = [-1] * len(slots)

    def augment(
        source_id: int,
        cutoff: int,
        seen_sources: set[int],
        seen_slots: set[int],
    ) -> bool:
        if source_id in seen_sources:
            return False
        seen_sources.add(source_id)
        source = sources[source_id]
        for slot_id, target_id in enumerate(slots):
            target = targets[target_id]
            if target.coordinate > cutoff:
                break
            if not (source.roots & target.roots) or slot_id in seen_slots:
                continue
            seen_slots.add(slot_id)
            previous = owner[slot_id]
            if previous < 0 or augment(previous, cutoff, seen_sources, seen_slots):
                owner[slot_id] = source_id
                return True
        return False

    for source_id, source in enumerate(sources):
        if not augment(source_id, source.value, set(), set()):
            return source.value
    return None


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    repo = Path(__file__).resolve().parents[5]

    data = reconstruct(10_000)
    assert data["counts"] == {
        "generated": 3207,
        "holes": 3459,
        "splitless": 1344,
        "hard": 518,
        "healed": 593,
        "maximum_rank": 9,
    }
    nontrivial_stages = check_literal_stages(data, 500)
    audits = prefix_audits(data)
    assert audits == {
        "rank_H_minus_Q": 1,
        "rank_H_minus_Q_minus_E": 0,
        "H_minus_Q_minus_E": 0,
        "H_minus_E": 0,
    }

    expanded_failures = {
        capacity: first_matching_failure(data, capacity)
        for capacity in (1, 2, 3, 4)
    }
    assert expanded_failures == {1: 1536, 2: 6000, 3: None, 4: None}

    cpp_failures = {}
    for capacity, expected in ((1, 1536), (2, 6000), (3, 35300), (4, 111620)):
        artifact = load_json(directory / f"dag_cpp_C{capacity}_1e6.json")
        cpp_failures[capacity] = artifact["failure"]["X"]
        assert cpp_failures[capacity] == expected
        assert artifact["failure"]["flow_value"] == artifact["failure"]["min_cut_capacity"]
        assert artifact["hard"] == artifact["matched"] + 1

    c40 = load_json(directory / "dag_cpp_C40_1e7.json")
    assert not c40["passed"] and c40["failure"]["X"] == 3_236_496
    assert c40["failure"]["flow_value"] == c40["failure"]["min_cut_capacity"]

    survivor = load_json(directory / "dag_cpp_C1000000_1e7.json")
    assert survivor["passed"] and survivor["hard"] == survivor["matched"] == 392_961

    c38 = load_json(directory / "result_1e7.json")
    c23 = load_json(
        repo / "problems/424/compute/wave3/C23_grounded_horn/result_1e7.json"
    )
    cross_counts = {
        "generated": c38["generated"],
        "holes": c38["holes"],
        "splitless": c38["splitless"],
        "hard": c38["hard"],
        "healed": c38["healed"],
    }
    assert cross_counts == {
        "generated": c23["generated"],
        "holes": c23["holes"],
        "splitless": c23["splitless_holes"],
        "hard": c23["hard_holes"],
        "healed": c23["final_healed_parents"],
    }
    assert c38["scalar"]["H_minus_Q_minus_E"]["first_positive"] is None
    assert c38["global_rank_filtered"]["same_rank_H_minus_Q"]["maximum_deficit"] == 1
    assert c38["singleton_leaf_6_gate"]["required_bank_capacity"]["maximum_deficit"] == 1

    result = {
        "schema_version": 1,
        "trial_limit": 10_000,
        "literal_stage_limit": 500,
        "literal_nontrivial_stages": nontrivial_stages,
        "trial_counts": data["counts"],
        "prefix_audits": audits,
        "expanded_failures": expanded_failures,
        "cpp_failures": cpp_failures,
        "C40_failure_X": c40["failure"]["X"],
        "C1000000_matched": survivor["matched"],
        "cross_counts_1e7": cross_counts,
        "status": "PASS",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
