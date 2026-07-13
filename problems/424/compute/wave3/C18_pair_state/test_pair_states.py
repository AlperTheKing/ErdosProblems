from __future__ import annotations

import unittest
from itertools import product

from orbit_witnesses import orbit_membership, parents
from relation_states import (
    GENERATORS,
    ROOTS as RELATION_ROOTS,
    State,
    enumerate_states as enumerate_relation_states,
    transition as relation_transition,
)
from tuple_states import (
    Form,
    ROOTS as TUPLE_ROOTS,
    TupleState,
    enumerate_states as enumerate_tuple_states,
    transition as tuple_transition,
)


def apply_word(seed: int, word: str) -> int:
    value = seed
    for letter in word:
        generator = int(letter)
        if value == generator:
            raise AssertionError((seed, word, value))
        value = generator * value - 1
    return value


class RelationStateTests(unittest.TestCase):
    def test_live_root_transitions(self) -> None:
        expected = {
            "P23": {
                (3, 2): State(9, 4, 1),
                (3, 5): State(9, 10, 1),
                (5, 2): State(15, 4, 1),
            },
            "P25": {
                (3, 2): State(15, 4, 3),
                (3, 3): State(5, 2, 1),
                (5, 2): State(25, 4, 3),
                (5, 3): State(25, 6, 3),
            },
            "P35": {
                (2, 2): State(5, 3, 1),
                (2, 3): State(10, 9, 2),
                (5, 2): State(25, 6, 2),
                (5, 3): State(25, 9, 2),
            },
        }
        for name, root in RELATION_ROOTS.items():
            actual = {
                maps: child
                for maps in product(GENERATORS, repeat=2)
                if (child := relation_transition(root, *maps)) is not None
            }
            self.assertEqual(expected[name], actual)

    def test_repeated_p35_branch_is_infinite(self) -> None:
        state = RELATION_ROOTS["P35"]
        offset = 0
        for depth in range(21):
            self.assertEqual(
                State(5 ** (depth + 1), 3 ** (depth + 1), offset), state
            )
            state = relation_transition(state, 5, 3)
            self.assertIsNotNone(state)
            offset += 5 ** (depth + 1) - 3 ** (depth + 1)

    def test_relation_census(self) -> None:
        depth, _ = enumerate_relation_states(6)
        counts = [sum(value == level for value in depth.values()) for level in range(7)]
        self.assertEqual([3, 11, 50, 154, 616, 1_838, 6_374], counts)


class TupleStateTests(unittest.TestCase):
    def test_pair_root_transitions(self) -> None:
        expected = {
            "P23": {
                (3, 2): (6, 1, TupleState((Form(4, 1), Form(9, 2)))),
                (3, 5): (15, 13, TupleState((Form(9, 8), Form(10, 9)))),
                (5, 2): (10, 7, TupleState((Form(4, 3), Form(15, 11)))),
            },
            "P25": {
                (3, 2): (6, 1, TupleState((Form(4, 1), Form(15, 3)))),
                (3, 3): (3, 1, TupleState((Form(2, 1), Form(5, 2)))),
                (5, 2): (10, 7, TupleState((Form(4, 3), Form(25, 18)))),
                (5, 3): (15, 7, TupleState((Form(6, 3), Form(25, 12)))),
            },
            "P35": {
                (2, 2): (2, 1, TupleState((Form(3, 2), Form(5, 3)))),
                (2, 3): (6, 1, TupleState((Form(9, 2), Form(10, 2)))),
                (5, 2): (10, 3, TupleState((Form(6, 2), Form(25, 8)))),
                (5, 3): (15, 13, TupleState((Form(9, 8), Form(25, 22)))),
            },
        }
        for name, wanted in expected.items():
            root = TUPLE_ROOTS[name]
            actual = {
                maps: result
                for maps in product(GENERATORS, repeat=2)
                if (result := tuple_transition(root, maps)) is not None
            }
            self.assertEqual(wanted, actual)

    def test_p235_has_one_first_transition(self) -> None:
        root = TUPLE_ROOTS["P235"]
        live = {
            maps: result
            for maps in product(GENERATORS, repeat=3)
            if (result := tuple_transition(root, maps)) is not None
        }
        self.assertEqual(
            {
                (5, 3, 2): (
                    30,
                    29,
                    TupleState(
                        (
                            Form(36, 35),
                            Form(100, 97),
                            Form(225, 218),
                        )
                    ),
                )
            },
            live,
        )

    def test_tuple_censuses(self) -> None:
        expected = {
            "P23": [1, 3, 20, 55, 227, 662, 2_447],
            "P25": [1, 4, 18, 68, 262, 842, 2_877],
            "P35": [1, 4, 17, 59, 267, 861, 2_927],
            "P235": [1, 1, 12, 24, 219],
        }
        for name, wanted in expected.items():
            max_depth = len(wanted) - 1
            depth = enumerate_tuple_states(TUPLE_ROOTS[name], max_depth)
            counts = [
                sum(value == level for value in depth.values())
                for level in range(max_depth + 1)
            ]
            self.assertEqual(wanted, counts)


class OrbitWitnessTests(unittest.TestCase):
    def test_first_pair_branch_overlap(self) -> None:
        member = orbit_membership(2_000)
        for parameter in range(1, 547):
            if member[2 * parameter] and member[3 * parameter]:
                multiplicity = len(parents(2 * parameter, member)) * len(
                    parents(3 * parameter, member)
                )
                self.assertLessEqual(multiplicity, 1)
        self.assertEqual((3, 5), parents(1_094, member))
        self.assertEqual((2,), parents(1_641, member))
        self.assertEqual(219, apply_word(5, "255"))
        self.assertEqual(365, apply_word(5, "3333"))
        self.assertEqual(821, apply_word(5, "35322"))

    def test_depth_five_p35_witness(self) -> None:
        left_parent = apply_word(5, "3252222")
        right_parent = apply_word(5, "232533252")
        left_value = apply_word(left_parent, "55555")
        right_value = apply_word(right_parent, "33333")
        self.assertEqual((2_129, 45_627), (left_parent, right_parent))
        self.assertEqual((6_652_344, 11_087_240), (left_value, right_value))
        self.assertEqual(5 * left_value, 3 * right_value)

    def test_first_p235_witness(self) -> None:
        limit = 192_585
        member = orbit_membership(limit)
        hits = [
            parameter
            for parameter in range(1, limit // 15 + 1)
            if member[6 * parameter]
            and member[10 * parameter]
            and member[15 * parameter]
        ]
        self.assertEqual(12_839, hits[0])
        self.assertEqual(15_407, apply_word(5, "2222232252"))
        self.assertEqual(42_797, apply_word(5, "323233352"))
        self.assertEqual(96_293, apply_word(5, "232225222322"))


if __name__ == "__main__":
    unittest.main()
