"""Diagnose why the corrected coarea LP is infeasible on H?AFBo]: is the switch family over-filtered, or is the
   construction genuinely infeasible?  Dump family size before/after validity filter, sigma & DGamma distributions,
   and the per-constraint achievability for the first gamma-min row.
"""
from fractions import Fraction as F
from _crux_extract import components_off_path
from _singleton_core import ell_map
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _coareaA_lp import switch_family

g6="H?AFBo]"; n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
_,cuts=gmins(n,E)
side=cuts[0]
st=struct_for_side(n,adj,side); M,ell,T,cyc=st[0],st[1],st[2],st[4]
N=F(n); Gamma=sum(ell[g]**2 for g in M)
f=list(M)[0]
for ff in M:
    if ell[ff]%2==1:
        for P in cyc[ff]:
            if len(P)==ell[ff]:
                f=ff; break
        break
P=None
for ff in M:
    if ell[ff]%2==1:
        for Q in cyc[ff]:
            if len(Q)==ell[ff]: P=list(Q); f=ff; break
    if P: break
L=ell[f]
print("side=%s f=%s P=%s L=%d Gamma=%d N=%d"%(''.join(map(str,side)),f,tuple(P),L,Gamma,n))
print("bad edges:",[(g,ell[g]) for g in M])
comps=components_off_path(n,adj,side,set(P))
print("off-row blue components:",[sorted(c) for c in comps])
fam=switch_family(n,adj,side,P)
print("family size (raw):",len(fam))
import sys
REQUIRE_BCONN = '--noconn' not in sys.argv
valid=[]; bconn_fail=0; gamma_none=0; sigma_neg=0
sigmas=[]; dgs=[]
for W in fam:
    s2=flip(side,W)
    if REQUIRE_BCONN and not Bconn(n,adj,s2): bconn_fail+=1; continue
    g1=gamma_of(n,adj,s2)
    if g1 is None: gamma_none+=1; continue
    dB,dM=deltas(n,adj,side,W); sigma=dB-dM
    if sigma<0: sigma_neg+=1; continue
    valid.append((W,sigma,g1-Gamma))
    sigmas.append(sigma); dgs.append(g1-Gamma)
print("REQUIRE_BCONN=%s  valid switches:%d  (Bconn_fail=%d gamma_none=%d sigma_neg=%d)"%(REQUIRE_BCONN,len(valid),bconn_fail,gamma_none,sigma_neg))
print("sigma values:",sorted(set(sigmas)))
print("DGamma values (sigma=0 only):",sorted(set(dg for (W,s,dg) in valid if s==0)))
# how many sigma=0 (cut-preserving) switches?
n0=sum(1 for (W,s,dg) in valid if s==0)
print("sigma=0 (cut-preserving) switches:",n0)
# chi=1 switches (both endpoints flipped) among sigma=0
nchi=sum(1 for (W,s,dg) in valid if s==0 and (P[0] in W and P[-1] in W))
print("sigma=0 AND chi=1 (both endpoints) switches:",nchi)
# target ingredients
h=[T[P[i]]/N for i in range(L)]; S=sum(h)
prods=[h[i]*h[(i+1)%L] for i in range(L)]; q=min(prods); r=prods.index(q)
a=[2*S - L*L*((h[(r+1)%L] if i==r else 0)+(h[r] if i==(r+1)%L else 0)) for i in range(L)]
mu=[F(L,5)-a[i]/(2*N) for i in range(L)]
L2delta=S*S-L*L*q
chiP=[0]*n
for end in (P[0],P[-1]):
    ch=endpt_chi(n,adj,side,end,M,n)
    for rr in range(n): chiP[rr]+=ch[rr]
E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
TARGET=F(L,5)*(N*N-Gamma)-E0-L2delta
print("h=",[str(x) for x in h]," r=",r)
print("mu (M1 targets)=",[str(m) for m in mu])
print("M2 target=1 (need chi=1 switches in support); TARGET(17)=",str(TARGET)," E0=",str(E0)," L2delta=",str(L2delta))
print("max DGamma over sigma=0 switches:", max((dg for (W,s,dg) in valid if s==0), default=None))
# Note: feasibility needs sum lambda DGamma = TARGET with support on sigma=0; if max DGamma*possible < TARGET -> infeasible
