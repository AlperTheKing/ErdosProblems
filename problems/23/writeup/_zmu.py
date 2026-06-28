"""Exact stress of Codex's ZMU lemma (block 21).
mu(e)=sum_f sum_{P in cyc[f], e consecutive in P} ell_f/|cyc[f]|, for cut edge e in B.
ZMU: if O nonempty, every cut edge e with mu(e)=0 has at least one endpoint with T=0.
Corollaries: (A) no zero-mu edge has both endpoints T>0 [==ZMU]; (B) no zero-mu edge has an endpoint T=N;
(C) every T=0 vertex has bad-degree 0 in M. Exact Fraction."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _superphi import blow

def mu_edges(info):
    N=info['n']; T=info['T']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    # mu per undirected cut edge
    mu={}
    for e in info['Bset']:
        mu[frozenset(e)]=F(0)
    for f in M:
        paths=cyc[f]; k=len(paths)
        if k==0: continue
        w=F(ell[f],k)
        for P in paths:
            for i in range(len(P)-1):
                e=frozenset((P[i],P[i+1]))
                if e in mu: mu[e]+=w
                # (if a consecutive pair isn't a listed B-edge, skip; shouldn't happen)
    return mu

def test(info):
    N=info['n']; T=info['T']
    O=[v for v in range(N) if T[v]>N]
    if not O: return None
    mu=mu_edges(info)
    Mdeg=[0]*N
    for (a,b) in info['M']: Mdeg[a]+=1; Mdeg[b]+=1
    zero_edges=[tuple(sorted(e)) for e,val in mu.items() if val==0]
    zmu_viol=[]; bothload=[]; sat=[]
    for (u,v) in zero_edges:
        t0=(T[u]==0 or T[v]==0)
        if not t0: zmu_viol.append((u,v,float(T[u]),float(T[v])))   # ZMU violation == both nonzero
        if T[u]>0 and T[v]>0: bothload.append((u,v))
        if T[u]==N or T[v]==N: sat.append((u,v,float(T[u]),float(T[v])))
    cC=[v for v in range(N) if T[v]==0 and Mdeg[v]>0]   # (C) violations: T=0 but bad-degree>0
    return dict(O=len(O), nzero=len(zero_edges), zmu_viol=zmu_viol, bothload=bothload, sat=sat, cC=cC)

def show(name,info):
    r=test(info)
    if r is None: print(f"  {name}: O empty (ZMU vacuous)"); return
    flag = "" if (not r['zmu_viol'] and not r['sat'] and not r['cC']) else "  <<< FLAG"
    print(f"  {name} (N={info['n']}): |O|={r['O']} zero-mu-edges={r['nzero']} | ZMU-viol(bothT>0)={len(r['zmu_viol'])} "
          f"(B)sat-endpoint={len(r['sat'])} (C)T0-with-baddeg={len(r['cC'])}{flag}", flush=True)
    if r['zmu_viol']: print(f"      ZMU VIOLATION witnesses: {r['zmu_viol'][:3]}")
    if r['sat']: print(f"      (B) saturated zero-mu endpoints: {r['sat'][:3]}")
    if r['cC']: print(f"      (C) T=0 vertices with bad-degree>0: {r['cC'][:3]}")

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nO=0; zedges=0; zmuV=0; satV=0; cCV=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=test(info)
            if r is None: continue
            nO+=1; zedges+=r['nzero']
            zmuV+=len(r['zmu_viol']); satV+=len(r['sat']); cCV+=len(r['cC'])
            if (r['zmu_viol'] or r['sat'] or r['cC']) and wit is None:
                wit=(g6,r['zmu_viol'][:2],r['sat'][:2],r['cC'][:2])
        print(f"  census N={nn}(str{stride}): graphs-with-O={nO} zero-mu-edges={zedges} | ZMU-viol={zmuV} (B)sat={satV} (C)T0baddeg={cCV}"
              + (f"  WITNESS {wit}" if wit else ""), flush=True)

if __name__=="__main__":
    print("=== ZMU exact stress ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); show(g6,loads(n,E))
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn>24: continue
        info=loads(nn,EE)
        if info: show(f"{g6}[{t}]",info)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1)
    m1,F1=mycielski(*C7)
    for name,(nn,EE) in [("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]:
        info=loads(nn,EE)
        if info: show(name,info)
    run_census(11,7,1)
