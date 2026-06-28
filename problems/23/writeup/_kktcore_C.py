import numpy as np, subprocess, itertools
from _h import dec, GENG, loads
from _kktcore2 import setup, maximizeL, Lval
def run_C(g6,info):
    L,n,M=setup(info)
    gmax,_=maximizeL(L,n)
    supps=[set(pf.keys()) for (f,lay,pf,h) in L]
    # best single
    b1=max(maximizeL(L,n,allowed=supps[ei],restarts=4)[0] for ei in range(len(M)))
    # best pair
    b2=b1
    for a,b in itertools.combinations(range(len(M)),2):
        v,_=maximizeL(L,n,allowed=supps[a]|supps[b],restarts=4)
        if v>b2: b2=v
    return gmax,b1,b2
print("=== (C) two-edge support reduction: does max L = best over edge-PAIRS? ===")
for g6 in ["I?BD@g]Qo","I?ABCc]}?","I?rFf_{N?"]:
    n,E=dec(g6); info=loads(n,E)
    gmax,b1,b2=run_C(g6,info)
    print(f"  {g6:13} N={n}: maxL={gmax:.4f} | best-single={b1:.4f}(gap {gmax-b1:+.3f}) | best-PAIR={b2:.4f}(gap {gmax-b2:+.3f})")
# N=22
n,E=dec("J???E?pNu\?"); nn=n*2; EE=[]
for (a,b) in E:
    for i in range(2):
        for j in range(2): EE.append((a*2+i,b*2+j))
info=loads(nn,EE); gmax,b1,b2=run_C("J???E?pNu?[2]",info)
print(f"  J???E?pNu?[2] N={nn}: maxL={gmax:.3f} | single gap={gmax-b1:+.3f} | PAIR gap={gmax-b2:+.3f}")
# census N=8 sample
out=subprocess.run([GENG,"-tc","8"],capture_output=True,text=True).stdout.split()
pairgap=None; pg6=None
for g6 in out:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    gmax,b1,b2=run_C(g6,info)
    if pairgap is None or (gmax-b2)>pairgap: pairgap=gmax-b2; pg6=g6
print(f"  census N=8: max PAIR gap = {pairgap:+.4f}@{pg6} (0 => two-edge reduction holds)")
