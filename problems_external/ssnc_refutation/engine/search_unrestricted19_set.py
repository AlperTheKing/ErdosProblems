#!/usr/bin/env python3
"""Independent set-based stochastic prototype for unrestricted order 19.

The mutable state is one trit per unordered pair: +1 means a->b, -1 means
b->a, and 0 means missing (a<b).  Search scoring uses Python sets.  A separate
matrix/triple-loop oracle is consulted only at replay boundaries.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
import itertools
import json
import math
import random
from typing import Iterable, Sequence


TARGET_N = 19
MIN_OUTDEGREE = 8
PROFILES = ("regular", "skew", "mixed")


class GraphInvariantError(ValueError):
    """Raised when raw data do not encode an oriented graph in the domain."""


@lru_cache(maxsize=None)
def pair_list(n: int) -> tuple[tuple[int, int], ...]:
    if n < 1:
        raise ValueError("n must be positive")
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


@lru_cache(maxsize=None)
def pair_index(n: int) -> dict[tuple[int, int], int]:
    return {pair: index for index, pair in enumerate(pair_list(n))}


@dataclass(frozen=True)
class RowLedger:
    vertex: int
    out_neighbors: tuple[int, ...]
    second_neighbors: tuple[int, ...]
    unreachable: tuple[int, ...]
    out_degree: int
    second_degree: int
    strict: bool


@dataclass
class PairStateGraph:
    n: int
    states: list[int]

    def __post_init__(self) -> None:
        if len(self.states) != len(pair_list(self.n)):
            raise GraphInvariantError("wrong number of unordered-pair states")
        if any(state not in (-1, 0, 1) for state in self.states):
            raise GraphInvariantError("pair states must be -1, 0, or 1")

    def clone(self) -> "PairStateGraph":
        return PairStateGraph(self.n, self.states.copy())

    @property
    def missing_count(self) -> int:
        return self.states.count(0)

    def outdegrees(self) -> list[int]:
        degrees = [0] * self.n
        for (a, b), state in zip(pair_list(self.n), self.states, strict=True):
            if state == 1:
                degrees[a] += 1
            elif state == -1:
                degrees[b] += 1
        return degrees

    def out_sets(self) -> list[set[int]]:
        rows = [set() for _ in range(self.n)]
        for (a, b), state in zip(pair_list(self.n), self.states, strict=True):
            if state == 1:
                rows[a].add(b)
            elif state == -1:
                rows[b].add(a)
        return rows

    def to_out_neighbors(self) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(sorted(row)) for row in self.out_sets())

    def validate(self, minimum_outdegree: int | None = None) -> None:
        if len(self.states) != len(pair_list(self.n)):
            raise GraphInvariantError("wrong number of unordered-pair states")
        if any(state not in (-1, 0, 1) for state in self.states):
            raise GraphInvariantError("invalid pair state")
        if minimum_outdegree is not None:
            degrees = self.outdegrees()
            if min(degrees) < minimum_outdegree:
                raise GraphInvariantError(
                    f"minimum outdegree {min(degrees)} is below {minimum_outdegree}"
                )

    @classmethod
    def from_out_neighbors(
        cls,
        rows: Sequence[Sequence[int]],
        *,
        minimum_outdegree: int | None = None,
    ) -> "PairStateGraph":
        n = len(rows)
        normalized: list[tuple[int, ...]] = []
        for source, row in enumerate(rows):
            values = tuple(row)
            if values != tuple(sorted(set(values))):
                raise GraphInvariantError(f"row {source} is not sorted and unique")
            if any(type(target) is not int or not (0 <= target < n) for target in values):
                raise GraphInvariantError(f"row {source} has an invalid target")
            if source in values:
                raise GraphInvariantError(f"loop at vertex {source}")
            normalized.append(values)

        row_sets = [set(row) for row in normalized]
        states: list[int] = []
        for a, b in pair_list(n):
            forward = b in row_sets[a]
            reverse = a in row_sets[b]
            if forward and reverse:
                raise GraphInvariantError(f"digon on pair {(a, b)}")
            states.append(1 if forward else -1 if reverse else 0)
        graph = cls(n, states)
        graph.validate(minimum_outdegree)
        return graph


def cyclic_tournament(n: int = TARGET_N) -> PairStateGraph:
    if n % 2 != 1:
        raise ValueError("cyclic tournament requires odd n")
    half = n // 2
    states = [
        1 if (b - a) % n <= half else -1
        for a, b in pair_list(n)
    ]
    graph = PairStateGraph(n, states)
    expected = [half] * n
    if graph.outdegrees() != expected:
        raise AssertionError("cyclic tournament construction drifted")
    return graph


def _reverse_random_legal_arcs(
    graph: PairStateGraph, rng: random.Random, accepted: int
) -> None:
    done = 0
    attempts = 0
    limit = max(1000, accepted * 1000)
    while done < accepted:
        attempts += 1
        if attempts > limit:
            raise RuntimeError("could not realize requested degree perturbation")
        index = rng.randrange(len(graph.states))
        state = graph.states[index]
        if state == 0:
            continue
        a, b = pair_list(graph.n)[index]
        source = a if state == 1 else b
        if graph.outdegrees()[source] <= MIN_OUTDEGREE:
            continue
        graph.states[index] = -state
        done += 1


def _remove_random_legal_arcs(
    graph: PairStateGraph, rng: random.Random, count: int
) -> None:
    for _ in range(count):
        degrees = graph.outdegrees()
        candidates: list[int] = []
        for index, ((a, b), state) in enumerate(
            zip(pair_list(graph.n), graph.states, strict=True)
        ):
            if state == 0:
                continue
            source = a if state == 1 else b
            if degrees[source] > MIN_OUTDEGREE:
                candidates.append(index)
        if not candidates:
            raise RuntimeError("no legal arc deletion despite positive total slack")
        graph.states[rng.choice(candidates)] = 0


def make_initial_graph(
    *,
    q: int,
    seed: int,
    profile: str,
) -> PairStateGraph:
    """Construct a deterministic unrestricted n=19 start with exactly q misses."""

    if not (0 <= q <= 19):
        raise ValueError("q must lie between 0 and 19")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}")
    rng = random.Random((seed << 7) ^ (q << 2) ^ PROFILES.index(profile))
    graph = cyclic_tournament(TARGET_N)
    reversals = {
        "regular": 0,
        "skew": 11,
        "mixed": 97,
    }[profile]
    _reverse_random_legal_arcs(graph, rng, reversals)
    _remove_random_legal_arcs(graph, rng, q)
    graph.validate(MIN_OUTDEGREE)
    if graph.missing_count != q:
        raise AssertionError("initial missing-pair count drifted")
    return graph


def set_ledger(graph: PairStateGraph) -> tuple[RowLedger, ...]:
    """Compute literal direct/new-second/unreachable sets using Python sets."""

    out = graph.out_sets()
    universe = set(range(graph.n))
    rows: list[RowLedger] = []
    for vertex in range(graph.n):
        reached_in_two: set[int] = set()
        for middle in out[vertex]:
            reached_in_two.update(out[middle])
        second = reached_in_two - out[vertex] - {vertex}
        unreachable = universe - out[vertex] - second - {vertex}
        rows.append(
            RowLedger(
                vertex=vertex,
                out_neighbors=tuple(sorted(out[vertex])),
                second_neighbors=tuple(sorted(second)),
                unreachable=tuple(sorted(unreachable)),
                out_degree=len(out[vertex]),
                second_degree=len(second),
                strict=len(second) < len(out[vertex]),
            )
        )
    return tuple(rows)


def matrix_oracle(
    raw_rows: Sequence[Sequence[int]],
    *,
    minimum_outdegree: int | None = None,
) -> tuple[RowLedger, ...]:
    """Independent raw replay using a Boolean matrix and explicit triples."""

    n = len(raw_rows)
    matrix = [[False] * n for _ in range(n)]
    normalized: list[tuple[int, ...]] = []
    for source, row in enumerate(raw_rows):
        values = tuple(row)
        if values != tuple(sorted(set(values))):
            raise GraphInvariantError(f"oracle row {source} is not sorted and unique")
        for target in values:
            if type(target) is not int or not (0 <= target < n):
                raise GraphInvariantError("oracle target is out of range")
            if source == target:
                raise GraphInvariantError("oracle rejected a loop")
            matrix[source][target] = True
        normalized.append(values)
    for a, b in pair_list(n):
        if matrix[a][b] and matrix[b][a]:
            raise GraphInvariantError(f"oracle rejected digon {(a, b)}")
    if minimum_outdegree is not None and any(
        len(row) < minimum_outdegree for row in normalized
    ):
        raise GraphInvariantError("oracle rejected minimum outdegree")

    ledger: list[RowLedger] = []
    for source in range(n):
        direct = tuple(target for target in range(n) if matrix[source][target])
        second: list[int] = []
        unreachable: list[int] = []
        for target in range(n):
            if target == source or matrix[source][target]:
                continue
            reachable = any(
                matrix[source][middle] and matrix[middle][target]
                for middle in range(n)
            )
            (second if reachable else unreachable).append(target)
        ledger.append(
            RowLedger(
                vertex=source,
                out_neighbors=direct,
                second_neighbors=tuple(second),
                unreachable=tuple(unreachable),
                out_degree=len(direct),
                second_degree=len(second),
                strict=len(second) < len(direct),
            )
        )
    return tuple(ledger)


def exact_objective(ledger: Iterable[RowLedger]) -> int:
    """A nonnegative integer that is zero exactly at a strict counterexample."""

    total = 0
    for row in ledger:
        if not row.strict:
            gap = row.second_degree - row.out_degree
            total += 1 + gap * gap
    return total


@dataclass(frozen=True)
class Mutation:
    index: int
    old_state: int
    new_state: int


def propose_mutation(
    graph: PairStateGraph, rng: random.Random
) -> Mutation:
    """Choose a one-pair transition that preserves minimum outdegree eight."""

    degrees = graph.outdegrees()
    indices = list(range(len(graph.states)))
    rng.shuffle(indices)
    for index in indices:
        old = graph.states[index]
        a, b = pair_list(graph.n)[index]
        if old == 0:
            options = [-1, 1]
        else:
            source = a if old == 1 else b
            options = [-old, 0] if degrees[source] > MIN_OUTDEGREE else []
        if options:
            return Mutation(index, old, rng.choice(options))
    raise RuntimeError("no legal pair mutation")


def apply_mutation(graph: PairStateGraph, mutation: Mutation) -> None:
    if graph.states[mutation.index] != mutation.old_state:
        raise GraphInvariantError("mutation old-state mismatch")
    graph.states[mutation.index] = mutation.new_state
    graph.validate(MIN_OUTDEGREE)


def revert_mutation(graph: PairStateGraph, mutation: Mutation) -> None:
    if graph.states[mutation.index] != mutation.new_state:
        raise GraphInvariantError("mutation new-state mismatch")
    graph.states[mutation.index] = mutation.old_state
    graph.validate(MIN_OUTDEGREE)


@dataclass(frozen=True)
class WalkResult:
    seed: int
    q_start: int
    profile: str
    steps: int
    accepted: int
    best_objective: int
    best_q: int
    hit: bool
    out_neighbors: tuple[tuple[int, ...], ...] | None
    ledger: tuple[RowLedger, ...] | None


def stochastic_walk(
    *,
    seed: int,
    q: int,
    profile: str,
    steps: int,
    start_temperature: float = 2.0,
) -> WalkResult:
    """Run one deterministic-seed annealed walk; return raw data only for a hit."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")
    rng = random.Random(seed)
    graph = make_initial_graph(q=q, seed=seed, profile=profile)
    current = exact_objective(set_ledger(graph))
    best = current
    best_q = graph.missing_count
    accepted = 0

    for step in range(steps):
        mutation = propose_mutation(graph, rng)
        apply_mutation(graph, mutation)
        candidate_ledger = set_ledger(graph)
        candidate = exact_objective(candidate_ledger)
        fraction = step / max(1, steps)
        temperature = max(0.05, start_temperature * (1.0 - fraction))
        delta = candidate - current
        take = delta <= 0 or rng.random() < math.exp(-delta / temperature)
        if take:
            current = candidate
            accepted += 1
        else:
            revert_mutation(graph, mutation)

        if current < best:
            best = current
            best_q = graph.missing_count
        if current == 0:
            raw = graph.to_out_neighbors()
            oracle = matrix_oracle(raw, minimum_outdegree=MIN_OUTDEGREE)
            replay = set_ledger(graph)
            if oracle != replay or exact_objective(oracle) != 0:
                raise GraphInvariantError("set/matrix replay disagreement at raw hit")
            return WalkResult(
                seed=seed,
                q_start=q,
                profile=profile,
                steps=step + 1,
                accepted=accepted,
                best_objective=0,
                best_q=graph.missing_count,
                hit=True,
                out_neighbors=raw,
                ledger=oracle,
            )

    return WalkResult(
        seed=seed,
        q_start=q,
        profile=profile,
        steps=steps,
        accepted=accepted,
        best_objective=best,
        best_q=best_q,
        hit=False,
        out_neighbors=None,
        ledger=None,
    )


