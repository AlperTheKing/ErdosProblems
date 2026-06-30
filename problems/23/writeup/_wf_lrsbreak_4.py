"""ADVERSARIAL FAMILY #4: try to BREAK the LRS certificate family.
Forms (all exact Fraction), each => Erdos via O PSD:
  B2:       max_v T(v) <= 2N
  PATH-LRS: per bad edge f, per shortest geodesic path P: (1/ell_f) sum_{v in P} T(v) + |M| <= N + N^2/25
  ROW-LRS:  per bad edge f: A_f + |M| <= N + N^2/25, A_f = sum_v p_f(v) T(v)/ell_f
  LRS:      sum_v T^2 <= Gamma*(N + N^2/25 - |M|)
Local (PATH/ROW) most likely to break.

BREAKER counts ONLY on a CP-SAT-verified triangle-free connected-B GLOBAL-max cut (cut == true max).
Census N=12,13 dense triangle-free (geng -tc) gamma-min cuts; random dense triangle-free N=14..22 CP-SAT max.

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import subprocess, random, itertools, sys
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from ortools.sat.python import cp_model

# p_f(v) = fraction of f's geodesics through v ; need cyc to reconstruct.
def pf_vec(n, cyc, f):
    Ps = cyc[f]; nP = len(Ps)
    return [F(sum(1 for P in Ps if v in P), nP) for v in range(n)]

def eval_forms(n, side, adj):
    """Return dict of worst-case margins for the four forms on this (connected-B) cut,
    or None if not a valid bad-edge structure. margin = lhs - rhs; >0 == VIOLATION."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    N = n
    beta = len(M)
    Gamma = sum(ell[f]*ell[f] for f in M)  # = sum_v T(v) as identity; use ell^2 def
    # sanity: sum_v T == Gamma (identity)
    sumT = sum(T)
    RHS = F(N) + F(N*N, 25) - beta   # N + N^2/25 - |M|
    rec = dict(N=N, beta=beta, Gamma=Gamma, sumT=sumT)

    # B2: max T(v) <= 2N  => margin = max T - 2N
    maxT = max(T)
    rec['B2_margin'] = maxT - 2*N
    rec['B2_ratio'] = float(maxT)/N

    # LRS: sum T^2 <= Gamma*(N + N^2/25 - beta) ; margin = sumT2 - Gamma*RHS_lrs
    sumT2 = sum(t*t for t in T)
    rec['LRS_margin'] = sumT2 - Gamma*RHS
    rec['LRS_ratio'] = float(sumT2)/float(Gamma*RHS) if Gamma*RHS != 0 else float('inf')

    # ROW-LRS: A_f + beta <= N + N^2/25 ; A_f = sum_v p_f(v) T(v) / ell_f
    # PATH-LRS: A_{f,P} + beta <= N+N^2/25 ; A_{f,P} = (1/ell_f) sum_{v in P} T(v)
    worst_row = None; worst_path = None
    for f in M:
        pf = pf_vec(n, cyc, f)
        ellf = ell[f]
        A_f = sum(pf[v]*T[v] for v in range(n)) / ellf
        m_row = A_f + beta - (F(N) + F(N*N,25))
        if worst_row is None or m_row > worst_row: worst_row = m_row
        for P in cyc[f]:
            A_fP = sum(T[v] for v in P) / ellf
            m_path = A_fP + beta - (F(N) + F(N*N,25))
            if worst_path is None or m_path > worst_path: worst_path = m_path
    rec['ROW_margin'] = worst_row
    rec['PATH_margin'] = worst_path
    return rec

# ---- CP-SAT exact global max cut (returns max value + one optimal cut, OPTIMAL status) ----
def cpsat_maxcut(n, E):
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(n)]
    cut = [m.NewBoolVar(f"c{i}") for i in range(len(E))]
    for k,(a,b) in enumerate(E):
        # cut_k = 1 iff x[a]!=x[b]
        m.Add(cut[k] <= x[a]+x[b])
        m.Add(cut[k] <= 2 - x[a] - x[b])
        m.Add(cut[k] >= x[a]-x[b])
        m.Add(cut[k] >= x[b]-x[a])
    m.Maximize(sum(cut))
    sv = cp_model.CpSolver()
    sv.parameters.num_search_workers = 8
    sv.parameters.max_time_in_seconds = 30
    r = sv.Solve(m)
    if r != cp_model.OPTIMAL:
        return None
    val = int(round(sv.ObjectiveValue()))
    return val

def all_maxcuts_bruteforce(n, adj, E):
    """enumerate all cuts achieving brute-force max (only n<=24-ish)."""
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best, cuts

