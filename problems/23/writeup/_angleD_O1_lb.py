"""ANGLE D |O|=1, PROOF attempt: lower-bound C_eff(o<->g) >= D_o = T(o)-N structurally.

The deficits R_Q(v)=N-T(v)>=0 (v in Q) act as resistors from v to ground.  Total ground capacity
sum_{v in Q} R_Q(v) = sum_{v!=o}(N-T(v)) = (N-1)N - (Gamma - T(o)) ... but more useful:
   sum_v (N-T(v)) = N^2 - Gamma,  so  sum_{v in Q}(N-T(v)) = (N^2-Gamma) + D_o   (since o-term is -D_o).
So Q carries deficit-mass  G_tot := (N^2-Gamma)+D_o  to ground.  IF the whole conjecture (N^2>=Gamma)
holds then G_tot>=D_o; we must show C_eff>=D_o WITHOUT assuming it, electrically.

ELECTRICAL LOWER BOUNDS to test on the census (each is an exact, structural sufficient condition):
 (LB-grd)  C_eff(o<->g) is a series of:  spreading through omega-network THEN grounding via R_Q.
           Crude Nash-Williams cut bound around o:  C_eff <= deg_omega(o) (NOT a lower bound) -- skip.
 (LB-star) Lower bound by grounding only o's omega-neighbors and shorting the rest:
           If we SHORT all of Q\\N(o) to o-side?? no.  Instead, the standard lower bound:
           C_eff(o<->g) >= 1 / ( R_path ) for ANY single o->g path of conductances in series-with-ground.
 (LB-1path) For each omega-neighbor w of o: series conductance through edge (o,w) [cond omega(ow)]
            then ground resistor at w R_Q(w):  c_w = 1/(1/omega(ow) + 1/R_Q(w)) = omega(ow)R_Q(w)/(omega(ow)+R_Q(w)).
            These parallel paths give  C_eff >= sum_{w in N(o)cap Q} c_w  ONLY IF the paths are
            edge/vertex disjoint after o (they share only o) -> they ARE vertex-disjoint (distinct w),
            so by Nash-Williams/parallel-of-series LOWER bound (Rayleigh monotonicity: deleting the
            rest of the network only lowers C_eff, and the remaining star gives exactly this sum):
                C_eff(o<->g) >= sum_{w in N_omega(o), w in Q} omega(ow)*R_Q(w)/(omega(ow)+R_Q(w)).
            CERTIFICATE (LB-1path):  sum_w omega(ow)R_Q(w)/(omega(ow)+R_Q(w)) >= D_o = T(o)-N.
   This is a CLEAN finite checkable sufficient condition using only o's omega-edge weights and the
   1-hop deficits.  Test how often it ALONE certifies |O|=1.   (If it gates census it's a real lemma.)

We also report the exact gap  C_eff - LB1  to see how lossy the star bound is."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import build_H, a_bar
from _satzmu_conn import struct_for_side
from _angleD_O1 import gmin_sides, ceff_electrical

def omega_of(adj,side,n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M_,ell,T,mu,cyc=st; N=n
    omega={}
    for f in M_:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); omega[e2]=omega.get(e2,F(0))+ae*F(1,k)
    return omega,T,N

def lb1_star(adj,side,n,o):
    r=omega_of(adj,side,n)
    if r is None: return None
    omega,T,N=r
    Do=T[o]-N
    lb=F(0); terms=[]
    for e,w in omega.items():
        u,v=tuple(e)
        if u!=o and v!=o: continue
        wl=v if u==o else u
        RQ=F(N)-T[wl]
        if RQ<=0:  # neighbor itself overloaded (can't ground) -> contributes 0 in this crude star
            continue
        c=w*RQ/(w+RQ)
        lb+=c; terms.append((wl,c))
    return lb,Do,terms

def test(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return ('skip',len(O))
    o=O[0]
    el=ceff_electrical(adj,side,n,o)
    if el is None: return ('bad',o)
    Ceff,To,Nf=el; Do=To-Nf
    s=lb1_star(adj,side,n,o)
    if s is None: return ('bad',o)
    lb,Do2,terms=s
    return ('ok',dict(o=o,Ceff=Ceff,Do=Do,lb=lb,lb_ge=(lb>=Do),ceff_ge=(Ceff>=Do),gap=Ceff-lb))

if __name__=="__main__":
    print("=== ANGLE D |O|=1 LOWER BOUND: star  sum_w w*RQ/(w+RQ) >= D_o ? ===")
    from _bdef_construct import Cn, mycielski
    named=[]
    n1,E1=mycielski(5,Cn(5)); m1,F1=mycielski(7,Cn(7))
    named=[("Grotzsch N=11",(n1,E1)),("Myc(C7) N=15",(m1,F1))]
    for g6 in ["I?ABCc]}?"]:
        nn,EE=dec(g6); named.append((g6,(nn,EE)))
    for nm,(nn,EE) in named:
        adj,sides=gmin_sides(nn,EE)
        for s in sides:
            r=test(adj,s,nn)
            if r is None or r[0]!='ok': continue
            d=r[1]
            print(f"  {nm}: o={d['o']} Ceff={float(d['Ceff']):.4f} Do={float(d['Do']):.4f} "
                  f"LBstar={float(d['lb']):.4f} LB>=Do={d['lb_ge']} Ceff>=Do={d['ceff_ge']}",flush=True)
            break
    print("--- census N=9,10 all gamma-min cuts, |O|=1 ---")
    for nn in (9,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; lbpass=0; ceffpass=0; minlbratio=None
        for g6 in outg:
            n,E=dec(g6); adj,sides=gmin_sides(n,E)
            for s in sides:
                r=test(adj,s,n)
                if r is None or r[0]!='ok': continue
                d=r[1]; tot+=1
                if d['lb_ge']: lbpass+=1
                if d['ceff_ge']: ceffpass+=1
                rr=d['lb']/d['Do'] if d['Do']>0 else None
                if rr is not None and (minlbratio is None or rr<minlbratio): minlbratio=rr
        print(f"  census N={nn}: |O|=1 cuts={tot} LBstar-certifies={lbpass} Ceff-certifies={ceffpass} "
              f"min(LBstar/Do)={float(minlbratio) if minlbratio else None}",flush=True)
