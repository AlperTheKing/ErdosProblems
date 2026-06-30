"""INDEPENDENT confirmation: GPT-Pro BLOCK-SBC (per-component rho(O_C)+m_C <= n_C+n_C^2/25) is FALSE on H?AFBo],
while GLOBAL SBC rho(O)+m <= N+N^2/25 still HOLDS. Audit the workflow agent's refutation."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins

def gram_O(M,cyc,idx=None):
    keys = idx if idx is not None else list(range(len(M)))
    pf=[]
    for f in [M[k] for k in keys]:
        Ps=cyc[f]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf.append(d)
    m=len(pf); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0)
            for v,pv in pf[i].items():
                if v in pf[j]: s+=pv*pf[j][v]
            O[i][j]=s; O[j][i]=s
    return O

def eig2(O):  # exact eigenvalues of 2x2
    a,b,c,d=O[0][0],O[0][1],O[1][0],O[1][1]
    tr=a+d; det=a*d-b*c; disc=tr*tr-4*det
    import math
    s=F(int(round(math.isqrt(disc.numerator)*1)), 1)  # disc should be perfect square here
    return tr,det,disc

n,E=dec('H?AFBo]')
adj,cuts=gmins(n,E)
print("H?AFBo] N=%d  #gamma-min cuts=%d"%(n,len(cuts)))
side=cuts[0]
st=struct_for_side(n,adj,side)
M,ell,T,mu,cyc=st
m=len(M)
print("  M=%s ell=%s  total m=%d  N=%d  N^2/25=%s"%(M,[ell[f] for f in M],m,n,F(n*n,25)))
comp,find=kcomponents(n,cyc)
# group bad edges by component
from collections import defaultdict
g=defaultdict(list)
for i,f in enumerate(M): g[find(f[0])].append(i)
for r,idxs in g.items():
    C=comp[r]; nC=len(C); mC=len(idxs)
    OC=gram_O(M,cyc,idxs)
    print("  K-comp root=%d verts=%s nC=%d mC=%d badedges=%s"%(r,sorted(C),nC,mC,[M[i] for i in idxs]))
    print("    O_C=%s"%[[str(x) for x in row] for row in OC])
    if len(OC)==2:
        tr,det,disc=eig2(OC)
        import math
        rt=math.isqrt(disc.numerator)
        rho=(tr+F(rt,disc.denominator if disc.denominator==1 else 1))/2 if disc.denominator==1 else None
        # disc rational; assume integer perfect square
        rho_val=(tr+F(int(math.isqrt(int(disc)))))/2
        print("    trace=%s det=%s disc=%s rho(O_C)=%s"%(tr,det,disc,rho_val))
        blockcap=F(nC)+F(nC*nC,25)
        print("    BLOCK-SBC: rho+mC=%s  vs  nC+nC^2/25=%s  -> %s"%(rho_val+mC,blockcap,"HOLDS" if rho_val+mC<=blockcap else "*** FAILS (gap %s) ***"%(rho_val+mC-blockcap)))
# global SBC
Oall=gram_O(M,cyc)
# rho(Oall) lower bound via Rayleigh at ell, and exact PSD check of global cap
import numpy as np
rho_all=max(abs(np.linalg.eigvals(np.array([[float(x) for x in r] for r in Oall]))))
globalcap=F(n)+F(n*n,25)
print("  GLOBAL: rho(O)~%.4f + m=%d = %.4f  vs N+N^2/25=%s=%.4f -> %s"%(rho_all,m,rho_all+m,globalcap,float(globalcap),"HOLDS" if rho_all+m<=float(globalcap) else "FAILS"))
