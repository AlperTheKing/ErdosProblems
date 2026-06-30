"""SELF-CONTAINED exact audit of the N=9 census BLOCK-SBC counterexample g6=H?AFBo].
   Confirm: tri-free, Bconn, GLOBAL MAX (brute maxcut_all + CP-SAT), gamma-min among connB max cuts,
   single positive K-comp, EXACT-PSD violation. All Fraction."""
from fractions import Fraction as F
from collections import deque
from _h import dec, maxcut_all, Bconn, bdist_restr, geos
from ortools.sat.python import cp_model

g6="H?AFBo]"
n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
trifree=all(not (adj[x]&adj[y]) for (x,y) in E)

# GLOBAL MAX via brute maxcut_all and CP-SAT
cuts_all=maxcut_all(n,adj)
maxcut=sum(1 for (u,v) in E if cuts_all[0][u]!=cuts_all[0][v])
m=cp_model.CpModel(); xb=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
for u,v in E:
    z=m.NewBoolVar("e%d_%d"%(u,v)); m.AddBoolXOr([xb[u],xb[v],z.Not()]); t.append(z)
m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=30; s.Solve(m)
cpopt=int(round(s.ObjectiveValue())); cpbd=int(round(s.BestObjectiveBound()))
print(f"g6={g6} N={n} |E|={len(E)} tri-free={trifree}")
print(f"  brute max-cut size={maxcut}  CP-SAT max={cpopt} bound={cpbd}  match={maxcut==cpopt==cpbd}")

# enumerate connB max cuts, compute Gamma, pick gamma-min, gate
def struct(side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    cyc={}; ell={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0])
    return M,ell,cyc

cand=[]
for side in cuts_all:
    if not Bconn(n,adj,side): continue
    st=struct(side)
    if st is None: continue
    M,ell,cyc=st
    if not M: continue
    G=sum(ell[f]**2 for f in M)
    cand.append((side,G,M,ell,cyc))
gm=min(G for _,G,_,_,_ in cand)
print(f"  connB max cuts with M: {len(cand)}  gamma-min Gamma={gm}")

def pf_dict(Ps):
    k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d
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

any_viol=False
for side,G,M,ell,cyc in cand:
    if G!=gm: continue
    # K-components
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
    for root,C in comp.items():
        M_C=[f for f in M if f[0] in C and f[1] in C]
        if not M_C: continue
        n_C=len(C); m_C=len(M_C)
        pf=[pf_dict(cyc[f]) for f in M_C]
        O=[[sum(pv*pf[j].get(v,F(0)) for v,pv in pf[i].items()) for j in range(m_C)] for i in range(m_C)]
        RHS=F(n_C)+F(n_C*n_C,25); c=RHS-F(m_C)
        B=[[ (c if r==col else F(0))-O[r][col] for col in range(m_C)] for r in range(m_C)]
        holds=is_psd(B)
        ones=sum(O[i][j] for i in range(m_C) for j in range(m_C))/F(m_C)
        if not holds:
            any_viol=True
            print(f"  VIOLATION side={side} C={sorted(C)} n_C={n_C} m_C={m_C} "
                  f"M_C={M_C} O={[[str(v) for v in r] for r in O]}")
            print(f"    rho_lb(allones)={ones} RHS={RHS}={float(RHS):.4f} LHS_lb={ones+m_C} -> PSD={holds}")
print("ANY genuine BLOCK-SBC violation on a gamma-min connB GLOBAL-MAX cut:",any_viol)
