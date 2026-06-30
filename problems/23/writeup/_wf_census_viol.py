"""Find the FIRST census tri-free graph (N=9,10) with a genuine BLOCK-SBC violation on a
   gamma-min connected-B GLOBAL-MAX cut (gmins). Confirm via EXACT PSD + report full detail."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _wf_adversarial import adj_of, block_sbc_components
from _stark1 import gmins

for nn in (9,10):
    outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
    found=None
    for g6 in outg:
        n,E=dec(g6); adj,cuts=gmins(n,E)
        for ci,side in enumerate(cuts):
            recs=block_sbc_components(n,adj,side)
            if recs is None: continue
            for r in recs:
                if r['violation']:
                    found=(g6,n,E,side,r); break
            if found: break
        if found: break
    if found:
        g6,n,E,side,r=found
        print(f"N={nn} FIRST census violator g6={g6}")
        print(f"  edges={sorted(E)}")
        print(f"  side={side}")
        print(f"  component C={r['C']} n_C={r['n_C']} m_C={r['m_C']}")
        print(f"  rho_lower(allones)={r['LB_allones']} true_rho~{r['frho']:.4f}")
        print(f"  RHS=n_C+n_C^2/25={r['RHS']}={float(r['RHS']):.4f}  LHS_low=rho_lb+m_C={r['LHS_low']}={float(r['LHS_low']):.4f}")
        print(f"  sbc_holds(PSD)={r['sbc_holds']}  -> VIOLATION={r['violation']}")
    else:
        print(f"N={nn}: no census violator found")
