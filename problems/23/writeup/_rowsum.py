"""Codex block 100: ROW-SUM strengthening of STAR-K-multi (per-overloaded-vertex scalar; multi-O analog of STAR-K1).
   Z = N I_O - K_OO - sum_q k_q k_q^T/(R_q+s_q) is a Z-matrix (off-diag <=0). Nonneg row sums => diag dominant => PSD => cond3.
   (ROW-SUM):  for every o in O,  sum_{q in Q} K[o,q] R_q/(R_q+s_q) >= T(o)-N.    (=STAR-K1 when |O|=1.)
   Test ROW-SUM on full gate; compare to STAR-K-multi (which holds) to see if ROW-SUM is strictly stronger."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins
from _stark_multi import stark_multi

def rowsum(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip=True)
    s={q:sum(K[o][q] for o in O) for q in Q}
    fails=0; minmarg=None; minratio=None
    for o in O:
        D=T[o]-N
        lhs=F(0)
        for q in Q:
            Rq=F(N)-T[q]; den=Rq+s[q]
            if den>0 and K[o][q]>0: lhs+=K[o][q]*Rq/den
        marg=lhs-D
        if marg<0: fails+=1
        if minmarg is None or marg<minmarg: minmarg=marg
        if D>0:
            rr=lhs/D
            if minratio is None or rr<minratio: minratio=rr
    return dict(O=len(O),fails=fails,minmarg=minmarg,minratio=minratio)

def run(nm,n,E,acc,report=False):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=rowsum(adj,s,n)
        if d is None or d.get('skip'): continue
        acc['tot']+=1
        if d['fails']>0:
            acc['rfail']+=1
            sm=stark_multi(adj,s,n)  # does STAR-K-multi still hold there?
            if sm and sm['psd']: acc['rfail_smok']+=1
        if d['minratio'] is not None and (acc['minratio'] is None or d['minratio']<acc['minratio']):
            acc['minratio']=d['minratio']; acc['wit']=(nm,)
        acc['maxO']=max(acc['maxO'],d['O'])
    if report and acc['tot']:
        print(f"  {nm}: O-cuts={acc['tot']} ROWSUM-FAIL={acc['rfail']} (STARK-multi-still-ok={acc['rfail_smok']}) maxO={acc['maxO']} min-ratio={float(acc['minratio']) if acc['minratio'] else None}",flush=True)

if __name__=="__main__":
    print("=== ROW-SUM (per-o): sum_q K[o,q]R_q/(R_q+s_q) >= T(o)-N ===",flush=True)
    from _superphi import blow
    G11=mycielski(5,Cn(5)); G23=mycielski(*G11); M15=mycielski(7,Cn(7))
    for nm,gen in [("Grotzsch=N11",G11),("Myc2(C5)=N23",G23),("MycC7=N15",M15)]:
        a={'tot':0,'rfail':0,'rfail_smok':0,'minratio':None,'wit':None,'maxO':0}; run(nm,gen[0],gen[1],a,True)
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); a={'tot':0,'rfail':0,'rfail_smok':0,'minratio':None,'wit':None,'maxO':0}; run(f"{g6}[{t}]",nn,EE,a,True)
    ag={'tot':0,'rfail':0,'rfail_smok':0,'minratio':None,'wit':None,'maxO':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,ag)
    print(f"  glued battery: O-cuts={ag['tot']} ROWSUM-FAIL={ag['rfail']} (STARK-multi-ok={ag['rfail_smok']}) maxO={ag['maxO']} min-ratio={float(ag['minratio']) if ag['minratio'] else None}",flush=True)
    # non-uniform C5 |O|>=2 (via gmins)
    import itertools
    an={'tot':0,'rfail':0,'rfail_smok':0,'minratio':None,'wit':None,'maxO':0}; seen=0
    for sizes in itertools.product([1,2,3,5,7,9],repeat=5):
        if sum(sizes)>22 or (sizes[0]>3 and sizes[4]>3): continue
        seen+=1
        if seen>300: break
        n,E,adj,side=odd_blowup(5,list(sizes)); run(f"C5{sizes}",n,E,an)
    print(f"  non-uniform C5 (|O| any): O-cuts={an['tot']} ROWSUM-FAIL={an['rfail']} (STARK-multi-ok={an['rfail_smok']}) maxO={an['maxO']} min-ratio={float(an['minratio']) if an['minratio'] else None}",flush=True)
    for nnn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'rfail':0,'rfail_smok':0,'minratio':None,'wit':None,'maxO':0}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}: O-cuts={acc['tot']} ROWSUM-FAIL={acc['rfail']} (STARK-multi-ok={acc['rfail_smok']}) maxO={acc['maxO']} min-ratio={float(acc['minratio']) if acc['minratio'] else None}",flush=True)
