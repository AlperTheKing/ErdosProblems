#!/usr/bin/env python3
"""Build and independently calibrate the C++ bitset SSNC verifier."""

from __future__ import annotations

import json
import random
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "verify_bitset.cpp"
FIXTURES = HERE / "fixtures" / "bitset"


def run(command: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, capture_output=True, text=True)


def invoke(binary: Path, certificate: Path) -> tuple[int, str, dict]:
    result = run([str(binary), str(certificate)])
    stdout = result.stdout.strip()
    if result.stderr:
        raise AssertionError(f"unexpected stderr for {certificate.name}: {result.stderr!r}")
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"non-JSON stdout for {certificate.name}: {stdout!r}") from exc
    return result.returncode, stdout, payload


def scalar_ledger(rows: list[list[int]]) -> tuple[list[dict], list[int]]:
    """Independent set-based oracle; no bit operations or verifier code reuse."""
    ledgers: list[dict] = []
    failing: list[int] = []
    for vertex, row in enumerate(rows):
        first = set(row)
        reachable_in_two: set[int] = set()
        for middle in first:
            reachable_in_two.update(rows[middle])
        second_new = sorted(reachable_in_two - first - {vertex})
        strict = len(second_new) < len(row)
        if not strict:
            failing.append(vertex)
        ledgers.append(
            {
                "vertex": vertex,
                "n1": row,
                "d1": len(row),
                "n2_new": second_new,
                "d2": len(second_new),
                "strict_d2_lt_d1": strict,
            }
        )
    return ledgers, failing


def check_fixture(binary: Path, name: str, expected_exit: int, expected_status: str) -> tuple[str, dict]:
    code, stdout, payload = invoke(binary, FIXTURES / name)
    assert code == expected_exit, (name, code, stdout)
    assert payload["status"] == expected_status, (name, payload)
    return stdout, payload


def random_oriented_rows(rng: random.Random, n: int) -> list[list[int]]:
    rows: list[list[int]] = [[] for _ in range(n)]
    for left in range(n):
        for right in range(left + 1, n):
            choice = rng.randrange(3)
            if choice == 1:
                rows[left].append(right)
            elif choice == 2:
                rows[right].append(left)
    return rows


def main() -> int:
    compiler = sys.argv[1] if len(sys.argv) > 1 else "g++"
    temp_root = HERE / "bitset_test_build"
    temp_root.mkdir(exist_ok=True)
    with nullcontext(str(temp_root)) as temp_name:
        temp = Path(temp_name)
        binary = temp / "verify_bitset.exe"
        build = [
            compiler,
            "-std=c++20",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            str(SOURCE),
            "-o",
            str(binary),
        ]
        print("BUILD:", " ".join(build))
        built = run(build)
        if built.stdout:
            print(built.stdout, end="")
        if built.stderr:
            print(built.stderr, end="", file=sys.stderr)
        if built.returncode != 0:
            return built.returncode
        print("BUILD PASS")

        cycle_stdout, cycle = check_fixture(
            binary, "cycle3.json", 1, "VALID_GRAPH_NOT_COUNTEREXAMPLE"
        )
        assert [entry["d1"] for entry in cycle["per_vertex"]] == [1, 1, 1]
        assert [entry["d2"] for entry in cycle["per_vertex"]] == [1, 1, 1]
        assert cycle["failing_vertices"] == [0, 1, 2]
        print("FIXTURE cycle3 PASS:", cycle_stdout)

        tournament_stdout, tournament = check_fixture(
            binary, "tournament_transitive3.json", 1, "VALID_GRAPH_NOT_COUNTEREXAMPLE"
        )
        assert tournament["failing_vertices"] == [2]
        print("FIXTURE tournament_transitive3 PASS:", tournament_stdout)

        for name, needle in [
            ("loop.json", "loop"),
            ("digon.json", "digon"),
            ("unsorted.json", "strictly increasing"),
            ("duplicate.json", "strictly increasing"),
            ("malformed.json", "expected"),
            ("extra_key.json", "unknown top-level key"),
        ]:
            stdout, payload = check_fixture(binary, name, 2, "INVALID_CERTIFICATE")
            assert any(needle in message for message in payload["errors"]), (name, payload)
            print(f"FIXTURE {name} PASS:", stdout)

        first_code, first_stdout, _ = invoke(binary, FIXTURES / "cycle3.json")
        second_code, second_stdout, _ = invoke(binary, FIXTURES / "cycle3.json")
        assert first_code == second_code == 1
        assert first_stdout == second_stdout
        print("DETERMINISM PASS")

        rng = random.Random(0x5E1A0)
        random_checks = 0
        for n in range(1, 13):
            for sample in range(8):
                rows = random_oriented_rows(rng, n)
                expected_ledger, expected_failing = scalar_ledger(rows)
                certificate = temp / f"random-n{n}-s{sample}.json"
                certificate.write_text(
                    json.dumps({"n": n, "out_neighbors": rows}, separators=(",", ":")),
                    encoding="ascii",
                )
                code, _, payload = invoke(binary, certificate)
                expected_code = 0 if not expected_failing else 1
                expected_status = (
                    "VERIFIED_COUNTEREXAMPLE"
                    if expected_code == 0
                    else "VALID_GRAPH_NOT_COUNTEREXAMPLE"
                )
                assert code == expected_code, (n, sample, code, payload)
                assert payload["status"] == expected_status
                assert payload["n"] == n
                assert payload["per_vertex"] == expected_ledger
                assert payload["failing_vertices"] == expected_failing
                assert payload["errors"] == []
                random_checks += 1
        print(f"RANDOM ORACLE CROSSCHECK PASS: {random_checks}/96")
        print("ALL TESTS PASS: 105 checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
