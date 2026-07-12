# R42 live-x graph-specific exclusion

## Exact finite lemma

Let `F*` be the 24-edge bipartite support graph and let `M*` be the 25
same-shore bad-edge set in

```text
tmp/fanout/r42_graph_specific_exclusion/t5_live_x_classifier_v_l9_r9_5000.json
canonical SHA-256 6595501f532577c3475d29e2a3c7e9f318debecd5e1014d0793e1b462d07494f.
```

This datum is a triangle-free 25/24 transversal circuit with an exact R48
local profile at the live middle-swap vertex `x=9`.  In particular, it is a
real counterexample to the support-only triangle-forcing lemmas.

Adjoin seven vertices.  For any placement of those vertices on the two cut
shores, there is no bipartite blue graph `B` such that:

1. `F* subset B`;
2. `B union M*` is triangle-free;
3. for every `h in M*`, every length-four `B`-path joining the endpoints of
   `h` belongs to the original complete shortest-row footprint of `h`;
4. the displayed cut is maximum:
   `|delta_B(W)| >= |delta_M*(W)|` for every vertex set `W`.

The statement does not assume that `B` is connected.  It therefore excludes
every connected production extension as a special case.

## Fixed-switch proof certificate

Set

```text
S = {4,5,6,7,8,11,14,16}.
```

Exactly 23 bad edges and two fixed blue edges cross `S`.  Hence condition 4
requires at least 21 added blue edges across `S`.

Write `k` for the number of new vertices placed on the old left shore.  Exact
SAT maximization under only valid mixed-triangle clauses and valid forbidden
new-row clauses gives:

```text
k                  0      1   2   3   4   5   6   7
safe capacity      21     19  17  15  13  11   9   7
required           21     21  21  21  21  21  21  21
```

Thus `k=1,...,7` are impossible.  For `k=0`, both `S` and
`S union {18,...,24}` require 21 added crossings.  Their separate capacities
are 21, but their exact joint capacity is 28, whereas maximum-cut requires a
sum of 42.  This excludes the final split.

The primary extension artifact is

```text
t5_live_x_maxcut_extension.json
canonical SHA-256 6bd2c4e89c9912cb3acbf76938436f5acadbc204bcec5b7f0bbf60fcbf7989bf.
```

An independent CNF reconstruction and CaDiCaL 1.9.5 replay gives all eight
splits UNSAT:

```text
t5_live_x_maxcut_extension_verification.json
canonical SHA-256 8618fe18d5539b7fdc702c9700c121e0b443d27eadec3935821ffd9d280b16a3.
```

The independent capacity artifact is

```text
t5_live_x_switch_capacity.json
canonical SHA-256 ddc0376f8de231fa8f86753aac6340e4aa5ca7930b9841b40dbd0f69342524ba.
```

## Production diagnosis

Inside the fixed support graph, complete profile coverage blankets the two
non-active blue edges at `x`, so the intrinsic active component is only the
two-vertex set containing `x` and its active neighbour.  That intrinsic fact
is not itself a production exclusion because an ambient row-safe blue edge
could enlarge the active component.

The quantified ambient extension result closes that loophole.  The first
production invariant violated by this live-x model is precisely the R47
`TriangleFreeRowPreservingMaximumCutExtension` gate, equivalently
`CheapGeometry`: maximum-cut demands more switch-crossing blue capacity than
triangle-freeness and complete-row preservation permit.

This lemma excludes the fixed live-x countermodel.  It is not an exhaustive
t=5 theorem and does not assert two-new-edge turnover or support
monotonicity.
