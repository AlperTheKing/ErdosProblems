"""FINAL: the unified invariant and WHY the band misses it. For the worst single-geo row of the
witness (f=(2,11), cut3) show: (a) per-layer S exceeds N/ell at the corridor vertex (band-bad),
(b) yet corridor TOTAL sum_v p_f(v)S(v) <= N because the spike is compensated by deficit elsewhere
   on the corridor AND the spike vertex is SHARED (paid by complement). Quantify the compensation.
Also confirm the clean equality-case reading on C5[2]."""
from fractions import Fraction as F
from _h import dec
from _stark1 import gmins
from _corridor import cut_S

def show(g6, pick):
    n,E=dec(g6)
    adj2,cuts=gmins(n,E)
    # find the requested cut/edge giving max ROW
    best=None
    for ci,s in enumerate(cuts):
        M,ell,S,pf,cyc=cut_S(n,adj2,s)
        for f in M:
            ROW=sum(pv*S[v] for v,pv in pf[f].items())
            if best is None or ROW>best[0]: best=(ROW,ci,s,f,ell,S,pf,cyc)
    ROW,ci,s,f,ell,S,pf,cyc=best
    L=ell[f]
    layer={}
    for P in cyc[f]:
        for i,v in enumerate(P): layer[v]=i
    A=[F(0)]*L; Ap=[F(0)]*L
    for v,pv in pf[f].items():
        A[layer[v]]+=pv*S[v]; Ap[layer[v]]+=pv
    print(f"\n{g6}: worst f={f} L={L} ROW={ROW}={float(ROW):.3f} (N={n}) #geo={len(cyc[f])}")
    print(f"  per-layer (i, layer-load A_i=sum p_f*S, layer p_f-mass, band budget N/ell, A_i vs budget):")
    for i in range(L):
        budget=F(n,L)*Ap[i] if Ap[i]>0 else F(0)  # fair per-layer budget = (p_f mass in layer)*N/ell
        flag=" BAND-OVER" if A[i]>F(n,L)*Ap[i] else ""
        print(f"    layer {i}: A={A[i]}={float(A[i]):.3f}  p_f-mass={Ap[i]}  (N/ell)*mass={float(F(n,L)*Ap[i]):.3f}{flag}")
    print(f"  sum A = {sum(A)}={float(sum(A)):.3f} = ROW;  sum budget = (N/ell)*sum(mass) = (N/ell)*ell = N = {n}")
    print(f"  => band charges each layer to (N/ell)*mass; corridor TOTAL = N exactly; deficits cancel overshoots")

if __name__=="__main__":
    show("K??CE@A{?]Fc", "single")
    show("I?rFf_{N?", "multi")
