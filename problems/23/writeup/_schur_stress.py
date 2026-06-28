import numpy as np
from _h import dec, loads
from _schur_spec import test
from _stress_sandwich import mycielski, rand_trifree
def Cblow(k,q):
    L=2*k+1; m=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return m,E
def one(label,n,E):
    if n>22: print(f"  {label:20} N={n}: skip(maxcut)"); return
    info=loads(n,E)
    if info is None: print(f"  {label:20} N={n}: skip"); return
    st,d=test(info)
    flag="" if st in ('ok','pass-noO') else "  <<<<< VIOLATION"
    mr = float(d['minrow']) if (d and 'minrow' in d and d['minrow'] is not None) else None
    print(f"  {label:20} N={n}: {st}{' minrow='+str(round(mr,3)) if mr is not None else ''} fails={d['fails'] if (d and 'fails' in d) else None}{flag}")
print("=== Schur SPEC cert HARD STRESS: blowups + Mycielskians + random tri-free ===")
for (k,q) in [(2,2),(2,3),(2,4),(3,2),(3,3),(4,2)]:
    m,E=Cblow(k,q); one(f"C{2*k+1}[{q}]",m,E)
n,E=dec("DUW"); n2,E2=mycielski(n,E); one("Grotzsch",n2,E2)
n7,E7=(7,[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,0)]); n3,E3=mycielski(n7,E7); one("Myciel(C7)",n3,E3)
for nn in range(12,23,2):
    for p in (0.4,0.55):
        for seed in range(2):
            m,E=rand_trifree(nn,p,seed*31+nn); one(f"rand{nn}_{p}_{seed}",m,E)
