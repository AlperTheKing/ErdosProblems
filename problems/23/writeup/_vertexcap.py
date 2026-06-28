"""Test the two-step A-alltie route:
 (DIFF-COMP) zero-mu B-edge uv with T(u)>0,T(v)>0  =>  K-component(u) != K-component(v).
 (VERTEX-CAP) for every vertex w with T(w)>0:  T(w) <= |C_w|  (size of its K-component).
If both hold: zero-mu both-pos edge => C_u,C_v distinct => |C_u|+|C_v|<=N => T(u)<=|C_u|<=N-|C_v|<=N-1,
   so T(u)=N forces v not positive => A-alltie.
Test exactly over census loads-cut N<=11 + Mycielskians + blowups. Report worst T(w)-|C_w| (should be <=0).
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _satzmu_conn import kcomponents

def kcomp_of(info):
    comp,find=kcomponents(info['n'], info['cyc'])
    return comp, find

def check(info):
    N=info['n']; T=info['T']
    mu=mu_edges(info)
    comp,find=kcomp_of(info)
    # VERTEX-CAP
    worst=None; vcviol=0
    for w in range(N):
        if T[w]>0:
            Cw=comp[find(w)]
            slack=F(len(Cw))-T[w]   # want >=0
            if worst is None or slack<worst: worst=slack
            if slack<0: vcviol+=1
    # DIFF-COMP
    dc_viol=0; dc_cases=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]>0 and T[v]>0:
            dc_cases+=1
            if find(u)==find(v): dc_viol+=1
    return worst, vcviol, dc_cases, dc_viol

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def blow(t):
    nn=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return nn,E

if __name__=="__main__":
    print("=== VERTEX-CAP (T(w)<=|C_w|) + DIFF-COMP (zero-mu both-pos => diff K-comp) ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gw=None; vcv=0; dcc=0; dcv=0; vcwit=None; dcwit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            w,vc,dc,dv=check(info)
            if w is not None and (gw is None or w<gw): gw=w; vcwit=g6
            vcv+=vc; dcc+=dc; dcv+=dv
            if dv>0 and dcwit is None: dcwit=g6
        print(f"  N={nn}: worst slack(|C|-T)={None if gw is None else float(gw)} VC-viol={vcv}({vcwit if vcv else ''}) | DIFF-COMP cases={dcc} viol={dcv}({dcwit or ''})", flush=True)
    # stress
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    cases=[("Grotzsch",n1,E1),("Myc(Grotzsch)N=23",n2,E2),("Myc(C7)N=15",m1,F1)]
    for t in [2,3,4]:
        nn,EE=blow(t); cases.append((f"C5[{t}]",nn,EE))
    for name,nn,EE in cases:
        info=loads(nn,EE)
        if info is None: print(f"  {name}: None"); continue
        w,vc,dc,dv=check(info)
        print(f"  {name} (N={info['n']}): worst slack(|C|-T)={None if w is None else float(w)} VC-viol={vc} | DIFF-COMP cases={dc} viol={dv}", flush=True)
