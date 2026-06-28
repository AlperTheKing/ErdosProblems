"""IICF (Inclusive Interval Corridor Flow) — Codex's corridor-flow model for CORR/LPD.
For graph + nonneg y: demand node (f,i,j) [i<j layers of bad edge f] with demand sqrt(w_fi*w_fj),
w_fi=sum_{v in I_i(f)} y_v p_f(v); edge (f,i,j)->v (inf cap) iff v in Corr(f,i,j)=union_{k=i..j} I_k(f);
v->sink cap = 0.5*(N-S(v))*y_v. Feasible (maxflow==total demand) <=> Hall cut for all U; U=V is CORR.
Codex showed CORR<=>IICF-feasible-for-all-y. So:
  (1) CONFIRM feasibility (maxflow==demand) on the gate set incl. the ADVERSARIAL worst-case y (max CORR deficit).
  (2) At tight cases, DUMP the min-cut: which vertices on source side, which demands cut; check if the cut
      Corr-sets / vertex sets form PREFIX/SUFFIX intervals inside each edge's layer system (the finite-reduction lead).
Float maxflow (sqrt is irrational); this is feasibility-stress + structure, not an exact closure."""
import numpy as np, networkx as nx, subprocess, random
from scipy.optimize import minimize
from _h import dec, GENG, loads
from _layerprice import layers_of

INF=1e9

def setup(info):
    n=info['n']; M=info['M']; N=n
    L=[]  # per edge: (f, lay dict i->list, pf dict, h)
    for f in M:
        lay,pf,h=layers_of(info,f); L.append((f,lay,pf,h))
    # S(v)
    S=[0.0]*n
    for (f,lay,pf,h) in L:
        for i in lay:
            for v in lay[i]: S[v]+=pf[v]
    # demand triples (ei,i,j) with corridor vertex set
    triples=[]
    for ei,(f,lay,pf,h) in enumerate(L):
        for i in range(h+1):
            for j in range(i+1,h+1):
                corr=set()
                for k in range(i,j+1): corr.update(lay[k])
                triples.append((ei,i,j,frozenset(corr)))
    return L,S,N,n,triples

def wvals(L,y):
    # w[ei][i] = sum_{v in lay[i]} y_v pf[v]
    W=[]
    for (f,lay,pf,h) in L:
        w={i:sum(y[v]*pf[v] for v in lay[i]) for i in range(h+1)}
        W.append(w)
    return W

def maxflow_iicf(L,S,N,n,triples,y):
    W=wvals(L,y)
    G=nx.DiGraph()
    total=0.0
    for t,(ei,i,j,corr) in enumerate(triples):
        d=np.sqrt(max(W[ei][i],0.0)*max(W[ei][j],0.0))
        if d<=0: continue
        total+=d
        dn=('d',t)
        G.add_edge('SRC',dn,capacity=d)
        for v in corr:
            G.add_edge(dn,('v',v),capacity=INF)
    for v in range(n):
        cap=0.5*(N-S[v])*y[v]
        if cap>0: G.add_edge(('v',v),'SINK',capacity=cap)
    if total<=0: return 0.0,0.0,None
    fv,_=nx.maximum_flow(G,'SRC','SINK')
    # min cut
    cut_val,(srcside,sinkside)=nx.minimum_cut(G,'SRC','SINK')
    return fv,total,(srcside,sinkside,cut_val)

def corr_deficit(L,S,N,n,y):
    W=wvals(L,y)
    lhs=sum(np.sqrt(max(W[ei][i],0.)*max(W[ei][j],0.)) for ei,(f,lay,pf,h) in enumerate(L) for i in range(h+1) for j in range(i+1,h+1))
    rhs=0.5*sum((N-S[v])*y[v] for v in range(n))
    return lhs-rhs

def worst_y(L,S,N,n):
    # maximize CORR deficit over simplex (concave); start from all-ones + a few restarts
    rng=random.Random(3); best=None; besty=None
    def neg(z):
        y=np.abs(z); s=y.sum();
        if s<=0: return 0.0
        return -corr_deficit(L,S,N,n,y/s*n)
    starts=[np.ones(n)]+[np.array([rng.random() for _ in range(n)]) for _ in range(6)]
    for z0 in starts:
        r=minimize(neg,z0,method='Nelder-Mead',options={'maxiter':2000,'xatol':1e-6,'fatol':1e-9})
        y=np.abs(r.x); y=y/ y.sum()*n
        d=corr_deficit(L,S,N,n,y)
        if best is None or d>best: best=d; besty=y
    return best,besty

def test_graph(g6,info,blow=None):
    L,S,N,n,triples=setup(info)
    rng=random.Random(11)
    worst=None; wy=None; wtag=None
    ys=[('ones',np.ones(n))]
    ys+=[('ray%d'%v,np.eye(n)[v]) for v in range(n)]
    ys+=[('rand%d'%k,np.array([rng.random() for _ in range(n)])) for k in range(15)]
    for tag,y in ys:
        fv,total,cut=maxflow_iicf(L,S,N,n,triples,list(y))
        deficit=total-fv  # >0 => infeasible (maxflow<demand)
        if worst is None or deficit>worst: worst=deficit; wy=y; wtag=tag
    # adversarial worst-y for CORR (tightness)
    bd,by=worst_y(L,S,N,n)
    fv,total,cut=maxflow_iicf(L,S,N,n,triples,list(by))
    adv_deficit=total-fv
    return worst,wtag,bd,adv_deficit

def main():
    print("=== IICF feasibility (maxflow==demand?) + worst-y CORR deficit ===")
    # gate set: census small + named + N=22 + blowups
    named=["FCp`_","H?bB@_W","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]
    for g6 in named:
        n,E=dec(g6); info=loads(n,E)
        worst,wtag,bd,adv=test_graph(g6,info)
        print(f"  {g6:13} N={n}: max flow-deficit(over y)={worst:+.2e}@{wtag} | worst-y CORR deficit={bd:+.4f} flow-deficit@worsty={adv:+.2e}")
    # N=22 witness
    n,E=dec("J???E?pNu\\?"); nn=n*2; EE=[]
    for (a,b) in E:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    info=loads(nn,EE); worst,wtag,bd,adv=test_graph("J???E?pNu?[2]",info)
    print(f"  J???E?pNu?[2] N={nn}: max flow-deficit={worst:+.2e} | worst-y CORR deficit={bd:+.4f} flow-def@worsty={adv:+.2e}")
    # census N=8,9 full + N=10,11 sample
    for nn2 in (8,9):
        out=subprocess.run([GENG,"-tc",str(nn2)],capture_output=True,text=True).stdout.split()
        bad=0; mx=None; mg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            L,S,N,n,triples=setup(info)
            rng=random.Random(5)
            for y in [np.ones(n)]+[np.array([rng.random() for _ in range(n)]) for _ in range(8)]:
                fv,total,cut=maxflow_iicf(L,S,N,n,triples,list(y))
                d=total-fv
                if mx is None or d>mx: mx=d; mg=g6
                if d>1e-6: bad+=1
        print(f"  census N={nn2}: flow-infeasible samples={bad} | max flow-deficit={mx:+.2e}@{mg}",flush=True)

if __name__=="__main__":
    main()
