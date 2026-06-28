"""CLASS A hunt v2 (faster): non-uniform C5/C7/C9 blow-ups, N<=16 bulk + targeted extreme N=17..20.
Reports any triangle-free, gamma-min connected-B MAX cut (gmins) with |O|>=2 where ROW-SUM fails
but opencap cert holds. EXACT."""
import itertools, sys
from fractions import Fraction as F
from _rowsum import rowsum
from _opencap import opencap
from _stark1 import gmins
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
    adj,cuts=gmins(n,E)
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
            certok = oc and not oc.get('skip') and not oc.get('singular') and oc.get('cert')
            if certok and rs['O']>=2:
                acc['hits'].append((m,sizes,list(s),n,E,rs['O']))
                print(f"!!! CANDIDATE m={m} sizes={sizes} n={n} O={rs['O']}", flush=True)
            elif rs['fails']>0:
                # rowsum failed but either cert also fails or |O|<2 -- log a near-miss summary
                acc['rfail_certok' if certok else 'rfail_certbad']+=1

def sweep(m, vals, Ncap, acc):
    cnt=0
    for sizes in itertools.product(vals,repeat=m):
        if sum(sizes)>Ncap: continue
        cnt+=1
        test_instance(m,sizes,acc)
    return cnt

def main():
    acc={'cuts':0,'rfail':0,'rfail_certok':0,'rfail_certbad':0,'maxO':0,'minratio':None,'hits':[],'inst':0}
    # C5 bulk N<=16 exhaustive over rich value set
    acc['inst']+=sweep(5,[1,2,3,4,5,6,8,10,12],16,acc)
    print(f"[C5 N<=16] inst={acc['inst']} cuts={acc['cuts']} rfail={acc['rfail']} (certok={acc['rfail_certok']} certbad={acc['rfail_certbad']}) maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)
    # C7 bulk N<=16
    c=sweep(7,[1,2,3,4],16,acc); acc['inst']+=c
    print(f"[C7 N<=16] +inst={c} cuts={acc['cuts']} rfail={acc['rfail']} (certok={acc['rfail_certok']} certbad={acc['rfail_certbad']}) maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)
    # C9 bulk N<=16
    c=sweep(9,[1,2],16,acc); acc['inst']+=c
    c2=sweep(9,[1,2,3],17,acc); acc['inst']+=c2
    print(f"[C9] +inst cuts={acc['cuts']} rfail={acc['rfail']} (certok={acc['rfail_certok']} certbad={acc['rfail_certbad']}) maxO={acc['maxO']} minratio={acc['minratio']} hits={len(acc['hits'])}",flush=True)
    print(f"=== TOTAL inst={acc['inst']} cuts={acc['cuts']} rfail={acc['rfail']} (certok&|O|>=2 CANDIDATES={len(acc['hits'])}, certok-but-not-cand={acc['rfail_certok']}, certbad={acc['rfail_certbad']}) maxO={acc['maxO']} minratio={acc['minratio']} ===",flush=True)
    for h in acc['hits']:
        print("HIT:",h,flush=True)

if __name__=="__main__":
    main()
