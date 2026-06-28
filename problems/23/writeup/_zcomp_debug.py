"""Investigate the N=11 loads-cut ZCOMP-BOUNDARY-O violations (my run found 22; Codex found 0). Find witnesses,
examine whether they are real or a definition/bug artifact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zcomp import zcomp_viol

outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
shown=0
for g6 in outg:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    v=zcomp_viol(info['n'],info['adj'],info['side'])
    if v:
        print(f"g6={g6} side={info['side']}")
        T=info['T']
        print(f"  T={[float(t) for t in T]}  O={[i for i in range(info['n']) if T[i]>info['n']]}  M={info['M']}")
        for item in v[:2]:
            print(f"  VIOL: {item}")
        shown+=1
        if shown>=4: break
print(f"(showed {shown} violating graphs)")
