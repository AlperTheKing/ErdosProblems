r"""Robustness: ZMU-SUM-both (zero-mu B-edge, both T>0 => T(u)+T(v)<=N) and A-alltie on RANDOM triangle-free
graphs N=12..18 (gamma-min/loads cut). Also support-disjointness on the same. Exact Fraction.
This stress-tests the reduction target the way the (k2) guardrail demanded (random + larger N)."""
import random, itertools
from fractions import Fraction as F
from _h import dec, loads, maxcut_all, Bconn, bdist_restr, geos, gmin

def rand_trianglefree(n, p, seed):
    random.seed(seed)
    adj=[set() for _ in range(n)]
    E=[]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    random.shuffle(pairs)
    for (i,j) in pairs:
        if random.random()>p: continue
        # triangle-free: no common neighbor
        if adj[i]&adj[j]: continue
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E

def struct_loads(n,E):
    info=loads(n,E)
    return info

def check(info):
    if info is None: return (0,0,0,0)  # cases, sumviol, suppviol, aviol
    N=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    from _zmu import mu_edges
    mu=mu_edges(info)
    pf={}; supp={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); s=set()
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
    cases=sumviol=suppviol=aviol=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        # support-disjointness
        for f in M:
            if pf.get((f,u),0)>0 and pf.get((f,v),0)>0: suppviol+=1
        # A-alltie
        for (a,b) in [(u,v),(v,u)]:
            if T[a]==N and T[b]!=0: aviol+=1
        # ZMU-SUM-both
        if T[u]>0 and T[v]>0:
            cases+=1
            if T[u]+T[v]>N: sumviol+=1
    return cases,sumviol,suppviol,aviol

if __name__=="__main__":
    print("=== random triangle-free stress: A-alltie + ZMU-SUM-both + support-disjointness ===")
    for n in range(12,19):
        tc=ts=tsupp=ta=0; ngr=0
        for seed in range(400):
            p=random.Random(seed*7+n).uniform(0.2,0.55)
            nn,E=rand_trianglefree(n,p,seed*1000+n)
            if len(E)<n: continue
            info=loads(nn,E)
            if info is None: continue
            ngr+=1
            c,s,sp,a=check(info)
            tc+=c; ts+=s; tsupp+=sp; ta+=a
        print(f"  N={n}: graphs={ngr} both-pos-zero-mu-cases={tc} SUM-viol={ts} supp-disj-viol={tsupp} A-alltie-viol={ta}",flush=True)
