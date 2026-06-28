"""Logical-strength check: is C-alltie strictly WEAKER than NO-Q-ONLY for proving cond(1)?
NO-Q-ONLY: no bad-edge-carrying K-component lies entirely in Q.
C-alltie only constrains components that contain a SATURATED vertex with a DEAD B-neighbor.
A Q-only component could (a priori) have NO saturated vertex, or a saturated vertex with NO dead
B-neighbor -- then C-alltie says nothing, but such a component could still break cond(1) (if critical).

So for cond(1) we actually need SAT-ZMU-CONN = A-alltie + C-alltie (A-alltie supplies the dead nb).
Check: A-alltie (zero-mu edge uv, T(u)=N => T(v)=0) -- is the OTHER endpoint of a zero-mu saturated
edge ALWAYS dead? Verify A-alltie exactly over census all gamma-min cuts so the A+C => SAT-ZMU-CONN
chain is on solid ground. Also confirm: a CRITICAL Q-only component (T==N everywhere) -- its boundary
B-edge uv has u saturated; is the other endpoint v dead? (A-alltie applied at the boundary.)
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def all_gmin(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj); cand = []
    for side in cuts:
        if not Bconn(n, adj, side): continue
        Mloc = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not Mloc: continue
        G = 0; ok = True
        for (u, v) in Mloc:
            d = bdist_restr(adj, side, u, v)
            if d < 0: ok = False; break
            G += (d+1)**2
        if ok: cand.append((side, G))
    if not cand: return adj, []
    gm = min(G for _, G in cand)
    return adj, [s for s, G in cand if G == gm]

def Acheck(n, E):
    adj, sides = all_gmin(n, E)
    aviol = 0; acase = 0
    for side in sides:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st; N = n
        for e, val in mu.items():
            if val != 0: continue
            u, v = e
            for (a, b) in ((u, v), (v, u)):
                if T[a] == N:
                    acase += 1
                    if T[b] != 0: aviol += 1
    return acase, aviol

if __name__ == "__main__":
    print("=== A-alltie exact check (other endpoint of saturated zero-mu edge is dead) ===")
    for nn in range(7, 12):
        og = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        tc = 0; tv = 0
        for g6 in og:
            n, E = dec(g6)
            c, v = Acheck(n, E)
            tc += c; tv += v
        print(f"  N={nn} (all gamma-min cuts): A-alltie cases(zero-mu edge w/ saturated end)={tc} violations={tv}", flush=True)
