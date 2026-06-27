#!/usr/bin/env python3
"""Diagnose the BND failure on Grotzsch M(C5): find the worst (peel, phi), show the decomposition.
Separate the two failure sources:
  (a) RE-ROUTING: a survivor bad edge e in M' whose cheapest geodesic in G (through V) is cheaper than its
      cheapest geodesic in G-C (forced to avoid C). Then LHS_sub overcounts and BND can break.
  (b) the toll mass on C being undercharged.
Print, for the worst phi: the per-edge contributions full vs sub, and where they diverge.
"""
import sys, random
from collections import deque
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of, mycielskian
from _gpi_induct_census import Bcomp_dist, all_geos_banned, m_phi, cut_dom_survivors

def per_edge(N,adj,side,M,phi,banned):
    out=[]
    for (u,v) in M:
        geos=all_geos_banned(N,adj,side,banned,u,v)
        if not geos: out.append((u,v,None,None)); continue
        h=len(geos[0]); out.append((u,v,h,h*m_phi(geos,phi)))
    return out

def main():
    C5=[(i,(i+1)%5) for i in range(5)]
    N,adj=mycielskian(5,C5)
    E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E); side,G,M=res
    K=N+N*N-G
    print("Grotzsch M(C5): N=%d beta=%d Gamma=%d K=%d  M=%s"%(N,len(M),G,K,M))
    rng=random.Random(7)
    phis=[[rng.random() for _ in range(N)] for _ in range(300)]
    worst=None
    for (bu,bv) in M:
        for C in all_shortest_geos(N,adj,side,bu,bv):
            Cset=set(C); h=len(C)
            Mp=[(a,b) for (a,b) in M if a not in Cset and b not in Cset]
            ok=True; Gp=0
            for (a,b) in Mp:
                d=Bcomp_dist(N,adj,side,Cset,a).get(b,-1)
                if d<0: ok=False; break
                Gp+=(d+1)**2
            if not ok: continue
            cd=cut_dom_survivors(N,adj,side,M,Cset)
            if cd is not True: continue   # P0 required
            Np=N-h; Kp=Np+Np*Np-Gp
            for phi in phis:
                pf=per_edge(N,adj,side,M,phi,set())
                ps=per_edge(N,adj,side,Mp,phi,Cset)
                lf=sum(x[3] for x in pf if x[3] is not None)
                ls=sum(x[3] for x in ps if x[3] is not None)
                sumC=sum(phi[v] for v in C); sumVp=sum(phi)-sumC
                viol=(lf-ls)-((K-Kp)*sumVp+K*sumC)
                if worst is None or viol>worst[0]:
                    worst=(viol,bu,bv,tuple(C),h,Gp,Kp,phi,pf,ps)
    viol,bu,bv,C,h,Gp,Kp,phi,pf,ps=worst
    print("\nWORST: peel bad-edge(%d,%d) C=%s h=%d  Gamma'=%d K'=%d  BND viol=%.4f"%(bu,bv,C,h,Gp,Kp,viol))
    print("  sumC=%.4f sumVp=%.4f  (K-K')=%d  K=%d"%(sum(phi[v] for v in C), sum(phi)-sum(phi[v] for v in C),K-Kp,K))
    # compare per-edge: which survivor edges got MORE expensive in G-C than in G?
    fmap={(min(u,v),max(u,v)):(h,val) for (u,v,h,val) in pf if val is not None}
    print("  --- survivor bad edges: full(through V) vs sub(avoid C) cheapest-toll ---")
    for (u,v,hh,val) in ps:
        key=(min(u,v),max(u,v))
        full=fmap.get(key,(None,None))
        flag=""
        if full[1] is not None and val>full[1]+1e-9: flag="  <== sub MORE EXPENSIVE (reroute forced off C)"
        print("    e=(%d,%d): full h*m=%.4f   sub h*m=%.4f%s"%(u,v,full[1] if full[1] is not None else -1,val,flag))
    # also report: the bad edge being peeled and edges incident to C
    print("  C vertices:",C)

if __name__=="__main__":
    main()
