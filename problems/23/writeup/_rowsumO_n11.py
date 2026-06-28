"""Full N=11 census EXACT ROWSUM-O check, with running max-residual print every 10000 graphs.
A single positive residual KILLS the certificate."""
import subprocess, sys
from fractions import Fraction as F
from _h import dec, GENG, loads
from _stress_rowsumO import rowsumO_exact

def run(nn):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    tot=len(out); ng=0; worst=F(-10**9); wg=None; viol=0
    for i,g6 in enumerate(out):
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        ng+=1
        r=rowsumO_exact(info)
        if r>worst: worst=r; wg=g6
        if r>0: viol+=1; print(f"  !!! VIOLATION {g6} resid={r}",flush=True)
        if (i+1)%10000==0:
            print(f"  ...{i+1}/{tot} processed (with-bad={ng}) running max-resid={float(worst):+.5f}@{wg} viol={viol}",flush=True)
    print(f"N={nn} DONE: graphs-with-bad={ng}/{tot} | max ROWSUM-O resid={worst}={float(worst):+.6f}@{wg} | violations={viol}",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]) if len(sys.argv)>1 else 11)
