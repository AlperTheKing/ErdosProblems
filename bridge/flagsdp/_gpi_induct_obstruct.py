#!/usr/bin/env python3
"""Confirm the structural obstruction on Grotzsch M(C5): for EVERY peel C with P0 (IH applies),
report  (i) how many survivor bad edges M' remain, (ii) K-K' sign, (iii) Gamma'.
The claim: every IH-valid peel either annihilates most bad edges (M' tiny => LHS_sub can't carry LHS_full)
or makes K-K'<0. I.e. the peel does NOT leave a smaller CD instance whose GPI carries the boundary.
"""
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of, mycielskian
from _gpi_induct_census import Bcomp_dist, cut_dom_survivors

def main():
    C5=[(i,(i+1)%5) for i in range(5)]
    N,adj=mycielskian(5,C5)
    E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E); side,G,M=res
    K=N+N*N-G
    print("Grotzsch M(C5): N=%d beta=%d Gamma=%d K=%d M=%s"%(N,len(M),G,K,M))
    print("peel-edge | C | h | #M'survive | Gamma' | N' | K' | K-K' | P0(CD'&conn)")
    nP0=0; nP0_Kdrop=0; nP0_Mfull=0
    for (bu,bv) in M:
        for C in all_shortest_geos(N,adj,side,bu,bv):
            Cset=set(C); h=len(C)
            Mp=[(a,b) for (a,b) in M if a not in Cset and b not in Cset]
            ok=True; Gp=0
            for (a,b) in Mp:
                d=Bcomp_dist(N,adj,side,Cset,a).get(b,-1)
                if d<0: ok=False; break
                Gp+=(d+1)**2
            connok=ok
            cd=cut_dom_survivors(N,adj,side,M,Cset) if ok else None
            P0=bool(ok and cd is True)
            Np=N-h; Kp=Np+Np*Np-Gp if ok else None
            tag=""
            if P0:
                nP0+=1
                if Kp-K<0: nP0_Kdrop+=1
                if len(Mp)==len(M)-1: nP0_Mfull+=1   # only the peeled edge gone
            if P0:
                print("  (%d,%d) %s h=%d  |M'|=%d  G'=%d  N'=%d  K'=%d  K-K'=%d  P0=%s"
                      %(bu,bv,tuple(C),h,len(Mp),Gp,Np,Kp,K-Kp,P0))
    print("\nP0-valid peels: %d ; of those, K decreased (K-K'>0): %d ; M' kept all-but-peeled-edge: %d"
          %(nP0, nP0-nP0_Kdrop, nP0_Mfull))
    print("INTERPRETATION: an IH-carrying peel needs K-K'>=0 (budget shrinks) AND M' large. "
          "If every P0 peel has K-K'<0 or kills extra bad edges, the induction cannot transfer GPI.")

if __name__=="__main__":
    main()
