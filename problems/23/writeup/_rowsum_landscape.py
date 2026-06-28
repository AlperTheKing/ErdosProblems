"""Honest landscape of ROWSUM-O margins on full census + understand the decomposition
   C(f) = ||p_f||^2 + sum_{g!=f} <p_f,p_g>.
Track:
  - worst C(f)/N (should be 1.0 at extremals, <1 else)
  - the split: diag=||p_f||^2, off=sum_{g!=f}<p_f,p_g>
  - At the worst (near-tight non-extremal) cases, what does the off-diagonal look like?
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def run(nmin,nmax):
    print("=== ROWSUM-O honest landscape (full census) ===")
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        worst=F(-10); wd=None; viol=0; nf=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']
            pfs={f:pf_vec(info,f) for f in M}
            S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
            for f in M:
                nf+=1
                Cf=sum(pfs[f][v]*S[v] for v in pfs[f])
                if Cf>n: viol+=1
                if Cf-n>worst:
                    diag=sum(v*v for v in pfs[f].values())
                    worst=Cf-n; wd=(g6,f,float(Cf),n,float(diag),float(Cf-diag))
        print(f"  N={nn}: bad_edges={nf} viol={viol} | worst (C-N)={float(worst):+.4f} @ {wd}",flush=True)

if __name__=="__main__":
    run(7,11)
