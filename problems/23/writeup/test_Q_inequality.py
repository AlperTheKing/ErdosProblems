#!/usr/bin/env python3
"""EXACT stress-test of GPT-Pro round-4's proposed closing inequality (Q) for NRS (#23 delta=0):
   (Q)   F - 2/25  <=  a*(D - 2/5) - kappa*rho + E_pent,   a=1/5 ('natural'), kappa>0, E_pent<=0.
In the band D<2/5, so RHS terms a*(D-2/5)<=0, -kappa*rho<=0, E_pent<=0 => F<2/25 (= NRS), IF (Q) holds.
NECESSARY condition (since E_pent<=0 only HURTS): margin m := a*(D-2/5) - (F-2/25) >= kappa*rho + |E_pent| >= kappa*rho.
So (Q) with kappa>0 REQUIRES  m >= kappa*rho > 0  wherever rho>0. We test m and rho exactly.
rho = F - alpha*D with alpha = alpha* = min over edges of P_ij (maximal KKT alpha keeping S=A(P-alpha)>=0)."""
from fractions import Fraction as F

def maxcut_opt(n, edges):
    best=-1; opt=[]
    for m in range(1<<n):
        c=sum(1 for (u,v) in edges if ((m>>u)&1)!=((m>>v)&1))
        if c>best: best=c; opt=[m]
        elif c==best: opt.append(m)
    return best,opt

def stats(name,n,edges):
    mc,opt=maxcut_opt(n,edges); K=len(opt); beta=len(edges)-mc
    Pe={}
    for (u,v) in edges:
        same=sum(1 for m in opt if ((m>>u)&1)==((m>>v)&1)); Pe[(u,v)]=F(same,K)
    alpha=min(Pe.values())
    Fv=F(2*beta,n*n); D=F(2*len(edges),n*n)
    rho=Fv-alpha*D
    a=F(1,5)
    m=a*(D-F(2,5))-(Fv-F(2,25))           # (Q) necessary margin (must be >= kappa*rho)
    print(f"{name:11} n={n} e={len(edges)} beta={beta}: F={Fv}={float(Fv):.5f} D={D}={float(D):.4f} alpha*={alpha}")
    print(f"            rho=F-alpha*D = {rho}={float(rho):.5f}   F-2/25={Fv-F(2,25)}   (1/5)(D-2/5)={a*(D-F(2,5))}")
    print(f"            (Q) necessary margin m = a(D-2/5)-(F-2/25) = {m} = {float(m):.6f}")
    if rho>0:
        verdict = "OK (m>0 leaves room)" if m>0 else "*** (Q) FAILS: rho>0 but m<=0, no room for kappa*rho>0 ***"
        print(f"            rho>0 => need m>=kappa*rho>0.  m={float(m):.6f}, rho={float(rho):.5f} -> {verdict}")
    else:
        print(f"            rho={float(rho):.5f}<=0 => (Q) margin not binding here (need E_pent<=0 consistent; m={float(m):.6f})")
    print()
    return name,m,rho

def cyc(n): return n,[(i,(i+1)%n) for i in range(n)]
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]
def g6dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[];idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: E.append((i,j))
            idx+=1
    return n,E

print("Testing GPT round-4 (Q): F-2/25 <= (1/5)(D-2/5) - kappa*rho + E_pent  (a=1/5, kappa>0, E_pent<=0)\n")
res=[]
res.append(stats("C5",*cyc(5)))
res.append(stats("C7",*cyc(7)))
res.append(stats("Petersen",*petersen()))
res.append(stats("band-max-n8",*g6dec("G?`F`w")))
print("SUMMARY (a=1/5):")
for name,m,rho in res:
    flag = "  <== BREAKS (Q): rho>0 yet margin m<=0" if (rho>0 and m<=0) else ""
    print(f"  {name:11} margin m={float(m):+.6f}  rho={float(rho):+.5f}{flag}")
print("\nIf any row has rho>0 and m<=0, (Q) with a=1/5 and kappa>0 is VIOLATED there (E_pent<=0 cannot rescue).")
