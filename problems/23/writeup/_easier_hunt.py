"""Adversarial hunt: does ANY gamma-min connected-B max cut have a bad edge f with per-edge
PATH-LRS(avg) violated  (O ell)_f > A*ell_f  while aggregate SUM-SBC ell^T O ell <= A ell^T ell still holds?
If NONE ever: SUM-SBC has no aggregation slack over PATH-LRS empirically -> direct proof must essentially reprove PATH-LRS.
Random triangle-free graphs (greedy), plus larger non-uniform C5/C7 blowups. EXACT."""
import random
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def pf_of(M,cyc):
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    return pf

def analyze(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); slack=F(N*N,25)-m
    pf=pf_of(M,cyc); Gamma=sum(ell[f]**2 for f in M)
    Oell={}  # (O ell)_f = sum_v p_f(v) T(v)
    for f in M: Oell[f]=sum(pf[f].get(v,F(0))*T[v] for v in pf[f])
    A=F(N)+slack
    peredge_fail=any(Oell[f]>A*ell[f] for f in M)
    S=sum(ell[f]*(Oell[f]-N*ell[f]) for f in M)  # = sum_f L_f Phi_f
    agg = S<=slack*Gamma
    acc['tot']+=1
    if peredge_fail:
        acc['pf']+=1
        if agg: acc['easier']+=1; acc['ew']=acc['ew'] or (name,n,m)
    if not agg: acc['aggfail']+=1; acc['aw']=acc['aw'] or (name,n,m,str(S),str(slack*Gamma))

def rand_trifree(n,p,rng):
    adj=[set() for _ in range(n)]; E=[]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]; rng.shuffle(pairs)
    for i,j in pairs:
        if rng.random()<p and not (adj[i]&adj[j]):
            adj[i].add(j); adj[j].add(i); E.append((i,j))
    return n,E
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    acc=dict(tot=0,pf=0,easier=0,ew=None,aggfail=0,aw=None)
    rng=random.Random(12345)
    for n in range(8,17):
        for _ in range(400):
            for p in (0.2,0.3,0.45):
                _,E=rand_trifree(n,p,rng)
                adj,cuts=gmins(n,E)
                for s in cuts[:3]: analyze("rnd",n,adj,s,acc)
    # bigger nonuniform blowups (n up to ~22, maxcut_all = 2^21 ok-ish but slow; cap n<=20)
    import itertools
    for sizes in itertools.product([1,2,3,4],repeat=5):
        n=sum(sizes)
        if n>20 or n<7: continue
        _,E=blowup(list(sizes)); adj,cuts=gmins(n,E)
        for s in cuts[:2]: analyze("C5%s"%(sizes,),n,adj,s,acc)
    print("tot=%d  per-edge-fail=%d  (of those aggregate-holds = EASIER) %d  ew=%s"%(acc['tot'],acc['pf'],acc['easier'],acc['ew']))
    print("aggregate SUM-SBC failures=%d  aw=%s"%(acc['aggfail'],acc['aw']))
