from __future__ import annotations

import ast
import builtins
import importlib.util
import inspect
import json
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ENGINE = Path(__file__).resolve().parents[1]
DECODER_PATH = ENGINE / "decode_cycle19_model.py"
MANIFEST_PATH = ENGINE / "instances" / "cycle19-fixed-v1" / "manifest.json"

SPEC = importlib.util.spec_from_file_location("cycle19_decoder_under_test", DECODER_PATH)
assert SPEC is not None and SPEC.loader is not None
decoder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(decoder)

MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class TextSolution:
    """A read-only Path stand-in, so parser tests never create solver files."""

    def __init__(self, text: str) -> None:
        self.text = text

    def read_text(self, *, encoding: str) -> str:
        if encoding != "ascii":
            raise AssertionError(f"unexpected solution encoding: {encoding}")
        return self.text


def orientation_variables() -> dict[tuple[int, int], int]:
    result: dict[tuple[int, int], int] = {}
    for identifier, name in MANIFEST["variable_map"].items():
        match = decoder.EDGE_NAME.fullmatch(name)
        if match is not None:
            result[tuple(map(int, match.groups()))] = int(identifier)
    return result


EDGE_VARIABLE = orientation_variables()


def even_circulant_assignment() -> dict[int, bool]:
    """Pin v -> v+d for d in {2,4,...,16} on the frozen cycle support."""

    forward_steps = {2, 4, 6, 8, 10, 12, 14, 16}
    return {
        variable: ((b - a) % 19) in forward_steps
        for (a, b), variable in EDGE_VARIABLE.items()
    }


def has_arc(assignment: dict[int, bool], tail: int, head: int) -> bool:
    a, b = sorted((tail, head))
    value = assignment[EDGE_VARIABLE[(a, b)]]
    return value if tail == a else not value


class Cycle19DecoderTests(unittest.TestCase):
    def test_cadical_multiline_signed_model_parsing(self) -> None:
        solution = TextSolution(
            """\
c CaDiCaL can wrap a model over multiple v lines
s SATISFIABLE
v 1 -2 0
v 3
v -4 0
"""
        )
        self.assertEqual(
            decoder.parse_solution(solution),
            {1: True, 2: False, 3: True, 4: False},
        )

    def test_conflicting_assignment_is_rejected(self) -> None:
        solution = TextSolution("s SATISFIABLE\nv 1 -2 0\nv -1 0\n")
        with self.assertRaisesRegex(ValueError, "conflicting assignments for variable 1"):
            decoder.parse_solution(solution)

    def test_non_sat_status_is_rejected(self) -> None:
        for text, expected in (
            ("s UNSATISFIABLE\n", "UNSATISFIABLE"),
            ("s UNKNOWN\n", "UNKNOWN"),
            ("v 1 0\n", "None"),
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, expected):
                    decoder.parse_solution(TextSolution(text))

    def test_frozen_support_and_signed_endpoint_order(self) -> None:
        self.assertEqual(
            MANIFEST["edge_variable_semantics"],
            "edge(a,b), a<b, is true iff the arc is a->b; false iff b->a",
        )
        self.assertEqual(len(EDGE_VARIABLE), 152)
        assignment = even_circulant_assignment()

        # edge(0,2)=true decodes in the stored low-to-high endpoint order.
        self.assertTrue(assignment[EDGE_VARIABLE[(0, 2)]])
        self.assertTrue(has_arc(assignment, 0, 2))
        self.assertFalse(has_arc(assignment, 2, 0))

        # edge(0,3)=false decodes in the opposite high-to-low endpoint order.
        self.assertFalse(assignment[EDGE_VARIABLE[(0, 3)]])
        self.assertTrue(has_arc(assignment, 3, 0))
        self.assertFalse(has_arc(assignment, 0, 3))

    def test_missing_wrap_edge_has_no_orientation_variable(self) -> None:
        missing = {tuple(edge) for edge in MANIFEST["missing_edges"]}
        self.assertEqual(len(missing), 19)
        self.assertIn((0, 18), missing)
        self.assertNotIn((0, 18), EDGE_VARIABLE)
        self.assertEqual(
            missing,
            {(v, v + 1) for v in range(18)} | {(0, 18)},
        )

    def test_symmetry_pin_is_checked_before_degree_and_ledger_checks(self) -> None:
        assignment = even_circulant_assignment()
        assignment[EDGE_VARIABLE[(0, 2)]] = False
        with self.assertRaisesRegex(
            ValueError, "violates the declared symmetry unit 0->2"
        ):
            decoder.decode(MANIFEST, assignment)

    def test_missing_orientation_assignment_is_rejected(self) -> None:
        assignment = even_circulant_assignment()
        missing_variable = EDGE_VARIABLE[(0, 2)]
        del assignment[missing_variable]
        with self.assertRaisesRegex(
            ValueError, rf"orientation variable {missing_variable} is unassigned"
        ):
            decoder.decode(MANIFEST, assignment)

    def test_success_return_has_exact_verifier_top_level_schema(self) -> None:
        # A successful call would itself be a counterexample.  Audit the sole
        # success return without fabricating one or weakening the decoder.
        source = textwrap.dedent(inspect.getsource(decoder.decode))
        tree = ast.parse(source)
        returns = [node for node in ast.walk(tree) if isinstance(node, ast.Return)]
        self.assertEqual(len(returns), 1)
        value = returns[0].value
        self.assertIsInstance(value, ast.Dict)
        assert isinstance(value, ast.Dict)
        self.assertEqual(
            [key.value for key in value.keys if isinstance(key, ast.Constant)],
            ["n", "out_neighbors"],
        )

    def test_pinned_near_miss_reaches_and_fails_target_ledger_guard(self) -> None:
        assignment = even_circulant_assignment()

        # The frozen, symmetry-pinned circulant has two unreachable targets in
        # every row and column, so an ordinary replay must fail before emission.
        with self.assertRaisesRegex(
            ValueError, "decoded model has 2 unreachable targets at 0"
        ):
            decoder.decode(MANIFEST, assignment)

        # Isolate the final independent column guard.  This test-only len shim
        # lets only the known two-element row ledgers pass the preceding
        # exact-three assertion; it cannot change adjacency or column counts.
        real_len = builtins.len

        def row_gate_shim(value: object) -> int:
            actual = real_len(value)  # type: ignore[arg-type]
            if (
                isinstance(value, list)
                and actual == 2
                and all(type(item) is int for item in value)
            ):
                return 3
            return actual

        with mock.patch.object(decoder, "len", row_gate_shim, create=True):
            with self.assertRaisesRegex(
                ValueError,
                r"decoded model violates target ledger: \[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2\]",
            ):
                decoder.decode(MANIFEST, assignment)


if __name__ == "__main__":
    unittest.main()
