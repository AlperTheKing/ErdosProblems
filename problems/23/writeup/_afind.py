"""Find N=10 census graphs that have a saturated u with a zero-mu incident edge (loads-cut)."""
import subprocess
from _h import dec, GENG, loads
from _zmu import mu_edges

outg=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
hits=[]
for g6 in outg:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    N=info['n']; T=info['T']
    if not any(t==N for t in T): continue
    mu=mu_edges(info)
    ok=False
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]==N or T[v]==N: ok=True; break
    if ok: hits.append(g6)
print(len(hits),"graphs")
for g in hits[:8]: print(g)
