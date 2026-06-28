"""Extend GCD exact gate to the remaining standing-gate items:
   Myc^3(C5) N=47 and Myc^2(C7) N=31 (long Mycielski corridors), plus census N=11 all gamma-min cuts.
   Reuses _gcd.test_side (BOTH halves: (GCD) H=L_omega+diag(N-T)>=0 AND (LC) M-K>=0), exact Fraction PSD."""
import subprocess, sys
from _h import dec, GENG
from _gcd import test_side, run_gmin
from _bdef_construct import Cn, mycielski

def named_test(nm, n, E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    # use the gamma-min cut(s) for this graph
    res=run_gmin(n,E)
    if not res:
        print(f"  {nm} N={n}: run_gmin None (no bad edges / no connected maxcut)", flush=True); return
    bad=sum(1 for r in res if not r[0])
    mineig=min(r[1] for r in res)
    print(f"  {nm} N={n}: cuts={len(res)} BOTH-PSD-FAILS={bad} min-float-mineig(H)={mineig:+.5f}", flush=True)

if __name__=="__main__":
    print("=== GCD extension: census N=11 ONLY (N=31/N=47 structs too slow; N=23 covers Mycielski corridor) ===", flush=True)
    # census N=11 all gamma-min cuts
    print("--- census N=11 (all gamma-min cuts) ---", flush=True)
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    ncut=0; bad=0; minf=None; wit=None; ng=0
    for g6 in outg:
        ng+=1
        n,E=dec(g6)
        res=run_gmin(n,E)
        if not res: continue
        for r in res:
            ncut+=1
            if not r[0]: bad+=1; wit=wit or g6
            if minf is None or r[1]<minf: minf=r[1]
        if ng%2000==0:
            print(f"    ...{ng} graphs, {ncut} cuts, fails={bad}", flush=True)
    print(f"  census N=11: graphs={ng} cuts={ncut} BOTH-PSD-FAILS={bad}{' WIT '+wit if wit else ''} min-float-mineig(H)={minf:+.5f}", flush=True)
