#!/usr/bin/env python3
"""Exact dual certificate that min ratio a_1/sum(Lambda) over ker(B)+ = 7/48,
hence a_1 >= (7/48) sum(Lambda), hence a_1 >= 7/8 for real lattice polytopes."""
import json, os
from fractions import Fraction as F
from math import gcd
import numpy as np
from scipy.optimize import linprog

HERE=r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve"
cert=json.load(open(os.path.join(HERE,"q2_basis_witness_certificate.json")))
NORMALS=cert["normals"]; PAIRS=[tuple(p) for p in cert["nonparallel_pairs"]]
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
TARGET=F(7,48)
rhs=np.array([float(m-TARGET) for m in mu])
BT=np.array([[float(B[r][cc]) for r in range(45)] for cc in range(n)])
# minimize sum of (B^T y)_e over tightish set to push to a vertex; just feasibility vertex
res=linprog(np.zeros(45),A_ub=BT,b_ub=rhs,bounds=[(None,None)]*45,method="highs")
yf=res.x
# identify tight constraints
tight=[cc for cc in range(n) if abs(float(sum(F(B[cc2][cc])*0 for cc2 in range(45)))+0)>=0 and
       abs((BT[cc]@yf)-(rhs[cc]))<1e-6]
print("num tight constraints:", len(tight))
# solve exactly: pick 45 independent tight rows of B^T, set (B^T y)=mu-7/48 there
import itertools
rowsB = [[F(B[r][cc]) for r in range(45)] for cc in range(n)]   # each row: coeff of y (len45)
# Gaussian elimination to pick 45 independent among tight
chosen=[]; M=[]
for cc in tight:
    row=rowsB[cc][:]+[mu[cc]-TARGET]
    # reduce against current pivots
    tmp=row[:]
    for pr,pc in M:
        if tmp[pc]!=0:
            f=tmp[pc]
            tmp=[a-f*b for a,b in zip(tmp,pr)]
    piv=next((i for i in range(45) if tmp[i]!=0),None)
    if piv is None: continue
    f=tmp[piv]; tmp=[a/f for a in tmp]
    for k in range(len(M)):
        pr,pc=M[k]
        if pr[piv]!=0:
            g=pr[piv]; M[k]=([a-g*b for a,b in zip(pr,tmp)],pc)
    M.append((tmp,piv)); chosen.append(cc)
    if len(M)==45: break
print("independent tight rows used:", len(M))
# Solve the underdetermined system (len(chosen) eqns, 45 unknowns y):
#   (B^T y)_cc = mu_cc - 7/48   for cc in chosen
# particular solution via Gauss-Jordan; free y set to 0.
m2=len(chosen)
aug=[[F(B[r][cc]) for r in range(45)]+[mu[cc]-TARGET] for cc in chosen]
pivots=[]; r=0
for col in range(45):
    piv=next((i for i in range(r,m2) if aug[i][col]!=0),None)
    if piv is None: continue
    aug[r],aug[piv]=aug[piv],aug[r]
    f=aug[r][col]; aug[r]=[x/f for x in aug[r]]
    for i in range(m2):
        if i!=r and aug[i][col]!=0:
            g=aug[i][col]; aug[i]=[x-g*b for x,b in zip(aug[i],aug[r])]
    pivots.append((r,col)); r+=1
    if r==m2: break
y=[F(0)]*45
for r,col in pivots:
    y[col]=aug[r][45]  # free vars are 0, RREF gives pivot value directly
# verify: B^T y <= mu - 7/48 for ALL 99 edges, exact
ok=True; nviol=0; maxv=F(0)
for cc in range(n):
    lhs=sum(F(B[k][cc])*y[k] for k in range(45))
    if lhs>mu[cc]-TARGET:
        ok=False; nviol+=1; maxv=max(maxv,lhs-(mu[cc]-TARGET))
print("EXACT dual valid (B^T y <= mu-7/48 for all 99):", ok, " violations:", nviol, " maxviol:", maxv)
if ok:
    print(">>> PROVEN exactly: a_1 = Lambda.mu >= (7/48) sum(Lambda) on ker(B) cap orthant.")
    print(">>> With sum(Lambda) >= 6 for any lattice 3-polytope: a_1 >= 7/8.")
