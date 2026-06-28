"""Saturation rigidity probes. For a saturated vertex u (T(u)=N):
 (R1) does u lie on the geodesic interval of EVERY bad edge f (phi_f(u)=0)?
 (R2) is p_f(u)=1 for every bad edge f with u on its interval (u a geodesic bottleneck)?
 (R3) sum over bad edges f of ell(f)*[u on interval] vs N -- since T(u)=sum ell(f) p_f(u)=N.
Census loads-cut + Mycielskians + blow-ups. Exact."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow as sblow

def bfs(adj,side,s):
    d={s:0}; q=deque([s])
    while q:
        x=q.popleft()
        for w in adj[x]:
            if side[w]!=side[x] and w not in d: d[w]=d[x]+1; q.append(w)
    return d

def probe(info):
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k)
    dmaps={}
    for f in M:
        s,t=f; dmaps[f]=(bfs(adj,side,s),bfs(adj,side,t))
    r1=[]; r2=[]
    for u in range(N):
        if T[u]!=N: continue
        for f in M:
            s,t=f; da,db=dmaps[f]; L=ell[f]-1
            oni = (da.get(u,99)+db.get(u,99)==L)
            # R1: u not on interval of some f?
            if not oni:
                # pf must be 0; record only if also pf>0 (impossible) - else note u OFF interval of some f
                r1.append((u,f,pf.get((f,u),F(0))))
            else:
                # R2: u on interval but pf<1?
                if pf.get((f,u),F(0))!=1:
                    r2.append((u,f,str(pf.get((f,u),F(0)))))
    return r1,r2

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    print("=== saturation rigidity: R1=u on interval of every f?  R2=p_f(u)=1 when on interval? ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tr1=0; tr2=0; ex1=None; ex2=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            if not any(t==info['n'] for t in info['T']): continue
            r1,r2=probe(info)
            # r1 'off interval' entries: count those that are OFF (sat u not on interval of some f)
            off=[x for x in r1]
            tr1+=len(off); tr2+=len(r2)
            if off and ex1 is None: ex1=(g6,off[:2])
            if r2 and ex2 is None: ex2=(g6,r2[:2])
        print(f"  N={nn}: sat-u-OFF-interval-of-some-f={tr1} {ex1 or ''} | on-interval-but-pf<1={tr2} {ex2 or ''}",flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=26: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        if not any(t==info['n'] for t in info['T']): print(f"  {name}: no sat vertex"); continue
        r1,r2=probe(info)
        print(f"  {name} N={nn}: sat-u-OFF={len(r1)} on-but-pf<1={len(r2)}  {r1[:1]} {r2[:1]}",flush=True)