def is_tri_free(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    for a,b in E:
        if adj[a]&adj[b]: return False
    return True

# track weakest survivor: collect worst (closest to violating) margin per form across ALL tested cuts
GLOB = dict(B2=None, PATH=None, ROW=None, LRS=None)
BREAKERS = []

def record(rec, g6_or_E, side, n):
    for key,fld in [('B2','B2_margin'),('PATH','PATH_margin'),('ROW','ROW_margin'),('LRS','LRS_margin')]:
        m = rec[fld]
        if GLOB[key] is None or m > GLOB[key][0]:
            GLOB[key] = (m, g6_or_E, list(side), n, rec['beta'], rec['Gamma'])
        if m > 0:
            BREAKERS.append((key, m, g6_or_E, list(side), n, dict(rec)))

def process_cut_exactmax(n, E, adj, side, true_max, label):
    """only call when side is a verified GLOBAL max cut, connected-B."""
    # verify cut value == true_max
    cval = sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    if cval != true_max: return
    if not Bconn(n, adj, side): return
    rec = eval_forms(n, side, adj)
    if rec is None: return
    record(rec, label, side, n)

CENSUS_FLOOR = {12: 28, 13: 30}  # dense triangle-free band; Turan max = floor(n^2/4)=36,42

def run_census(nn):
    floor = CENSUS_FLOOR[nn]
    out = subprocess.run([GENG,"-tc","-d3",str(nn),f"{floor}:"],capture_output=True,text=True).stdout.split()
    cnt=0; tested=0
    for g6 in out:
        n,E = dec(g6)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        tmax, cuts = all_maxcuts_bruteforce(n, adj, E)
        for side in cuts:
            process_cut_exactmax(n, E, adj, side, tmax, g6)
        cnt+=1; tested+=1
    return cnt

def rand_dense_trifree(n, seed, attempts=400):
    """generate a dense-ish triangle-free graph on n vertices."""
    rng = random.Random(seed)
    # start from C5 blowup-ish skeleton (bipartite-like dense tri-free) then add random tri-free edges
    E=set()
    adj=[set() for _ in range(n)]
    order=[(a,b) for a in range(n) for b in range(a+1,n)]
    rng.shuffle(order)
    for a,b in order:
        if adj[a]&adj[b]: continue  # would form triangle
        E.add((a,b)); adj[a].add(b); adj[b].add(a)
    return sorted(E)

if __name__=="__main__":
    print("=== FAMILY #4: LRS-break census + random dense triangle-free ===", flush=True)
    # ---- census N=12,13 (CP-SAT-equivalent: brute force max IS exact global max) ----
    for nn in (12,13):
        c=run_census(nn)
        print(f"census N={nn} dense (edges>={CENSUS_FLOOR[nn]}, d3): tested {c} tri-free graphs, all max cuts BRUTE-FORCE exact (=global max).", flush=True)
        print(f"  current worst margins: "
              f"B2={float(GLOB['B2'][0]):.4f} PATH={float(GLOB['PATH'][0]):.4f} "
              f"ROW={float(GLOB['ROW'][0]):.4f} LRS={float(GLOB['LRS'][0]):.4f}", flush=True)
    # ---- random dense triangle-free N=14..22, CP-SAT exact max ----
    for n in range(14,23):
        for s in range(60):
            E = rand_dense_trifree(n, seed=1000*n+s)
            if not is_tri_free(n,E): continue
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            tmax = cpsat_maxcut(n, E)
            if tmax is None: continue  # not proven optimal in time -> skip (honesty)
            # enumerate all global-max cuts via brute force (n<=22 ok) to test each
            bmax, cuts = all_maxcuts_bruteforce(n, adj, E)
            assert bmax == tmax, f"CP-SAT {tmax} != brute {bmax} n={n} s={s}"
            for side in cuts:
                process_cut_exactmax(n, E, adj, side, tmax, f"rand_n{n}_s{s}:{sorted(E)}")
        print(f"random N={n}: done 60 dense tri-free, CP-SAT==brute confirmed. "
              f"worst: B2={float(GLOB['B2'][0]):.4f} PATH={float(GLOB['PATH'][0]):.4f} "
              f"ROW={float(GLOB['ROW'][0]):.4f} LRS={float(GLOB['LRS'][0]):.4f}", flush=True)

    print("\n=== RESULTS ===", flush=True)
    for key in ('B2','PATH','ROW','LRS'):
        m,lbl,side,n,beta,Gamma = GLOB[key]
        st = "VIOLATED" if m>0 else "survived"
        print(f"{key}: worst margin={m} ({float(m):.6f}) [{st}] N={n} beta={beta} Gamma={Gamma}", flush=True)
    print(f"\nBREAKERS found: {len(BREAKERS)}", flush=True)
    for b in BREAKERS[:10]:
        print(b[0], float(b[1]), 'N=',b[4], b[5]['beta'], flush=True)
