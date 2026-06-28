"""AGGRESSIVE stress of (SM) sum_v T^2<=N*Gamma and (Cycle-SM) sum_v p_f(v)T(v)<=N*ell(f).
The sandwich passed N<=11 but FAILED at N=22 blow-up; must confirm (SM)/(Cycle-SM) do NOT.
Families: blow-ups t=2 of HIGH-Gamma N=10/11 graphs (near-extremal), Mycielskians (iterated),
random triangle-free N=12..22. Exact rational. ANY violation kills GPT's route."""
from fractions import Fraction as F
import random, subprocess
from _h import dec, GENG, loads
from _sm_test import sm_quants, blowup
from _stress_sandwich import mycielski, rand_trifree

def one(label,n,E,acc):
    if n>23: return
    info=loads(n,E)
    if info is None: return
    ok,sl,cyc_slack,wf=sm_quants(info)
    acc['n']+=1
    bad = (not ok) or (cyc_slack<0)
    if not ok: acc['SM']+=1
    if cyc_slack<0: acc['CY']+=1
    if bad or label.startswith('!'):
        print(f"  {label:24} N={n} G={info['G']} | (SM):{ok} slack={float(sl):+.2f} | (Cycle-SM) min={float(cyc_slack):+.3f} {'<<<VIOLATION' if bad else ''}")
    return bad

if __name__=="__main__":
    acc={'n':0,'SM':0,'CY':0}
    print("=== blow-ups t=2 of HIGHEST-Gamma N=11 graphs (near-extremal) ===")
    out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    # rank by Gamma
    cand=[]
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        cand.append((info['G'],g6))
    cand.sort(reverse=True)
    print(f"  top Gamma at N=11: {[(g,s) for g,s in cand[:5]]}")
    for g,g6 in cand[:40]:
        n,E=dec(g6); nn,EE=blowup(n,E,2)
        one(f"{g6}[2]",nn,EE,acc)
    print("=== blow-ups t=2 of N=10 sample (200) ===")
    out10=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
    for g6 in out10[:200]:
        n,E=dec(g6); nn,EE=blowup(n,E,2)
        one(f"{g6}[2]",nn,EE,acc)
    print("=== Mycielskians ===")
    n,E=dec("DUW"); n2,E2=mycielski(n,E); one("!Myciel(C5)",n2,E2,acc)
    n7,E7=(7,[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,0)]); n3,E3=mycielski(n7,E7); one("!Myciel(C7)",n3,E3,acc)
    print("=== random triangle-free N=12..22 ===")
    for nn in range(12,23):
        for p in (0.35,0.5,0.65):
            for seed in range(3):
                m,E=rand_trifree(nn,p,seed*7+nn)
                one(f"rand{nn}_{p}_{seed}",m,E,acc)
    print(f"\nSTRESS SUMMARY: tested {acc['n']} | (SM) violations:{acc['SM']} | (Cycle-SM) violations:{acc['CY']}")
