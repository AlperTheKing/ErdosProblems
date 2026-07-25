from __future__ import annotations

import itertools
import pathlib
import subprocess
import sys

from pysat.formula import CNF
from pysat.solvers import Solver


ROOT = pathlib.Path(__file__).resolve().parent
GEN = ROOT / "generate_d2c_cnf.exe"
VERIFY = ROOT / "verify_b.exe"


def assumptions_for(edges: set[tuple[int, int]]) -> list[int]:
    pairs = list(itertools.combinations(range(25), 2))
    return [i + 1 if p in edges else -(i + 1) for i, p in enumerate(pairs)]


def query(path: pathlib.Path, assumptions: list[int]) -> bool:
    formula = CNF(from_file=str(path))
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        return solver.solve(assumptions=assumptions)


def write_matrix(path: pathlib.Path, edges: set[tuple[int, int]]) -> None:
    rows = [["0"] * 25 for _ in range(25)]
    for u, v in edges:
        rows[u][v] = rows[v][u] = "1"
    path.write_text(
        "N 25\n" + "\n".join("".join(row) for row in rows) + "\n",
        encoding="ascii",
    )


def verify_matrix(path: pathlib.Path, minimum: int, expected: int) -> None:
    p = subprocess.run(
        [
            str(VERIFY),
            "--input",
            str(path),
            "--expect-n",
            "25",
            "--min-edges",
            str(minimum),
            "--quiet",
        ],
        text=True,
        capture_output=True,
    )
    if p.returncode != expected:
        raise RuntimeError(
            f"verifier returned {p.returncode}, expected {expected}: {p.stderr}"
        )


def main() -> int:
    k156 = ROOT / "calibration" / "target_k156.cnf"
    p = subprocess.run(
        [
            str(GEN),
            "--n",
            "25",
            "--min-edges",
            "156",
            "--output",
            str(k156),
        ],
        text=True,
        capture_output=True,
    )
    if p.returncode:
        raise RuntimeError(p.stderr)
    k157 = ROOT / "d2c_n25_m157.cnf"
    if not k157.exists():
        raise RuntimeError("generate d2c_n25_m157.cnf first")

    bipartite = {
        (u, v)
        for u in range(12)
        for v in range(12, 25)
    }
    plus_chord = set(bipartite)
    plus_chord.add((0, 1))

    tests = [
        ("K12,13 at threshold 156", k156, bipartite, True),
        ("K12,13 at threshold 157", k157, bipartite, False),
        ("K12,13 plus one chord at threshold 157", k157, plus_chord, False),
    ]
    for name, path, graph, expected in tests:
        actual = query(path, assumptions_for(graph))
        if actual != expected:
            raise RuntimeError(f"{name}: expected {expected}, got {actual}")
        print(f"TARGET_BOUNDARY_AUDIT {name} SAT={actual}")
    matrix = ROOT / "calibration" / "target_k1213.matrix"
    chord_matrix = ROOT / "calibration" / "target_k1213_plus_chord.matrix"
    write_matrix(matrix, bipartite)
    write_matrix(chord_matrix, plus_chord)
    verify_matrix(matrix, 156, 0)
    verify_matrix(chord_matrix, 157, 1)
    matrix.unlink()
    chord_matrix.unlink()
    print("TARGET_BOUNDARY_VERIFIER_PASS K12,13 accepted; chord mutant rejected")
    k156.unlink()
    print("TARGET_BOUNDARY_AUDIT_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
