"""ROUTE CROSS-TERM (per-bad-edge row-sum reduction of (CV)).

(CV) per K-component c:   w^T O_c w <= (N+eta) Gamma_c,   eta=N^2/25-beta, A=N+eta,
   where O_c=P^T P (P[v,f]=p_f(v)=#geodesics of f through v), w_f=ell_f/|cyc_f|, Gamma_c=sum_f ell_f^2.
Equivalent:  sum_{v in c} T_v^2 <= A * sum_{v in c} T_v.

CROSS-TERM REDUCTION (the algebra that dissolves the off-diagonal coupling):
   Define  R_f := sum_v p_f(v) T(v)  =  sum_g w_g <p_f,p_g>      (f's row of O_c, weighted by w).
   Then    w^T O_c w = sum_{f in c} w_f R_f.
   PER-EDGE inequality (CX):   R_f <= A * ell_f * |cyc_f|     for every bad edge f.
   Summing against w_f = ell_f/|cyc_f| >= 0:
       sum_f w_f R_f <= A * sum_f (ell_f/|cyc_f|) * ell_f * |cyc_f| = A * sum_f ell_f^2 = A*Gamma_c.
   => (CX) for all f  ==>  (CV) for the whole component.  EXACT, no slack lost.
   (CX) is TIGHT at every C5[t] balanced blow-up (R_f = N*ell_f*|cyc_f| there, eta=0).
   Interpretation of (CX): the multiplicity-weighted average of the load T over the geodesic
   bundle of f is <= N+eta.

This gate checks (a) the per-edge (CX) on every bad edge, (b) the assembled (CV) per component,
on the FULL standing battery, EXACT Fraction. Reports binding edge/component + extremal ratio."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; beta=len(M); eta=F(N*N,25)-beta; A=F(N)+eta
    # p_f vectors
    P={}; w={}
    for f in M:
        Ps=cyc[f]; pf={}
        for Q in Ps:
            for v in Q: pf[v]=pf.get(v,0)+1
        P[f]=pf; w[f]=F(ell[f],len(Ps))
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    comps={}
    for v in range(n): comps.setdefault(cid[v],[]).append(v)
    # --- (CX) per-edge check ---
    for f in M:
        nf=len(cyc[f]); ellf=ell[f]
        Rf=sum(cnt*T[v] for v,cnt in P[f].items())   # = sum_v p_f(v) T(v)
        rhs=A*ellf*nf
        acc['ne']+=1
        # extremal ratio R_f/(ell_f*|cyc_f|) vs A  (== load-bundle-average vs A)
        ratio=F(Rf,ellf*nf)
        margin=rhs-Rf
        if margin<acc['cx_minm'][0]: acc['cx_minm']=(margin,name,N,beta,str(f),str(ratio),str(A))
        if margin<0:
            acc['cx_viol']+=1
            if acc['cx_first'] is None: acc['cx_first']=(name,N,beta,str(f),str(ratio),str(A))
    # --- assembled (CV) per component ---
    for c,vs in comps.items():
        S2=sum(T[v]*T[v] for v in vs); G=sum(T[v] for v in vs)
        if G==0: continue
        margin=A*G-S2
        acc['nc']+=1
        if margin<acc['cv_minm'][0]: acc['cv_minm']=(margin,name,N,beta,len(vs),str(G))
        if margin<0:
            acc['cv_viol']+=1
            if acc['cv_first'] is None: acc['cv_first']=(name,N,beta,len(vs),str(margin))

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
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'ne':0,'cx_viol':0,'cx_first':None,'cx_minm':(F(10**18),'','','','','',''),
         'nc':0,'cv_viol':0,'cv_first':None,'cv_minm':(F(10**18),'','','','','')}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: CX-viol=%d CV-viol=%d"%(acc['cx_viol'],acc['cv_viol']),flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done (CX-viol=%d CV-viol=%d)"%(acc['cx_viol'],acc['cv_viol']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['cx_viol']; w0=acc['cv_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (CX+%d CV+%d)"%(nn,acc['cx_viol']-v0,acc['cv_viol']-w0),flush=True)
    print("\n  --- PER-EDGE (CX): R_f <= (N+eta) ell_f |cyc_f| ---",flush=True)
    print("  edges tested=%d  (CX) violations=%d"%(acc['ne'],acc['cx_viol']),flush=True)
    print("  CX MIN margin = %s at (name,N,beta,f,ratio R_f/(ell_f|cyc_f|),A)=%s"%(float(acc['cx_minm'][0]),acc['cx_minm'][1:]),flush=True)
    if acc['cx_first']: print("  CX first violation: %s"%(acc['cx_first'],),flush=True)
    print("  --- ASSEMBLED (CV): sum_{v in c} T_v^2 <= (N+eta) Gamma_c ---",flush=True)
    print("  components tested=%d  (CV) violations=%d"%(acc['nc'],acc['cv_viol']),flush=True)
    print("  CV MIN margin = %s at (name,N,beta,|c|,Gamma_c)=%s"%(float(acc['cv_minm'][0]),acc['cv_minm'][1:]),flush=True)
    if acc['cv_first']: print("  CV first violation: %s"%(acc['cv_first'],),flush=True)
    print("\n  === (CX) per-edge %s ;  (CV) assembled %s ==="%(
        "HOLDS" if not acc['cx_viol'] else "FAILS", "HOLDS" if not acc['cv_viol'] else "FAILS"),flush=True)
