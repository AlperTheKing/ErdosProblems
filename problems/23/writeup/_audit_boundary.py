"""Engineered near-extremal cases to stress condition-(1) strictness (margin N - max K_QQ rowsum -> 0)
and singular Aqq. Take C5[t] (uniform T=N) and perturb: unequal blow-up sizes (C5 with part sizes
t1..t5) which creates over/under-load. These are the structures closest to the extremal where
K_QQ row sums can approach N. Test full cert exact + report margin = N - max KQQ rowsum and singular."""
from fractions import Fraction as F
from _h import loads
from _audit_stress import full_test, report
from _audit_strictness import aqq_data

def c5_unequal(sizes):
    """C5 with part i blown to sizes[i]; edges between consecutive parts (complete bipartite)."""
    off=[0];
    for s in sizes: off.append(off[-1]+s)
    n=off[5]; E=[]
    for i in range(5):
        for a in range(sizes[i]):
            for b in range(sizes[(i+1)%5]):
                E.append((off[i]+a, off[(i+1)%5]+b))
    return n,E

if __name__=="__main__":
    print("=== engineered unequal C5 blow-ups (near-extremal, push margin to 0) ===",flush=True)
    import itertools
    cases=[]
    # vary part sizes around equal; small unequal perturbations create overload
    for sizes in [(3,3,3,3,2),(4,3,3,3,3),(4,4,3,3,3),(5,4,4,4,4),(2,2,2,2,3),(3,2,2,2,2),
                  (4,4,4,4,3),(5,5,4,4,4),(3,3,3,2,2),(4,3,4,3,2),(5,4,3,4,3),(2,3,2,3,2)]:
        n,E=c5_unequal(sizes)
        if n>24: continue
        cases.append((sizes,n,E))
    worst_margin=None; sing=0; fails=0; tested=0; mb=0; zeromargin=0
    for sizes,n,E in cases:
        info=loads(n,E)
        if info is None: print(f"  {sizes} N={n}: loads=None",flush=True); continue
        d=aqq_data(info)
        res=full_test(info)
        st=res['status']
        if d is None:
            print(f"  {sizes} N={n}: noO (T uniform or balanced)",flush=True); continue
        tested+=1
        if d['singular']: sing+=1
        mb=max(mb,d['n_boundary'])
        if d['margin']<=0: zeromargin+=1
        if worst_margin is None or d['margin']<worst_margin: worst_margin=d['margin']
        flag=''
        if st=='FAIL': fails+=1; flag=' '+report(str(sizes),n,res)
        elif st=='SINGULAR_AQQ': flag=' SINGULAR'
        print(f"  {sizes} N={n}: {st} margin(N-maxKQQrow)={float(d['margin']):+.4f} #boundary(T=N)={d['n_boundary']} "
              f"{'minrow='+str(float(res['minrow']))+' k2='+str(float(res['mink2'])) if st=='ok' else ''}{flag}",flush=True)
    print(f"  SUMMARY: tested {tested} | singular={sing} | margin<=0:{zeromargin} | worst margin={float(worst_margin) if worst_margin is not None else 'na'} | max #boundary={mb} | FAILS={fails}",flush=True)
