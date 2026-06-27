#!/usr/bin/env python3
"""Verify (exactly, for Step-1's question) that for a weighted C5-blowup:
  (1) beta = min_i a_i a_{i+1}  (the max cut is whole-class; allowing class-splitting cuts never beats it),
  (2) F = 2*beta/N^2 is STRICTLY locally maximized at the balanced point a_i=N/5, with first-variation
      dbeta[eps] = (N/5)*min_i(eps_i+eps_{i+1}) <= 0 (strict <0) for every measure-preserving eps (sum=0).
Brute max cut over ALL 2-colorings (incl. class-splitting) on integer blow-ups confirms (1)."""
from itertools import product
from fractions import Fraction as Fr

def beta_C5_blowup(a):
    """a = integer weights (a0..a4). Build C5-blowup, brute max cut over ALL vertex 2-colorings."""
    n=sum(a); off=[0];
    for x in a: off.append(off[-1]+x)
    cls=[]
    for i in range(5):
        for _ in range(a[i]): cls.append(i)
    edges=[(u,v) for u in range(n) for v in range(u+1,n) if (cls[v]-cls[u])%5 in (1,4)]
    e=len(edges); best=-1
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for (u,v) in edges if side[u]!=side[v])
        if c>best: best=c
    return e-best   # beta = e - maxcut

def min_consec(a):
    return min(a[i]*a[(i+1)%5] for i in range(5))

if __name__=="__main__":
    print("(1) beta == min_i a_i a_{i+1} over integer weighted C5-blowups (brute max cut incl. class-splitting):")
    weights=[(1,1,1,1,1),(2,1,1,1,1),(3,1,1,1,1),(2,2,1,1,1),(2,1,2,1,1),(3,2,1,1,2),(2,2,2,1,1),(3,1,2,1,2),(2,2,2,2,1)]
    allok=True
    for a in weights:
        b=beta_C5_blowup(a); mc=min_consec(a); ok=(b==mc); allok&=ok
        print(f"   a={a} N={sum(a)}: brute beta={b}  min_i a_i a_(i+1)={mc}  match={ok}")
    print(f"   ALL MATCH: {allok}")

    print("\n(2) First-variation at balance a_i=N/5 (use a_i=5 each, N=25): dbeta[eps]=(N/5)*min_i(eps_i+eps_(i+1)).")
    base=[5,5,5,5,5]; N=25; b0=min_consec(base)
    print(f"   balanced beta={b0} = (N/5)^2 = {(N//5)**2}; F=2beta/N^2={Fr(2*b0,N*N)} = 2/25={Fr(2,25)}")
    import random
    worst=Fr(-10); allneg=True; tested=0
    # all measure-preserving integer eps with small support, sum 0, not all zero
    cand=[]
    for e in product(range(-3,4),repeat=5):
        if sum(e)==0 and any(e): cand.append(e)
    for e in cand:
        # directional derivative of min_i a_i a_(i+1) at balance = min_i (a_(i+1) e_i + a_i e_(i+1)) = 5*min_i(e_i+e_(i+1))
        dd=5*min(e[i]+e[(i+1)%5] for i in range(5))   # = (N/5)*min_i(eps_i+eps_(i+1)), N/5=5
        tested+=1
        if dd>0: allneg=False; print(f"   !!! POSITIVE dir-deriv at eps={e}: dd={dd}")
        worst=max(worst,Fr(dd))
    print(f"   measure-preserving eps tested={tested}; ALL dir-derivs <= 0: {allneg}; max dir-deriv (closest to 0)={worst}")
    # confirm the only zero-derivative direction is eps=0 (strictness)
    zero_dirs=[e for e in cand if 5*min(e[i]+e[(i+1)%5] for i in range(5))==0]
    print(f"   nonzero measure-preserving eps with dir-deriv EXACTLY 0: {len(zero_dirs)} (expect 0 => strict local max)")
    if zero_dirs[:3]: print(f"      examples: {zero_dirs[:3]}")
