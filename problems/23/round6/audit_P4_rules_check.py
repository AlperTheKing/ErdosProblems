"""audit_P4_rules_check — exact Python evaluation of P4's surviving suggestion

     R(mu) = min( min over arcs of length EXACTLY 1/2 , min over arcs of length EXACTLY 1/3 )

on the nine recorded witnesses and on W8/W9/W10, and cross-validation of audit_P4_rules.cpp.

The window sizes realisable by an arc of length exactly L on the grid Z_M are floor(L*M) and
ceil(L*M) (half-open arc), plus L*M-1 and L*M+1 when L*M is an integer (open / closed arc; the
closed 1/3-arc is still independent because endpoints at distance exactly 1/3 are NOT adjacent).
"""
import sys
import os
import subprocess
from fractions import Fraction as F

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "round5")))
from claude_witness_regression import WITNESSES  # noqa: E402
from audit_P4_core import adj_matrix, normalise, mono, arcbound, psi_bruteforce  # noqa: E402

ONE25 = F(1, 25)


def sizes_half(M):
    return sorted({M // 2} if M % 2 == 0 else {M // 2, M // 2 + 1})


def sizes_third(M):
    if M % 3 == 0:
        return sorted({M // 3 - 1, M // 3, M // 3 + 1})
    return sorted({M // 3, M // 3 + 1})


def fam_min(x, adj, M, sizes):
    best = None
    for i in range(M):
        for l in sizes:
            if l <= 0 or l >= M:
                continue
            inA = [False] * M
            for t in range(l):
                inA[(i + t) % M] = True
            v = mono(x, adj, inA)
            if best is None or v < best:
                best = v
    return best


EXTRA = [
    ("W8  (P4)", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    ("W9  (P4)", 20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
    ("W10 (P4)", 20, [0, 5, 5, 0, 0, 0, 0, 6, 4, 5, 0, 0, 0, 0, 5, 4, 6, 0, 0, 0]),
]

if __name__ == "__main__":
    rows = [(n, m, w) for (n, m, w, _) in WITNESSES] + EXTRA
    print(f"{'witness':28s} {'half(exact)':>12s} {'third(exact)':>12s} {'R':>10s} "
          f"{'ARCBOUND':>10s} {'psi':>10s}  cpp-agrees")
    bad = []
    for name, m, w in rows:
        adj = adj_matrix(m)
        q = sum(w)
        x = normalise(w)
        h = fam_min(x, adj, m, sizes_half(m))
        t = fam_min(x, adj, m, sizes_third(m))
        R = min(h, t)
        ab = arcbound(x, adj, m)
        ps = psi_bruteforce(x, adj, m)
        out = subprocess.run(["./audit_P4_rules.exe", "eval", str(m), str(q), "ht",
                              ",".join(map(str, w))], capture_output=True, text=True).stdout
        cppval = int(out.split("min over family =")[1].split("/")[0].strip())
        agree = F(cppval, q * q) == R
        print(f"{name:28s} {float(h):12.6f} {float(t):12.6f} {float(R):10.6f} "
              f"{float(ab):10.6f} {float(ps):10.6f}  {agree}"
              + ("   <== R > 1/25 : RULE REFUTED" if R > ONE25 else ""))
        if not agree:
            bad.append(name)
        if R > ONE25:
            bad.append(name + " (rule violation)")
    print("\ncpp/python disagreements or rule violations:", bad or "none")
