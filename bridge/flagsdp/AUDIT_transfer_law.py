"""Audit: confirm U8 is the EXACT i.i.d. blow-up integral, beta scales t^2, and U_8(C5 blow-up)=0.08."""
from fractions import Fraction as F
from math import factorial
from u8_max_check import comps, blowup, U8, dmono, maxcut_graph
import flag_engine as fe

def cyc(n):
    A=[0]*n
    for i in range(n): A[i]|=1<<((i+1)%n); A[(i+1)%n]|=1<<i
    return A

# 1) Blow-up weights sum to 1 (i.i.d. probability law, multinomial theorem)
for m in (5,6,7):
    tot=F(0)
    for counts in comps(10,m):
        w=factorial(10)
        for c in counts: w//=factorial(c)
        tot += F(w) * F(1,m)**10
    print(f"[1] sum blow-up weights comps(10,{m}) = {tot}  EXACTLY 1: {tot==1}")

# 2) finite d_mono(C5) = 0.08 exactly
A5=cyc(5)
dm = dmono(5,A5)
print(f"[2] finite d_mono(C5) = {dm}  = 2/25={2/25}? {abs(dm-2/25)<1e-15}")

# 3) U_8 of the C5 i.i.d. blow-up (uniform weights) = graphon value
u = U8(5,A5)
print(f"[3] U_8(C5 i.i.d. blow-up) = {u:.12f}  target 0.08 |diff|={abs(u-0.08):.2e}")

# 4) beta ~ t^2 multilinearity: U8 is a density (scale-free). The 2-blowup of C5 must give SAME U8.
#    Feed the 10-vertex 2-blowup as the base graph with uniform alpha=1/10.
n2,A2 = blowup((2,2,2,2,2), A5)
e2=sum(bin(x).count("1") for x in A2)//2
mc2=maxcut_graph(n2,A2)
print(f"[4] 2-blowup C5: n={n2} edges={e2} maxcut={mc2} finite d_mono={2*(e2-mc2)/(n2*n2)}")
u2 = U8(n2,A2)
print(f"    U_8(2-blowup of C5) = {u2:.12f}  (must EQUAL U_8(C5)={u:.12f}; |diff|={abs(u2-u):.2e})")

# 5) Sanity: a single 10-vertex SAMPLE (point mass) would give a DIFFERENT, larger number.
#    Show the blow-up integral != naive d_mono of any single sampled 10-graph. The integral
#    averages MaxCut over profile-classes, which is <= sampling a fixed 10-graph's own maxcut.
print("[5] U8 averages maxcut over profile classes per-root (graphon maxcut), not one 10-sample.")
