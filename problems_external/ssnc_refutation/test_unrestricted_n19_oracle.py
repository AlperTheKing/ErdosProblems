"""Adversarial tests for unrestricted_n19_oracle.py.

Only Python's standard library is used.  The tests generate graphs from raw
pair states and do not share an incremental score implementation.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations, product
import json
import random
import unittest

from unrestricted_n19_oracle import (
    CANDIDATE_SCHEMA,
    CandidateError,
    analyze,
    candidate_bytes,
    candidate_object,
    normalize_rows,
    pair_state,
    parse_candidate_bytes,
    parse_candidate_object,
    set_pair_state,
)


def rows_from_states(n: int, states: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    pairs = tuple(combinations(range(n), 2))
    assert len(states) == len(pairs)
    rows = [set() for _ in range(n)]
    for (a, b), state in zip(pairs, states):
        if state == 1:
            rows[a].add(b)
        elif state == 2:
            rows[b].add(a)
        else:
            assert state == 0
    return normalize_rows([sorted(row) for row in rows])


def brute_row(rows: tuple[tuple[int, ...], ...], v: int) -> dict[str, object]:
    """Independent triple-loop definition, used only in tests."""
    n = len(rows)
    out = set(rows[v])
    raw2 = {
        target
        for middle in range(n)
        for target in range(n)
        if middle in out and target in rows[middle]
    }
    new2 = {target for target in raw2 if target != v and target not in out}
    unreachable = set(range(n)) - {v} - out - new2
    penalty = max(0, len(new2) - len(out) + 1)
    return {
        "out": sorted(out),
        "raw2": sorted(raw2),
        "new2": sorted(new2),
        "unreachable": sorted(unreachable),
        "penalty": penalty,
    }


def tournament19() -> tuple[tuple[int, ...], ...]:
    rows = []
    for v in range(19):
        rows.append(sorted((v + delta) % 19 for delta in range(1, 10)))
    return normalize_rows(rows)


def degree8_cycle_missing() -> tuple[tuple[int, ...], ...]:
    rows = [set(row) for row in tournament19()]
    for v in range(19):
        rows[v].remove((v + 1) % 19)
    return normalize_rows([sorted(row) for row in rows])


def reverse_rows(rows: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    reversed_rows = [set() for _ in rows]
    for v, row in enumerate(rows):
        for w in row:
            reversed_rows[w].add(v)
    return normalize_rows([sorted(row) for row in reversed_rows])


def permute_rows(
    rows: tuple[tuple[int, ...], ...], permutation: list[int]
) -> tuple[tuple[int, ...], ...]:
    result = [set() for _ in rows]
    for v, row in enumerate(rows):
        for w in row:
            result[permutation[v]].add(permutation[w])
    return normalize_rows([sorted(row) for row in result])


class ExhaustiveSmallTests(unittest.TestCase):
    def test_all_oriented_graphs_through_order_four(self) -> None:
        checked = 0
        overlap_seen = False
        for n in range(1, 5):
            pair_count = n * (n - 1) // 2
            for states in product(range(3), repeat=pair_count):
                rows = rows_from_states(n, states)
                result = analyze(rows, min_outdegree=0)
                brute_penalty = 0
                for v, entry in enumerate(result["ledger"]):
                    brute = brute_row(rows, v)
                    self.assertEqual(entry["N+"], brute["out"])
                    self.assertEqual(entry["raw_length2"], brute["raw2"])
                    self.assertEqual(entry["new_N2+"], brute["new2"])
                    self.assertEqual(entry["unreachable"], brute["unreachable"])
                    self.assertEqual(entry["row_penalty"], brute["penalty"])
                    brute_penalty += int(brute["penalty"])
                    overlap_seen |= bool(entry["direct_raw2_overlap"])
                self.assertEqual(result["strict_objective"], brute_penalty)
                self.assertEqual(
                    result["strict_objective"] == 0,
                    all(entry["strict"] for entry in result["ledger"]),
                )
                self.assertEqual(result["score_zero"], result["strict_all"])
                checked += 1
        self.assertEqual(checked, 760)
        self.assertTrue(overlap_seen)
        print(f"exhaustive_small_graphs={checked}")

    def test_direct_and_two_step_overlap_is_not_new_second(self) -> None:
        # 0->1 is direct and also 0->2->1.
        rows = normalize_rows([[1, 2], [], [1]])
        row0 = analyze(rows)["ledger"][0]
        self.assertIn(1, row0["raw_length2"])
        self.assertIn(1, row0["direct_raw2_overlap"])
        self.assertNotIn(1, row0["new_N2+"])


class NineteenVertexTests(unittest.TestCase):
    def test_minimum_degree_boundaries(self) -> None:
        degree9 = tournament19()
        degree8 = degree8_cycle_missing()
        degree7 = set_pair_state(degree8, 0, 2, 0)
        a9 = analyze(degree9, min_outdegree=8)
        a8 = analyze(degree8, min_outdegree=8)
        a7 = analyze(degree7, min_outdegree=8)
        self.assertEqual(a9["min_outdegree_actual"], 9)
        self.assertEqual(a8["min_outdegree_actual"], 8)
        self.assertEqual(a7["min_outdegree_actual"], 7)
        self.assertTrue(a9["domain_valid"])
        self.assertTrue(a8["domain_valid"])
        self.assertFalse(a7["domain_valid"])
        self.assertEqual(a7["domain_deficit"], 1)

    def test_every_pair_mutation_reverts_exactly(self) -> None:
        baseline = degree8_cycle_missing()
        baseline_bytes = candidate_bytes(baseline)
        baseline_analysis = analyze(baseline, min_outdegree=8)
        mutations = 0
        for a, b in combinations(range(19), 2):
            old = pair_state(baseline, a, b)
            changed = set_pair_state(baseline, a, b, (old + 1) % 3)
            restored = set_pair_state(changed, a, b, old)
            self.assertEqual(candidate_bytes(restored), baseline_bytes)
            self.assertEqual(analyze(restored, min_outdegree=8), baseline_analysis)
            mutations += 1
        self.assertEqual(mutations, 171)
        print(f"mutation_revert_pairs={mutations}")

    def test_deterministic_random_walk_and_all_six_transitions(self) -> None:
        rows = degree8_cycle_missing()
        observed: set[tuple[int, int]] = set()

        # Pair (0,1) starts missing.  This sequence realizes every ordered
        # transition between the three legal pair states exactly once.
        sequence = (1, 2, 0, 2, 1, 0)
        for new_state in sequence:
            old_state = pair_state(rows, 0, 1)
            observed.add((old_state, new_state))
            rows = set_pair_state(rows, 0, 1, new_state)

        rng = random.Random(20260721)
        pairs = tuple(combinations(range(19), 2))
        for _ in range(1000):
            a, b = rng.choice(pairs)
            old_state = pair_state(rows, a, b)
            new_state = rng.choice(tuple(s for s in (0, 1, 2) if s != old_state))
            observed.add((old_state, new_state))
            rows = set_pair_state(rows, a, b, new_state)
            result = analyze(rows, min_outdegree=8)
            brute_penalty = sum(int(brute_row(rows, v)["penalty"]) for v in range(19))
            brute_deficit = sum(max(0, 8 - len(row)) for row in rows)
            self.assertEqual(result["strict_objective"], brute_penalty)
            self.assertEqual(result["domain_deficit"], brute_deficit)
            self.assertEqual(result["objective"], brute_penalty + brute_deficit)
            self.assertEqual(
                result["score_zero"],
                result["domain_valid"] and result["strict_all"],
            )

        expected = {(a, b) for a in range(3) for b in range(3) if a != b}
        self.assertEqual(observed, expected)
        print("pair_state_transitions=6/6 random_walk_steps=1000")

    def test_vertex_relabelling_safe_and_arc_reversal_unsafe(self) -> None:
        rows = degree8_cycle_missing()
        permutation = list(range(19))
        random.Random(1908).shuffle(permutation)
        relabelled = permute_rows(rows, permutation)
        original = analyze(rows, min_outdegree=8)
        changed = analyze(relabelled, min_outdegree=8)
        self.assertEqual(original["objective"], changed["objective"])
        original_rows = sorted(
            (e["out_degree"], e["new_second_degree"], e["row_penalty"])
            for e in original["ledger"]
        )
        changed_rows = sorted(
            (e["out_degree"], e["new_second_degree"], e["row_penalty"])
            for e in changed["ledger"]
        )
        self.assertEqual(original_rows, changed_rows)

        # Edges 0->2 and 1->2: reversal changes strict objective 1 -> 2.
        asymmetric = normalize_rows([[2], [2], []])
        self.assertEqual(analyze(asymmetric)["strict_objective"], 1)
        self.assertEqual(analyze(reverse_rows(asymmetric))["strict_objective"], 2)


class ParserAdversaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = degree8_cycle_missing()
        self.valid = candidate_object(self.rows)

    def assert_bad_object(self, value: object) -> None:
        with self.assertRaises(CandidateError):
            parse_candidate_object(value, expected_n=19)

    def test_canonical_roundtrip(self) -> None:
        self.assertEqual(parse_candidate_bytes(candidate_bytes(self.rows), expected_n=19), self.rows)

    def test_object_mutations_rejected(self) -> None:
        mutations: list[object] = []

        value = deepcopy(self.valid); value["schema"] = "wrong"; mutations.append(value)
        value = deepcopy(self.valid); value["extra"] = 1; mutations.append(value)
        value = deepcopy(self.valid); del value["n"]; mutations.append(value)
        value = deepcopy(self.valid); value["n"] = 18; mutations.append(value)
        value = deepcopy(self.valid); value["n"] = True; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"] = value["out_neighbors"][:-1]; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0] = list(reversed(value["out_neighbors"][0])); mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0].append(value["out_neighbors"][0][0]); value["out_neighbors"][0].sort(); mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0].append(0); value["out_neighbors"][0].sort(); mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0][0] = -1; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0][-1] = 19; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0][0] = "2"; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0][0] = 2.0; mutations.append(value)
        value = deepcopy(self.valid); value["out_neighbors"][0][0] = True; mutations.append(value)

        # Force a digon on a present pair.
        value = deepcopy(self.valid)
        a = 0
        b = value["out_neighbors"][a][0]
        value["out_neighbors"][b].append(a)
        value["out_neighbors"][b].sort()
        mutations.append(value)

        for mutation in mutations:
            self.assert_bad_object(mutation)
        self.assertEqual(len(mutations), 15)
        print(f"parser_object_mutations={len(mutations)}")

    def test_byte_mutations_rejected(self) -> None:
        bad_payloads = [
            b"not json",
            candidate_bytes(self.rows) + b"{}",
            b"\xef\xbb\xbf" + candidate_bytes(self.rows),
            b"\xff",
            json.dumps([1, 2, 3]).encode("ascii"),
        ]
        for payload in bad_payloads:
            with self.assertRaises(CandidateError):
                parse_candidate_bytes(payload, expected_n=19)
        self.assertEqual(len(bad_payloads), 5)
        print(f"parser_byte_mutations={len(bad_payloads)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

