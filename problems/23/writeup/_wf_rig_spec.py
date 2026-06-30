"""ROUTE (c) SPECTRAL / variance-rigidity gate.  EXACT Fraction.  Filename _wf_rig_spec.py (unique).

Notation (all from struct_for_side): N=n, M=bad edges, beta=|M|=m, ell[f]=geodesic length (#vertices),
T=load vector (Fractions), Gamma=sum ell^2, sum_v T_v=Gamma (handshake).
  V2     := sum_v (T_v - N)^2                         (load variance about N)
  sumTTN := sum_v T_v (T_v - N) = V2 + N*(Gamma-N^2)  (identity, |V|=N, sum T=Gamma)
  TVcut  := sum_{cut  uv} |T_u - T_v|
  TVbad  := sum_{bad  uv} |T_u - T_v|
  cutpress := sum_{cut uv} (T_u - T_v)^2   (= (T)^T L_cut (T), L_cut = Laplacian of cut-edge subgraph)
  budget := N^2/25 - beta ;  Gbud := Gamma*budget.

THE TWO INEQUALITIES THIS GATE CHECKS (exact):
  (A) VARIANCE-RIGIDITY :  V2 <= K * Gbud          -- find the TRUE extremal K (battery max).
  (B) LOAD-PSC-c (literal target, for c in {5,25}):
        Lc := sumTTN + (N/c)*(TVcut - TVbad) <= Gbud.
      We report rho_c := Lc/Gbud (LOAD-PSC-c holds iff rho_c <= 1) and the SUFFICIENT-COND cap
        capK_c := (Gbud - (N/c)(TVcut-TVbad) - N*(Gamma-N^2)) / Gbud = (RHSp_c)/Gbud
      i.e. the largest K for which "V2<=K*Gbud" would still give LOAD-PSC-c by the naive drop.
      If min capK_c over battery < true K of (A), then (A) does NOT imply LOAD-PSC by the naive drop.

SPECTRAL DIAGNOSTIC (float, NOT a pass/fail; reported for the sharper form):
  lambda2 = smallest nonzero eigenvalue of L_cut (cut-edge Laplacian) restricted to span perp to ker.
  ratio2 := V2 / cutpress  (so V2 <= cutpress/lambda would need lambda <= 1/max(ratio2)).
"""
import sys, subprocess
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\writeup")
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

