"""Test refined hypotheses for A-alltie:
 (H1) HANDSHAKE COROLLARY (should be a THEOREM): if ALL incident B-edges of v are zero-mu, then T(v)=0.
 (H2) For every (sat u T=N, zero-mu edge uv): are ALL of v's incident B-edges zero-mu? [the real reduction]
Census loads-cut N<=11 + Mycielskians + blow-ups. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow as sblow

def Bnbrs(info,x):
    adj=info['adj']; side=info['side']
    return [w for w in adj[x] if side[w]!=side[x]]

def test(info):
    N=info['n']; T=info['T']
    mu=mu_edges(info)
    # H1: vertices with all incident B-edges zero-mu
    h1_viol=[]
    for v in range(N):
        nb=Bnbrs(info,v)
        if not nb: continue
        if all(mu.get(frozenset((v,w)),F(0))==0 for w in nb):
            if T[v]!=0: h1_viol.append((v,float(T[v])))
    # H2: for every sat-u zero-mu edge uv, are all v's B-edges zero-mu?
    h2_cases=0; h2_viol=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]!=N: continue
            h2_cases+=1
            nb=Bnbrs(info,b)
            allzero=all(mu.get(frozenset((b,w)),F(0))==0 for w in nb)
            if not allzero:
                h2_viol.append((a,b,[(w,str(mu.get(frozenset((b,w)),F(0)))) for w in nb]))
    return h1_viol,h2_cases,h2_viol

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
    print("=== refined A-alltie hypotheses ===")
    th1=0; th2c=0; th2v=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        n1=0;c2=0;v2=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            h1,c,h2=test(info)
            n1+=len(h1); c2+=c; v2+=len(h2)
            if h2 and v2<=3:
                print(f"   H2 VIOL {g6}: {h2[:2]}")
        print(f"  census N={nn}: H1-viol(allzero but T!=0)={n1}  H2-cases={c2} H2-viol(not-all-v-edges-zero)={v2}",flush=True)
        th1+=n1; th2c+=c2; th2v+=v2
    # Mycielskians + blow-ups
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=30: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        h1,c,h2=test(info)
        print(f"  {name} N={nn}: H1-viol={len(h1)} H2-cases={c} H2-viol={len(h2)}"+(f"  {h2[:1]}" if h2 else ""),flush=True)
        th1+=len(h1); th2c+=c; th2v+=len(h2)
    print(f"\nTOTAL: H1-viol={th1}  H2-cases={th2c} H2-viol={th2v}")
