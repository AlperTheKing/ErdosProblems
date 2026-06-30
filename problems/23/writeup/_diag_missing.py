"""Diagnose the Farkas-missing direction: print full generator vectors + F for representative
glued and nonuniform-C5 rows, and contrast with a tight pure-C5 (F=0) row. EXACT Fractions."""
from fractions import Fraction as F
from _wf_farkas_cert import (blow_cyclic, glue_C5_C7, from_E, gmins, struct_for_side,
                             row_generators, Bconn)

def show(name, n, adj, side):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if ell[f]!=5: continue
        P=cyc[f][0]
        Ftar,gens,labels=row_generators(n,adj,side,st,f,P)
        nz=[(labels[k],gens[k]) for k in range(len(gens)) if gens[k]!=0]
        print(f"[{name}] bad={f} P={tuple(P)} F={Ftar}")
        print(f"   nonzero gens: {nz}")
        return  # one representative row per cut

# tight balanced C5[2] (F=0)
n,adj,_=blow_cyclic(5,[2,2,2,2,2]); E=[(u,v) for u in range(n) for v in adj[u] if v>u]
_,cuts=gmins(n,E); show("C5[2] balanced (F=0)", n,adj,cuts[0])

# nonuniform C5(2,1,2,1,3) (F>0)
n,adj,_=blow_cyclic(5,[2,1,2,1,3]); E=[(u,v) for u in range(n) for v in adj[u] if v>u]
_,cuts=gmins(n,E); show("C5(2,1,2,1,3) nonunif", n,adj,cuts[0])

# glued C5|C7 (F=49)
n,E=glue_C5_C7(); adj=from_E(n,E)
_,cuts=gmins(n,E); show("glue C5|C7", n,adj,cuts[0])
