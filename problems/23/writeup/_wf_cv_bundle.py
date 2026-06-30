"""ROUTE = HOT-CORE-BUNDLE (per-edge u_f-average load).  EXACT Fraction gate, full standing battery.

REDUCTION (algebra, exact -- proven below by the identity check, not assumed):
  Per K-component c with bad edges fs.  For f in fs let p_f(v)=#geodesics of f through v,
  w_f = ell_f/|cyc_f|, q_f = w_f*p_f.  Then T = sum_f q_f (load), and
     ||q_f||_1 = w_f * sum_v p_f(v) = w_f * ell_f*|cyc_f| = ell_f^2 .           [IDENT-1, checked]
  Define u_f = q_f / ell_f^2 (so sum_v u_f(v) = 1, u_f >= 0: a probability vector on slots).
  Then:
     Gamma_c = sum_{v in c} T_v = sum_f ||q_f||_1 = sum_f ell_f^2 .             [IDENT-2, checked]
     S2 := sum_{v in c} T_v^2 = <T, sum_f q_f> = sum_f <q_f, T> = sum_f ell_f^2 <u_f, T> . [IDENT-3, checked]
  Hence  S2 = sum_f ell_f^2 * <u_f,T>  and  Gamma_c = sum_f ell_f^2 ,  with weights ell_f^2 >= 0.

  CENTRAL INEQUALITY (BND), per bad edge f in c:
        <u_f, T>  <=  N + eta        (eta = N^2/25 - beta),  i.e. the u_f-average load <= N+eta.
  IMPLICATION (BND for all f in c)  ==>  (CV):
        S2 = sum_f ell_f^2 <u_f,T>  <=  sum_f ell_f^2 (N+eta) = (N+eta) Gamma_c .     [convex combo]
  This is the load-WEIGHTED-AVERAGE statement; it is STRICTLY WEAKER than the dead pointwise
  max_v T_v <= N+eta (which FAILS at Myc(Grotzsch): maxT=37.10 > 28.16), because <u_f,T> averages
  the load over f's geodesic distribution and smooths out the hub spike.
  TIGHT at balanced C5[t]: every <u_f,T> = N exactly (eta=0).

GATE: on every component, compute (a) the IDENT checks [must all be True], (b) the (BND) margin
N+eta - <u_f,T> for each bad edge [must be >=0], (c) the (CV) margin (N+eta)Gamma-S2 [sanity, must be >=0].
ALL exact Fraction. Report min (BND) margin + binding config; min (CV) margin; viol counts.
"""
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
    beta=len(M); A=F(n)+F(n*n,25)-beta            # A = N + eta
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    comps={}
    for v in range(n): comps.setdefault(cid[v],[]).append(v)
    # p_f vectors and w_f
    pf={}; w={}
    for f in M:
        Ps=cyc[f]; pv=[F(0)]*n
        for P in Ps:
            for v in P: pv[v]+=1
        pf[f]=pv; w[f]=F(ell[f],len(Ps))
    fcomp={f:find(f[0]) for f in M}
    for c,vs in comps.items():
        fs=[f for f in M if fcomp[f]==c]
        if not fs: continue
        S2=sum(T[v]*T[v] for v in vs); G=sum(T[v] for v in vs)
        if G==0: continue
        acc['nc']+=1
        # --- IDENT checks (exact) ---
        Gell=sum(ell[f]*ell[f] for f in fs)
        if G!=Gell: acc['ident_fail']+=1; acc['ident_ex']=acc['ident_ex'] or (name,n,'G!=sum ell^2',str(G),str(Gell))
        for f in fs:
            q1=w[f]*sum(pf[f][v] for v in range(n))   # ||q_f||_1
            if q1!=ell[f]*ell[f]: acc['ident_fail']+=1; acc['ident_ex']=acc['ident_ex'] or (name,n,'||q_f||1!=ell^2',str(f),str(q1))
        # S2 via sum_f ell^2 <u_f,T> ?  <u_f,T> = (w_f/ell_f^2) sum_v p_f(v) T_v
        S2b=F(0)
        uft={}
        for f in fs:
            num=w[f]*sum(pf[f][v]*T[v] for v in range(n))   # = ell_f^2 <u_f,T>
            uft[f]=num/(ell[f]*ell[f])                        # <u_f,T>
            S2b+=num
        if S2b!=S2: acc['ident_fail']+=1; acc['ident_ex']=acc['ident_ex'] or (name,n,'S2 reconstruct',str(S2),str(S2b))
        # --- (CV) direct margin (sanity) ---
        cvm=A*G-S2
        if cvm<acc['cv_minm'][0]: acc['cv_minm']=(cvm,name,n,beta,len(vs),str(G))
        if cvm<0: acc['cv_viol']+=1
        # --- (BND) per-edge margin ---
        for f in fs:
            bm=A-uft[f]            # N+eta - <u_f,T>
            acc['nb']+=1
            if bm<acc['bnd_minm'][0]: acc['bnd_minm']=(bm,name,n,beta,len(vs),str(f),float(uft[f]),float(A))
            if bm<0:
                acc['bnd_viol']+=1
                if acc['bnd_first'] is None:
                    acc['bnd_first']=(name,n,beta,str(f),str(uft[f]),float(A))

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nc':0,'nb':0,'cv_viol':0,'bnd_viol':0,'ident_fail':0,'ident_ex':None,'bnd_first':None,
         'cv_minm':(F(10**18),'','','','',''),'bnd_minm':(F(10**18),'','','','','',0,0)}
    # two-lane + k-lane
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: BND viol=%d  CV viol=%d  ident_fail=%d"%(acc['bnd_viol'],acc['cv_viol'],acc['ident_fail']),flush=True)
    # blow-ups C5/C7/C9[t]
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    # non-uniform blow-ups
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    # Grotzsch / Mycielskians / glued
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued: BND viol=%d  CV viol=%d  ident_fail=%d"%(acc['bnd_viol'],acc['cv_viol'],acc['ident_fail']),flush=True)
    # census geng -tc N=7..11 ALL gmins cuts
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['bnd_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (BND viol+%d)"%(nn,acc['bnd_viol']-v0),flush=True)
    print("\n  IDENT failures (must be 0) = %d  %s"%(acc['ident_fail'],acc['ident_ex'] or ''),flush=True)
    print("  components=%d  per-edge BND checks=%d"%(acc['nc'],acc['nb']),flush=True)
    print("  (CV) violations=%d  MIN (CV) margin=%s at %s"%(acc['cv_viol'],float(acc['cv_minm'][0]),acc['cv_minm'][1:]),flush=True)
    print("  (BND) violations=%d  MIN (BND) margin=%s at %s"%(acc['bnd_viol'],float(acc['bnd_minm'][0]),acc['bnd_minm'][1:]),flush=True)
    if acc['bnd_first']: print("  first BND violation: %s"%(acc['bnd_first'],),flush=True)
    ok = (acc['ident_fail']==0 and acc['bnd_viol']==0)
    print("\n  === (BND) <u_f,T> <= N+eta  per bad edge  %s ;  IDENT %s ;  =>(CV) %s ==="%(
        "HOLDS" if acc['bnd_viol']==0 else "FAILS",
        "OK" if acc['ident_fail']==0 else "BROKEN",
        "PROVEN-ON-BATTERY" if ok else "GAP"),flush=True)
