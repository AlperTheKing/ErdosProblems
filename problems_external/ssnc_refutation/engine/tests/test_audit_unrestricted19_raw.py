"""Cross-calibration for the independent C++ raw-adjacency auditor."""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import unittest


ENGINE_DIR = Path(__file__).resolve().parents[1]
PYTHON_ENGINE = ENGINE_DIR / "search_unrestricted19_set.py"
GCC_AUDITOR = ENGINE_DIR / "audit_unrestricted19_raw_gcc.exe"
CLANG_AUDITOR = ENGINE_DIR / "audit_unrestricted19_raw_clang.exe"

SPEC = importlib.util.spec_from_file_location("unrestricted19_set_for_cpp_audit", PYTHON_ENGINE)
assert SPEC is not None and SPEC.loader is not None
oracle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = oracle
SPEC.loader.exec_module(oracle)


def raw_object(rows: tuple[tuple[int, ...], ...]) -> dict[str, object]:
    return {"n": len(rows), "out_neighbors": [list(row) for row in rows]}


def python_reference(rows: tuple[tuple[int, ...], ...]) -> dict[str, object]:
    graph = oracle.PairStateGraph.from_out_neighbors(rows)
    ledger = oracle.set_ledger(graph)
    out = [set(row) for row in rows]
    result_rows: list[dict[str, object]] = []
    exact_total = 0
    witness_total = 0
    for row in ledger:
        counts = [
            sum(target in out[middle] for middle in out[row.vertex])
            for target in range(graph.n)
        ]
        witness_mass = sum(
            counts[target] * (counts[target] + 1) // 2
            for target in row.second_neighbors
        )
        eligible_counts = sorted(
            counts[target]
            for target in range(graph.n)
            if target != row.vertex and target not in out[row.vertex]
        )
        need = max(0, graph.n - 2 * row.out_degree)
        witness_energy = sum(eligible_counts[:need]) + max(0, need - len(eligible_counts))
        if row.strict:
            exact_penalty = 0
        else:
            exact_penalty = row.second_degree - row.out_degree + 1
        exact_total += exact_penalty
        witness_total += witness_energy
        result_rows.append(
            {
                "vertex": row.vertex,
                "out_neighbors": list(row.out_neighbors),
                "second_neighbors": list(row.second_neighbors),
                "unreachable": list(row.unreachable),
                "witness_counts": counts,
                "d1": row.out_degree,
                "d2": row.second_degree,
                "strict": row.strict,
                "exact_penalty": exact_penalty,
                "witness_mass": witness_mass,
                "witness_energy": witness_energy,
            }
        )
    minimum = min(len(row) for row in rows)
    all_strict = all(row.strict for row in ledger)
    total_arcs = sum(len(row) for row in rows)
    q = graph.n * (graph.n - 1) // 2 - total_arcs
    in_domain = graph.n == 19 and minimum >= 8
    accepted = in_domain and all_strict
    return {
        "status": "VERIFIED_COUNTEREXAMPLE" if accepted else "VERIFIED_NONHIT",
        "n": graph.n,
        "minimum_outdegree": minimum,
        "missing_pairs": q,
        "in_n19_domain": in_domain,
        "all_strict": all_strict,
        "accepted_counterexample": accepted,
        "exact_objective": exact_total,
        "witness_energy": witness_total,
        "rows": result_rows,
    }


def exhaustive_rows_through_four() -> list[tuple[tuple[int, ...], ...]]:
    cases: list[tuple[tuple[int, ...], ...]] = []
    for n in range(1, 5):
        for states in itertools.product((-1, 0, 1), repeat=len(oracle.pair_list(n))):
            graph = oracle.PairStateGraph(n, list(states))
            cases.append(graph.to_out_neighbors())
    return cases


def deterministic_n19_rows() -> list[tuple[tuple[int, ...], ...]]:
    cases = []
    for q in range(1, 20):
        profile = oracle.PROFILES[(q - 1) % len(oracle.PROFILES)]
        graph = oracle.make_initial_graph(q=q, seed=319000 + q, profile=profile)
        cases.append(graph.to_out_neighbors())
    return cases


def run_batch(
    executable: Path,
    cases: list[tuple[tuple[int, ...], ...]],
) -> list[dict[str, object]]:
    payload = "\n".join(
        json.dumps(raw_object(rows), separators=(",", ":"))
        for rows in cases
    )
    completed = subprocess.run(
        [str(executable), "--jsonl"],
        input=payload + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"{executable.name} failed {completed.returncode}: {completed.stderr}"
        )
    outputs = [json.loads(line) for line in completed.stdout.splitlines() if line]
    if len(outputs) != len(cases):
        raise AssertionError("auditor output count disagrees with input count")
    return outputs


