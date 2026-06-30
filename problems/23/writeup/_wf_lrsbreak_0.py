"""ADVERSARIAL break of the LRS certificate family (Family #0: k-LANE generalization of build_two_lane).
Build: x-path of length L + k parallel fully-connected lanes (each lane vertex set per path index, complete
bipartite between consecutive indices) + many bad chords on the path to RAISE |M| toward N^2/25 while keeping
load concentrated. For each candidate:
  1) triangle-free check
  2) Bconn check (proposed parity cut)
  3) CP-SAT GLOBAL max verify: parity-cut size == CP-SAT optimum == best bound  (cut==true max)
  4) struct_for_side -> M,ell,T,mu,cyc ; p_f(v)
  5) EXACT (Fraction) check of B2, PATH-LRS, ROW-LRS, LRS.
A breaker counts ONLY when CP-SAT-exact GLOBAL max == parity cut (triangle-free, Bconn). Report weakest surviving form.

Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import sys
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import Bconn
from ortools.sat.python import cp_model

# ---------- k-lane builder ----------
def build_k_lane(L, k, bad):
    """x_i = i for i=0..L (path). lane j vertex at index i: lv(j,i) = (L+1) + j*(L+1) + i, j=0..k-1.
    Edges: path x_i-x_{i+1}; x_i - lv(j,i) for all j; complete bipartite lane(*,i) - lane(*,i+1).
    bad = list of path chords (a,b) with same parity (monochromatic under parity cut).
    Returns n, sorted(E), side (parity cut), bad."""
    nx = L+1
    def lv(j,i): return (L+1) + j*(L+1) + i
    n = (L+1) + k*(L+1)
    E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        for j in range(k):
            u,v=i,lv(j,i); E.add((min(u,v),max(u,v)))
    for i in range(L):
        for ja in range(k):
            for jb in range(k):
                u,v=lv(ja,i),lv(jb,i+1); E.add((min(u,v),max(u,v)))
    for e in bad:
        a,b=e; E.add((min(a,b),max(a,b)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1):
        for j in range(k): side[lv(j,i)]=1-(i%2)
    return n,sorted(E),side,bad

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def trifree(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def cpmax(n,edges,tlim=120):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlim
    s.parameters.num_search_workers=16
    st=s.Solve(m)
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), st==cp_model.OPTIMAL

def lrs_check(n,adj,side):
    """Return dict of exact LRS-family quantities + pass/fail, or None if struct invalid."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    N=n
    # p_f(v) = (#geos thru v)/|cyc_f|
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[f]=d
    Gamma=sum(F(ell[f])**2 for f in M)
    absM=len(M)
    RHS_const=F(N)+F(N*N,25)-F(absM)   # N + N^2/25 - |M|  (the per-form RHS for ROW/PATH; LRS uses Gamma*RHS_const)
    # B2: max T(v) <= 2N
    maxT=max(T) if T else F(0)
    B2_ok = (maxT <= F(2*N))
    # LRS: sum T^2 <= Gamma*(N + N^2/25 - |M|)
    sumT2=sum(t*t for t in T)
    LRS_lhs=sumT2; LRS_rhs=Gamma*RHS_const
    LRS_ok=(LRS_lhs <= LRS_rhs)
    # ROW-LRS per f: A_f + |M| <= N + N^2/25 ; A_f = sum_v p_f(v) T(v) / ell(f)
    rowworst=None; ROW_ok=True
    for f in M:
        Af = sum(pf[f].get(v,F(0))*T[v] for v in pf[f]) / F(ell[f])
        lhs = Af + F(absM)
        rhs = F(N)+F(N*N,25)
        ok = lhs<=rhs
        slack = rhs-lhs
        if rowworst is None or slack<rowworst[0]: rowworst=(slack,f,Af,lhs,rhs)
        if not ok: ROW_ok=False
    # PATH-LRS per (f,P): A_{f,P}+|M| <= N+N^2/25 ; A_{f,P}=(1/ell_f) sum_{v in P} T(v)
    pathworst=None; PATH_ok=True
    for f in M:
        for P in cyc[f]:
            Afp = sum(T[v] for v in P)/F(ell[f])
            lhs = Afp + F(absM)
            rhs = F(N)+F(N*N,25)
            ok = lhs<=rhs
            slack = rhs-lhs
            if pathworst is None or slack<pathworst[0]: pathworst=(slack,f,P,Afp,lhs,rhs)
            if not ok: PATH_ok=False
    return dict(N=N,absM=absM,Gamma=Gamma,maxT=maxT,
                B2_ok=B2_ok, LRS_ok=LRS_ok, ROW_ok=ROW_ok, PATH_ok=PATH_ok,
                LRS_lhs=LRS_lhs, LRS_rhs=LRS_rhs,
                rowworst=rowworst, pathworst=pathworst,
                ratioM=F(absM)/F(N*N,25), N2_25=F(N*N,25))

