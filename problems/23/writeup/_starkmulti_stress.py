"""Stress STAR-K-multi on NON-UNIFORM |O|>=2 blow-ups via PROPER gamma-min cuts (the frontier that killed STAR-O1).
   Compare STAR-K-multi (sufficient) vs full-g (always holds) -- if STAR-K-multi fails where full-g holds, it's too
   lossy for |O|>=2. C5/C7 blow-ups with small bad-endpoint parts (|O|>=2), N<=22 for gmins feasibility."""
import itertools
from fractions import Fraction as F
from _stark1 import odd_blowup, gmins
from _opencap import opencap
from _stark_multi import stark_multi

def stress(m, size_choices, maxN=22, maxinst=400):
    tot=0; smfail=0; fgfail=0; both=0; o2=0; worst=None
    seen=0
    for sizes in itertools.product(size_choices, repeat=m):
        n=sum(sizes)
        if n>maxN or n<m: continue
        # need small bad-endpoint parts to get |O|>=2: parts 0 and m-1 (the same-side adjacent pair for odd m)
        if sizes[0]>3 and sizes[m-1]>3: continue
        seen+=1
        if seen>maxinst: break
        nn,E,adj,side=odd_blowup(m,list(sizes))
        adj2,cuts=gmins(n,E)
        for s in cuts:
            sm=stark_multi(adj2,s,n)
            if sm is None or sm.get('skip'): continue
            if sm['O']<2: continue
            tot+=1; o2+=1
            fg=opencap(adj2,s,n)
            fgok = fg['cert'] if (fg and not fg.get('skip')) else None
            if not sm['psd']:
                smfail+=1
                if fgok:
                    if worst is None: worst=(m,sizes,sm['O'])
            if fgok is False: fgfail+=1
            if (not sm['psd']) and fgok: both+=1
    return dict(seen=seen,tot=tot,o2=o2,smfail=smfail,fgfail=fgfail,sm_fail_fg_ok=both,worst=worst)

if __name__=="__main__":
    print("=== STAR-K-multi stress on NON-UNIFORM |O|>=2 blow-ups (gamma-min cuts) ===",flush=True)
    r=stress(5,[1,2,3,5,7,9,11],maxN=22)
    print(f"  C5 non-uniform: instances scanned={r['seen']} |O|>=2 cuts={r['o2']} STARK-multi-FAIL={r['smfail']} (of which full-g-OK={r['sm_fail_fg_ok']}) full-g-FAIL={r['fgfail']} worst={r['worst']}",flush=True)
    r7=stress(7,[1,2,3,5,7],maxN=22)
    print(f"  C7 non-uniform: instances scanned={r7['seen']} |O|>=2 cuts={r7['o2']} STARK-multi-FAIL={r7['smfail']} (of which full-g-OK={r7['sm_fail_fg_ok']}) full-g-FAIL={r7['fgfail']} worst={r7['worst']}",flush=True)
