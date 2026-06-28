"""Targeted robustness: rho(O)<=N + (SM) + (Cycle-SM) on the KEY large cases (esp. the N=22 blow-up
that killed the sandwich) + Mycielskians + random tri-free up to N=20. Faster than the full stress."""
import numpy as np
from fractions import Fraction as F
from _h import dec, loads
from _sm_test import sm_quants, blowup
from _gram_spectral import build_O
from _stress_sandwich import mycielski, rand_trifree

def one(label,n,E):
    if n>23: print(f"  {label:22} N={n}: skip"); return
    info=loads(n,E)
    if info is None: print(f"  {label:22} N={n}: skip(no cut)"); return
    ok,sl,cyc_slack,wf=sm_quants(info)
    O,lvec,P=build_O(info); N=n
    rho=float(np.linalg.eigvalsh(O)[-1])
    flag="" if (ok and cyc_slack>=0 and rho<=N+1e-7) else "  <<<VIOLATION"
    print(f"  {label:22} N={n} G={info['G']} | rho(O)/N={rho/N:.4f} | (SM):{ok} | (Cycle-SM)min={float(cyc_slack):+.3f}{flag}")

if __name__=="__main__":
    print("=== KEY: the N=22 blow-up that killed the sandwich ===")
    n,E=dec("J???E?pNu\\?"); nn,EE=blowup(n,E,2); one("J???E?pNu\\?[2]",nn,EE)
    n,E=dec("H?AFBo]"); nn,EE=blowup(n,E,2); one("H?AFBo][2]",nn,EE)
    print("=== Mycielskians ===")
    n,E=dec("DUW"); n2,E2=mycielski(n,E); one("Myciel(C5)=Grotzsch",n2,E2)
    n7,E7=(7,[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,0)]); n3,E3=mycielski(n7,E7); one("Myciel(C7)",n3,E3)
    print("=== random triangle-free N=12..20 ===")
    for nn in range(12,21,2):
        for p in (0.4,0.55):
            for seed in range(3):
                m,E=rand_trifree(nn,p,seed*13+nn)
                one(f"rand{nn}_{p}_{seed}",m,E)
