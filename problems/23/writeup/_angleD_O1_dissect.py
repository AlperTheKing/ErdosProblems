"""ANGLE D |O|=1 dissection: WHY does star LB1 >= D_o hold?  Test a cleaner, fully analytic bound.

For |O|=1 we want C_eff(o<->g) >= D_o = T(o)-N.  We proved (Rayleigh) C_eff >= LB1 = sum_{w~o,Q} c_w,
c_w = omega(ow) RQ(w)/(omega(ow)+RQ(w)).  Empirically LB1>=Do with margin.  Try to PROVE LB1>=Do.

A sufficient (stronger, simpler) bound:  if RQ(w) >= omega(ow) for the relevant w, then c_w >= omega(ow)/2.
More robustly test the candidate ANALYTIC inequalities, exact, per |O|=1 instance:
 (A) deg_omega(o) := sum_{w} omega(ow) >= D_o + something?   (note deg_omega(o)=H_oo-(N-T(o))=H_oo+Do-... )
     Actually H_oo = deg_omega(o)+(N-T(o)) = deg_omega(o)-Do.  And S(o)=Ceff-Do<=H_oo? compare.
 (B) The 'no-overloaded-neighbor' structural fact: are o's omega-neighbors always in Q (RQ>0)?
     If EVERY omega-neighbor w of o has RQ(w)>0 we at least have all star terms active.  Report
     #neighbors with RQ<=0 (overloaded neighbors) -- if 0 always, star is 'full'.
 (C) Compare LB1 to a coarser bound  LBmin = sum_w min(omega(ow),RQ(w))/2  (since c_w>=min/2).
 (D) The exact slack  LB1 - Do  and  deg_omega(o)-Do, and whether deg_omega(o)>=Do alone (cut bound)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _gcd import build_H
from _angleD_O1 import gmin_sides, ceff_electrical
from _angleD_O1_lb import omega_of

def dissect(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]; Do=T[o]-N
    om,T2,N2=omega_of(adj,side,n)
    deg=F(0); ovn=0; LB1=F(0); LBmin=F(0); nb=0
    for e,w in om.items():
        u,v=tuple(e)
        if u!=o and v!=o: continue
        wl=v if u==o else u; nb+=1
        deg+=w
        RQ=F(N)-T[wl]
        if RQ<=0: ovn+=1; continue
        LB1+=w*RQ/(w+RQ)
        LBmin+=min(w,RQ)/2
    return dict(o=o,Do=Do,deg=deg,ovn=ovn,nb=nb,LB1=LB1,LBmin=LBmin,
                deg_ge=(deg>=Do),LB1_ge=(LB1>=Do),LBmin_ge=(LBmin>=Do))

if __name__=="__main__":
    print("=== |O|=1 dissection: deg_omega(o)>=Do? overloaded-neighbors? LBmin>=Do? ===")
    agg={'tot':0,'deg':0,'lb1':0,'lbmin':0,'ovn_any':0}
    mins={'deg':None,'lb1':None,'lbmin':None}
    for nn in (9,10,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        t=0;dg=0;l1=0;lm=0;ov=0
        for g6 in outg:
            n,E=dec(g6); adj,sides=gmin_sides(n,E)
            for s in sides:
                d=dissect(adj,s,n)
                if d is None: continue
                t+=1; agg['tot']+=1
                if d['deg_ge']: dg+=1; agg['deg']+=1
                if d['LB1_ge']: l1+=1; agg['lb1']+=1
                if d['LBmin_ge']: lm+=1; agg['lbmin']+=1
                if d['ovn']>0: ov+=1; agg['ovn_any']+=1
                for key,val in [('deg',d['deg']/d['Do']),('lb1',d['LB1']/d['Do']),('lbmin',d['LBmin']/d['Do'])]:
                    if d['Do']>0 and (mins[key] is None or val<mins[key]): mins[key]=val
        print(f"  N={nn}: |O|=1={t} deg>=Do:{dg} LB1>=Do:{l1} LBmin>=Do:{lm} has-overloaded-nbr:{ov}",flush=True)
    print(f"  TOTAL |O|=1 cuts={agg['tot']}  deg-cert={agg['deg']}  LB1-cert={agg['lb1']}  "
          f"LBmin-cert={agg['lbmin']}  cuts-with-overloaded-nbr={agg['ovn_any']}")
    print(f"  min ratios: deg/Do={float(mins['deg']) if mins['deg'] else None:.4f} "
          f"LB1/Do={float(mins['lb1']) if mins['lb1'] else None:.4f} "
          f"LBmin/Do={float(mins['lbmin']) if mins['lbmin'] else None:.4f}")
