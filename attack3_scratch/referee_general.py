"""
GENERAL mechanism of the (Q) failure, and the Cauchy looseness.

(Q) claims  m^3 R2 <= (N^2/25)^2  for all ell, R2 = sum_M (d/sum)^2.
Single-heavy-edge ell forces R2 -> 1 (one demand at stretch 1, rest 0) whenever there is
ONE B-edge that lies on every geodesic of exactly one bad demand and on no other demand's
forced route. Then m^3 R2 -> m^3. So (Q) DEMANDS m^3 <= (N^2/25)^2, i.e.
   m <= (N^2/25)^(2/3) = (N/5)^(4/3).
Whenever m > (N/5)^(4/3) and such a separating heavy edge exists, (Q) is FALSE while MT25 may hold.

Check the threshold against the regime the strategy actually needs (m < N^2/25):
   (N/5)^(4/3)  vs  N^2/25 = (N/5)^2.  Since (N/5)^(4/3) << (N/5)^2 for N>5,
   the band  (N/5)^(4/3) < m < (N/5)^2  is NONEMPTY and is EXACTLY the regime Module 3 must cover.
   So (Q) is false on a positive-measure chunk of the very regime it is invoked for.

Also: even when R2 is computed at the rho-OPTIMAL ell, the Cauchy step rho<=sqrt(m R2) is an
EQUALITY only if all stretches equal; it is the lossy link the writeup itself flags.
We show the gap between sqrt(m R2_opt) and the bound is what's really being asked, i.e. the
'remaining work' is NOT (Q) but a sharp (non-Cauchy) argument.
"""
import math
print("Threshold analysis: (Q) forces  m <= (N/5)^(4/3); strategy needs m up to (N/5)^2.")
print(f"{'N':>4} {'(N/5)^(4/3)':>12} {'N^2/25':>8}  band where (Q) false but strategy active")
for N in [10,13,15,20,25,30,50,100]:
    lo=(N/5.0)**(4/3); hi=(N/5.0)**2
    print(f"{N:>4} {lo:12.3f} {hi:8.3f}   m in ({math.ceil(lo)} .. {math.floor(hi)})  nonempty={math.ceil(lo)<=math.floor(hi)}")
print()
# Concretely: does a single-heavy-edge separating metric exist generically? Need a B-edge that is
# a 'private bridge' for one bad demand. In C5[k] every demand has many parallel geodesics, so R2 stays
# low (that's WHY C5 is the extremal and (Q) holds there). The danger is sparse-M graphs with bridges,
# exactly K23-type. We already exhibited m^3 R2 = 64 > 45.70 on K23 (m=4, N=13, (N/5)^(4/3)=4.04... wait):
for (N,m) in [(13,4)]:
    print(f"K23: N={N} m={m}: (N/5)^(4/3)={(N/5)**(4/3):.4f}  so m={m} {'>' if m>(N/5)**(4/3) else '<='} threshold "
          f"=> (Q) {'must fail (single-bridge)' if m>(N/5)**(4/3) else 'could hold'}; observed m^3 R2=64 vs target {(N*N/25)**2:.2f}")
print("DONE", flush=True)
