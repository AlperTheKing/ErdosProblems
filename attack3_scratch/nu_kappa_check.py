from fractions import Fraction as F
# Audit the load-bearing identity  nu*(K) = t / kappa*.
# The brief's reduction is: lemma (16) says exists p with E_p|{e in S:a in C_e}| <= n^2/(25t)
# for every edge a. From such a p one builds a fractional odd-cycle packing.
#
# The colleague writes "nu*(K) = t/kappa*" and "y_C=(t/(kappa . ...))" with an ELLIPSIS,
# i.e. the exact relation is NOT written down. Let us test whether nu*=t/kappa* even holds
# dimensionally/at C5.
#
# At C5[q]: t=q^2, n=5q, kappa* should be 1 (brief: tight, =1 at C5), nu*=t=q^2.
# t/kappa* = q^2/1 = q^2 = nu*.  OK at C5.
#
# At K23-N13: brief gives kappa*=6/5. If nu*=t/kappa* held, nu* = t/(6/5) = 5t/6.
# We need the ACTUAL nu* of K23-N13 to test. Brief does not give it numerically here,
# but the target inequality is nu* >= 25 t^2/n^2. With kappa*=6/5 and "nu*=t/kappa*":
#   nu* = 5t/6, and 25 t^2/n^2 = t * (25 t/n^2) = t / floor where floor=n^2/(25t)=1.69.
#   25 t^2/n^2 = t/1.69 = 0.5917 t.   nu*=t/kappa*=t/1.2=0.8333 t.
#   So 0.8333 t >= 0.5917 t holds. Consistent, IF nu*=t/kappa* is the true relation.
#
# BUT the relation nu* = t/kappa* is itself UNPROVEN in the sketch (written with an ellipsis).
# kappa* is a per-edge MAX congestion; turning a low-congestion selector distribution into a
# packing of value t/kappa* requires an LP-duality/flow argument that is NOT the same as the
# constant-25 chain. If instead the correct relation were nu* >= t/kappa* (one direction) that
# would still need kappa* <= floor to conclude. So the chain still must deliver kappa*<=floor,
# which it does not (it delivers t<=n^2/25, the wrong-direction bound).

t = F(25); n = F(25)  # C5[5]
print("C5[5]: t/kappa*(=1) =", t/F(1), " nu*=", F(25*t*t,n*n))
ts = F(1)  # symbolic unit t
print("K23 with kappa*=6/5: nu*=t/kappa* =", ts/F(6,5), "t ;  target 25t^2/n^2 = t/1.69 =", float(ts/F(169,100)),"t")
print("Consistent numerically, but nu*=t/kappa* is ASSERTED via an ellipsis, not derived,")
print("and even granting it, the chain must still prove kappa*<=floor, which it does NOT.")
