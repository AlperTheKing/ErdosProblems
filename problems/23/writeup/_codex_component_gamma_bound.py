"""Codex probe: does every K-component satisfy a local Gamma bound?

For a K-component C (vertices connected by K[v,w]>0), all bad-edge intervals touching C
are contained in C. Test the candidate

    sum_{v in C} T(v) <= |C|^2

for every component C that meets a bad-edge support. If true, then a proper component
cannot be globally saturated at level N>|C|, which would prove NO-CRITICAL.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K


def comps(K):
    n = len(K)
    comp = [-1] * n
    cid = 0
    for s in range(n):
        if comp[s] != -1:
            continue
        comp[s] = cid
        st = [s]
        while st:
            u = st.pop()
            for v in range(n):
                if v != u and comp[v] == -1 and K[u][v] > 0:
                    comp[v] = cid
                    st.append(v)
        cid += 1
    return comp, cid


def check(info):
    K, T, O, Q, N, n = build_K(info)
    comp, nc = comps(K)
    bad = []
    rows = []
    for c in range(nc):
        C = [v for v in range(n) if comp[v] == c]
        mass = sum(T[v] for v in C)
        rhs = F(len(C) * len(C))
        meets = any(T[v] > 0 for v in C)
        if meets:
            rows.append((len(C), mass, rhs, C))
            if mass > rhs:
                bad.append((C, mass, rhs))
    return bad, rows


def run_census(nmin=5, nmax=11):
    print("=== component local bound: sum_C T <= |C|^2 ===")
    for nn in range(nmin, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        cfg = 0
        viol = 0
        worst = None
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            cfg += 1
            bad, rows = check(info)
            for C, mass, rhs in bad:
                viol += 1
                gap = mass - rhs
                if worst is None or gap > worst[0]:
                    worst = (gap, g6, C, mass, rhs)
        msg = f"  N={nn}: cfg={cfg} violations={viol}"
        if worst:
            gap, g6, C, mass, rhs = worst
            msg += f" worst_gap={gap} ({float(gap):.4f}) @{g6} C={C} mass={mass} rhs={rhs}"
        print(msg, flush=True)


if __name__ == "__main__":
    run_census()