def run_case(L,k,bad,tlim=120,verbose=True):
    n,E,side,bad=build_k_lane(L,k,bad)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N=n
    tf=trifree(n,adj); bc=Bconn(n,adj,side); pc=cutsize(n,adj,side)
    if not tf:
        if verbose: print(f"L={L} k={k} |bad|={len(bad)} N={N}: NOT triangle-free (skip)")
        return None
    if not bc:
        if verbose: print(f"L={L} k={k} |bad|={len(bad)} N={N}: B not connected (skip)")
        return None
    opt,bd,isopt=cpmax(n,E,tlim)
    globalmax = (pc==opt==bd) and isopt
    res=lrs_check(n,adj,side)
    if verbose:
        print(f"L={L} k={k} |bad|={len(bad)} N={N} edges={len(E)} tf={tf} Bconn={bc} "
              f"paritycut={pc} CP-SAT opt={opt} bound={bd} OPTIMAL={isopt} GLOBALMAX={globalmax}")
    if res is None:
        if verbose: print("  struct_for_side -> None (no bad edges / no geos)")
        return dict(globalmax=globalmax,res=None,N=N,absM=0)
    r=res
    if verbose:
        print(f"  |M|={r['absM']} Gamma={r['Gamma']} N^2/25={float(r['N2_25']):.2f} "
              f"|M|/(N^2/25)={float(r['ratioM']):.4f} maxT={float(r['maxT']):.3f} 2N={2*N}")
        print(f"  B2 {'OK' if r['B2_ok'] else 'FAIL'} | LRS {'OK' if r['LRS_ok'] else 'FAIL'} "
              f"(lhs={float(r['LRS_lhs']):.1f} rhs={float(r['LRS_rhs']):.1f}) | "
              f"ROW-LRS {'OK' if r['ROW_ok'] else 'FAIL'} (minslack={float(r['rowworst'][0]):.4f}) | "
              f"PATH-LRS {'OK' if r['PATH_ok'] else 'FAIL'} (minslack={float(r['pathworst'][0]):.4f})")
        broken=[nm for nm,ok in [('B2',r['B2_ok']),('PATH-LRS',r['PATH_ok']),('ROW-LRS',r['ROW_ok']),('LRS',r['LRS_ok'])] if not ok]
        if broken and globalmax:
            print(f"  *** BREAKER (GLOBAL-max verified): forms broken = {broken} ***")
        elif broken:
            print(f"  (forms broken = {broken} but NOT CP-SAT global-max -> heuristic only, NOT a breaker)")
    return dict(globalmax=globalmax,res=res,N=N,absM=r['absM'],bad=bad,L=L,k=k)

if __name__=="__main__":
    # Path chords (a,b) are monochromatic iff a,b same parity. To raise |M|, add many same-parity chords
    # that remain triangle-free. On the x-path with lanes, two even (or two odd) path vertices i,j with
    # |i-j|>=2 are non-adjacent and (since lanes only connect consecutive indices) share no common neighbor
    # unless |i-j|==2 (they'd share lane verts at the middle index). So |i-j|>=4 chords are safest.
    cases=[]
    # original two-lane sanity (k=2) reproduced via this builder
    # k=3 lanes, raise bad-edge count
    def evenchords(L, step, gap):
        out=[]
        for a in range(0,L+1,2):
            for b in range(a+gap, L+1, 2):
                out.append((a,b))
        return out
    def greedy_trifree_chords(L, k, gap):
        """Greedily add same-parity path chords (|i-j|>=gap) that keep the WHOLE graph triangle-free.
        Re-checks the full adjacency (path+lanes+already-added chords) before committing each chord."""
        base_n, base_E, _, _ = build_k_lane(L, k, [])
        adj=[set() for _ in range(base_n)]
        for a,b in base_E: adj[a].add(b); adj[b].add(a)
        chords=[]
        cand=[(a,b) for a in range(0,L+1) for b in range(a+gap,L+1) if (a%2)==(b%2)]
        for (a,b) in cand:
            if b in adj[a]: continue
            if adj[a]&adj[b]: continue   # would form triangle
            adj[a].add(b); adj[b].add(a); chords.append((a,b))
        return chords
    # Start modest, then push |M| up. Keep triangle-free via greedy full-graph check.
    for (L,k) in [(8,3),(8,4),(8,5),(10,3),(10,4),(10,5),(12,3),(12,4),(12,5),(16,3),(16,4),(20,3),(20,4)]:
        bad=greedy_trifree_chords(L,k,4)
        if bad: cases.append((L,k,bad))
    print("=== Family #0: k-LANE LRS-break sweep ===")
    survived={'B2':True,'PATH-LRS':True,'ROW-LRS':True,'LRS':True}
    breakers=[]
    maxratio=F(0)
    for (L,k,bad) in cases:
        out=run_case(L,k,bad,tlim=120)
        print()
        if out and out['res'] is not None:
            r=out['res']
            if r['ratioM']>maxratio: maxratio=r['ratioM']
            for nm,ok in [('B2',r['B2_ok']),('PATH-LRS',r['PATH_ok']),('ROW-LRS',r['ROW_ok']),('LRS',r['LRS_ok'])]:
                if not ok and out['globalmax']:
                    survived[nm]=False
                    breakers.append((nm,out))
    print("=== SUMMARY ===")
    print("max |M|/(N^2/25) reached:", float(maxratio))
    print("forms that survived ALL CP-SAT-global-max cases:", [nm for nm,s in survived.items() if s])
    print("forms broken on a CP-SAT-global-max cut:", sorted(set(b[0] for b in breakers)))
