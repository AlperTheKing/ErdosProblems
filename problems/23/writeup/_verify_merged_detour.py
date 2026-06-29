"""Verify Codex block-201: FULL-DETOUR-N39 + edge(13,27) merging the two detour components. Claim: parity is
GAMMA-MIN global max, no bracket hub, scalar NET FAILS (E_P=2>c=1 at I=(0,2)) but position-flow PASSES.
=> scalar NET is dead even on gamma-min (component COUNT too coarse); position-flow (capacity) is robust.
My earlier _net_gate scalar-NET 0-viol on gamma-min census+Mycielskians was a BLIND SPOT (no merged detour)."""
from fractions import Fraction as F
from collections import deque
from _M_tailswitch_gate import build_pd, cutsize
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _satzmu_conn import struct_for_side
from _h import Bconn, bdist_restr
from _closed_tail_gate import offpath_components
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
def gamma(n,adj,s):
    g=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v); g+=(d+1)**2
    return g

n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
n,E,side=add_cut_path(n,list(E),side,0,12,14)
E=sorted(set(E))
# add merging edge (13,27): both must be opposite-side to be a cut edge
print("side[13]=%d side[27]=%d (cut edge needs opposite)"%(side[13],side[27]))
E=sorted(set(E+[(13,27)])); adj=adj_from_edges(n,E)
pc=cutsize(n,adj,side); opt,bd=cpmax(n,E)
print("n=%d edges=%d parity-cut=%d CP-SAT-max=%d bound=%d global-max=%s Bconn=%s"%(n,len(E),pc,opt,bd,pc==opt==bd,Bconn(n,adj,side)))
print("Gamma(parity)=%d"%gamma(n,adj,side))
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
                J=sorted(pos[v] for v in Q); atoms.append((J[0],J[-1]))
                for i in range(J[0],J[-1]+1): load[i]+=F(1,k)
    if not atoms: continue
    comps=offpath_components(n,adj,side,Pset,pos)
    cl=[(min(pos[x] for x in A),max(pos[x] for x in A),len(C)) for C,A in comps if A]
    print("f=%s atoms=%s components(span,|C|)=%s"%(f,atoms,cl))
    worst=None
    for a in range(L):
        for b in range(a,L):
            EP=sum(1 for (lo,hi) in atoms if not (hi<a or lo>b))
            c=sum(1 for (lo,hi,_) in cl if not (hi<a or lo>b))
            if worst is None or (EP-c)>worst[0]: worst=(EP-c,(a,b),EP,c)
    print("  scalar NET worst (E_P-c)=%d at I=%s (E_P=%d c=%d) NET %s"%(worst[0],worst[1],worst[2],worst[3],"FAILS" if worst[0]>0 else "holds"))
    posidx=[i for i in range(L) if load[i]>0]; nc=len(cl); npn=len(posidx)
    Nn=2+npn+nc; capm=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
    for j,i in enumerate(posidx): capm[0][2+j]=load[i]; total+=load[i]
    for jc,(lo,hi,cc) in enumerate(cl): capm[2+npn+jc][1]=cc
    BIG=total+1
    for j,i in enumerate(posidx):
        for jc,(lo,hi,cc) in enumerate(cl):
            if lo<=i<=hi: capm[2+j][2+npn+jc]=BIG
    print("  position-FLOW feasible=%s (demand=%s)"%(maxflow(capm,0,1,Nn)==total,total))
