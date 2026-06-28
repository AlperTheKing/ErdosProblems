"""HUNT: triangle-free graph + gamma-min connected-B MAX cut where ROW-SUM FAILS (fails>0)
but full-g (opencap cert) HOLDS, with |O|>=2. That is a real counterexample.
EXACT only. Validity: gmins (gamma-min connected-B max cuts via maxcut_all=2^N, keep N<=20)."""
import itertools, subprocess
from fractions import Fraction as F
from _opencap import opencap, build_K
from _rowsum import rowsum
from _stark_multi import stark_multi
from _stark1 import odd_blowup, gmins
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

HITS=[]
STATS=dict(inst=0, ocuts=0, rfail=0, maxO=0, minratio=None, hits=0)

def check(nm, n, E):
    if n>20: return
    if not is_triangle_free(n,E): return
    STATS['inst']+=1
    adj,cuts=gmins(n,E)
    for s in cuts:
        rd=rowsum(adj,s,n)
        if rd is None or rd.get('skip'): continue
        STATS['ocuts']+=1
        STATS['maxO']=max(STATS['maxO'], rd['O'])
        if rd.get('minratio') is not None:
            mr=rd['minratio']
            if STATS['minratio'] is None or mr<STATS['minratio']: STATS['minratio']=mr
        if rd['fails']>0:
            STATS['rfail']+=1
            # is this a REAL counterexample? full-g must hold and |O|>=2
            oc=opencap(adj,s,n)
            if oc is None or oc.get('skip') or oc.get('singular'): continue
            if oc.get('cert') and rd['O']>=2:
                STATS['hits']+=1
                K,T=build_K(adj,s,n); N=n
                O=[v for v in range(n) if T[v]>N]
                # find the failing o
                Q=[v for v in range(n) if T[v]<=N]
                sden={q:sum(K[o2][q] for o2 in O) for q in Q}
                fo=None
                for o in O:
                    D=T[o]-N; lhs=F(0)
                    for q in Q:
                        Rq=F(N)-T[q]; den=Rq+sden[q]
                        if den>0 and K[o][q]>0: lhs+=K[o][q]*Rq/den
                    if lhs-D<0: fo=(o,T[o],N); break
                rec=dict(nm=nm,n=n,E=E,side=list(s),O=O,fo=fo,minmarg=rd['minmarg'])
                HITS.append(rec)
                print(f"  *** HIT {nm} n={n} |O|={rd['O']} failing-o={fo} cert=True ***",flush=True)

def summary(tag):
    mr=STATS['minratio']
    print(f"[{tag}] inst={STATS['inst']} O-cuts={STATS['ocuts']} ROWSUM-FAIL={STATS['rfail']} "
          f"maxO={STATS['maxO']} min-ratio={float(mr) if mr is not None else None} HITS={STATS['hits']}",flush=True)

if __name__=="__main__":
    print("=== HUNT ROW-SUM counterexample (Class E) ===",flush=True)
    # --- A. non-uniform C5 blow-ups, full sweep up to n<=20 ---
    for sizes in itertools.product([1,2,3,4,5,6,7,8],repeat=5):
        if sum(sizes)>20: continue
        n,E,adj,side=odd_blowup(5,list(sizes))
        check(f"C5{sizes}",n,E)
    summary("C5 blowups")
    # --- B. non-uniform C7 blow-ups n<=20 ---
    for sizes in itertools.product([1,2,3,4],repeat=7):
        if sum(sizes)>20: continue
        n,E,adj,side=odd_blowup(7,list(sizes))
        check(f"C7{sizes}",n,E)
    summary("+C7 blowups")
    # --- C. C9, C11 small blowups n<=20 ---
    for sizes in itertools.product([1,2],repeat=9):
        if sum(sizes)>20: continue
        n,E,adj,side=odd_blowup(9,list(sizes))
        check(f"C9{sizes}",n,E)
    for sizes in itertools.product([1,2],repeat=11):
        if sum(sizes)>20: continue
        n,E,adj,side=odd_blowup(11,list(sizes))
        check(f"C11{sizes}",n,E)
    summary("+C9/C11")
    # --- D. Mycielskian of small blow-ups (Myc doubles+1: base must be <=9 to stay n<=19) ---
    for sizes in itertools.product([1,2],repeat=5):
        bn=sum(sizes)
        if bn>9: continue
        bN,bE,_,_=odd_blowup(5,list(sizes))
        n,E=mycielski(bN,bE)
        check(f"Myc(C5{sizes})",n,E)
    for sizes in itertools.product([1,2],repeat=7):
        bn=sum(sizes)
        if bn>9: continue
        bN,bE,_,_=odd_blowup(7,list(sizes))
        n,E=mycielski(bN,bE)
        check(f"Myc(C7{sizes})",n,E)
    summary("+Myc(blowups)")
    print("--- DONE ---",flush=True)
    print(f"TOTAL HITS={len(HITS)}",flush=True)
    for h in HITS:
        print(h,flush=True)
