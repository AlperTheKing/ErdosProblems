#!/usr/bin/env python3

from __future__ import annotations

import unittest

from search_exact_cover import (
    Affine,
    Candidate,
    append_generator,
    class_mask,
    exact_cover,
    exact_cover_cp_sat,
    generate_affines,
    passes_outer_image_obstruction,
    progression_candidates,
)


class ExactCoverTests(unittest.TestCase):
    def test_word_application_order(self) -> None:
        affine = Affine(1, 0, ())
        affine = append_generator(affine, 2)
        affine = append_generator(affine, 3)
        self.assertEqual(affine, Affine(6, 1, (2, 3)))

    def test_generation_deduplicates_functions(self) -> None:
        affines = generate_affines(216, 6)
        keys = {(affine.slope, affine.intercept) for affine in affines}
        self.assertEqual(len(keys), len(affines))
        self.assertIn((6, 1), keys)
        self.assertIn((6, 2), keys)

    def test_exact_cover_solver_on_2_4_4(self) -> None:
        period = 4
        candidates = [
            Candidate(class_mask(0, 2, period), Affine(2, 0, (2,))),
            Candidate(class_mask(1, 4, period), Affine(4, 1, (2, 2))),
            Candidate(class_mask(3, 4, period), Affine(4, 3, (2, 2))),
        ]
        result, stats = exact_cover((1 << period) - 1, candidates, 100)
        self.assertTrue(stats.exhausted)
        self.assertIsNotNone(result)
        self.assertEqual(len(result or []), 3)
        cp_result, cp_stats = exact_cover_cp_sat(
            (1 << period) - 1, candidates, workers=1
        )
        self.assertEqual(cp_stats.status, "OPTIMAL")
        self.assertEqual(len(cp_result or []), 3)

    def test_progression_conjugation(self) -> None:
        # g_3 o g_2 = 6u+1 preserves 2Z+1 and induces 6y+3.
        affine = Affine(6, 1, (2, 3))
        candidates = progression_candidates([affine], 2, 1, 6)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].mask, class_mask(3, 6, 6))

    def test_outer_image_obstruction(self) -> None:
        self.assertFalse(passes_outer_image_obstruction(1, (0,)))
        self.assertTrue(passes_outer_image_obstruction(6, (0, 1, 2, 4)))
        self.assertFalse(passes_outer_image_obstruction(6, (3,)))


if __name__ == "__main__":
    unittest.main()
