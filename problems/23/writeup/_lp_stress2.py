import numpy as np, subprocess
from _h import dec, GENG, loads
from _layerprice import solve_layerprice, Cblow
# full N=10, N=11 stride 8, blowups
def census(nn,stride):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    nt=0; infeas=0; worst=None; wg=None
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        nt+=1; t,ok=solve_layerprice(info)
        if t>n+1e-3: infeas+=1
        if worst is None or t-n>worst: worst=t-n; wg=g6
    print(f"  N={nn} (stride {stride}): cfg={nt} | INFEASIBLE(t*>N):{infeas} | max(t*-N)={worst:+.4f}@{wg}",flush=True)
print("=== layer-price feasibility fuller stress ===")
census(10,1); census(11,8)
print("--- blowups ---")
for (k,q) in [(2,4),(3,3),(4,2),(2,3)]:
    m,E=Cblow(k,q); info=loads(m,E)
    if info is None: print(f"  C{2*k+1}[{q}] N={m}: skip"); continue
    t,ok=solve_layerprice(info)
    print(f"  C{2*k+1}[{q}] N={m} | t*={t:.4f} <= N? {t<=m+1e-3}",flush=True)
