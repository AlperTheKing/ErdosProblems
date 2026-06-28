"""Classify A-alltie witness cases over census + blow-ups + Mycielskians.
For each (saturated u with T=N, zero-mu incident edge uv):
  - is u an ENDPOINT of every bad edge through it, or interior to some?
  - does v have B-degree 1 (leaf), or more?
  - T(v) (should be 0)
We want to know if A-alltie is ever non-trivial: u interior to a bad edge, AND/OR v has Bdeg>1."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow as sblow

def Bdeg(info,x):
    adj=info['adj']; side=info['side']
    return sum(1 for w in adj[x] if side[w]!=side[x])

def classify(g6, info, label=None):
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for x in range(N):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k)
    rows=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]!=N: continue
            # is a interior to some bad edge through a?
            interior = any(pf.get((f,a),0)>0 and a not in f for f in M)
            bdeg_v=Bdeg(info,b)
            rows.append(dict(g6=label or g6,u=a,v=b,Tv=T[b],u_interior=interior,vdeg=bdeg_v))
    return rows

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
    allrows=[]
    # census
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            if not any(t==info['n'] for t in info['T']): continue
            allrows+=classify(g6,info)
    # Mycielskians
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    for name,(nn,EE) in [("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]:
        info=loads(nn,EE)
        if info and any(t==info['n'] for t in info['T']): allrows+=classify(name,info,label=name)
    # blow-ups of small overloaded graphs
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        try:
            nn,EE=sblow(g6,t)
        except Exception as ex:
            continue
        if nn>30: continue
        info=loads(nn,EE)
        if info and any(t2==info['n'] for t2 in info['T']): allrows+=classify(f"{g6}[{t}]",info,label=f"{g6}[{t}]")
    # summarize
    tot=len(allrows)
    viol=[r for r in allrows if r['Tv']!=0]
    uint=[r for r in allrows if r['u_interior']]
    vdeg2=[r for r in allrows if r['vdeg']>1]
    print(f"TOTAL (sat u, zero-mu uv) cases: {tot}")
    print(f"  A-violations (T(v)!=0): {len(viol)}  {viol[:3]}")
    print(f"  cases where u is INTERIOR to a bad edge through it: {len(uint)}")
    for r in uint[:10]: print("     ",r)
    print(f"  cases where v has B-degree > 1: {len(vdeg2)}")
    for r in vdeg2[:10]: print("     ",r)
