r"""KEY claim for A-alltie: at a saturated vertex u (T(u)=N), every loaded vertex lies on a geodesic through u:
   (KEY)  T(x)>0  =>  x in U_u  (x on some F_u-geodesic).   Equivalently V-minus-U_u subset Dead.
This + support-disjointness (v notin U_u) => v in Dead => T(v)=0 => A-alltie.
Test EXACT over census N<=11 + Mycielskians + blow-ups. Report any KEY violation: a loaded vertex x (T(x)>0)
NOT on any geodesic through some saturated u."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow as sblow

def keyviol(g6, info):
    N=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    pf={}; supp={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); s=set()
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
    viols=[]
    for u in range(N):
        if T[u]!=N: continue
        Fu=[f for f in M if pf.get((f,u),0)>0]
        Uu=set().union(*[supp[f] for f in Fu]) if Fu else set()
        # KEY: every loaded vertex in U_u
        for x in range(N):
            if T[x]>0 and x not in Uu:
                viols.append((u,x,str(T[x])))
    return viols

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
    print("=== KEY: saturated u => every loaded x on a geodesic through u ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tv=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            v=keyviol(g6,info)
            if v: tv+=len(v); wit=wit or (g6,v[:2])
        print(f"  census N={nn}: KEY-violations (loaded x off all u-geodesics)={tv} {wit or ''}",flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=26: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        v=keyviol(name,info)
        print(f"  {name} N={nn}: KEY-viol={len(v)} {v[:2]}",flush=True)
