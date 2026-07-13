"""Enumerate exact inverse-map relation states for the C18 collision lane.

A pair state ``(A, B, C)`` denotes the Diophantine relation

    A*x - B*y = C,  x,y in the fixed affine orbit.

If ``x = i*u - 1`` and ``y = j*v - 1``, its parent relation is

    (A*i)*u - (B*j)*v = C + A - B.

The state is dead when the gcd of the two new coefficients does not divide
the right-hand side.  Otherwise all three entries are divided by that gcd.
All arithmetic in this file is integral and exact.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from math import gcd


GENERATORS = (2, 3, 5)


@dataclass(frozen=True, order=True)
class State:
    left: int
    right: int
    offset: int


ROOTS = {
    "P23": State(3, 2, 0),
    "P25": State(5, 2, 0),
    "P35": State(5, 3, 0),
}


def transition(state: State, left_map: int, right_map: int) -> State | None:
    """Return the primitive parent state, or ``None`` if it has no integers."""

    left = state.left * left_map
    right = state.right * right_map
    offset = state.offset + state.left - state.right
    divisor = gcd(left, right)
    if offset % divisor:
        return None
    return State(left // divisor, right // divisor, offset // divisor)


def enumerate_states(
    max_depth: int,
) -> tuple[dict[State, int], dict[State, tuple[State, int, int]]]:
    """Breadth-first enumeration from the three pair-collision roots."""

    depth = {state: 0 for state in ROOTS.values()}
    parent: dict[State, tuple[State, int, int]] = {}
    queue = deque(ROOTS.values())
    while queue:
        state = queue.popleft()
        if depth[state] == max_depth:
            continue
        for left_map in GENERATORS:
            for right_map in GENERATORS:
                child = transition(state, left_map, right_map)
                if child is None or child in depth:
                    continue
                depth[child] = depth[state] + 1
                parent[child] = (state, left_map, right_map)
                queue.append(child)
    return depth, parent


def path_to(state: State, parent: dict[State, tuple[State, int, int]]) -> str:
    labels: list[str] = []
    while state in parent:
        previous, left_map, right_map = parent[state]
        labels.append(f"{left_map}{right_map}")
        state = previous
    root = next(name for name, candidate in ROOTS.items() if candidate == state)
    return root + ":" + "/".join(reversed(labels))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--largest", type=int, default=12)
    args = parser.parse_args()

    depth, parent = enumerate_states(args.depth)
    print("depth\tnew\tcumulative\tmax_left\tmax_right\tmax_abs_offset")
    cumulative = 0
    for level in range(args.depth + 1):
        states = [state for state, value in depth.items() if value == level]
        cumulative += len(states)
        print(
            level,
            len(states),
            cumulative,
            max((state.left for state in states), default=0),
            max((state.right for state in states), default=0),
            max((abs(state.offset) for state in states), default=0),
            sep="\t",
        )

    print("\nroot transitions")
    for name, state in ROOTS.items():
        for left_map in GENERATORS:
            for right_map in GENERATORS:
                child = transition(state, left_map, right_map)
                target = "DEAD" if child is None else repr(child)
                print(f"{name}\t{left_map}{right_map}\t{target}")

    print("\nlargest states")
    key = lambda state: (state.left + state.right, abs(state.offset), state)
    for state in sorted(depth, key=key, reverse=True)[: args.largest]:
        print(f"d={depth[state]}\t{state!r}\t{path_to(state, parent)}")


if __name__ == "__main__":
    main()
