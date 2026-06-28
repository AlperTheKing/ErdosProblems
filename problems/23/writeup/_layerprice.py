"""GPT's LAYER-PRICE SOS (non-circular certificate for N*I - K PSD => ROWSUM-O => Gamma<=N^2).
Find layer-prices b_{f,i}>0 (i = geodesic layer of bad edge f) with:
  (harmonic)  sum_i 1/b_{f,i} <= 1            for each bad edge f
  (budget)    sum_{f, i: v in I_i(f)} b_{f,i} * p_f(v) <= N    for each vertex v
Then N*I-K = sum_f (D_f - p_f p_f^T) + (N*I - sum_f D_f) PSD, D_f(v)=b_{f,layer(v)}*p_f(v):
  - D_f - p_f p_f^T PSD <=> sum_v p_f(v)^2/D_f(v) = sum_i (1/b_{f,i}) sum_{v in I_i}p_f(v) = sum_i 1/b_{f,i} <= 1.
  - N*I - sum_f D_f PSD (diagonal) <=> budget <=N per vertex.
Uniform b_{f,i}=ell(f) gives D_f=diag(ell(f)p_f), sum_f D_f=diag(T); fails where T(v)>N. Layer prices vary across
layers to keep budget<=N. SOLVE the convex feasibility (min max-vertex-budget t* s.t. harmonic) and check t*<=N.
Substitute c=1/b (c in (0,1], sum_i c_{f,i}<=1 linear; budget sum p_f(v)/c convex). All numeric (then exact-check)."""
import numpy as np
from scipy.optimize import minimize, linprog
from collections import deque
from fractions import Fraction as F
from _h import dec, loads

def layers_of(info,f):
    a,b=f; n=info['n']; adj=info['adj']; side=info['side']
    da={a:0}; q=deque([a])
    while q:
        x=q.popleft()
        for y in adj[x]:
            if side[x]!=side[y] and y not in da: da[y]=da[x]+1; q.append(y)
    Ps=info['cyc'][f]; nf=len(Ps); cnt={}
    for P in Ps:
        for v in P: cnt[v]=cnt.get(v,0)+1
    pf={v:cnt[v]/nf for v in cnt}
    h=info['ell'][f]-1
    lay={i:[] for i in range(h+1)}
    for v in pf:
        lay[da[v]].append(v)
    return lay,pf,h

def solve_layerprice(info):
    """returns t* = min over harmonic-feasible prices of max-vertex-budget. Feasible (<=N) => SOS works."""
    n=info['n']; M=info['M']; N=n
    # variables: c_{f,i}=1/b_{f,i} for each (f, layer i in 0..h_f). index them.
    idx={}; nv=0; perf=[]
    Ls=[]
    for f in M:
        lay,pf,h=layers_of(info,f); Ls.append((lay,pf,h))
        rng=[]
        for i in range(h+1):
            idx[(f,i)]=nv; rng.append(nv); nv+=1
        perf.append(rng)
    # objective: minimize t (last var). vars = [c_0..c_{nv-1}, t]
    nvar=nv+1
    # budget(v) = sum_{f,i: v in I_i} p_f(v)/c_{f,i} <= t  (convex)
    # build vertex -> list of (var_index, p_f(v))
    vbud={v:[] for v in range(n)}
    for fi,f in enumerate(M):
        lay,pf,h=Ls[fi]
        for i in range(h+1):
            ci=idx[(f,i)]
            for v in lay[i]:
                vbud[v].append((ci, pf[v]))
    def obj(z): return z[nv]
    def obj_grad(z):
        g=np.zeros(nvar); g[nv]=1.0; return g
    cons=[]
    # harmonic: sum_i c_{f,i} <= 1  => 1 - sum c >=0
    for rng in perf:
        cons.append({'type':'ineq','fun':(lambda z,rng=rng: 1.0-sum(z[k] for k in rng))})
    # budget: t - sum p/c >=0
    for v in range(n):
        terms=vbud[v]
        if not terms: continue
        cons.append({'type':'ineq','fun':(lambda z,terms=terms,nv=nv: z[nv]-sum(p/max(z[ci],1e-9) for ci,p in terms))})
    x0=np.full(nvar,0.5);
    # init c so sum_i c_{f,i}=~1: set c=1/(h+1)
    for fi,rng in enumerate(perf):
        for k in rng: x0[k]=1.0/len(rng)
    x0[nv]=float(N)
    bnds=[(1e-6,1.0)]*nv+[(0,None)]
    res=minimize(obj,x0,jac=obj_grad,constraints=cons,bounds=bnds,method='SLSQP',options={'maxiter':500,'ftol':1e-9})
    return res.fun, res.success

def Cblow(k,q):
    L=2*k+1; m=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return m,E

if __name__=="__main__":
    print("=== layer-price feasibility: t* (min max-budget) <= N ? ===")
    tests=["DUW","FCp`_","H?bB@_W","I?rFf_{N?","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]
    for g6 in tests:
        n,E=dec(g6); info=loads(n,E)
        t,ok=solve_layerprice(info)
        print(f"  {g6:14} N={n} Gamma={info['G']} | t*={t:.4f} <= N={n}? {t<=n+1e-4} (solver_ok={ok})")
    print("--- blowups ---")
    for (k,q) in [(2,2),(2,3),(3,2)]:
        m,E=Cblow(k,q); info=loads(m,E)
        t,ok=solve_layerprice(info)
        print(f"  C{2*k+1}[{q}] N={m} | t*={t:.4f} <= N={m}? {t<=m+1e-4}")
