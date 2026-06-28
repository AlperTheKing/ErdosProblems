"""HUNT batch 2: long-corridor / glued / blowup-of-Mycielskian constructions, |O|>=2.
Same counterexample criterion: ROW-SUM fails but opencap cert holds, |O|>=2, gamma-min connected-B max cut, EXACT."""
import itertools
from fractions import Fraction as F
from _opencap import opencap, build_K
from _rowsum import rowsum
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
            oc=opencap(adj,s,n)
            if oc is None or oc.get('skip') or oc.get('singular'): continue
            if oc.get('cert') and rd['O']>=2:
                STATS['hits']+=1
                K,T=build_K(adj,s,n); N=n
                O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
                sden={q:sum(K[o2][q] for o2 in O) for q in Q}
                fo=None
                for o in O:
                    D=T[o]-N; lhs=F(0)
                    for q in Q:
                        Rq=F(N)-T[q]; den=Rq+sden[q]
                        if den>0 and K[o][q]>0: lhs+=K[o][q]*Rq/den
                    if lhs-D<0: fo=(o,T[o],N); break
                HITS.append(dict(nm=nm,n=n,E=E,side=list(s),O=O,fo=fo))
                print(f"  *** HIT {nm} n={n} |O|={rd['O']} failing-o={fo} cert=True ***",flush=True)

def summary(tag):
    mr=STATS['minratio']
    print(f"[{tag}] inst={STATS['inst']} O-cuts={STATS['ocuts']} ROWSUM-FAIL={STATS['rfail']} "
          f"maxO={STATS['maxO']} min-ratio={float(mr) if mr is not None else None} HITS={STATS['hits']}",flush=True)

def odd_path_glue(m1, s1, m2, s2, link):
    """Two odd-cycle blowups glued by extra edges between them (corridor)."""
    n1,E1,_,_=odd_blowup(m1,list(s1))
    n2,E2,_,_=odd_blowup(m2,list(s2))
    n,E=union_disjoint((n1,E1),(n2,E2))
    for (a,b) in link: E=E+[(a, n1+b)]
    return n,E

if __name__=="__main__":
    print("=== HUNT batch 2: corridors / glued / blowup-of-Myc ===",flush=True)
    # --- E. glued two odd cycles via single/double bridge (corridors) ---
    for s1 in itertools.product([1,2,3],repeat=5):
        for s2 in itertools.product([1,2],repeat=5):
            n1=sum(s1); n2=sum(s2)
            if n1+n2>20: continue
            # bridge between part-0 vertex of each
            n,E=odd_path_glue(5,s1,5,s2,[(0,0)])
            check(f"C5{s1}-C5{s2}/b1",n,E)
    summary("C5-C5 single bridge")
    # double bridge variants on a smaller set
    for s1 in itertools.product([1,2],repeat=5):
        for s2 in itertools.product([1,2],repeat=5):
            if sum(s1)+sum(s2)>20: continue
            n,E=odd_path_glue(5,s1,5,s2,[(0,0),(2,3)])
            check(f"C5{s1}-C5{s2}/b2",n,E)
    summary("+C5-C5 double bridge")
    # --- F. C5 island + Mycielski(C5)/Mycielski(C7) gadget (carries O) with bridges ---
    g11=mycielski(5,Cn(5))   # Grotzsch N=11
    g15=mycielski(7,Cn(7))   # N=15
    for iszt in [[1,1,1,1,1],[2,1,1,1,1],[1,2,1,2,1]]:
        iN,iE,_,_=odd_blowup(5,iszt)
        for (gN,gE) in [g11,g15]:
            if iN+gN>20: continue
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                check(f"C5{iszt}+gad{gN}{br}",n,E)
    summary("+island+Myc gadget")
    # --- G. blow-up of Mycielskian(C5)=Grotzsch by 2 is too big (22); do partial: Myc(C5) with one part doubled ---
    # blow-up of a small Mycielskian: Myc(C5)=11 nodes, blow one vertex by t to stay <=20
    g11N,g11E=g11
    for v in range(g11N):
        for t in [2,3,5]:
            # duplicate vertex v t-1 times (independent copies sharing neighbors) -> still triangle-free if v's nbhd indep
            extra=t-1
            n=g11N+extra; E=list(g11E)
            nbr=set()
            for a,b in g11E:
                if a==v: nbr.add(b)
                if b==v: nbr.add(a)
            for c in range(extra):
                nv=g11N+c
                for w in nbr: E.append((nv,w))
            if n>20: continue
            check(f"Myc(C5)-blow-v{v}x{t}",n,E)
    summary("+Grotzsch vertex-blowup")
    print("--- DONE ---",flush=True)
    print(f"TOTAL HITS={len(HITS)}",flush=True)
    for h in HITS: print(h,flush=True)
