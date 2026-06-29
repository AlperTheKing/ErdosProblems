"""VERIFY Codex's full-detour (M)-counterexample exactly (my independent gate):
build base build_pd(12,[(0,8),(2,6)]) + add_cut_path(0,12,14); parity side. Confirm:
 (1) triangle-free, Bconn, parity is GLOBAL MAX (CP-SAT exact);
 (2) f=(0,12) unique B-geodesic P=[0..12]; P-contained chords (0,8),(2,6) interior-overlap;
 (3) ROWSUM-O: every bad-edge row sum <= N (so NOT a ROWSUM counterexample);
 (4) NET: for f, E_P(whole)=2 and c=2 (tight, true) -- the route via NET survives;
 (5) interval-Hall / UPO on parity: does demand(I)<=cap(I) hold? (if yes, overlap is benign);
 (6) does the closed-SWEEP switch MISS here (confirming (M)-switch-proof cannot catch a genuine max overlap)?
Exact Fraction where it matters."""
from fractions import Fraction as F
from _M_tailswitch_gate import build_pd, tri_free, cutsize
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _h import Bconn
from _satzmu_conn import struct_for_side
from _closed_tail_gate import gain, offpath_components, closed

def make():
    n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
    n,E,side=add_cut_path(n,list(E),side,0,12,14)
    return n,sorted(set(E)),side

def cpsat_max(n,edges):
    try:
        from ortools.sat.python import cp_model
    except Exception as e:
        return None,None
    m=cp_model.CpModel(); x=[m.NewBoolVar(f"x{i}") for i in range(n)]; terms=[]
    for a,b in edges:
        z=m.NewBoolVar(f"e{a}_{b}"); m.AddBoolXOr([x[a],x[b],z.Not()]); terms.append(z)
    m.Maximize(sum(terms)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=60
    st=s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()

n,E,side=make(); adj=adj_from_edges(n,E)
print(f"n={n} tri-free={tri_free(n,adj)} Bconn={Bconn(n,adj,side)} parity-cut={cutsize(n,adj,side)}")
opt,bound=cpsat_max(n,E)
print(f"CP-SAT maxcut={opt} bound={bound} parity-is-GLOBAL-max={opt is not None and cutsize(n,adj,side)==opt==bound}")

st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
N=n
S=[F(0)]*n
for g in M:
    k=len(cyc[g])
    for P in cyc[g]:
        for v in P: S[v]+=F(1,k)
print(f"bad edges M={M}")
print(f"ell={ell}  Gamma={sum(ell[f]**2 for f in M)}")
# (3) ROWSUM-O
rows={}
for f in M:
    k=len(cyc[f])
    row=sum((F(1,k)*sum(1 for P in cyc[f] if v in P))*S[v] for v in range(n))
    rows[f]=row
mx=max(rows.values())
print(f"ROWSUM-O rows={{ {', '.join(f'{f}:{rows[f]}' for f in M)} }}  max={mx}  N={N}  ROWSUM-O {'HOLDS' if mx<=N else 'FAILS'}")
# (2)+(4)+(5)+(6) for the unique f with overlap
for f in M:
    if len(cyc[f])!=1: continue
    P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
    chords=[]
    for g in M:
        if g==f: continue
        for Q in cyc[g]:
            if set(Q)<=Pset:
                pp=sorted(pos[v] for v in Q)
                if pp[-1]-pp[0]==len(pp)-1: chords.append((g,pp[0],pp[-1])); break
    # interior overlap?
    ov=None
    for i in range(len(chords)):
        for j in range(i+1,len(chords)):
            _,a1,b1=chords[i]; _,a2,b2=chords[j]
            if a1>a2: a1,b1,a2,b2=a2,b2,a1,b1
            if a2<min(b1,b2): ov=((a1,b1),(a2,b2))
    if ov is None: continue
    print(f"f={f} L={L} P unique={'yes'} chords={chords} INTERIOR-OVERLAP={ov}")
    # (4) NET on whole interval: E_P (P-contained atoms) vs c (#components touching)
    comps=offpath_components(n,adj,side,Pset,pos)
    spans=[(min(pos[x] for x in A),max(pos[x] for x in A)) for C,A in comps if A]
    atoms=[]
    for g in M:
        if g==f: continue
        k=len(cyc[g])
        for Q in cyc[g]:
            if set(Q)<=Pset:
                J=sorted(pos[v] for v in Q); atoms.append((J[0],J[-1],F(1,k)))
    a,b=0,L-1
    EP=sum(w for (lo,hi,w) in atoms if not (hi<a or lo>b))
    c=sum(1 for (lo,hi) in spans if not (hi<a or lo>b))
    print(f"  NET whole-interval: E_P={EP}  c(#comp touching)={c}  NET {'HOLDS' if EP<=c else 'FAILS'} (tight={EP==c})")
    # (5) interval-Hall on parity
    dvec=[S[v]-1 for v in P_f]
    worst=None
    for a in range(L):
        for bb in range(a,L):
            dem=sum(dvec[i] for i in range(a,bb+1))
            cap=sum(cc for C,A in comps if A for cc in [len(C)] if not (max(pos[x] for x in A)<a or min(pos[x] for x in A)>bb))
            sl=F(cap)-dem
            if worst is None or sl<worst[0]: worst=(sl,(a,bb),str(dem),cap)
    print(f"  interval-Hall worst slack cap-demand = {worst[0]} at I={worst[1]} (demand={worst[2]}, cap={worst[3]})  => {'HOLDS' if worst[0]>=0 else 'FAILS'}")
    # (6) closed-sweep switch: does it find a positive-gain switch? (should MISS since cut is global max)
    found=False
    (a1,b1),(a2,b2)=ov; r=min(b1,b2)
    for k in range(a2,r):
        cL=closed(set(P_f[0:k+1]),comps); cR=closed(set(P_f[k+1:L]),comps)
        if gain(n,adj,side,cL)>0 or gain(n,adj,side,cR)>0: found=True
    print(f"  closed-SWEEP switch finds positive-gain k? {found}  => {'(M)-switch would FALSE-CATCH' if found else 'sweep MISSES (correct: cut is global max, no improving switch) => (M)-switch-proof cannot catch this'}")
