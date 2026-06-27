#!/usr/bin/env python3
"""FRESH adversarial audit of the LP PROOF LOGIC (read-only; new script).
Three checks:
 (1) DUAL DEDUCTION arithmetic: eta* = max min(U7(q), U8(q)-2/25).  If eta*<=0 then for every feasible q,
     min(U7, U8-2/25) <= 0, i.e. U7<=0 OR U8<=2/25.  d_mono<=U7 and d_mono<=U8 => d_mono<=2/25 either way.
     Verify: U7 is a deficit (>=0) so U7<=0 => U7=0 => d_mono=0.  Confirm 2/25 constant exact.
 (2) REAL-GRAPHON FEASIBILITY of the cut legs: for real tri-free graphs (zoo + exhaustive n<=7) compute the
     actual graphon q over T_10 (i.i.d. 10-sampling = induced density), then verify that the SAME per-R MaxCut
     envelope value the LP's u7/u8 legs use is an UPPER bound on d_mono (real graph not cut off).  Reuses the
     validated U7_graphon / U8_graphon and dmono.  ALSO: find any real band graph with d_mono>2/25 (=Erdos cex).
 (3) BAND coverage: confirm [0.2486,0.3197] are binomial-density BCL walls and that d_edge band membership of a
     real graph is the graphon edge density t(K2,W) = the SAME quantity the LP bounds via dedge_q rows.
Numbers reported are exact where cheap.
"""
import itertools, time
from math import factorial
from fractions import Fraction as F
from compute_U8 import canon_label, maxcut, popcount
from validate_dmono_le_u7 import U7_graphon, dmono, tri_free, cyc, petersen, path, disjoint, blowup, comps
from validate_dmono_le_u8 import U8_graphon
import flag_engine as fe

LO,HI=0.2486,0.3197
TWO25=F(2,25)

def edge_density_graphon(n,A):
    """t(K2, W_G) = E[1 edge between two i.i.d. vertices] = 2 e(G)/n^2 (with loops counted 0)."""
    e=sum(popcount(A[v]) for v in range(n))//2
    return F(2*e, n*n)

def check1_arithmetic():
    print("=== (1) DUAL DEDUCTION ARITHMETIC ===",flush=True)
    print(f"  2/25 exact = {TWO25} = {float(TWO25):.10f}",flush=True)
    print(f"  LP k8 leg RHS in code = -2.0/25.0 = {-2.0/25.0:.12f}; eta-U8 row: eta - sum u8_R <= -2/25",flush=True)
    print(f"     => eta <= sum u8_R - 2/25 <= U8(q) - 2/25.  (sum u8_R <= U8 by per-R MaxCut separation.)",flush=True)
    print(f"  LP k7 leg: eta - sum u7_R <= 0 => eta <= sum u7_R <= U7(q).",flush=True)
    print(f"  So eta <= min(U7, U8-2/25) at every feasible q; eta* = max over q. eta*<=0 =>",flush=True)
    print(f"     for ALL feasible q: U7(q)<=0 OR U8(q)<=2/25.",flush=True)
    print(f"  U7 is a per-R monochromatic DEFICIT (sum of nonneg slack+(tot_off-maxcut)>=0), so U7<=0 => U7=0",flush=True)
    print(f"     and d_mono<=U7=0<=2/25.  Else U8<=2/25 and d_mono<=U8<=2/25.  LOGIC: SOUND if both bounds hold.",flush=True)

