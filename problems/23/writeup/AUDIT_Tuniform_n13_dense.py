#!/usr/bin/env python3
"""EXHAUSTIVE dense-end N=13: all triangle-free connected graphs with e>=EMIN edges
(geng -tc 13 EMIN:42) -- the HIGH-Gamma / LOW-slack regime that stresses U the most.
Reuses worker from AUDIT_Tuniform_n13_partial. EXACT Fractions.
Usage: python AUDIT_Tuniform_n13_dense.py EMIN
"""
import sys, subprocess, time
from fractions import Fraction
from multiprocessing import Pool
from AUDIT_Tuniform_n13_partial import worker
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def main():
    EMIN=int(sys.argv[1]) if len(sys.argv)>1 else 28
    t0=time.time()
    print(f"=== EXHAUSTIVE dense N=13 e>={EMIN} U-census ===",flush=True)
    proc=subprocess.Popen([GENG,"-tc","13",f"{EMIN}:42"],stdout=subprocess.PIPE,text=True,bufsize=1<<20)
    def gen():
        for line in proc.stdout:
            g=line.strip()
            if g: yield g
    checked=0;skipped=0;viols=[];min_slack=None;worst=None;badgeo=0
    with Pool(processes=60) as pool:
        for out in pool.imap_unordered(worker, gen(), chunksize=50):
            if out[0]=='skip': skipped+=1; continue
            if out[0]=='badgeo': badgeo+=1; print("BADGEO",out[1],flush=True); continue
            _,g6,n,G,K,maxT=out; checked+=1
            slack=Fraction(K)-maxT
            if min_slack is None or slack<min_slack: min_slack=slack; worst=(g6,n,G,K,maxT)
            if out[0]=='viol': viols.append(out); print(f"!!! VIOLATION {out}",flush=True)
            if checked%5000==0:
                print(f"  ...checked={checked} skipped={skipped} viols={len(viols)} min_slack={min_slack} ({float(min_slack):.3f}) t={time.time()-t0:.0f}s",flush=True)
    print(f"--- DONE dense N=13 e>={EMIN}: checked={checked} skipped={skipped} badgeo={badgeo} viols={len(viols)} (EXHAUSTIVE over e>={EMIN}) ---",flush=True)
    print(f"min_slack(K-maxT)={min_slack} ({float(min_slack):.4f}) at {worst}",flush=True)
    print(f"elapsed={time.time()-t0:.1f}s",flush=True)
    print("ZERO VIOLATIONS." if not viols else f"VIOLATIONS: {viols}",flush=True)

if __name__=='__main__': main()
