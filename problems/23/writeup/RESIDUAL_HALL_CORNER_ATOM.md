# Residual Hall Corner Atom

This is the active replacement for the superseded no-two-hole corridor route.
The hard `h_blowup(3)` all-max side shows that component-local single-miss is
false, but the exact residual Hall condition survives.

## Setup

Work in one completed terminal-shadow switch `S`.

Let

```text
F = crossing bad edges,
E = old blue boundary exits,
Wit(f,e) = f witnesses e.
```

Let

```text
L0 = min_{f in F} ell(f),
lambda0 = min_{e in E} lambda(e),
F0 = {f in F : ell(f)=L0},
F1 = F \ F0,
E0 = {e in E : lambda(e)=lambda0}.
```

Stage 0 chooses an injective matching

```text
mu : F0 -> E0
```

minimizing

```text
sum_{f in F0} c(mu(f)),      c(e)=|{g in F1 : Wit(g,e)}|.
```

Delete the matched exits and form the residual graph

```text
H1 = (F1, E \ mu(F0), Wit).
```

## Active Target

For every residual connected component `(A,B)` of `H1`, prove Hall:

```text
forall X subset A,     |N_H1(X)| >= |X|.
```

Equivalently, each residual component has a matching saturating its `F1` side.

This is strictly weaker than component-local single-miss and is the correct
condition needed by the stage-0 residual matching step.

## Hard H3 Calibration

The first known obstruction to single-miss is:

```text
graph: h_blowup(3), n=27
side:  111111111111111100000000000
negative vertex: v=18
```

For the chosen switch:

```text
S =
{3,4,5,6,7,8,9,10,11,12,13,14,15,18,21,22,23,24,25,26}
```

The stage-0 matching is:

```text
(19,24)->(3,19), (19,25)->(4,19), (19,26)->(5,19),
(20,24)->(3,20), (20,25)->(4,20), (20,26)->(5,20).
```

The residual component has:

```text
A =
{(0,15),(1,15),(2,15),(16,24),(16,25),(16,26),
 (17,24),(17,25),(17,26)}

B =
{(0,18),(1,18),(2,18),(6,19),(6,20),(7,19),(7,20),(8,19),(8,20)}
```

It has `75` witness edges and satisfies Hall exactly.

However:

```text
(0,15) misses (1,18),(2,18)
(1,15) misses (0,18),(2,18)
(2,15) misses (0,18),(1,18)
```

So any proof of residual matching must allow two-miss rows.

## Corner Replacement Handle

Orient each exit `e=xy` as `(inside(e), outside(e))` relative to `S`, and
orient each crossing bad edge `f` as `(inside(f), outside(f))`.

For a residual miss `(f,e)`, the tested replacement rule is:

```text
there exists e' in B with Wit(f,e') and one of:
  outside(e') = outside(e),
  inside(e') = inside(f),
  e' = (inside(e), outside(f)).
```

On the hard H3 component every miss is repaired by the corner case.  Example:

```text
f=(0,15), oriented (15,0)
e=(1,18), oriented (18,1)
corner replacement e'=(0,18), oriented (18,0), and Wit(f,e').
```

This suggests the geometric lemma should not forbid two missed exits.  It
should prove that every right-closed deficient Hall set has enough side-door or
corner exits to inject its extra blue boundary into residual bad edges.

Important guardrail: the local replacement rule alone does not imply Hall.
For example, take rows `f0,f1,f2` and exits `e0,e1,e2`, with all exits sharing
the same outside door, and incidences

```text
N(f0)={e0},   N(f1)={e0},   N(f2)={e0,e1,e2}.
```

Every missed incidence of `f0` or `f1` has the same-outside replacement `e0`,
and the component is balanced and connected, but `{f0,f1}` has neighborhood
`{e0}`.  Therefore the proof cannot quotient away the prefix-hull/side-door
structure; it must prove the extra-door Hall statement below.

## Proof Atom To Formalize

Assume a deficient set exists in one residual component:

```text
X subset A,     |N(X)| < |X|.
```

Choose it minimal under the usual peeling of one-door rows, so every remaining
row has at least two doors into the candidate exit set.  Build the blue-closed
prefix hull from the terminal witnesses of `X`.

