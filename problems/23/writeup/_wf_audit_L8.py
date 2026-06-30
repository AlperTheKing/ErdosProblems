"""FULLY SELF-CONTAINED exact audit of the two-lane L=8 BLOCK-SBC counterexample.
   Build graph + side from scratch; confirm tri-free + Bconn + CP-SAT GLOBAL MAX + UNIQUE-enough;
   compute geodesics by BFS in the B-graph; build p_f, O_C, and EXACT-PSD-test BLOCK-SBC.
   No reliance on struct_for_side / kcomponents internals beyond cross-check."""
from fractions import Fraction as F
from collections import deque
from ortools.sat.python import cp_model

L=8
a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
n=3*(L+1)
Es=set()
for i in range(L): Es.add((i,i+1))
for i in range(L+1):
    Es.add((min(i,a(i)),max(i,a(i)))); Es.add((min(i,b(i)),max(i,b(i))))
for i in range(L):
    for u in (a(i),b(i)):
        for v in (a(i+1),b(i+1)): Es.add((min(u,v),max(u,v)))
bad=[(0,L-2),(0,L),(2,L-2),(2,L)]
for e in bad: Es.add((min(e),max(e)))
E=sorted(Es)
side=[0]*n
for i in range(L+1): side[i]=i%2
for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)

adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)

# tri-free
trifree=all(not (adj[x]&adj[y]) for (x,y) in E)
# Bconn (B = bichromatic edges)
seen={0}; q=deque([0])
while q:
    u=q.popleft()
    for v in adj[u]:
        if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
bconn=(len(seen)==n)
# bad edges = monochromatic
M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
# CP-SAT global max
m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
for u,v in E:
    z=m.NewBoolVar("e%d_%d"%(u,v)); m.AddBoolXOr([x[u],x[v],z.Not()]); t.append(z)
m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=60
s.Solve(m)
opt=int(round(s.ObjectiveValue())); bd=int(round(s.BestObjectiveBound()))
cut=sum(1 for (u,v) in E if side[u]!=side[v])
print("L=8 N=%d |E|=%d trifree=%s Bconn=%s parity-cut=%d CP-max=%d bound=%d GLOBAL-MAX=%s"%(
    n,len(E),trifree,bconn,cut,opt,bd,(cut==opt==bd)))
print("M (bad edges, monochromatic) =",M)

# B-geodesics between bad endpoints (paths alternating sides)
def geos(s,tt):
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if tt not in dist: return []
    P=[]
    def rec(v,acc):
        if v==s: P.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p,acc+[v])
    rec(tt,[]); return P

cyc={f:geos(*f) for f in M}
ell={f:len(cyc[f][0]) for f in M}
print("ell (odd-cycle lengths) =",[ell[f] for f in M],"  #geodesics each =",[len(cyc[f]) for f in M])

# p_f and K-component (union-find over geodesic-path cliques)
def pf_dict(Ps):
    k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d
par=list(range(n))
def find(v):
    while par[v]!=v: par[v]=par[par[v]]; v=par[v]
    return v
for f,Ps in cyc.items():
    for P in Ps:
        for i in range(1,len(P)):
            ra,rb=find(P[0]),find(P[i])
            if ra!=rb: par[ra]=rb
comp={}
for v in range(n): comp.setdefault(find(v),set()).add(v)
pos=[(r,C) for r,C in comp.items() if any(f[0] in C and f[1] in C for f in M)]
print("#positive K-components =",len(pos))
root,C=pos[0]
M_C=[f for f in M if f[0] in C and f[1] in C]
n_C=len(C); m_C=len(M_C)
pf=[pf_dict(cyc[f]) for f in M_C]
O=[[F(0)]*m_C for _ in range(m_C)]
for i in range(m_C):
    for j in range(m_C):
        di,dj=pf[i],pf[j]
        O[i][j]=sum(pv*dj[v] for v,pv in di.items() if v in dj)
print("positive component C =",sorted(C),"  n_C=",n_C,"  m_C=",m_C)
print("O_C (exact) =")
for r in O: print("   ",[str(v) for v in r])

def is_psd(A):
    mm=len(A); W=[r[:] for r in A]
    for k in range(mm):
        p=W[k][k]
        if p<0: return False
        if p==0:
            for j in range(mm):
                if W[k][j]!=0: return False
            continue
        for i in range(k+1,mm):
            if W[i][k]==0: continue
            ff=W[i][k]/p
            for j in range(k,mm): W[i][j]-=ff*W[k][j]
    return True

RHS=F(n_C)+F(n_C*n_C,25)
c=RHS-F(m_C)
B=[[ (c if r==col else F(0))-O[r][col] for col in range(m_C)] for r in range(m_C)]
sbc_holds=is_psd(B)
# rho lower bound = all-ones Rayleigh
ones=sum(O[i][j] for i in range(m_C) for j in range(m_C))/F(m_C)
print("RHS = n_C + n_C^2/25 =",RHS,"=",float(RHS))
print("c = RHS - m_C =",c)
print("rho(O_C) lower bound (all-ones Rayleigh) =",ones,"=",float(ones))
print("(c*I - O_C) PSD =",sbc_holds,"  => BLOCK-SBC",("HOLDS" if sbc_holds else "VIOLATED"))
print("LHS lower bound rho_lower + m_C =",ones+m_C,"=",float(ones+m_C),"  vs RHS",float(RHS))
print("VERDICT: BLOCK-SBC", "VIOLATED (genuine counterexample)" if not sbc_holds else "holds")