CS=(5,25)

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); Gamma=sum(ell[f]**2 for f in M); N=n
    V2=sum((t-N)**2 for t in T)
    sumTTN=sum(t*(t-N) for t in T)
    tvcut=F(0); tvbad=F(0); cutpress=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=T[u]-T[v]
                if side[u]!=side[v]: tvcut+=abs(d); cutpress+=d*d
                else: tvbad+=abs(d)
    budget=F(N*N,25)-m
    Gbud=Gamma*budget
    acc['n']+=1
    # (A) variance-rigidity true K = V2/Gbud  (UNIVERSAL K)
    if Gbud>0:
        K=F(V2)/Gbud
        if K>acc['Kmax'][0]: acc['Kmax']=(K,name,N,m,str(V2),str(Gbud))
        # (A') N-normalized: ratioN = V2/(N*Gbud) = K/N  -- the bounded form, conjectured <=1
        ratioN=F(V2)/(N*Gbud)
        if ratioN>acc['rN'][0]: acc['rN']=(ratioN,name,N,m)
        if V2>N*Gbud:
            acc['vN']+=1
            if acc['fN'] is None: acc['fN']=(name,N,m,str(F(V2)/Gbud))
    elif Gbud==0:
        # equality stratum: must have V2==0 else K=+inf (refutes any finite K)
        if V2!=0:
            acc['Kinf']+=1
            if acc['Kinf_first'] is None: acc['Kinf_first']=(name,N,m,str(V2))
    else:  # Gbud<0 impossible if budget>=0; budget could be <0 only if beta>N^2/25 -- flag
        acc['negbud']+=1
    # (C) PURE LOAD-ONLY (no cut-pressure):  sumTTN <= Gbud  (= V2 <= RHSp).  Tight at C5[t].
    if sumTTN>Gbud:
        acc['vP0']+=1
        if acc['fP0'] is None: acc['fP0']=(name,N,m,float(sumTTN),float(Gbud))
    if Gbud>0:
        rho0=F(sumTTN)/Gbud
        if rho0>acc['rho0'][0]: acc['rho0']=(rho0,name,N,m)
    # spectral ratio2 = V2/cutpress
    if cutpress>0:
        r2=F(V2)/cutpress
        if r2>acc['r2max'][0]: acc['r2max']=(r2,name,N,m)
    # (B) LOAD-PSC-c literal + sufficient-cond cap
    NGN=N*(Gamma-N*N)   # = N*(Gamma - N^2)
    for c in CS:
        P=F(N,c)*(tvcut-tvbad)
        Lc=sumTTN+P
        # rho_c = Lc/Gbud, holds iff Lc<=Gbud
        if Lc>Gbud:
            acc['vL%d'%c]+=1
            if acc['fL%d'%c] is None: acc['fL%d'%c]=(name,N,m,float(Lc),float(Gbud))
        if Gbud>0:
            rho=F(Lc)/Gbud
            if rho>acc['rho%d'%c][0]: acc['rho%d'%c]=(rho,name,N,m)
            # sufficient-cond cap on K:  K*Gbud <= Gbud - P - NGN  => capK = (Gbud - P - NGN)/Gbud
            capK=F(Gbud-P-NGN)/Gbud
            if capK<acc['capK%d'%c][0]: acc['capK%d'%c]=(capK,name,N,m)

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    acc={'n':0,'Kinf':0,'Kinf_first':None,'negbud':0,
         'Kmax':(F(-1),'','','','',''),'r2max':(F(-1),'','',''),
         'rN':(F(-1),'','',''),'vN':0,'fN':None,
         'vP0':0,'fP0':None,'rho0':(F(-10**18),'','','')}
    for c in CS:
        acc['vL%d'%c]=0; acc['fL%d'%c]=None
        acc['rho%d'%c]=(F(-10**18),'','','')
        acc['capK%d'%c]=(F(10**18),'','','')
    print("=== ROUTE(c) SPECTRAL/variance-rigidity gate ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane done: Kmax so far=%s"%float(acc['Kmax'][0]),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done: Kmax=%s"%(nn,float(acc['Kmax'][0])),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                        ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  total configs=%d"%acc['n'],flush=True)
    print("  --- (A) VARIANCE-RIGIDITY  V2 <= K*Gbud ---",flush=True)
    km=acc['Kmax']
    print("    TRUE extremal K = %s = %s  at %s (N=%s,beta=%s)"%(km[0],float(km[0]),km[1],km[2],km[3]),flush=True)
    print("    V2=%s  Gbud=%s"%(km[4],km[5]),flush=True)
    print("    Gbud==0 with V2!=0 (would refute any finite K): %d  first=%s"%(acc['Kinf'],acc['Kinf_first']),flush=True)
    print("    budget<0 (beta>N^2/25) configs: %d"%acc['negbud'],flush=True)
    print("    spectral ratio2 max V2/cutpress = %s = %s at %s"%(acc['r2max'][0],float(acc['r2max'][0]),acc['r2max'][1:]),flush=True)
    print("  --- (A') N-NORMALIZED  V2 <= N*Gbud  (ratioN=V2/(N*Gbud)=K/N) ---",flush=True)
    rn=acc['rN']
    print("    max ratioN = %s = %s at %s (N=%s,beta=%s) ; violations(V2>N*Gbud)=%d first=%s"%(
        rn[0],float(rn[0]),rn[1],rn[2],rn[3],acc['vN'],acc['fN']),flush=True)
    print("  --- (C) PURE LOAD-ONLY  sumTTN <= Gbud  (=V2<=RHSp; LOAD-PSC w/o cut-pressure) ---",flush=True)
    print("    violations(sumTTN>Gbud)=%d  max rho0=%s=%s at %s  first=%s"%(
        acc['vP0'],acc['rho0'][0],float(acc['rho0'][0]),acc['rho0'][1:],acc['fP0']),flush=True)
    print("  --- (B) LOAD-PSC-c literal target ---",flush=True)
    for c in CS:
        print("    c=%d: violations(Lc>Gbud)=%d  max rho_c=%s(holds iff<=1) at %s"%(
            c,acc['vL%d'%c],float(acc['rho%d'%c][0]),acc['rho%d'%c][1:]),flush=True)
        if acc['fL%d'%c]: print("        first viol: %s"%(acc['fL%d'%c],),flush=True)
        print("        SUFFICIENT-COND cap on K (min (RHSp_c)/Gbud) = %s = %s at %s"%(
            acc['capK%d'%c][0],float(acc['capK%d'%c][0]),acc['capK%d'%c][1:]),flush=True)
    print("\n  VERDICT: (A) holds with K_true above; whether (A)=>LOAD-PSC requires K_true <= min capK_c.",flush=True)