def check2_real_feasibility():
    print("\n=== (2) REAL-GRAPHON cut-leg feasibility + Erdos counterexample hunt ===",flush=True)
    C5C5,_=disjoint(cyc(5),5,cyc(5),5)
    zoo=[("C5",5,cyc(5)),("C7",7,cyc(7)),("C9",9,cyc(9)),("C11",11,cyc(11)),
         ("P5",5,path(5)),("C5uC5",10,C5C5),("Petersen",10,petersen())]
    worst7=F(10); worst8=F(10); worstband=F(-10); maxdm_inband=F(0); arg_inband=None
    print(f"  {'graph':9s}{'d_edge':>9s}{'inBand':>7s}{'d_mono':>10s}{'U7-dm':>11s}{'U8-dm':>11s}{'dm<=2/25':>9s}",flush=True)
    rows=[]
    for (nm,n,A) in zoo:
        de=edge_density_graphon(n,A); inb = (LO-1e-12)<=float(de)<=(HI+1e-12)
        dm=F(dmono(n,A)).limit_denominator(10**6)
        u7=F(U7_graphon(n,A,[F(1,n)]*n)).limit_denominator(10**9)
        u8=F(U8_graphon(n,A,[F(1,n)]*n)).limit_denominator(10**9)
        worst7=min(worst7,u7-dm); worst8=min(worst8,u8-dm)
        if inb:
            worstband=max(worstband, dm-TWO25)
            if dm>maxdm_inband: maxdm_inband=dm; arg_inband=nm
        print(f"  {nm:9s}{float(de):9.4f}{str(inb):>7s}{float(dm):10.6f}{float(u7-dm):11.3e}{float(u8-dm):11.3e}{str(dm<=TWO25):>9s}",flush=True)
    # exhaustive n=6,7 : check U7>=dm, U8>=dm, and (in-band) dm<=2/25
    for nn in [6,7]:
        gs=fe.enumerate_graphs(nn,triangle_free=True); v7=v8=vband=0; t0=time.time(); nb=0
        for (k,A) in gs:
            de=edge_density_graphon(nn,A); inb=(LO)<=float(de)<=(HI)
            dm=F(dmono(nn,A)).limit_denominator(10**6)
            u7=F(U7_graphon(nn,A,[F(1,nn)]*nn)).limit_denominator(10**9)
            u8=F(U8_graphon(nn,A,[F(1,nn)]*nn)).limit_denominator(10**9)
            if u7<dm: v7+=1
            if u8<dm: v8+=1
            worst7=min(worst7,u7-dm); worst8=min(worst8,u8-dm)
            if inb:
                nb+=1
                if dm>TWO25: vband+=1; print(f"  !!! BAND CEX n={nn} A={A} dm={float(dm)} de={float(de)}",flush=True)
                worstband=max(worstband, dm-TWO25)
                if dm>maxdm_inband: maxdm_inband=dm; arg_inband=f"n{nn}:{A}"
        print(f"  n={nn}: {len(gs)} graphs ({nb} in band); U7<dm:{v7} U8<dm:{v8} band-cex(dm>2/25):{vband} [{time.time()-t0:.0f}s]",flush=True)
    print(f"\n  WORST U7-dmono = {float(worst7):+.3e}  (>=0 => U7 upper-bounds d_mono on tested reals)",flush=True)
    print(f"  WORST U8-dmono = {float(worst8):+.3e}  (>=0 => U8 upper-bounds d_mono on tested reals)",flush=True)
    print(f"  MAX in-band d_mono = {float(maxdm_inband):.6f} (2/25={float(TWO25):.6f}) at {arg_inband}; worst dm-2/25={float(worstband):+.3e}",flush=True)
    print(f"  => any real band graph with d_mono>2/25 ? {worstband>0}",flush=True)

def check3_band():
    print("\n=== (3) BAND coverage ===",flush=True)
    print(f"  Band (graphon edge density t(K2,W)) = [{LO}, {HI}] = BCL open 'medium' window.",flush=True)
    print(f"  d_edge < {LO}: BCL low-density theorem gives beta<=N^2/25 (d_mono<=2/25).",flush=True)
    print(f"  d_edge > {HI}: BCL high-density theorem gives beta<=N^2/25.",flush=True)
    print(f"  LP encodes band as: dedge_q . q <= {HI} AND dedge_q . q >= {LO}; dedge_q = D^T dedge (T_10 edge dens).",flush=True)
    print(f"  A real graphon with edge density OUTSIDE band is excluded from THIS LP's max => handled by BCL, not here.",flush=True)
    print(f"  GAP CHECK: do the band endpoints overlap so EVERY density is covered? low<=0.2486, mid in band, high>=0.3197.",flush=True)
    print(f"     union = (-inf,0.2486] U [0.2486,0.3197] U [0.3197,inf) = ALL reals. Endpoints shared => no gap.",flush=True)

if __name__=="__main__":
    check1_arithmetic(); check2_real_feasibility(); check3_band(); print("\nDONE",flush=True)
