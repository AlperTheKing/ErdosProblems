"""Verify the foundational ATOMS of GPT-Pro's PATH-SWITCH proof on the killer graphs:
  (b) MAX-CUT MARGIN: for every vertex set U, delta_B(U) - delta_M(U) >= 0 (flipping U cannot increase the cut).
  (a) NEUTRAL-SWITCH gamma-monotonicity: for every cut-preserving switch W (delta_B(W)=delta_M(W), so the flipped
      cut is still MAXIMUM), Gamma does not decrease: Gamma(s^W) >= Gamma(s).
These are the nonneg atoms of the DUAL-PATH certificate. If either fails, GPT's proof scaffolding is unsound.
EXACT Fraction. Test single vertices + all small sets |U|<=2 on the killer graphs."""
from itertools import combinations
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _verify_two_lane import build_two_lane

def cut_size(n,E,side): return sum(1 for x,y in E if side[x]!=side[y])
def gamma_of(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    return sum(T)  # Gamma = sum_v T(v) = sum_f ell^2

def margins_and_neutral(name,n,E,adj,side,maxcut,acc,maxU=2):
    # (b) max-cut margin for sets up to size maxU
    base=cut_size(n,E,side)
    for k in range(1,maxU+1):
        for U in combinations(range(n),k):
            nb=side[:]
            for v in U: nb[v]^=1
            c=cut_size(n,E,nb)
            dBminusdM = base - c   # flipping U changes cut by (dM(U)-dB(U)) = base-c... cut_new = base + dM - dB
            # cut_new - base = delta_M(U) - delta_B(U); so delta_B - delta_M = base - cut_new
            if (base - c) < 0:
                acc['vB']+=1
                if acc['fB'] is None: acc['fB']=(name,U,base,c)
            # (a) neutral switch: cut_new == base == maxcut => still max; check Gamma
            if c==base==maxcut:
                if Bconn(n,adj,nb):
                    g0=gamma_of(n,adj,side); g1=gamma_of(n,adj,nb)
                    if g0 is not None and g1 is not None and g1 < g0:
                        acc['vA']+=1
                        if acc['fA'] is None: acc['fA']=(name,U,str(g0),str(g1))
                    acc['neutral']+=1
    acc['graphs']+=1

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    acc=dict(graphs=0,vB=0,vA=0,neutral=0,fB=None,fA=None)
    # killer graphs via gmins (gamma-min cut + its max-cut value)
    cases=[('H?AFBo]',dec('H?AFBo]'))]
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4]):
        cases.append(('C5%s'%parts,blowup(parts)))
    for name,(n,E) in cases:
        adj,cuts=gmins(n,E)
        maxcut=cut_size(n,E,cuts[0]) if cuts else 0
        for side in cuts[:2]:
            margins_and_neutral(name,n,E,adj,side,maxcut,acc,maxU=2)
    # two-lane (explicit side); maxcut = its cut size (CP-SAT-confirmed global max)
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); adj=adj_of(n,E)
        maxcut=cut_size(n,E,side)
        margins_and_neutral('two-lane L=%d'%L,n,E,adj,side,maxcut,acc,maxU=2)
    print("  graphs tested=%d  neutral switches checked=%d"%(acc['graphs'],acc['neutral']))
    print("  (b) max-cut margin delta_B(U)>=delta_M(U) for |U|<=2: violations=%d %s"%(acc['vB'],acc['fB'] or ''))
    print("  (a) neutral-switch Gamma-monotone (Gamma(s^W)>=Gamma(s)): violations=%d %s"%(acc['vA'],acc['fA'] or ''))
    print("  === GPT-Pro proof ATOMS %s ==="%("SOUND (both nonneg) on killer graphs" if acc['vB']==0 and acc['vA']==0 else "*** UNSOUND ***"))
