#!/usr/bin/env python3
"""Fast n=7 exhaustive: confirm on EVERY tri-free graph that U7>=dmono, U8>=dmono, H_R>=0, and no band cex.
Floats with 1e-9 tol. The three soundness pillars at n=7 (the largest cheap exhaustive class)."""
import time
from validate_dmono_le_u7 import U7_graphon, dmono, tri_free
from validate_dmono_le_u8 import U8_graphon
from horn_soundness import buildW, horn_min_W
from compute_U8 import popcount
from fractions import Fraction as F
import flag_engine as fe

LO,HI=0.2486,0.3197; TWO25=2.0/25.0
def de(n,A): return 2*(sum(popcount(A[v]) for v in range(n))//2)/(n*n)

gs=fe.enumerate_graphs(7,triangle_free=True)
v7=v8=vh=vb=0; nb=0; w7=w8=wh=1e9; t0=time.time()
for (k,A) in gs:
    n=7; d=dmono(n,A); u7=float(U7_graphon(n,A,[F(1,n)]*n)); u8=float(U8_graphon(n,A,[F(1,n)]*n))
    W=buildW(n,A); h,_=horn_min_W(W)
    if u7<d-1e-9: v7+=1; print("U7<dm",A,u7,d)
    if u8<d-1e-9: v8+=1; print("U8<dm",A,u8,d)
    if h<-1e-9: vh+=1; print("H_R<0",A,h)
    w7=min(w7,u7-d); w8=min(w8,u8-d); wh=min(wh,h)
    e=de(n,A)
    if LO<=e<=HI:
        nb+=1
        if d>TWO25+1e-9: vb+=1; print("BAND CEX",A,d,e)
print(f"n=7 EXHAUSTIVE {len(gs)} graphs ({nb} in band) [{time.time()-t0:.0f}s]")
print(f"  U7<dm:{v7} U8<dm:{v8} H_R<0:{vh} band-cex:{vb}")
print(f"  worst U7-dm={w7:+.3e} worst U8-dm={w8:+.3e} worst H_R={wh:+.3e}")
print(f"  ALL THREE PILLARS HOLD AT n=7 ? {v7==0 and v8==0 and vh==0 and vb==0}")
print("DONE")
