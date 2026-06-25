import sys
from validate_dmono_le_u8 import U8_graphon, dmono, tri_free, cyc, petersen
from fractions import Fraction as F
# C11 and a few odd cycles / blowups
tests=[("C11",11,cyc(11)),("C9",9,cyc(9)),("C13",13,cyc(13))]
print(f"{'graph':8s}{'d_mono':>12s}{'U_8':>14s}{'U8>=dm':>8s}{'ratio':>8s}")
for (name,n,A) in tests:
    if not tri_free(n,A): print(name,'not tri-free'); continue
    dm=dmono(n,A); U8=float(U8_graphon(n,A,[F(1,n)]*n)); ok=U8>=dm-1e-12
    print(f"{name:8s}{dm:12.6f}{U8:14.6e}{str(ok):>8s}{(U8/dm if dm>0 else float('inf')):8.3f}")
print("C11 expected: d_mono=2/121=%.6f, agent-1 cited 8/2025=%.6f"%(2/121, 8/2025))
print("DONE")
