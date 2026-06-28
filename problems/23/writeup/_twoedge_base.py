import numpy as np, subprocess, itertools
from _h import dec, GENG, loads
from _kktcore2 import setup, maximizeL
def pairgap(info):
    L,n,M=setup(info)
    if len(M)<2: return 0.0
    gmax,_=maximizeL(L,n,restarts=6)
    supps=[set(pf.keys()) for (f,lay,pf,h) in L]
    b2=0.0
    for a,b in itertools.combinations(range(len(M)),2):
        v,_=maximizeL(L,n,allowed=supps[a]|supps[b],restarts=3)
        if v>b2: b2=v
    return gmax-b2
print("=== two-edge support reduction on BASE census (max pair-gap; 0 => holds) ===")
for nn,stride in [(9,2),(10,12),(11,60)]:
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    mx=None; mg=None; nt=0; bad=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1; g=pairgap(info)
        if mx is None or g>mx: mx=g; mg=g6
        if g>1e-3: bad+=1
    print(f"  N={nn} (stride {stride}): cfg={nt} | two-edge FAILS:{bad} | max pair-gap={mx:+.4f}@{mg}",flush=True)
