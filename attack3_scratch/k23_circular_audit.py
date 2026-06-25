from fractions import Fraction as F

# AUDIT 3: the "improving move terminates at n^2/(25t)" claim.
# (P1) descent: if kappa(p) > n^2/(25t), an improving rotation exists -> kappa strictly decreases.
# (P2) termination: monotone decrease => kappa -> kappa* = min over (S,(C_e)).
# (P3) rigidity: equality in the constant-25 chain forces K = C5[n/5].

# CIRCULARITY on (P1): "above the floor an improving move exists" == "min kappa* <= floor".
# So (P1) assumes exactly the goal. One verified instance (4/3->6/5) is not a chain to the floor.
print("(P1) 'improving move exists above floor' <=> goal 'kappa*<=floor'. CIRCULAR if asserted.")
print("     Verified strict decrease only at ONE point (4/3->6/5); not chained to the floor.")
print()

# (P3) rigidity characterizes EQUALITY only: kappa*=floor => K=C5. It does NOT give
# kappa* <= floor when K != C5 (that is the goal). So it cannot certify the descent endpoint.
print("(P3) rigidity only characterizes EQUALITY; gives no bound on the descent endpoint value.")
print()

# (SYM) 'optimal p = uniform orbit measure' is asserted to get 2 lambda_v<=d(v) and
# cycle-degree tightness. But kappa* = max_w min_S (...) saddle determines optimal p, not symmetry.
# At K23 the min-player optimum is a convex combo of 4 singleton vertex-cuts, NOT the orbit measure.
print("(SYM) 'optimal p = uniform orbit measure' ASSERTED; at K23 optimum = 4 singleton cuts,")
print("      not orbit measure => 2 lambda_v<=d(v) and cycle-degree tightness can fail there.")
print()

# Where is 25 derived vs asserted?
def f(s): return F(s,(s+1)**2)
print("f(s)=s/(s+1)^2 : f(4)=", f(4), " f(5)=", f(5), " f(6)=", f(6))
print("max at s=4 -> 4/25 -> 25; this optimum is the C5 layer count, NOT re-derived at K23.")
