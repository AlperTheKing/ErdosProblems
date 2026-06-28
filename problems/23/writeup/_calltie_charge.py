"""Discharging-pattern probe at a saturated v with dead B-neighbor z.
Goal: find a LOCAL certificate that forces v's K-component to meet O, using:
  - handshake: sum_{e at v,B} mu(e) = 2N - D(v)
  - per-edge mu(v,w) for B-neighbors w of v
  - load T(w) and 'charge' N-T(w) at each B-neighbor
  - the bad edges f through v: their endpoints, ell, and where their geodesics go.

Conjecture to test (direct transport):
  (T1) A saturated v with a dead B-neighbor is an ENDPOINT of at least one bad edge f.
       [intuition: if v were purely interior, geodesics pass straight through; a dead neighbor
        means v's geodesics can't use that side, concentrating betweenness.]
  (T2) v is the endpoint of a bad edge f whose OTHER vertices include a vertex of higher load,
       and chaining reaches O.
Dump exact data for ALL non-vacuous cases (census N=11 all cuts + witness).
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
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

def cases(n, E, verbose=False):
    adj, sides = all_gmin(n, E)
    out = []
    for side in sides:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        N = n
        O = set(v for v in range(N) if T[v] > N)
        if not O: continue
        comp, find = kcomponents(n, cyc)
        for v in range(N):
            if T[v] != N: continue
            deadnb = [z for z in adj[v] if side[z] != side[v] and T[z] == 0]
            if not deadnb: continue
            endpt = [f for f in M if v in f]
            interior_only = (len(endpt) == 0)
            out.append(dict(v=v, deadnb=deadnb, endpt=endpt, interior_only=interior_only,
                            D=sum(ell[f] for f in endpt)))
    return out

def run_census():
    total = 0; interior_only = 0; with_endpt = 0
    minD = None
    for nn in range(7, 12):
        og = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        ncase = 0; nint = 0
        for g6 in og:
            n, E = dec(g6)
            cs = cases(n, E)
            for c in cs:
                ncase += 1; total += 1
                if c['interior_only']: nint += 1; interior_only += 1
                else: with_endpt += 1
        print(f"  N={nn}: cases={ncase} interior-only(v NOT endpoint of any bad edge)={nint}", flush=True)
    print(f"TOTAL cases={total}: v-is-endpoint-of-some-bad-edge={with_endpt}  v-interior-only={interior_only}")
    print(f"  => (T1) 'sat v with dead nb is a bad-edge ENDPOINT' holds for ALL? {interior_only==0}")

if __name__ == "__main__":
    print("=== Discharging probe: is a saturated v with a dead B-neighbor always a bad-edge ENDPOINT? ===")
    run_census()
