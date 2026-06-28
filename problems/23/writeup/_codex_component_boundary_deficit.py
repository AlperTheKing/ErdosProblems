"""Codex probe: boundary-deficit law for K-components.

Candidate:
  If a K-component C contains no overloaded vertex, then

      N*|C| - sum_{v in C} T(v) >= delta_B(C).

Since B is connected, any proper load-bearing C has delta_B(C)>0. Thus this
would rule out a critical Q-only component, whose deficit is 0.
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
    Oset = set(O)
    rows = []
    for c in range(nc):
        C = [v for v in range(n) if comp[v] == c]
        Cset = set(C)
        hasO = bool(Cset & Oset)
        mass = sum(T[v] for v in C)
        deficit = F(N * len(C)) - mass
        dB = sum(1 for a, b in info["Bset"] if (a in Cset) != (b in Cset))
        meets = any(T[v] > 0 for v in C)
        rows.append((hasO, meets, C, deficit, dB))
    bad = [row for row in rows if (not row[0]) and row[3] < row[4]]
    return bad, rows


def run_census(nmin=5, nmax=11):
    print("=== component boundary-deficit: no-O C => N|C|-sum_C T >= delta_B(C) ===")
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
            for hasO, meets, C, deficit, dB in bad:
                viol += 1
                gap = deficit - dB
                if worst is None or gap < worst[0]:
                    worst = (gap, g6, C, deficit, dB, meets)
        msg = f"  N={nn}: cfg={cfg} violations={viol}"
        if worst:
            gap, g6, C, deficit, dB, meets = worst
            msg += f" worst_gap={gap} ({float(gap):.4f}) @{g6} C={C} deficit={deficit} dB={dB} meets={meets}"
        print(msg, flush=True)


if __name__ == "__main__":
    run_census()
