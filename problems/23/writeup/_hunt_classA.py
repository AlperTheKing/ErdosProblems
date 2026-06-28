"""CLASS A hunt: extreme non-uniform odd-cycle blow-ups C5/C7/C9.
Look for: triangle-free, gamma-min connected-B MAX cut (via gmins), |O|>=2,
ROW-SUM fails (rowsum 'fails'>0) BUT full-g holds (opencap cert==True).
EXACT only. Route ALL blow-ups through gmins for valid gamma-min cuts."""
import itertools, sys
from fractions import Fraction as F
from _rowsum import rowsum
from _opencap import opencap
from _stark1 import gmins, odd_blowup
from _bdef_construct import is_triangle_free

def cycle_edges(m, sizes):
    n=sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                E.append((start[i]+a, start[j]+b))
    return n,E

def test_instance(m, sizes, acc):
    n,E=cycle_edges(m,sizes)
    if not is_triangle_free(n,E): return
    adj,cuts=gmins(n,E)   # gamma-min connected-B MAX cuts only
    for s in cuts:
        rs=rowsum(adj,s,n)
        if rs is None or rs.get('skip'): continue
        acc['cuts']+=1
        acc['maxO']=max(acc['maxO'], rs['O'])
        if rs['minratio'] is not None:
            fr=float(rs['minratio'])
            if acc['minratio'] is None or fr<acc['minratio']: acc['minratio']=fr
        if rs['fails']>0:
            acc['rfail']+=1
            oc=opencap(adj,s,n)
            if oc and not oc.get('skip') and not oc.get('singular') and oc.get('cert') and rs['O']>=2:
                # REAL COUNTEREXAMPLE candidate
                # find a failing o
                acc['hits'].append((m,sizes,list(s),n,E))
                print(f"!!! CANDIDATE m={m} sizes={sizes} n={n} O={rs['O']} side={list(s)}", flush=True)

def main():
    acc={'cuts':0,'rfail':0,'maxO':0,'minratio':None,'hits':[]}
    inst=0
    # C5: drive multiple overloaded vertices. Bad-endpoint same-side pair is parts 0 and 4 (adjacent, same parity).
    # Make several parts small to create overloads. Sweep widely with N<=20.
    sizevals=[1,2,3,4,5,6,7,9,11,13]
    for sizes in itertools.product(sizevals,repeat=5):
        if sum(sizes)>20: continue
        inst+=1
        test_instance(5,sizes,acc)
    print(f"[C5 done] instances={inst} cuts={acc['cuts']} rfail={acc['rfail']} maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)

    # C7: N<=20, parts small near the bad pair
    inst7=0
    for sizes in itertools.product([1,2,3,4,5],repeat=7):
        if sum(sizes)>20: continue
        inst7+=1
        test_instance(7,sizes,acc)
    print(f"[C7 done] instances+={inst7} cuts={acc['cuts']} rfail={acc['rfail']} maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)

    # C9: N<=20
    inst9=0
    for sizes in itertools.product([1,2,3],repeat=9):
        if sum(sizes)>20: continue
        inst9+=1
        test_instance(9,sizes,acc)
    print(f"[C9 done] instances+={inst9} cuts={acc['cuts']} rfail={acc['rfail']} maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)

    total_inst=inst+inst7+inst9
    print(f"=== TOTAL instances={total_inst} cuts={acc['cuts']} rfail={acc['rfail']} maxO={acc['maxO']} minratio={acc['minratio']} CANDIDATES={len(acc['hits'])} ===",flush=True)
    for h in acc['hits']:
        print("HIT:",h,flush=True)

if __name__=="__main__":
    main()
