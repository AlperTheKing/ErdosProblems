from __future__ import annotations

import pathlib
import subprocess
import sys

from pysat.formula import CNF
from pysat.solvers import Solver


ROOT = pathlib.Path(__file__).resolve().parent
GEN = ROOT / "generate_d2c_cnf.exe"
VERIFY = ROOT / "verify_b.exe"
DECODE = ROOT / "decode_model.exe"
CASES = ROOT / "calibration"


def run(cmd: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != expected:
        raise RuntimeError(
            f"command returned {p.returncode}, expected {expected}: {cmd}\n"
            f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}"
        )
    return p


def solve_case(name: str, n: int, minimum: int, expected_sat: bool) -> None:
    pin = CASES / f"{name}.edges"
    cnf_path = CASES / f"{name}.cnf"
    map_path = CASES / f"{name}.map"
    model_path = CASES / f"{name}.model"
    matrix_path = CASES / f"{name}.matrix"
    run(
        [
            str(GEN),
            "--n",
            str(n),
            "--min-edges",
            str(minimum),
            "--pin",
            str(pin),
            "--output",
            str(cnf_path),
            "--map",
            str(map_path),
        ]
    )
    formula = CNF(from_file=str(cnf_path))
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        sat = solver.solve()
        if sat != expected_sat:
            raise RuntimeError(f"{name}: SAT={sat}, expected {expected_sat}")
        if sat:
            model = solver.get_model()
            model_path.write_text(
                "s SATISFIABLE\nv " + " ".join(map(str, model)) + " 0\n",
                encoding="ascii",
            )
            run([str(DECODE), str(map_path), str(model_path), str(matrix_path)])
            run(
                [
                    str(VERIFY),
                    "--input",
                    str(matrix_path),
                    "--expect-n",
                    str(n),
                    "--min-edges",
                    str(minimum),
                    "--quiet",
                ]
            )
    print(f"CALIBRATED {name} SAT={sat} vars={formula.nv} clauses={len(formula.clauses)}")


def negative_verifier_mutants() -> None:
    for name, n, minimum in [
        ("k33_plus_chord", 6, 9),
        ("k33_missing_edge", 6, 8),
        ("asymmetric_matrix", 5, 0),
    ]:
        p = run(
            [
                str(VERIFY),
                "--input",
                str(CASES / f"{name}.matrix"),
                "--expect-n",
                str(n),
                "--min-edges",
                str(minimum),
                "--quiet",
            ],
            expected=1,
        )
        print(f"CALIBRATED verifier_reject {name}: {p.stderr.strip()}")


def main() -> int:
    solve_case("c4", 4, 4, True)
    solve_case("c5", 5, 5, True)
    solve_case("k33", 6, 9, True)
    solve_case("k4_minus_edge", 4, 5, False)
    solve_case("k33_plus_chord", 6, 10, False)
    solve_case("k33_missing_edge", 6, 8, False)
    negative_verifier_mutants()
    print("CALIBRATION_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
