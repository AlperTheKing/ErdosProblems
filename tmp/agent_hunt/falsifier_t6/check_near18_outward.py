#!/usr/bin/env python3
"""Exact outward-degree audit of the R46 18-vtx near-candidate double star.
Rebuild from R46's description: L = {v,m,a,b0..b4}, R = {x0..x4,y0..y4};
edges: v,m -> all x_i; a -> x0..x3; a -> y_j (all j); b_j -> y_j.
Report: |F*|, deg(v), deg(m), outward(N(v) u N(m)), kappa at the double star
S* = {v,m} u N(v) u N(m) against the 25 forced atoms vb_j, mb_j, b_ib_j, x4y_j.
Integer arithmetic only.
"""

V, Mm, A = "v", "m", "a"
B = [f"b{j}" for j in range(5)]
X = [f"x{i}" for i in range(5)]
Y = [f"y{j}" for j in range(5)]
left = [V, Mm, A] + B
right = X + Y

edges = set()
for x in X:
    edges.add((V, x))
    edges.add((Mm, x))
for x in X[:4]:
    edges.add((A, x))
for y in Y:
    edges.add((A, y))
for j in range(5):
    edges.add((B[j], Y[j]))

assert len(edges) == 24, len(edges)

atoms = []
for j in range(5):
    atoms.append((V, B[j]))
    atoms.append((Mm, B[j]))
for i in range(5):
    for j in range(i + 1, 5):
        atoms.append((B[i], B[j]))
for j in range(5):
    atoms.append(("x4", Y[j]))
assert len(atoms) == 25, len(atoms)

def nbrs(u):
    return {b for a, b in edges if a == u} | {a for a, b in edges if b == u}

deg_v, deg_m = len(nbrs(V)), len(nbrs(Mm))
star_right = nbrs(V) | nbrs(Mm)
outward = sum(
    1 for (a, b) in edges
    if (b in star_right and a not in (V, Mm)) or (a in star_right and b not in (V, Mm))
)
S = {V, Mm} | star_right
blue_cross = sum(1 for (a, b) in edges if (a in S) != (b in S))
bad_cross = sum(1 for (a, b) in atoms if (a in S) != (b in S))
t = 5
print({
    "supportEdges": len(edges),
    "degV": deg_v,
    "degM": deg_m,
    "sharedStar": sorted(star_right),
    "outwardStarDegree": outward,
    "twoT": 2 * t,
    "doubleStarSwitch": sorted(S),
    "badCross": bad_cross,
    "blueCross": blue_cross,
    "kappa": bad_cross - blue_cross,
    "farkasIdentity_2t_minus_outward": 2 * t - outward,
})
owner_bad_cross = sum(
    1 for (a, b) in atoms if (a in (V, Mm)) != (b in (V, Mm))
    and ((a in S) != (b in S))
)
coverage_bad_cross = bad_cross - owner_bad_cross
assert deg_v == deg_m == t
assert outward == 4
assert owner_bad_cross == 2 * t == 10          # ALL owner bads always cross S*
assert coverage_bad_cross == 5                  # x4y_j: x4 inside shared star
assert bad_cross - blue_cross == 11             # full kappa(S*)
assert 2 * t - outward == 6                     # pure-star component only
print(
    "PASS: kappa(S*) = ownerBads(10) + starTouchingRightBads(5) - outward(4) = 11;"
    " pure-star identity 2t-outward=6 = farkas ablation 'owner stars only';"
    " full-double-star value 11 = farkas ablation 'drop b-clique' (b-clique never crosses S*)."
    " => outward >= 2t is NECESSARY for kappa(S*)<=0 (owner bads alone force it), not sufficient."
)
