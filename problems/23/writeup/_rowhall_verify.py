"""Consolidated adversarial verification of Codex's row-Hall decomposition (blocks 101/103/109):
   for each o in O and every subset H of bad edges (full enum, small |M|):
     X_f=sum_{o' in O}p_f(o'); psi_o(q)=K[o,q]/(R_q+s_q); c_f(o)=X_f(p_f(o)+sum_q psi_o(q)p_f(q));
     A_H(v)=sum_{f in H} X_f p_f(v).
   (RH)  ROW-HALL:      sum_{f in H} c_f(o) <= |union supp(p_f)|
   (TM)  truncated-mass: sum_{f in H} c_f(o) <= sum_v min(1, A_H(v))
   (QC)  Q-CAP:         sum_{q in Q} psi_o(q) A_H(q) <= sum_{q in Q} min(1, A_H(q))
   Tested on the ADVERSARIAL small-|M| gate (Mycielskians, glued, small non-uniform blow-ups) -- coverage
   beyond Codex's N=11 census. Exact Fraction."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins

def pf_dict(cyc, f):
    Ps=cyc[f]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d

def verify(adj, side, n, maxM=14):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T2,mu,cyc=st
    if len(M)>maxM: return dict(skip='bigM', nbad=len(M))
    K,T=build_K(adj,side,n); N=n
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip='Oempty')
    pf={f:pf_dict(cyc,f) for f in M}
    supp={f:set(pf[f].keys()) for f in M}
    Xf={f:sum(pf[f].get(o,F(0)) for o in O) for f in M}
    s={q:sum(K[o][q] for o in O) for q in Q}
    res={'O':len(O),'nbad':len(M),'RH_fail':0,'TM_fail':0,'QC_fail':0}
    Ml=list(M)
    for o in O:
        psi={q:(K[o][q]/(F(N)-T[q]+s[q])) for q in Q if (F(N)-T[q]+s[q])>0}
        cf={f: Xf[f]*(pf[f].get(o,F(0)) + sum(psi.get(q,F(0))*pf[f].get(q,F(0)) for q in Q)) for f in M}
        for r in range(1,1<<len(Ml)):
            H=[Ml[i] for i in range(len(Ml)) if r>>i&1]
            # A_H on all vertices
            AH={}
            for f in H:
                for v,pv in pf[f].items(): AH[v]=AH.get(v,F(0))+Xf[f]*pv
            dem=sum(cf[f] for f in H)
            unionsupp=len(set().union(*[supp[f] for f in H]))
            tmcap=sum(min(F(1),AH.get(v,F(0))) for v in AH)
            qclhs=sum(psi.get(q,F(0))*AH.get(q,F(0)) for q in Q)
            qcrhs=sum(min(F(1),AH.get(q,F(0))) for q in Q)
            if dem>unionsupp: res['RH_fail']+=1
            if dem>tmcap: res['TM_fail']+=1
            if qclhs>qcrhs: res['QC_fail']+=1
    return res

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=verify(adj,s,n)
        if d is None or d.get('skip'): continue
        acc['tot']+=1
        acc['RH']+=d['RH_fail']; acc['TM']+=d['TM_fail']; acc['QC']+=d['QC_fail']
        acc['maxO']=max(acc['maxO'],d['O'])

if __name__=="__main__":
    print("=== row-Hall decomposition adversarial verify (RH / TM / QC), exact, small |M| ===",flush=True)
    G11=mycielski(5,Cn(5)); G23=mycielski(*G11); M15=mycielski(7,Cn(7))
    for nm,g in [("Grotzsch11",G11),("Myc2C5_23",G23),("MycC7_15",M15)]:
        a={'tot':0,'RH':0,'TM':0,'QC':0,'maxO':0}; run(nm,g[0],g[1],a)
        print(f"  {nm}: O-cuts={a['tot']} RH-FAIL={a['RH']} TM-FAIL={a['TM']} QC-FAIL={a['QC']} maxO={a['maxO']}",flush=True)
    # small non-uniform blow-ups with |O|>=1, small |M| (keep bad-endpoint parts tiny so |M| small)
    ab={'tot':0,'RH':0,'TM':0,'QC':0,'maxO':0}
    for sizes in [[1,3,2,2,3],[2,3,2,2,3],[1,4,3,2,4],[2,4,2,3,4],[1,5,3,2,5]]:
        n,E,adj,side=odd_blowup(5,sizes); run(f"C5{sizes}",n,E,ab)
    print(f"  small non-uniform C5 blow-ups: O-cuts={ab['tot']} RH-FAIL={ab['RH']} TM-FAIL={ab['TM']} QC-FAIL={ab['QC']} maxO={ab['maxO']}",flush=True)
    # glued battery (small |M|)
    ag={'tot':0,'RH':0,'TM':0,'QC':0,'maxO':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,ag)
    print(f"  glued battery: O-cuts={ag['tot']} RH-FAIL={ag['RH']} TM-FAIL={ag['TM']} QC-FAIL={ag['QC']} maxO={ag['maxO']}",flush=True)
    # census N=9,10 (small |M| mostly)
    for nnn in (9,10):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'RH':0,'TM':0,'QC':0,'maxO':0}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: O-cuts={acc['tot']} RH-FAIL={acc['RH']} TM-FAIL={acc['TM']} QC-FAIL={acc['QC']} maxO={acc['maxO']}",flush=True)
