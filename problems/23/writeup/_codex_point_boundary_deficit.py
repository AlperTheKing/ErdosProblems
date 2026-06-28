"""Probe pointwise boundary-deficit strengthening.

For a full K-component C with C∩O=empty, test whether every v in C satisfies

    T(v) + deg_B(v, V\\C) <= N.

This implies the component boundary-deficit lemma by summing over v in C.
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
    hasO = [False] * nc
    for o in O:
        hasO[comp[o]] = True
    outdeg = [0] * n
    for a, b in info["Bset"]:
        if comp[a] != comp[b]:
            outdeg[a] += 1
            outdeg[b] += 1
    bad = []
    for v in range(n):
        if not hasO[comp[v]]:
            margin = F(N) - T[v] - outdeg[v]
            if margin < 0:
                bad.append((v, comp[v], T[v], outdeg[v], margin))
    return bad


if __name__ == "__main__":
    print("=== point boundary-deficit: no-O component vertex v => T[v]+B_outdeg[v] <= N ===")
    for nn in range(5, 12):
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
            for row in check(info):
                viol += 1
                if worst is None or row[-1] < worst[-1]:
                    worst = (g6,) + row
        msg = f"  N={nn}: cfg={cfg} violations={viol}"
        if worst:
            g6, v, c, T, outdeg, margin = worst
            msg += f" worst @{g6} v={v} comp={c} T={T} Bout={outdeg} margin={margin}"
        print(msg, flush=True)
