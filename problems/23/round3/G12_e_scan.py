"""G12: exhaustive scan over connected triangle-free graphs (nauty geng -tc)

For every graph it computes
  bip(G)                     exact (bitmask maxcut)
  nu*(G)                     LP over ALL odd cycles (float HiGHS; candidates re-checked exactly)
  M1 = min_v e(G-N(v))       exact
  M2 = |E| - max_{I ind} sum_{v in I} d(v)   exact
and reports
  (i) any graph with bip > nu*      -> integrality gap witness
  (ii) max of bip/N^2, nu*/N^2, M1/N^2, M2/N^2
  (iii) validation that bip <= M1 and bip <= M2 always (the covering theorems)

Usage:  python G12_e_scan.py <nmin> <nmax>
"""
import subprocess
import sys
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import G12_core as C

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def bip_fast(n, E):
    nbr = [0] * n
    for u, v in E:
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u
    m = len(E)
    best = m
    full = (1 << n) - 1
    for S in range(1 << (n - 1)):
        cross = 0
        T = full ^ S
        s = S
        while s:
            b = s & -s
            u = b.bit_length() - 1
            cross += bin(nbr[u] & T).count("1")
            s ^= b
        if m - cross < best:
            best = m - cross
            if best == 0:
                break
    return best


def mwis_degree(n, E):
    """max over independent sets I of sum_{v in I} d(v); exact branch and bound."""
    d = [0] * n
    A = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
        A[u] |= 1 << v
        A[v] |= 1 << u
    best = [0]

    def rec(avail, cur):
        if avail == 0:
            if cur > best[0]:
                best[0] = cur
            return
        bd = cur
        s = avail
        while s:
            b = s & -s
            bd += d[b.bit_length() - 1]
            s ^= b
        if bd <= best[0]:
            return
        # branch on the max-degree available vertex
        s = avail
        bv, bdeg = -1, -1
        while s:
            b = s & -s
            v = b.bit_length() - 1
            if d[v] > bdeg:
                bdeg, bv = d[v], v
            s ^= b
        rec(avail & ~A[bv] & ~(1 << bv), cur + d[bv])
        rec(avail & ~(1 << bv), cur)
    rec((1 << n) - 1, 0)
    return best[0]


def m1(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return min(sum(1 for a, b in E if a not in A[v] and b not in A[v]) for v in range(n))


def nu_float(n, E, cycs):
    """LP: max 1^T y s.t. A y <= 1, y >= 0, over the given odd cycles."""
    if not cycs:
        return 0.0
    m = len(E)
    A = np.zeros((m, len(cycs)))
    for j, Cc in enumerate(cycs):
        for e in Cc:
            A[e, j] = 1.0
    res = linprog(c=-np.ones(len(cycs)), A_ub=A, b_ub=np.ones(m),
                  bounds=(0, None), method="highs")
    return -res.fun


def main():
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    for n in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True)
        gs = [ln.strip() for ln in out.stdout.split("\n") if ln.strip()]
        best = dict(bip=(0, None), nu=(0.0, None), M1=(0, None), M2=(0, None))
        gapwit = []
        viol = []
        cnt = 0
        for g6 in gs:
            nn, E = C.graph6_to_edges(g6)
            b = bip_fast(nn, E)
            cnt += 1
            if b == 0:
                continue
            cycs = C.odd_cycles(nn, E)
            nu = nu_float(nn, E, cycs)
            a1 = m1(nn, E)
            a2 = len(E) - mwis_degree(nn, E)
            if b - nu > 1e-6:
                gapwit.append((g6, b, nu))
            if b > a1 or b > a2:
                viol.append((g6, b, a1, a2))
            for key, val in (("bip", b), ("nu", nu), ("M1", a1), ("M2", a2)):
                if val / (nn * nn) > best[key][0] / (nn * nn) if best[key][1] else True:
                    pass
            if b / (nn * nn) > (best["bip"][0] / (nn * nn) if best["bip"][1] else -1):
                best["bip"] = (b, g6)
            if nu / (nn * nn) > (best["nu"][0] / (nn * nn) if best["nu"][1] else -1):
                best["nu"] = (nu, g6)
            if a1 / (nn * nn) > (best["M1"][0] / (nn * nn) if best["M1"][1] else -1):
                best["M1"] = (a1, g6)
            if a2 / (nn * nn) > (best["M2"][0] / (nn * nn) if best["M2"][1] else -1):
                best["M2"] = (a2, g6)
        print(f"n={n}: {cnt} connected triangle-free graphs", flush=True)
        print(f"   max bip = {best['bip'][0]} ({best['bip'][1]})  bip/N^2 = "
              f"{F(best['bip'][0], n*n)} = {best['bip'][0]/(n*n):.6f}   N^2/25 = {F(n*n,25)}", flush=True)
        print(f"   max nu* = {best['nu'][0]:.6f} ({best['nu'][1]})  nu*/N^2 = {best['nu'][0]/(n*n):.6f}", flush=True)
        print(f"   max M1  = {best['M1'][0]} ({best['M1'][1]})  M1/N^2 = {F(best['M1'][0], n*n)}"
              f" = {best['M1'][0]/(n*n):.6f}", flush=True)
        print(f"   max M2  = {best['M2'][0]} ({best['M2'][1]})  M2/N^2 = {F(best['M2'][0], n*n)}"
              f" = {best['M2'][0]/(n*n):.6f}", flush=True)
        print(f"   covering-theorem violations (bip > M1 or bip > M2): {len(viol)}", flush=True)
        print(f"   integrality gap witnesses (bip > nu*): {len(gapwit)}", flush=True)
        for g6, b, nu in gapwit[:20]:
            print(f"       {g6} bip={b} nu*~{nu:.6f}", flush=True)


if __name__ == "__main__":
    main()
