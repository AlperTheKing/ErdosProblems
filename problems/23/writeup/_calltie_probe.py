"""C-alltie probe. Statement (C-alltie):
   If O nonempty, T(z)=0, z B-adjacent to v with T(v)=N, then Kcomp(v) meets O.

We dissect the LOCAL structure to find the proof mechanism:
 - For a saturated v (T=N) B-adjacent to a dead z (T=0):
   * which bad edges f have v in supp(p_f)? (these define Kcomp(v))
   * is v an ENDPOINT of any bad edge? (D(v))
   * handshake: sum_{e at v, B} mu(e) = 2T(v)-D(v) = 2N - D(v)
   * Does some geodesic through v reach into O? i.e. does supp(p_f) for some f through v meet O?
 - Test the SHARPER claim: Kcomp(v) = the unique load-bearing K-component (= K|_{T>0} connected),
   and that component always meets O when O nonempty.
Exact Fraction.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K
from _satzmu_conn import struct_for_side, kcomponents

def probe_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    N = n
    O = set(v for v in range(N) if T[v] > N)
    if not O: return None
    comp, find = kcomponents(n, cyc)
    # support of each bad edge
    supp = {f: set(v for P in Ps for v in P) for f, Ps in cyc.items()}
    out = []
    for v in range(N):
        if T[v] != N: continue
        for z in adj[v]:
            if side[z] != side[v] and T[z] == 0:
                Cv = comp[find(v)]
                meets = bool(Cv & O)
                # bad edges through v
                through = [f for f in M if v in supp[f]]
                # is v an endpoint of any bad edge
                endpt = [f for f in M if v in f]
                # do any of v's through-edges have supp meeting O?
                f_to_O = [f for f in through if supp[f] & O]
                out.append(dict(v=v, z=z, Cv=sorted(Cv), meetsO=meets, O=sorted(O),
                                nthrough=len(through), endpt=len(endpt),
                                f_to_O=len(f_to_O), Cv_size=len(Cv)))
    return out

def run_census(Nmax, Nmin=7):
    total_cases = 0
    Cv_eq_loadcomp = 0   # Kcomp(v) == full load-bearing comp
    bad = 0
    for nn in range(Nmin, Nmax+1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        ncases = 0; nbad = 0
        for g6 in out:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None: continue
            r = probe_side(info['n'], info['adj'], info['side'])
            if r is None: continue
            for c in r:
                ncases += 1; total_cases += 1
                if not c['meetsO']:
                    nbad += 1; bad += 1
        print(f"  N={nn}: C-alltie cases (sat v ~ dead z)={ncases} viol={nbad}", flush=True)
    print(f"TOTAL cases={total_cases} violations={bad}")

if __name__ == "__main__":
    print("=== C-alltie local-structure probe (loads-cut) ===")
    # named witnesses with O nonempty
    for g6 in ["G?bF`w", "I?BD@g]Qo", "I?ABCc]}?", "J??CE?{{?]?", "I??CABoNo"]:
        n, E = dec(g6); info = loads(n, E)
        if info is None:
            print(f"  {g6}: loads None"); continue
        r = probe_side(info['n'], info['adj'], info['side'])
        if r is None:
            print(f"  {g6}: O empty (no C-alltie cases)"); continue
        print(f"  {g6} (N={info['n']}): {len(r)} cases")
        for c in r[:5]:
            print(f"     v={c['v']} z={c['z']} T(v)=N, T(z)=0 | Kcomp(v) meets O={c['meetsO']} "
                  f"|Cv|={c['Cv_size']} #f-through-v={c['nthrough']} #v-endpoint={c['endpt']} "
                  f"#through-f reaching O={c['f_to_O']}")
    print("--- census ---")
    run_census(11, 7)
