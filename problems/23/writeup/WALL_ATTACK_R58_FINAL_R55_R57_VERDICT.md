# R58 final verdict on the R55/R57 route

## Status

The R55/R57 route is retired. This is a verdict about the proposed
certificate interface and bridge lemmas, not a disproof of Erdos Problem 23.

The final bounded attack produced two independent obstructions.

## 1. The current R57 extraction interface is false

The 16-vertex graph archived in
`WALL_ATTACK_R57_CURRENT_INTERFACE_COUNTEREXAMPLE.md` is triangle-free,
has a connected maximum cut, and is Gamma-minimal. It contains two checked
length-five rows with the required fork shape, but no pair of vertex masks has
strictly negative four-corner margin.

The exact exhaustive replay checks all `2^15` cuts and all `2^16` mask
pairs:

```
vertices=16 edges=17 triangles=0
maxcut=16 maxcut_orbits=1 connected_maxcuts=1
min_connected_maxcut_gamma=25 displayed_gamma=25
shortest_st_distance=4 shortest_rows=2
min_switch_loss=0 row_union_pair_count=65536 min_pair_margin=0
PASS_R57_CURRENT_INTERFACE_COUNTEREXAMPLE
```

Therefore the local 15-shape catalogue cannot be promoted to a full-graph
negative-switch theorem without an additional boundary-incidence hypothesis.

## 2. The positive-defect compiled bridge is also false

Nine checked copies of the same bad atom are allowed by the compiled
`AllBadsChecked` interface. Give four copies row

[
P=(s,a_1,a_2,a_3,t)
]

and five copies row

[
Q=(s,b_1,b_2,b_3,t).
]

Using the exact R53 six-family evaluator, all (2^9=512) tuples have been
enumerated. The collision minimum is 179, the minimum grouped defect on that
face is 50, and there are 420 lex-minimal states. Every one admits an optimum
using both fork halves. A forced optimum has demand 358, flow 308, and a
residual unit core

[
|O_K|=293,qquad operatorname{cap}(S_K)=292.
]

Its owner set is

[
A={s,t,a_1,a_2,a_3,b_1,b_2}.
]

The exact overload values are

[
operatorname{shoreCollision}=159,qquad
operatorname{shoreZero}=71,qquad
operatorname{internalActive}=0,
]

so

[
159+16|A|=159+112=200+71.
]

Both proposed conclusions fail:

1. Maximum-cut submodularity gives nonnegative four-corner margin for every
   pair (X,Ysubseteq V).
2. Either one-row replacement changes the split (4/5) to (3/6) or (5/4)
   while leaving ((mathrm{collision},mathrm{defect})=(179,50)).

This is an interface countermodel, not a graph-level counterexample. It
violates `CompleteShortestRowDB.badKeys_nodup`, which is absent from the
stated bridge. Adding nodup blocks this model but does not create the missing
core-to-window boundary map.

## 3. Exact missing boundary certificate

For a local window (W) and (X,Ysubseteq W), the full and local
four-corner margins satisfy

[
operatorname{margin}_{G}(X,Y)
=
operatorname{margin}_{G[W]}(X,Y)
+
eta_W(X)+eta_W(Y).
]

Thus a catalogue margin (-1) needs

[
eta_W(X)+eta_W(Y)le 0.
]

Equivalently, define external positive and negative incidence multisets:

- (mathrm{ExtPos}(X,Y)): blue edges crossing (X), blue edges crossing
  (Y), and two copies of every bad opposite-corner edge;
- (mathrm{ExtNeg}(X,Y)): bad edges crossing (X), bad edges crossing
  (Y), and two copies of every blue opposite-corner edge.

The needed theorem is an injection

[
mathrm{ExtPos}(X,Y)hookrightarrow mathrm{ExtNeg}(X,Y).
]

The frozen R55 record indexes sources, obligations, and grouped capacities.
It has no maps from external graph-boundary incidences into source keys or
from source keys into negative boundary incidences. Moreover,
`supportBoundary` and `outsideBlueBoundary` use `toFinset`, erasing the
atom multiplicity detected by owner overload.

## 4. Decision

No implementation-ready proof of the external domination injection follows
from the current R55 fields. Supplying checked paths, windows, masks, and the
external injection as a new `CheckedProtectedForkPair` field would merely
assume the missing provider theorem.

Under the final-attempt rule, the route is therefore dead:

[
oxed{	ext{R55/R57 does not close the delta-zero theorem.}}
]

The valid Lean lemmas, exact classifications, and counterexamples remain
independent mathematical contributions and are being collected in a separate
obstruction-and-certificate paper. That paper must not claim a proof of
Erdos Problem 23.