def run_one(executable: Path, payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(executable)],
        input=json.dumps(payload, separators=(",", ":")),
        text=True,
        capture_output=True,
        check=False,
    )


class IndependentCppRawAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for executable in (GCC_AUDITOR, CLANG_AUDITOR):
            if not executable.is_file():
                raise unittest.SkipTest(f"missing compiled auditor {executable}")
        cls.small = exhaustive_rows_through_four()
        cls.n19 = deterministic_n19_rows()
        cls.cases = cls.small + cls.n19
        cls.references = [python_reference(rows) for rows in cls.cases]
        cls.gcc = run_batch(GCC_AUDITOR, cls.cases)
        cls.clang = run_batch(CLANG_AUDITOR, cls.cases)

    def test_01_exhaustive_case_count(self) -> None:
        self.assertEqual(len(self.small), 1 + 3 + 27 + 729)

    def test_02_gcc_matches_python_set_oracle(self) -> None:
        self.assertEqual(self.gcc, self.references)

    def test_03_clang_matches_python_set_oracle(self) -> None:
        self.assertEqual(self.clang, self.references)

    def test_04_two_compilers_are_byte_semantic_equivalent(self) -> None:
        self.assertEqual(self.gcc, self.clang)

    def test_05_energy_zero_equivalence_per_row_and_graph(self) -> None:
        for audit in self.gcc:
            self.assertEqual(audit["exact_objective"] == 0, audit["all_strict"])
            self.assertEqual(audit["witness_energy"] == 0, audit["all_strict"])
            for row in audit["rows"]:
                self.assertEqual(row["exact_penalty"] == 0, row["strict"])
                self.assertEqual(row["witness_energy"] == 0, row["strict"])

    def test_06_n19_calibration_covers_every_positive_q(self) -> None:
        audits = self.gcc[len(self.small):]
        self.assertEqual([item["missing_pairs"] for item in audits], list(range(1, 20)))
        self.assertTrue(all(item["in_n19_domain"] for item in audits))
        self.assertTrue(all(item["minimum_outdegree"] >= 8 for item in audits))

    def test_07_redundant_witness_fixture(self) -> None:
        rows = ((1, 2), (3, 4), (3, 4), (), ())
        audit = run_batch(GCC_AUDITOR, [rows])[0]
        row = audit["rows"][0]
        self.assertEqual(row["d1"], 2)
        self.assertEqual(row["d2"], 2)
        self.assertEqual(row["witness_counts"][3:5], [2, 2])
        self.assertEqual(row["witness_mass"], 6)
        self.assertEqual(row["exact_penalty"], 1)
        self.assertEqual(row["witness_energy"], 2)

    def test_08_directed_cycle_is_nonstrict_equality(self) -> None:
        audit = run_batch(GCC_AUDITOR, [((1,), (2,), (0,))])[0]
        self.assertEqual(
            [(row["d1"], row["d2"], row["strict"]) for row in audit["rows"]],
            [(1, 1, False)] * 3,
        )
        self.assertEqual(audit["exact_objective"], 3)

    def test_09_loop_is_rejected(self) -> None:
        completed = run_one(GCC_AUDITOR, {"n": 1, "out_neighbors": [[0]]})
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("loop", completed.stderr)

    def test_10_digon_is_rejected(self) -> None:
        completed = run_one(
            GCC_AUDITOR, {"n": 2, "out_neighbors": [[1], [0]]}
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("digon", completed.stderr)

    def test_11_duplicate_and_unsorted_rows_are_rejected(self) -> None:
        for row in ([1, 1], [2, 1]):
            completed = run_one(
                GCC_AUDITOR, {"n": 3, "out_neighbors": [row, [], []]}
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("sorted and unique", completed.stderr)

    def test_12_schema_errors_are_rejected(self) -> None:
        mutants = (
            {"out_neighbors": [[]]},
            {"n": 1, "out_neighbors": [[]], "extra": 0},
            {"n": 2, "out_neighbors": [[]]},
            {"n": 64, "out_neighbors": []},
        )
        for payload in mutants:
            completed = run_one(GCC_AUDITOR, payload)
            self.assertNotEqual(completed.returncode, 0)

    def test_13_low_degree_n19_is_not_in_domain(self) -> None:
        rows = tuple(() for _ in range(19))
        audit = run_batch(GCC_AUDITOR, [rows])[0]
        self.assertFalse(audit["in_n19_domain"])
        self.assertFalse(audit["accepted_counterexample"])
        self.assertEqual(audit["status"], "VERIFIED_NONHIT")

    def test_14_calibration_outputs_no_counterexample_claim(self) -> None:
        self.assertTrue(all(not audit["accepted_counterexample"] for audit in self.gcc))
        self.assertTrue(all(audit["status"] == "VERIFIED_NONHIT" for audit in self.gcc))


if __name__ == "__main__":
    unittest.main()
