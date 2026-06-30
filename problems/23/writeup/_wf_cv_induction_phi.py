"""ROUTE INDUCTION (amortized).  The naive per-step STEP_t <= (N+eta_r)ell^2 is FALSE (C5[5] margin -560).
Correct telescoping invariant = RUNNING potential
   Phi_t = (N+eta_r)*Gamma_{c,t} - sum_v T_t(v)^2 ,   Gamma_{c,t}=sum_{s<=t} ell_{f_s}^2,  T_t=prefix load.
Phi_0=0, Phi_r = (CV) margin.  We GATE whether Phi_t >= 0 for ALL prefixes t and ALL tested edge orders,
and ALSO the per-order minimum (does SOME order keep it >=0 -- a 'good order' would give an induction).
Exact Fraction, full standing battery (model on _cv_gate.py)."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords
from _wf_cv_induction import comp_edges, step_terms, blowup, adj_of, bridge, orders

def phi_run(badlist, vs, n, Afin):
    """Return (min Phi over prefixes, prefix index of min) for ONE order = badlist as given.
    Phi_t = Afin*Gamma_t - sum_v T_t^2. Use incremental: sum_v T_t^2 = sum T_{t-1}^2 + STEP_t."""
    prefixT=[F(0)]*n
    Gamma=F(0); S2=F(0)
    minphi=None; argmin=0
    for t,(f,wf,pf,l) in enumerate(badlist,start=1):
        step=step_terms(prefixT,wf,pf,vs)
        S2+=step
        Gamma+=F(l*l)
        for v in vs: prefixT[v]+=wf*pf[v]
        phi=Afin*Gamma - S2
        if minphi is None or phi<minphi: minphi=phi; argmin=t
    return minphi,argmin

def chk(name, n, adj, side, acc):
    if not Bconn(n,adj,side): return
    res=comp_edges(n,adj,side)
    if res is None: return
    beta,comps,comp_bad,T=res
    N=n
    Afin=F(N)+F(N*N,25)-beta
    for c,badlist in comp_bad.items():
        if not badlist: continue
        vs=comps[c]
        # ANY-ORDER: min over prefixes for each tested order
        bestorder_minphi=None    # the largest (best) min-phi across orders -> does some order stay >=0
        worst_minphi=None        # smallest min-phi across orders
        for oname,perm in orders(badlist):
            mp,arg=phi_run(perm,vs,n,Afin)
            acc['nrun']+=1
            if bestorder_minphi is None or mp>bestorder_minphi[0]: bestorder_minphi=(mp,oname,arg)
            if worst_minphi is None or mp<worst_minphi[0]: worst_minphi=(mp,oname,arg)
            if mp<0:
                acc['negruns']+=1
        acc['ncomp']+=1
        # track: does the BEST order keep Phi>=0?
        if bestorder_minphi[0]<0:
            acc['noGoodOrder']+=1
            if acc['firstNoGood'] is None:
                acc['firstNoGood']=(name,N,beta,len(vs),str(bestorder_minphi[0]),bestorder_minphi[1])
        if bestorder_minphi[0]<acc['minBest'][0]:
            acc['minBest']=(bestorder_minphi[0],name,N,beta,len(vs),bestorder_minphi[1],bestorder_minphi[2])
        if worst_minphi[0]<acc['minWorst'][0]:
            acc['minWorst']=(worst_minphi[0],name,N,beta,len(vs),worst_minphi[1])

if __name__=="__main__":
    acc=dict(nrun=0,ncomp=0,negruns=0,noGoodOrder=0,firstNoGood=None,
             minBest=(F(10**18),),minWorst=(F(10**18),))
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: negruns=%d noGoodOrder=%d"%(acc['negruns'],acc['noGoodOrder']),flush=True)
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
    print("  blow-ups + Mycielskians + glued done (noGoodOrder=%d)"%acc['noGoodOrder'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['noGoodOrder']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (noGoodOrder+%d)"%(nn,acc['noGoodOrder']-v0),flush=True)
    print("\n  runs=%d  components=%d"%(acc['nrun'],acc['ncomp']),flush=True)
    print("  negative-Phi runs (some order dips <0)=%d"%acc['negruns'],flush=True)
    print("  components with NO good order (best order still dips <0)=%d"%acc['noGoodOrder'],flush=True)
    print("    MIN best-order minPhi = %s at (name,N,beta,|c|,order,arg)=%s"%(float(acc['minBest'][0]),acc['minBest'][1:]),flush=True)
    print("    MIN worst-order minPhi = %s at (name,N,beta,|c|,order)=%s"%(float(acc['minWorst'][0]),acc['minWorst'][1:]),flush=True)
    if acc['firstNoGood']: print("    first NO-good-order: %s"%(acc['firstNoGood'],),flush=True)
    print("\n  === some-order Phi_t>=0 (amortized induction feasible) %s ==="%("HOLDS" if not acc['noGoodOrder'] else "FAILS for some component"),flush=True)
