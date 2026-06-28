"""Find NON-VACUOUS C-alltie instances: across ALL gamma-min cuts of the census + constructions,
find a config with a saturated v (T=N) B-adjacent to a dead z (T=0), O nonempty.
Report the FULL local structure so we can understand the mechanism (or confirm vacuity).
Also test: does ANY config (any cut, not just gamma-min) realize the hypothesis?
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def cases_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    N = n
    O = set(v for v in range(N) if T[v] > N)
    if not O: return ('Oempty', [])
    comp, find = kcomponents(n, cyc)
    res = []
    for v in range(N):
        if T[v] != N: continue
        for z in adj[v]:
            if side[z] != side[v] and T[z] == 0:
                Cv = comp[find(v)]
                res.append((v, z, bool(Cv & O), sorted(Cv), sorted(O)))
    return ('ok', res)

def all_gmin_cuts(n, E):
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
    if not cand: return []
    gm = min(G for _, G in cand)
    return [(adj, side) for side, G in cand if G == gm]

def run_census(Nmax, Nmin=7, allcuts=True):
    found = 0
    nonvac_graphs = []
    for nn in range(Nmin, Nmax+1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        ncases = 0; viol = 0; first_nonvac = None
        for g6 in out:
            n, E = dec(g6)
            if allcuts:
                cuts = all_gmin_cuts(n, E)
            else:
                info = loads(n, E)
                if info is None: continue
                cuts = [(info['adj'], info['side'])]
            for adj, side in cuts:
                r = cases_side(n, adj, side)
                if r is None or r[0] != 'ok': continue
                for (v, z, meets, Cv, O) in r[1]:
                    ncases += 1
                    if first_nonvac is None: first_nonvac = (g6, v, z, meets)
                    if not meets: viol += 1
        print(f"  N={nn} (allcuts={allcuts}): non-vacuous C-alltie cases={ncases} viol={viol}"
              + (f"  FIRST {first_nonvac}" if first_nonvac else ""), flush=True)
        found += ncases
    print(f"TOTAL non-vacuous cases={found}")

if __name__ == "__main__":
    print("=== Searching for NON-VACUOUS C-alltie instances over ALL gamma-min cuts ===")
    run_census(11, 7, allcuts=True)
