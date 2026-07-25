from __future__ import annotations

import itertools
import pathlib
import subprocess
import sys

from pysat.formula import CNF
from pysat.solvers import Solver


ROOT = pathlib.Path(__file__).resolve().parent
GEN = ROOT / "generate_d2c_cnf.exe"
OUT = ROOT / "calibration"


def is_d2c(n: int, pairs: list[tuple[int, int]], mask: int) -> bool:
    a = [[False] * n for _ in range(n)]
    for i, (u, v) in enumerate(pairs):
        if (mask >> i) & 1:
            a[u][v] = a[v][u] = True
    if mask.bit_count() == n * (n - 1) // 2:
        return False
    for s in range(n):
        for t in range(s + 1, n):
            if a[s][t]:
                continue
            if not any(a[s][k] and a[k][t] for k in range(n)):
                return False
    for ei, (u, v) in enumerate(pairs):
        if not ((mask >> ei) & 1):
            continue
        has_witness = False
        for s in range(n):
            for t in range(s + 1, n):
                direct = a[s][t] and {s, t} != {u, v}
                if direct:
                    continue
                path2 = False
                for k in range(n):
                    if k == s or k == t:
                        continue
                    left = a[s][k] and {s, k} != {u, v}
                    right = a[k][t] and {k, t} != {u, v}
                    if left and right:
                        path2 = True
                        break
                if not path2:
                    has_witness = True
                    break
            if has_witness:
                break
        if not has_witness:
            return False
    return True


def audit(n: int, minimum: int) -> tuple[int, int]:
    pairs = list(itertools.combinations(range(n), 2))
    cnf_path = OUT / f"audit_n{n}_k{minimum}.cnf"
    p = subprocess.run(
        [
            str(GEN),
            "--n",
            str(n),
            "--min-edges",
            str(minimum),
            "--output",
            str(cnf_path),
        ],
        text=True,
        capture_output=True,
    )
    if p.returncode:
        raise RuntimeError(p.stderr)
    formula = CNF(from_file=str(cnf_path))
    sat_count = 0
    expected_count = 0
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for mask in range(1 << len(pairs)):
            expected = is_d2c(n, pairs, mask) and mask.bit_count() >= minimum
            assumptions = [
                i + 1 if ((mask >> i) & 1) else -(i + 1)
                for i in range(len(pairs))
            ]
            actual = solver.solve(assumptions=assumptions)
            if actual:
                sat_count += 1
            if expected:
                expected_count += 1
            if actual != expected:
                raise RuntimeError(
                    f"mismatch n={n} k={minimum} mask={mask} "
                    f"expected={expected} actual={actual}"
                )
    cnf_path.unlink()
    return sat_count, expected_count


def main() -> int:
    total_graphs = 0
    total_queries = 0
    for n in range(3, 7):
        m = n * (n - 1) // 2
        total_graphs += 1 << m
        for minimum in range(m + 1):
            actual, expected = audit(n, minimum)
            total_queries += 1 << m
            print(
                f"AUDITED n={n} min_edges={minimum} "
                f"sat_graphs={actual} expected_graphs={expected}"
            )
    print(
        f"EXHAUSTIVE_AUDIT_PASS orders=3..6 "
        f"distinct_graphs={total_graphs} sat_queries={total_queries}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
