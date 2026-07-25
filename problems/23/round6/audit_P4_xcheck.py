"""audit_P4_xcheck — cross-validate audit_P4_exhaust.cpp (integer, incremental) against the
slow exact Python arc enumerator on small (m,q), and against the recorded witnesses.
"""
import subprocess
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import adj_matrix, arcbound, normalise


def compositions(m, q):
    if m == 1:
        yield [q]
        return
    for v in range(q + 1):
        for rest in compositions(m - 1, q - v):
            yield [v] + rest


def py_scan(m, q):
    adj = adj_matrix(m)
    viol = eq = n = 0
    for w in compositions(m, q):
        n += 1
        x = [F(wi, q) for wi in w]
        ab = arcbound(x, adj, m)          # = (integer min) / q^2
        i = ab * q * q
        assert i.denominator == 1
        if 25 * int(i) > q * q:
            viol += 1
        elif 25 * int(i) == q * q:
            eq += 1
    return n, viol, eq


if __name__ == "__main__":
    for m, q in [(5, 10), (8, 8), (11, 6), (7, 7), (10, 6)]:
        n, viol, eq = py_scan(m, q)
        out = subprocess.run(["./audit_P4_exhaust.exe", str(m), str(q)],
                             capture_output=True, text=True).stdout.strip()
        print(f"  python: Gamma_{m} q={q}: weightings={n} violations={viol} equalities={eq}")
        print(f"  cpp   : {out}")
        assert f"weightings={n} " in out and f"violations(25*min>q^2)={viol}" in out \
            and f"equalities={eq}" in out, "MISMATCH between python and cpp"
    print("cross-check PASSED (python slow enumerator == C++ incremental enumerator)")
