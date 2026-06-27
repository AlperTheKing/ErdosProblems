#!/usr/bin/env python3
"""ADVERSARIAL: the extremal family is C5 blow-ups. Scan UNBALANCED C5 blow-ups (the only graphs achieving
d_mono near 2/25) and check: (a) which land in the band [0.2486,0.3197], (b) none exceed d_mono=2/25, and the
band-resident ones obey it.  Also small dense near-band graphs (Petersen, Kneser-ish).  d_mono via class-uniform
maxcut (multilinear => integer maxcut on the 5-class quotient with weights)."""
from fractions import Fraction as F
import itertools

def c5_blowup_dmono_dedge(a):
    """C5 with class sizes a=(a0..a4). edges between consecutive classes. n=sum a.
    e = sum a_i a_{i+1}. maxcut over class-uniform 2-colorings (multilinear => vertex optimum)."""
    n=sum(a); e=sum(a[i]*a[(i+1)%5] for i in range(5))
    best=0
    for mask in range(32):
        cut=sum(a[i]*a[(i+1)%5] for i in range(5) if ((mask>>i)&1)!=((mask>>((i+1)%5))&1))
        if cut>best: best=cut
    beta=e-best
    dmono=F(2*beta, n*n); dedge=F(2*e, n*n)
    return dmono, dedge, n, e, beta, best

TWO25=F(2,25); LO,HI=0.2486,0.3197
print("=== C5 blow-ups: d_mono and band membership ===")
worst=F(-10); worstband=F(-10); maxdm=F(0); arg=None; bandviol=0
# scan all class-size vectors up to total size S
for S in range(5, 26):
    for a in itertools.combinations_with_replacement(range(0,S+1),5):
        if sum(a)!=S: continue
        # permutations matter for the cycle; but d_mono invariant under rotation/reflection. Try all distinct rotations?
        # cycle adjacency depends on cyclic order; test all 5!/... -> just test all orderings via permutations of the multiset
        seen=set()
        for p in set(itertools.permutations(a)):
            dm,de,n,e,beta,mc=c5_blowup_dmono_dedge(p)
            if dm>maxdm: maxdm=dm; arg=p
            if dm>TWO25:
                print(f"  !!! d_mono>2/25: a={p} dm={float(dm):.5f}")
            inb=LO<=float(de)<=HI
            if inb and dm>TWO25+1e-12: bandviol+=1; print(f"  !!! BAND CEX a={p} dm={float(dm):.5f} de={float(de):.4f}")
            if inb and dm-TWO25>worstband: worstband=dm-TWO25
print(f"max d_mono over C5 blow-ups (S<=25) = {float(maxdm):.6f} (2/25={float(TWO25):.6f}) at a={arg}")
print(f"  any C5 blow-up with d_mono>2/25 ? {maxdm>TWO25}")
print(f"  worst in-band (d_mono-2/25) = {float(worstband):+.3e}; band violations = {bandviol}")
# balanced C5[m]: d_mono = 2*m^2/(5m)^2 = 2/25 exactly, d_edge = 2*5m^2/(25m^2)=2/5=0.4 (OUTSIDE band, high side)
dm,de,n,e,beta,mc=c5_blowup_dmono_dedge((3,3,3,3,3))
print(f"balanced C5[3]: d_mono={float(dm):.6f} (=2/25 exactly: {dm==TWO25}), d_edge={float(de):.4f} inBand={LO<=float(de)<=HI}")
print("DONE")
