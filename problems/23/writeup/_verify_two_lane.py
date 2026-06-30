"""INDEPENDENT verification of GPT-Pro/Codex two-lane family as a counterexample to the rho(O)<=N / ROWSUM-O
route. Build the graph from scratch, confirm triangle-free + connected-B + CP-SAT GLOBAL MAX + UNIQUE max cut
(=> gamma-min), then compute the overlap Gram O_{fg}=<p_f,p_g> EXACTLY (my own struct_for_side), and check:
  ROWSUM-O: max_f (O*1)_f vs N ;  rho(O) vs N ;  Gamma=sum ell^2 vs N^2.
If a triangle-free gamma-min connected-B GLOBAL-max cut has rho(O)>N while Gamma<=N^2, the rho(O)<=N route is
DEAD (sufficient but false)."""
import sys
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side
from _h import Bconn
from ortools.sat.python import cp_model

def build_two_lane(L):
    # x_i=i (i=0..L), a_i=(L+1)+i, b_i=(L+1)+(L+1)+i for i=0..L
    nx=L+1
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1)
    E=set()
    for i in range(L): E.add((i,i+1))             # x path
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))   # x_i to its lane verts
    for i in range(L):                            # lane bipartite between consecutive
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    # bad edges (0,L-2),(0,L),(2,L-2),(2,L)
    bad=[(0,L-2),(0,L),(2,L-2),(2,L)]
    for e in bad: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side,bad

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def trifree(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True
def cpmax_unique(n,edges):
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=60
    s.Solve(m); return int(s.ObjectiveValue()), s.BestObjectiveBound()

def Ogram(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    O=[[F(0)]*len(M) for _ in range(len(M))]
    for i,f in enumerate(M):
        for j,g in enumerate(M):
            O[i][j]=sum(pf[f].get(v,F(0))*pf[g].get(v,F(0)) for v in pf[f])
    return M,ell,O

for L in (8,12):
    n,E,side,bad=build_two_lane(L)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N=n
    tf=trifree(n,adj); bc=Bconn(n,adj,side); pc=cutsize(n,adj,side)
    opt,bd=cpmax_unique(n,E)
    res=Ogram(n,adj,side)
    print("L=%d N=%d edges=%d tri-free=%s Bconn=%s parity-cut=%d CP-SAT-max=%d bound=%d global-max=%s"%(
        L,N,len(E),tf,bc,pc,opt,bd,pc==opt==bd))
    if res is None: print("  struct_for_side None"); continue
    M,ell,O=res
    rowsums=[sum(O[i]) for i in range(len(M))]
    Gamma=sum(ell[f]**2 for f in M)
    Of=np.array([[float(x) for x in r] for r in O])
    rho=max(abs(np.linalg.eigvals(Of)))
    print("  bad=%s ell=%s Gamma=%d N^2=%d Gamma<=N^2:%s"%(M,[ell[f] for f in M],Gamma,N*N,Gamma<=N*N))
    print("  O rowsums=%s  MAX rowsum=%s  N=%d  ROWSUM-O %s"%([str(x) for x in rowsums],max(rowsums),N,"HOLDS" if max(rowsums)<=N else "FAILS"))
    print("  rho(O)=%.4f  N=%d  rho/N=%.4f  rho(O)<=N %s"%(rho,N,rho/N,"HOLDS" if rho<=N else "FAILS"))
    print("  === %s ==="%("ROUTE DEAD: gamma-min connB GLOBAL-max, Gamma<=N^2, but rho(O)>N" if (pc==opt==bd and tf and bc and Gamma<=N*N and rho>N) else "rho(O)<=N here (route survives at this L)"))
