#!/usr/bin/env python3
"""Exact confirmation of the min-ratio and the sharp homogeneous reach."""
import json, os
from fractions import Fraction as F
from math import gcd
import numpy as np
from scipy.optimize import linprog

HERE = r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve"
cert = json.load(open(os.path.join(HERE, "q2_basis_witness_certificate.json")))
NORMALS = cert["normals"]; PAIRS=[tuple(p) for p in cert["nonparallel_pairs"]]
mu=[F(x) for x in cert["mu"]]; n=99

def pcross(a,b):
    u=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    g=0
    for x in u: g=gcd(g,abs(x))
    return None if g==0 else [x//g for x in u]
B=[[0]*n for _ in range(45)]
for c,(i,j) in enumerate(PAIRS):
    u=pcross(NORMALS[i],NORMALS[j])
    for k in range(3):
        B[3*i+k][c]=u[k]; B[3*j+k][c]=-u[k]

def inker(L):  # exact check B.L == 0
    return all(sum(a*x for a,x in zip(br,L))==0 for br in B)

# --- reconstruct the min-ratio ray exactly from the LP support (24 edges, each 1/4)
c=np.array([float(x) for x in mu]); Bf=np.array([[float(x) for x in r] for r in B])
Aeq=np.vstack([Bf,np.ones((1,n))]); beq=np.concatenate([np.zeros(45),[6.0]])
res=linprog(c,A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*n,method="highs")
supp=[i for i in range(n) if res.x[i]>1e-7]
Lstar=[F(0)]*n
for i in supp: Lstar[i]=F(1,4)
print("ray support size:", len(supp), " sum(Lstar)=", sum(Lstar))
print("Lstar in ker(B):", inker(Lstar))
print("mu.Lstar =", sum(m*l for m,l in zip(mu,Lstar)), " ratio a_1/sum =",
      sum(m*l for m,l in zip(mu,Lstar))/sum(Lstar))

# --- exact dual certificate for a_1 >= (7/48) sum(Lambda) on ker(B)+orthant
# want y (45) with (B^T y)_e <= mu_e - 7/48 for all e.  Get float dual, rationalize.
TARGET=F(7,48)
rhs=np.array([float(m-TARGET) for m in mu])
BT=np.array([[float(B[r][cc]) for r in range(45)] for cc in range(n)])  # 99x45
res2=linprog(np.zeros(45),A_ub=BT,b_ub=rhs,bounds=[(None,None)]*45,method="highs")
print("\nFarkas a_1>=(7/48)sum feasibility:", res2.status, res2.message)
if res2.status==0:
    # rationalize y with denominator 48 and verify exactly
    y=[F(round(v*48),48) for v in res2.x]
    ok=True; worst=None
    for cc in range(n):
        lhs=sum(F(B[r][cc])*y[r] for r in range(45))
        if lhs> mu[cc]-TARGET:
            ok=False; worst=(cc,lhs,mu[cc]-TARGET)
    print("rationalized y (denom 48) exact-valid:", ok, "worst:", worst)
    if not ok:
        # try denominator 48 rounding both ways failed; report max violation
        pass

# --- superset test: exhaustive small simplices over the 15 hive normals; min a_1
import itertools, sys
sys.path.insert(0, HERE)
import hive4
def rank3(S): return hive4._rank(S)>=3
def posspan(S):
    for j in range(4):
        rest=[S[k] for k in range(4) if k!=j]
        if hive4._det3(rest)==0: continue
        M=[[rest[0][a],rest[1][a],rest[2][a]] for a in range(3)]
        if hive4._det3(M)==0: continue
        y=hive4._solve3(M,[-S[j][a] for a in range(3)])
        if y and all(v>0 for v in y): return True
        return False
    return False

mina1=None; viol=[]; count=0
T=3
for idxs in itertools.combinations(range(15),4):
    S=[NORMALS[i] for i in idxs]
    if not rank3(S) or not posspan(S): continue
    for t in itertools.product(range(-T,T+1),repeat=4):
        A=list(S); b=list(t)
        Vs=hive4.vertices(A,b)
        if len(Vs)!=4 or hive4._affine_rank(Vs)!=3: continue
        if max(hive4.denominators(Vs))!=1: continue  # lattice only
        box=hive4.bounding_box(Vs)
        L=[1]+[hive4.lattice_count(A,b,nn,box) for nn in range(1,4)]
        poly=hive4.interpolate(L)
        a1=poly[1]; count+=1
        if mina1 is None or a1<mina1: mina1=a1
        if a1<F(11,6): viol.append((idxs,t,str(a1)))
print("\nsuperset simplex scan: lattice simplices tested =", count,
      " min a_1 =", mina1, " (11/6=", float(F(11,6)),")")
print("simplices with a_1 < 11/6:", len(viol))
for v in viol[:10]: print("  ", v)
