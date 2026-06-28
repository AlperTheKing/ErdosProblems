"""Exact superharmonic-vector diagnostic for GCD.

H = L_omega + diag(N-T) is a symmetric Z-matrix.  If, on every active omega
component, there is a strictly positive vector x with Hx >= 0, then H is a
PSD M-matrix on that component.  Vertices outside omega traffic have only the
positive diagonal N.

This script tests the natural candidates x=S and x=T exactly.
"""

from __future__ import annotations

import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, is_triangle_free, mycielski, union_disjoint
from _gcd import build_H, run_gmin, test_side
from _h import GENG, dec, loads
from _superphi import blow


def S_vec(info):
    n = info["n"]
    S = [F(0) for _ in range(n)]
    for f in info["M"]:
        ps = info["cyc"][f]
        k = len(ps)
        for p in ps:
            for v in p:
                S[v] += F(1, k)
    return S


def matvec(H, x):
    n = len(x)
    return [sum(H[i][j] * x[j] for j in range(n)) for i in range(n)]


def check_info(info):
    H, T, _N = build_H(info["adj"], info["side"], info["n"])
    S = S_vec(info)
    HS = matvec(H, S)
    HT = matvec(H, T)
    return min(HS), min(HT), sum(1 for v in S if v == 0), sum(1 for v in S if v > 0)


def check_loads(label, n, E):
    info = loads(n, E)
    if info is None or not info["M"]:
        return None
    return label, info["n"], check_info(info)


def main():
    named = []
    c5 = (5, Cn(5))
    n1, e1 = mycielski(*c5)
    n2, e2 = mycielski(n1, e1)
    m1, f1 = mycielski(7, Cn(7))
    named += [("Grotzsch", n1, e1), ("MycGrotzsch", n2, e2), ("MycC7", m1, f1)]
    for g6 in ["G?bF`w", "I?BD@g]Qo", "I?ABCc]}?", "J??CE?{{?]?"]:
        n, E = dec(g6)
        named.append((g6, n, E))
    for g6, t in [("J???E?pNu\\?", 2), ("I?BD@g]Qo", 2), ("G?bF`w", 3)]:
        n, E = blow(g6, t)
        named.append((f"{g6}[{t}]", n, E))

    print("=== H*S and H*T exact nonnegativity ===")
    for label, n, E in named:
        row = check_loads(label, n, E)
        if row is None:
            continue
        _label, nn, (mins, mint, zc, pc) = row
        print(f"  {label} N={nn}: minHS={mins} ({float(mins):+.6g}) minHT={mint} ({float(mint):+.6g}) Spos={pc} Szero={zc}")

    print("--- glued-island loads cuts ---")
    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    bad = 0
    total = 0
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, E = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    E = E + [(i, iN + j)]
                if n > 22 or not is_triangle_free(n, E):
                    continue
                info = loads(n, E)
                if info is None or not info["M"]:
                    continue
                mins, mint, _zc, _pc = check_info(info)
                total += 1
                if mins < 0 or mint < 0:
                    bad += 1
                    print("BAD glued", iN, gN, br, mins, mint)
    print(f"  glued loads cuts: total={total} bad={bad}")

    print("--- census loads cuts N=7..10 ---")
    for nn in range(7, 11):
        bad = 0
        total = 0
        worst = None
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            info = loads(n, E)
            if info is None or not info["M"]:
                continue
            mins, mint, _zc, _pc = check_info(info)
            total += 1
            if worst is None or mins < worst[0]:
                worst = (mins, g6)
            if mins < 0 or mint < 0:
                bad += 1
                print("BAD census", nn, g6, mins, mint)
        print(f"  N={nn}: total={total} bad={bad} worstHS={worst[0] if worst else None}@{worst[1] if worst else None}")


if __name__ == "__main__":
    main()
