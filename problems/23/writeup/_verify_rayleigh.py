"""Adversarial check: is LB1 <= C_eff EXACTLY (Fraction) everywhere?  Load-bearing Rayleigh ineq.
   If LB1>C_eff anywhere, the 'C_eff>=LB1 rigorous lower bound' claim is FALSE."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _angleD_O1 import gmin_sides, ceff_electrical
from _angleD_O1_lb import lb1_star
from _gcd import build_H

def check(adj,side,n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]
    el=ceff_electrical(adj,side,n,o)
    if el is None: return None
    Ceff,To,Nf=el
    s=lb1_star(adj,side,n,o)
    if s is None: return None
    lb,Do,terms=s
    return (lb<=Ceff, Ceff-lb)

tot=0; viol=0; minw=None
for nn in (9,10,11):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); adj,sides=gmin_sides(n,E)
        for s in sides:
            c=check(adj,s,n)
            if c is None: continue
            tot+=1
            ok,gap=c
            if not ok: viol+=1
            if minw is None or gap<minw: minw=gap
print("Rayleigh LB1<=Ceff EXACT: tot=%d VIOLATIONS=%d min(Ceff-LB1)=%s" % (tot,viol,float(minw)))