Target geometric contradiction:

```text
No reduced deficient multidoor fan core exists.
```

Concrete form:

```text
Let U be the blue closure of the prefix hull.
Let B+ = delta_B(U) \ Wit(X).
Let M+ = delta_M(U) \ X.
Build the extra-door graph D_X from B+ to M+.

For every reduced nonempty Z subset B+,
  where every g in N_D_X(Z) has at least two Z-doors,
prove |N_D_X(Z)| >= |Z|.
```

By the peeling argument this implies the full extra-door Hall condition, and
then max-cut gives the original residual Hall inequality.

## Lean-Checked Wrappers

The non-geometric wrappers are isolated in
`problems/23/lean/ResidualHallScratch.lean`.

Machine-checked pieces:

```text
exists_reduced_deficient_of_descent:
  If every deficient non-reduced object has a strictly smaller deficient
  descendant, then any deficient object has a reduced deficient descendant.

no_deficient_of_descent_and_no_reduced:
  If non-reduced deficient objects descend and no reduced deficient object
  exists, then no deficient object exists.

deficient_set_contradicts_extra_charge:
  X.card + Mextra.card <= deltaM.card,
  deltaB.card <= Y.card + Bextra.card,
  Bextra.card <= Mextra.card,
  deltaM.card <= deltaB.card,
  Y.card < X.card
  are contradictory.

no_hall_deficient_set_of_extra_charge:
  If every Hall-deficient set admits such a blue-closed extra-charge
  certificate, then residual Hall holds.

no_hall_deficient_set_of_reduced_extra_charge:
  If every deficient non-reduced set has a smaller deficient descendant,
  and every reduced deficient set admits the extra-charge certificate, then
  residual Hall holds.
```

Therefore the remaining proof obligation is purely geometric:

```text
1. One-door peeling:
   every deficient non-reduced extra-door set has a strictly smaller
   deficient descendant.

2. RFC / no-naked-leaf:
   no reduced deficient multidoor fan core exists in a completed
   blue-closed prefix hull.
```

The old `THCorridorScratch.lean` `AtMostOneMiss` target is archived and marked
superseded; it should not be used as a proof input.

## Exact Gates

Regression evidence, not proof inputs:

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 5 --max-n 4 --h3-hard --max-add 2 --max-enum 30

tested=21
status={'ok': 21}
VERDICT: PASS
```

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 3 \
  --h3-hard --max-add 2 --max-enum 30

tested=175
components=178
status={'ok': 175}
VERDICT: PASS
```

The same run includes components with `max_row_miss=2` and `max_row_miss=4`,
so the gate is genuinely checking Hall beyond the old single-miss sufficient
condition.

The reduced fan-core gate is the proof-facing regression for the stronger
side-door atom:

```text
python problems/23/writeup/_rfc_gate.py --h3-hard --max-cross 15

switches=120
(X,U) instances=1367
rfc_fail=0
toobig=0
VERDICT: RFC HOLDS
```

Here the hard H3 switch itself contributes the uncapped case
`crossM=15`, `bdyB=15`, `447` nontrivial prefix-hull instances, and no reduced
deficient `Z`.

## Lean Wrapper Status

The finite cardinal wrapper is isolated in:

```text
problems/23/lean/ResidualHallScratch.lean
```

Verified through the Formal Conjectures Lake environment:

```text
lake env lean E:/Projects/ErdosProblems/problems/23/lean/ResidualHallScratch.lean
rg "\b(sorry|admit|axiom)\b" E:/Projects/ErdosProblems/problems/23/lean/ResidualHallScratch.lean
```

Result: Lean exits `0`; no `sorry`, `admit`, or `axiom`.

This file proves only the abstract counting bridge:

```text
extra bad boundary pays extra blue boundary
+ max-cut boundary inequality
=> no residual Hall-deficient row set.
```

The remaining unproved geometry is exactly the RFC/NL atom that supplies that
extra-charge inequality for the blue-closed prefix hull.

The proof-facing NL statement is frozen in:

```text
problems/23/writeup/NO_NAKED_LEAF_RFC_TARGET.md
```
