"""Adversarial replay of the hash-pinned irregular-19 singleton obstruction.

No SAT solver is called.  The tests check the two finite row-equation
certificates against IRREGULAR19_INCIDENCE_SEED.json and deliberately mutate
each load-bearing input.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest


N = 19
EXPECTED_SHA256 = (
    "B4BFB3000D9F14E7C763764DDF474FECD166DE12CC7F96B9D593F8801DF5EF69"
)
SEED = Path(__file__).resolve().parents[2] / "IRREGULAR19_INCIDENCE_SEED.json"


def load_raw() -> tuple[bytes, dict[str, object]]:
    raw = SEED.read_bytes()
    return raw, json.loads(raw)


def extract(data: dict[str, object]) -> tuple[
    frozenset[tuple[int, int]],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
]:
    missing = frozenset(
        tuple(sorted(edge)) for edge in data["missing_graph"]["edges"]
    )
    blocks = tuple(
        tuple(block) for block in data["incidence"]["root_blocks_by_target"]
    )
    rows = tuple(
        tuple(row)
        for row in data["incidence"]["declared_unreachable_targets_by_source"]
    )
    return missing, blocks, rows


def transpose(blocks: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(target for target, block in enumerate(blocks) if source in block)
        for source in range(N)
    )


def missing_row(
    vertex: int, missing: frozenset[tuple[int, int]]
) -> tuple[int, ...]:
    row = [0] * N
    for a, b in missing:
        if a == vertex:
            row[b] = 1
        elif b == vertex:
            row[a] = 1
    return tuple(row)


def singleton_map(
    blocks: tuple[tuple[int, ...], ...]
) -> dict[int, int]:
    return {
        target: block[0]
        for target, block in enumerate(blocks)
        if len(block) == 1
    }


def duplicate_roots(
    blocks: tuple[tuple[int, ...], ...]
) -> dict[int, tuple[int, ...]]:
    inverse: dict[int, list[int]] = defaultdict(list)
    for target, root in singleton_map(blocks).items():
        inverse[root].append(target)
    return {
        root: tuple(targets)
        for root, targets in inverse.items()
        if len(targets) > 1
    }


def shared_singleton_pair_units(
    left: int,
    right: int,
    root: int,
    missing: frozenset[tuple[int, int]],
    blocks: tuple[tuple[int, ...], ...],
) -> tuple[tuple[tuple[int, int], bool], ...]:
    """Replay the two coordinates of the singleton row equations.

    For R_left=R_right={root}, saturation gives
    A_left+M_left=e_root+A_root and
    A_right+M_right=e_root+A_root.
    At coordinates left and right, if {left,right} is present, these equations
    force both orientations of that pair false.
    """

    if blocks[left] != (root,) or blocks[right] != (root,):
        raise ValueError("targets do not share the stated singleton root")
    if len({left, right, root}) != 3:
        raise ValueError("targets and root must be distinct")
    if tuple(sorted((left, right))) in missing:
        raise ValueError("the target pair is missing, not oriented")
    return (((left, right), False), ((right, left), False))


def singleton_cycle_residual(
    left: int,
    right: int,
    missing: frozenset[tuple[int, int]],
    blocks: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    """Return M_left+M_right-e_left-e_right for a singleton 2-cycle."""

    if blocks[left] != (right,) or blocks[right] != (left,):
        raise ValueError("the stated targets are not a singleton 2-cycle")
    residual = [
        a + b
        for a, b in zip(
            missing_row(left, missing), missing_row(right, missing), strict=True
        )
    ]
    residual[left] -= 1
    residual[right] -= 1
    return tuple(residual)


def clause_satisfied(
    clause: tuple[tuple[tuple[int, int], bool], ...],
    assignment: dict[tuple[int, int], bool],
) -> bool:
    return any(assignment[variable] == sign for variable, sign in clause)


class Irregular19SingletonObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw, cls.data = load_raw()
        cls.missing, cls.blocks, cls.rows = extract(cls.data)

    def test_01_seed_identity_is_exact(self) -> None:
        self.assertEqual(sha256(self.raw).hexdigest().upper(), EXPECTED_SHA256)
        self.assertEqual(self.data["schema"], "ssnc-irregular19-incidence-seed-v1")
        self.assertEqual(self.data["n"], N)
        self.assertEqual(self.data["vertices"], list(range(N)))

    def test_02_missing_graph_and_saturation(self) -> None:
        degrees = [sum(vertex in edge for edge in self.missing) for vertex in range(N)]
        self.assertEqual(
            degrees,
            [4, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        )
        self.assertEqual(
            [len(block) for block in self.blocks],
            [2 * degree - 1 for degree in degrees],
        )

    def test_03_W_direction_is_the_transpose_of_R(self) -> None:
        self.assertEqual(transpose(self.blocks), self.rows)
        self.assertIn(14, self.rows[18])
        self.assertIn(15, self.rows[18])
        self.assertNotIn(18, self.rows[14])

    def test_04_repeated_singletons_are_exact(self) -> None:
        self.assertEqual(
            duplicate_roots(self.blocks),
            {15: (10, 18), 6: (12, 17), 18: (14, 15)},
        )

    def test_05_shared_root_forces_both_present_pair_arcs_false(self) -> None:
        units = shared_singleton_pair_units(
            14, 15, 18, self.missing, self.blocks
        )
        self.assertEqual(
            units,
            (((14, 15), False), ((15, 14), False)),
        )
        self.assertNotIn((14, 15), self.missing)

    def test_06_exact_one_pair_clause_closes_shared_root(self) -> None:
        units = dict(
            shared_singleton_pair_units(14, 15, 18, self.missing, self.blocks)
        )
        present_pair_clause = (((14, 15), True), ((15, 14), True))
        self.assertFalse(clause_satisfied(present_pair_clause, units))

        # One-clause mutation: deleting the at-least-one clause admits both
        # arcs false while preserving the usual at-most-one pair clause.
        at_most_one_clause = (((14, 15), False), ((15, 14), False))
        self.assertTrue(clause_satisfied(at_most_one_clause, units))

    def test_07_shared_root_mutation_is_rejected(self) -> None:
        mutant = list(self.blocks)
        mutant[15] = (17,)
        with self.assertRaisesRegex(ValueError, "do not share"):
            shared_singleton_pair_units(
                14, 15, 18, self.missing, tuple(mutant)
            )

    def test_08_missing_pair_mutation_is_rejected(self) -> None:
        mutant = frozenset(set(self.missing) | {(14, 15)})
        with self.assertRaisesRegex(ValueError, "missing"):
            shared_singleton_pair_units(14, 15, 18, mutant, self.blocks)

    def test_09_singleton_cycle_residual_is_exact(self) -> None:
        residual = singleton_cycle_residual(15, 18, self.missing, self.blocks)
        self.assertEqual(
            {i: value for i, value in enumerate(residual) if value},
            {5: 1, 8: 1, 15: -1, 18: -1},
        )

    def test_10_cycle_direction_mutation_is_rejected(self) -> None:
        mutant = list(self.blocks)
        mutant[18] = (14,)
        with self.assertRaisesRegex(ValueError, "not a singleton 2-cycle"):
            singleton_cycle_residual(15, 18, self.missing, tuple(mutant))

    def test_11_fixed_missing_graph_is_load_bearing(self) -> None:
        # If 15 and 18 were each other's unique missing neighbours, the
        # potential residual would vanish.  The pinned JSON instead has
        # missing neighbours 5 and 8, which is why the certificate closes.
        fake_missing = frozenset({(15, 18)})
        residual = singleton_cycle_residual(
            15, 18, fake_missing, self.blocks
        )
        self.assertFalse(any(residual))

    def test_12_stored_orientation_is_not_used(self) -> None:
        mutant = deepcopy(self.data)
        mutant["orientation"]["out_neighbors"] = [[] for _ in range(N)]
        missing, blocks, rows = extract(mutant)
        self.assertEqual(missing, self.missing)
        self.assertEqual(blocks, self.blocks)
        self.assertEqual(rows, self.rows)
        self.assertEqual(
            singleton_cycle_residual(15, 18, missing, blocks),
            singleton_cycle_residual(15, 18, self.missing, self.blocks),
        )


if __name__ == "__main__":
    unittest.main()
