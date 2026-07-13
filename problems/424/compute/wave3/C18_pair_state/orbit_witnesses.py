"""Attach exact fixed-orbit witnesses to C18 pair-state transitions."""

from __future__ import annotations

import argparse

from relation_states import GENERATORS, ROOTS, transition


PAIR_FORMS = {
    "P23": (2, 3),
    "P25": (2, 5),
    "P35": (3, 5),
}


def orbit_membership(limit: int) -> bytearray:
    member = bytearray(limit + 1)
    for seed in (2, 3, 5):
        if seed <= limit:
            member[seed] = 1
    for value in range(6, limit + 1):
        shifted = value + 1
        for generator in GENERATORS:
            if shifted % generator:
                continue
            parent = shifted // generator
            if parent != generator and member[parent]:
                member[value] = 1
                break
    return member


def parents(value: int, member: bytearray) -> tuple[int, ...]:
    shifted = value + 1
    result = []
    for generator in GENERATORS:
        if shifted % generator:
            continue
        parent = shifted // generator
        if parent != generator and parent < len(member) and member[parent]:
            result.append(generator)
    return tuple(result)


def repeated_parent_depth(value: int, generator: int, member: bytearray) -> int:
    depth = 0
    while True:
        shifted = value + 1
        if shifted % generator:
            return depth
        parent = shifted // generator
        if parent == generator or parent >= len(member) or not member[parent]:
            return depth
        depth += 1
        value = parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000_000)
    args = parser.parse_args()

    member = orbit_membership(args.limit)
    print(f"limit={args.limit}\tB_count={sum(member)}")

    for name, (left_scale, right_scale) in PAIR_FORMS.items():
        first_by_branch: dict[tuple[int, int], tuple[int, int, int, int, int]] = {}
        first_overlap: tuple[int, tuple[int, ...], tuple[int, ...]] | None = None
        pair_count = 0
        max_repeated = 0
        max_repeated_witness: tuple[int, int, int] | None = None
        max_t = args.limit // right_scale
        for parameter in range(1, max_t + 1):
            left_value = left_scale * parameter
            right_value = right_scale * parameter
            if not (member[left_value] and member[right_value]):
                continue
            pair_count += 1
            left_parents = parents(left_value, member)
            right_parents = parents(right_value, member)
            if first_overlap is None and len(left_parents) * len(right_parents) > 1:
                first_overlap = (parameter, left_parents, right_parents)
            for left_map in left_parents:
                for right_map in right_parents:
                    branch = (left_map, right_map)
                    if branch not in first_by_branch:
                        first_by_branch[branch] = (
                            parameter,
                            left_value,
                            right_value,
                            (left_value + 1) // left_map,
                            (right_value + 1) // right_map,
                        )

            if name == "P35":
                depth = min(
                    repeated_parent_depth(left_value, 5, member),
                    repeated_parent_depth(right_value, 3, member),
                )
                if depth > max_repeated:
                    max_repeated = depth
                    max_repeated_witness = (parameter, left_value, right_value)

        print(f"\n{name}\tpairs={pair_count}\tmax_t={max_t}")
        print(f"first_overlap={first_overlap}")
        for branch in sorted(first_by_branch):
            state = transition(ROOTS[name], *branch)
            print(f"branch={branch}\tstate={state!r}\twitness={first_by_branch[branch]}")
        if name == "P35":
            print(f"repeated_53_depth={max_repeated}\twitness={max_repeated_witness}")

    triple_count = 0
    first_triple = None
    for parameter in range(1, args.limit // 15 + 1):
        values = (6 * parameter, 10 * parameter, 15 * parameter)
        if all(member[value] for value in values):
            triple_count += 1
            if first_triple is None:
                first_triple = (parameter, values)
    print(f"\nP235\ttriples={triple_count}\tfirst={first_triple}")


if __name__ == "__main__":
    main()
