"""Test a weaker component deficit inequality.

For a full positive-K component C disjoint from O, define
  deficit(C)=N|C|-sum_{v in C}T(v).
Test whether
  deficit(C) >= #{B-boundary edges xy with x in C, T(x)=N}
(counting only saturated endpoints on the C side).

This is weaker than boundary-deficit >= full dB(C), but it still excludes a
critical Q-only component because then deficit=0 and every C-boundary endpoint
is saturated.
"""

from fractions import Fraction as F
import subprocess

from _h import GENG, dec, loads
from _cond1_proof import build_K


def k_components(K, n):
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s] or all(K[s][v] == 0 for v in range(n)):
            continue
        stack = [s]
        seen[s] = True
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in range(n):
                if not seen[v] and K[u][v] > 0:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps


def violations(info):
    K, T, O, Q, N, n = build_K(info)
    Oset = set(O)
    out = []
    for C in k_components(K, n):
        Cset = set(C)
        if Cset & Oset:
            continue
        deficit = F(N * len(C)) - sum(T[v] for v in C)
        sat_boundary = 0
        full_boundary = 0
        for a, b in info["Bset"]:
            if (a in Cset) ^ (b in Cset):
                full_boundary += 1
                cend = a if a in Cset else b
                if T[cend] == N:
                    sat_boundary += 1
        if deficit < sat_boundary:
            out.append((C, deficit, sat_boundary, full_boundary, [T[v] for v in C]))
    return out


def main():
    for N in range(7, 12):
        tested = 0
        comps = 0
        min_slack = None
        first = None
        for g6 in subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split():
            info = loads(*dec(g6))
            if info is None:
                continue
            bad = violations(info)
            tested += 1
            if bad:
                first = (g6, bad[0])
                break
        print(f"N={N}: tested={tested} first_violation={first}", flush=True)
        if first:
            return


if __name__ == "__main__":
    main()
