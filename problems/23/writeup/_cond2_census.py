"""Full-census exact decomposition check for cond(2)-free claim, ALL graphs N<=11.
For every triangle-free connected G with an overloaded set O (|O|>=1):
 verify (i) (N I - K_QQ)^{-1} exists & entrywise >=0 [cond1], (ii) for every offdiag o!=o',
 term2 q := K[o,Q] Inv K[Q,o'] >= 0, (iii) E[o,o'] = -K[o,o'] - q <= 0.
Reports per-N: configs-with-O, singular_AQQ, cond1 inv-neg, q-neg, E-offdiag>0. Exact Fractions."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond2_free import analyze

def run(nn, stride=1):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    cfg=0; withO=0; sing=0; invneg=0; qneg=0; c2fail=0; off2=0
    gmin_inv=None; gmin_q=None; gmax_E=None
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        cfg+=1
        r=analyze(info)
        if r is None: continue            # no O
        if r['status']=='SINGULAR_AQQ': sing+=1; continue
        withO+=1
        if r['inv_min']<0: invneg+=1
        if gmin_inv is None or r['inv_min']<gmin_inv: gmin_inv=r['inv_min']
        if r['worst_q'] is not None:
            off2+=1
            if r['worst_q']<0: qneg+=1
            if gmin_q is None or r['worst_q']<gmin_q: gmin_q=r['worst_q']
        if r['worst_E'] is not None and (gmax_E is None or r['worst_E']>gmax_E): gmax_E=r['worst_E']
        if not r['cond2_holds']: c2fail+=1
    print(f"N={nn}(str{stride}): cfg={cfg} withO={withO} (|O|>=2:{off2}) sing={sing} | "
          f"invneg={invneg}(min={float(gmin_inv) if gmin_inv is not None else 'na'}) | "
          f"qneg={qneg}(min q={float(gmin_q) if gmin_q is not None else 'na'}) | "
          f"E_offdiag>0 fails={c2fail}(max E={float(gmax_E) if gmax_E is not None else 'na'})",flush=True)

if __name__=="__main__":
    import sys
    args=[(int(a.split(':')[0]),int(a.split(':')[1])) for a in sys.argv[1:]] if len(sys.argv)>1 else [(7,1),(8,1),(9,1),(10,1),(11,1)]
    for nn,st in args: run(nn,st)
