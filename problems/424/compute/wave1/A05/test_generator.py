import unittest

from generator import canonical_digest, fixed_point_up_to, generated_up_to


class GeneratorTests(unittest.TestCase):
    def test_small_boundaries(self) -> None:
        self.assertEqual(generated_up_to(0), [])
        self.assertEqual(generated_up_to(1), [])
        self.assertEqual(generated_up_to(2), [2])
        self.assertEqual(generated_up_to(3), [2, 3])
        self.assertEqual(generated_up_to(4), [2, 3])
        self.assertEqual(generated_up_to(5), [2, 3, 5])

    def test_known_prefix(self) -> None:
        expected = [2, 3, 5, 9, 14, 17, 26, 27, 33]
        self.assertEqual(generated_up_to(33), expected)

    def test_every_bound_through_300(self) -> None:
        for limit in range(1, 301):
            with self.subTest(limit=limit):
                self.assertEqual(generated_up_to(limit), fixed_point_up_to(limit))

    def test_independent_oracle_at_5000(self) -> None:
        self.assertEqual(generated_up_to(5000), fixed_point_up_to(5000))

    def test_canonical_digest_has_no_trailing_newline(self) -> None:
        self.assertEqual(
            canonical_digest([2, 3, 5]),
            "56797ac85eadbd8607fa3f46cb5fa694570ac2ff3ce931cbefc2726bcf401f31",
        )


if __name__ == "__main__":
    unittest.main()
