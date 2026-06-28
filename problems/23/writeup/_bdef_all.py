"""Codex block 22: Gamma_C + dB(C) <= N|C| for EVERY full K-component C (NOT just C disjoint from O).
Via mass identity mass(C)=sum_{v in C}T[v]=Gamma_C, this is N|C|-mass(C) >= dB(C). Includes C=V (conjecture-strength).
Exact Fraction. Report min slack (N|C|-mass-dB) with witness + #violations, separating C-with-O from C-disjoint-O."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _superphi import blow
from _bdef import components

def check(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=set(v for v in range(n) if T[v]>N)
    res=[]
    for C in components(K,n):
        Cs=set(C); mass=sum(T[v] for v in C)
        dB=sum(1 for (a,b) in info['Bset'] if (a in Cs)^(b in Cs))
        slack=F(N*len(C))-mass-dB
        hasO=bool(Cs&O); isV=(len(C)==n)
        res.append((tuple(C),slack,hasO,isV,dB,len(C)))
    return res

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def show(name,info):
    res=check(info); N=info['n']
    viol=[r for r in res if r[1]<0]
    worst=min(res,key=lambda r:r[1])
    print(f"  {name} (N={N}): K-comps={len(res)} viol={len(viol)} | min slack(N|C|-Gamma_C-dB)={float(worst[1]):+.3f}"
          f" @ |C|={worst[5]} hasO={worst[2]} isV={worst[3]} dB={worst[4]}", flush=True)
    if viol: print(f"      *** VIOLATION: {viol[0]}")

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        ncomp=0; viol=0; worst=None; wg=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in check(info):
                ncomp+=1
                if r[1]<0: viol+=1
                if worst is None or r[1]<worst: worst=r[1]; wg=(g6,r[5],r[2],r[3])
        print(f"  census N={nn}(str{stride}): K-comps={ncomp} viol={viol} min slack={float(worst):+.3f} @ {wg}", flush=True)

if __name__=="__main__":
    print("=== Gamma_C+dB<=N|C| for ALL K-components (block 22) ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","J?AEB?oE?W?"]:
        n,E=dec(g6); show(g6,loads(n,E))
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn>24: continue
        info=loads(nn,EE)
        if info: show(f"{g6}[{t}]",info)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    for name,(nn,EE) in [("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]:
        info=loads(nn,EE)
        if info: show(name,info)
    run_census(10,7,1)