def exhaustive_small_oracle_calibration(n: int = 4) -> int:
    """Compare the two semantics on all 3^(n choose 2) oriented graphs."""

    checked = 0
    for states in itertools.product((-1, 0, 1), repeat=len(pair_list(n))):
        graph = PairStateGraph(n, list(states))
        set_rows = set_ledger(graph)
        matrix_rows = matrix_oracle(graph.to_out_neighbors())
        if set_rows != matrix_rows:
            raise AssertionError(f"oracle disagreement at state {states}")
        if (exact_objective(set_rows) == 0) != all(row.strict for row in set_rows):
            raise AssertionError("objective zero-set drifted")
        checked += 1
    return checked


def mutation_revert_calibration(seed: int = 190019, steps: int = 500) -> int:
    rng = random.Random(seed)
    graph = make_initial_graph(q=9, seed=seed, profile="mixed")
    for _ in range(steps):
        before = graph.states.copy()
        mutation = propose_mutation(graph, rng)
        apply_mutation(graph, mutation)
        revert_mutation(graph, mutation)
        if graph.states != before:
            raise AssertionError("mutation/revert failed exact restoration")
    return steps


def calibration_report(walk_steps: int = 80) -> dict[str, object]:
    exhaustive = exhaustive_small_oracle_calibration(4)
    reverted = mutation_revert_calibration()
    cases = (
        (0, 190001, "regular"),
        (3, 190002, "skew"),
        (7, 190003, "mixed"),
        (12, 190004, "regular"),
        (16, 190005, "skew"),
        (19, 190006, "mixed"),
    )
    initial_profiles: list[dict[str, object]] = []
    walks: list[dict[str, object]] = []
    for q, seed, profile in cases:
        graph = make_initial_graph(q=q, seed=seed, profile=profile)
        degrees = graph.outdegrees()
        initial_profiles.append(
            {
                "q": q,
                "seed": seed,
                "profile": profile,
                "degree_profile": degrees,
                "objective": exact_objective(set_ledger(graph)),
            }
        )
        result = stochastic_walk(
            seed=seed,
            q=q,
            profile=profile,
            steps=walk_steps,
        )
        walks.append(
            {
                "q_start": q,
                "seed": seed,
                "profile": profile,
                "steps": result.steps,
                "accepted": result.accepted,
                "best_objective": result.best_objective,
                "best_q": result.best_q,
                "hit": result.hit,
            }
        )
    return {
        "status": "CALIBRATION_PASS",
        "production_run": False,
        "exhaustive_small_n": 4,
        "exhaustive_small_states": exhaustive,
        "mutation_revert_steps": reverted,
        "initial_profiles": initial_profiles,
        "walks": walks,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="run exhaustive-small and deterministic bounded calibrations",
    )
    parser.add_argument("--walk-steps", type=int, default=80)
    args = parser.parse_args(argv)
    if not args.calibrate:
        parser.error("production mode is intentionally absent; use --calibrate")
    report = calibration_report(args.walk_steps)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
