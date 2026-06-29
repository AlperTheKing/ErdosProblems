"""Verify Codex block-200: build_pd(12,[(0,4),(8,12)]) parity is GLOBAL MAX but scalar NET fails (E_P>c) while
position-flow passes -- so scalar NET (199) needs gamma-min; position-flow (198) is robust under global-max.
Check: (1) CP-SAT global max?; (2) is parity gamma-min (vs gmins Gamma)?; (3) scalar NET E_P vs c at I=(0,8)
and worst I; (4) position-flow feasible? Exact."""
from fractions import Fraction as F
from collections import deque
from _M_tailswitch_gate import build_pd, cutsize
from _tail_positive_extra_counterexample import adj_from_edges
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _h import Bconn, bdist_restr
from _closed_tail_gate import gain, offpath_components, closed
from ortools.sat.python import cp_model

def cpmax(n,edges):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=30
    s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()
def maxflow(cap,src,snk,Nn):
    flow=F(0)
    while True:
        par=[-1]*Nn; par[src]=src; q=deque([src])
        while q:
            u=q.popleft()
            for v in range(Nn):
                if par[v]==-1 and cap[u][v]>0: par[v]=u; q.append(v)
        if par[snk]==-1: break
        v=snk; b=None
        while v!=src: u=par[v]; b=cap[u][v] if b is None else min(b,cap[u][v]); v=u
        v=snk
        while v!=src: u=par[v]; cap[u][v]-=b; cap[v][u]+=b; v=u
        flow+=b
    return flow

n,E=build_pd(12,[(0,4),(8,12)]); side=[v%2 for v in range(n)]; adj=adj_from_edges(n,E)
pc=cutsize(n,adj,side); opt,bd=cpmax(n,E)
print("n=%d parity-cut=%d CP-SAT-max=%d bound=%d parity-global-max=%s Bconn=%s"%(n,pc,opt,bd,pc==opt==bd,Bconn(n,adj,side)))
# is parity gamma-min?
gadj,gcuts=gmins(n,E)
def gamma(n,adj,s):
    g=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v); g+=(d+1)**2
    return g
gpar=gamma(n,adj,side); gm=min(gamma(n,gadj,c) for c in gcuts) if gcuts else None
print("Gamma(parity)=%s  gamma-min(over gmins)=%s  parity-is-gamma-min=%s"%(gpar,gm,gpar==gm))
st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
for f in M:
    if len(cyc[f])!=1: continue
    P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
    atoms=[]; load=[F(0)]*L
    for g in M:
        if g==f: continue
        k=len(cyc[g])
        for Q in cyc[g]:
            if set(Q)<=Pset:
                J=sorted(pos[v] for v in Q); atoms.append((J[0],J[-1],F(1,k)))
                for i in range(J[0],J[-1]+1): load[i]+=F(1,k)
    comps=offpath_components(n,adj,side,Pset,pos)
    spans=[(min(pos[x] for x in A),max(pos[x] for x in A)) for C,A in comps if A]
    if not atoms: continue
    print("f=%s P=%s atoms(intervals)=%s spans=%s"%(f,P_f,[(lo,hi) for lo,hi,_ in atoms],spans))
    worst=None
    for a in range(L):
        for b in range(a,L):
            EP=sum(w for (lo,hi,w) in atoms if not (hi<a or lo>b))
            c=sum(1 for (lo,hi) in spans if not (hi<a or lo>b))
            if worst is None or (EP-c)>worst[0]: worst=(EP-c,(a,b),EP,c)
    print("  scalar NET worst (E_P - c) = %s at I=%s (E_P=%s, c=%s)  NET %s"%(worst[0],worst[1],worst[2],worst[3],"FAILS" if worst[0]>0 else "holds"))
    # position-flow
    posidx=[i for i in range(L) if load[i]>0]; nc=len(comps); npn=len(posidx)
    Nn=2+npn+nc; capm=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
    for j,i in enumerate(posidx): capm[0][2+j]=load[i]; total+=load[i]
    cl=[(min(pos[x] for x in A),max(pos[x] for x in A),len(C)) for C,A in comps if A]
    for jc,(lo,hi,cc) in enumerate(cl): capm[2+npn+jc][1]=cc
    BIG=total+1
    for j,i in enumerate(posidx):
        for jc,(lo,hi,cc) in enumerate(cl):
            if lo<=i<=hi: capm[2+j][2+npn+jc]=BIG
    feas=maxflow(capm,0,1,Nn)==total
    print("  position-FLOW feasible = %s (total demand=%s)"%(feas,total))
