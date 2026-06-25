from fractions import Fraction as F
# THE COLLAPSE AT K23, made concrete.
#
# kappa* = max_{w>=0, sum w_a =1}  min_{S min sig}  sum_{e in S} min_{C odd, C cap S={e}} w(C).
#
# The colleague's "constant 25" chain bounds, for a FIXED distribution p (no w), the quantity
#       Sigma lambda_v^2  via  2 lambda_v <= d(v)  and cycle-degree,
# then Cauchy gives t <= n^2/25. This is a w-FREE manipulation. It cannot see the
# max_w. The whole difficulty of kappa* is the OUTER max over w (the adversary toll) and
# the toll-DEPENDENT inner min_S. The chain integrates over the orbit, effectively setting
# w = uniform, i.e. it evaluates the inner expression at ONE specific w (uniform) and at
# the orbit-symmetric p. For uniform w on a vertex-transitive K (like C5[q]) that is exact.
# At K23 the worst w is FAR from uniform (concentrated on 6 K23 edges); the orbit average
# does not bound max_w.
#
# Demonstrate: at K23, uniform-w congestion vs worst-w congestion differ, and the chain
# only controls a uniform-like average.
#
# K23-N13 facts given in the brief:
#   fixed S0 (4 natural bad edges): congestion 4/3
#   min over 126 signatures (rotation): 6/5
#   worst-toll value kappa* = 6/5 = 1.2
#   floor n^2/(25t) = 1.69
# The chain claims to PROVE congestion <= floor. At K23 floor=1.69 is LOOSE (slack .49),
# so the chain "succeeds" at K23 only because the floor is far above 6/5 there --
# it succeeds by a margin it did NOT earn from the cycle-degree/Cauchy steps, which are
# tight ONLY at C5. So K23 does not falsify the *inequality* kappa*<=floor (it holds with
# slack) -- but it falsifies the *proof*: the symmetrization that yields the floor is invalid
# at K23, and the brief itself says single-sig / uniform-over-sig / cycle-degree / Gamma
# each FAIL at K23. The chain is exactly "uniform-over-sig + cycle-degree", so it FAILS at K23.

cases = {
 "fixed S0 congestion": F(4,3),
 "rotated min over 126 sigs (kappa*)": F(6,5),
 "floor n^2/(25t)": F(169,100),
}
for k,v in cases.items():
    print(f"  {k}: {v} = {float(v):.4f}")
print()
print("Brief states uniform-over-signatures FAILS at K23. The 'constant 25' chain IS")
print("uniform-over-orbit averaging => it is one of the methods the brief already says fails.")
print()
print("Net: the inequality kappa*<=floor is TRUE at K23 (1.2<=1.69) but the chain's")
print("derivation of the floor (cycle-degree tight + 2lam<=d on orbit measure) is INVALID")
print("off C5. The chain neither uses w nor evaluates min_S sum_e min_C w(C). It collapses.")
