# GPT Pro Kempe-Pressure Answer Digest - 2026-06-11

Question asked: combine global terminal-list-criticality with the three Kempe
decompositions to prove K6, or explain exactly why the current hypotheses are
insufficient.

Status: no proof of K6. GPT Pro identified a new verified reduction and a
precise remaining gap.

## Verified Reduction: Boundary-Support Obstruction

Fix a target `G`, a vertex `v`, `H=G-v`, and a deleted-vertex colouring `phi`.
Let `a,a'` be the two A-coloured neighbours of `v`, and define `L_a` as before:
`a` has all three colours, the other five neighbours of `v` forbid `A`, and all
other vertices are free.

Let `K` be the `(A,B)`-Kempe component of `phi` containing `a'`. Let
`R_C(K)` be the set of vertices of `K` that have at least one neighbour outside
`K` with colour `C`.

Define `M_{a,K}` on `K` by taking `L_a` and additionally forbidding colour `C`
on `R_C(K)`.

Then `K` is not `M_{a,K}`-colourable.

Proof, independently checked:

If `K` had such a colouring, paste it into the original colouring outside `K`.
There are no cross-edge conflicts, because every edge leaving an `(A,B)`-Kempe
component goes to a `C`-coloured vertex, and vertices in `R_C(K)` were forbidden
to receive `C`. The only original `L_a` violation was at `a'`, which lies in
`K`; inside `K` the new colouring satisfies `L_a`. This would give an
`L_a`-colouring of all `H`, contradicting the no-critical-edge/global
terminal-list lock.

Equivalent phrasing:

Every `L_a`-colouring of `K` must use colour `C` somewhere on the third-colour
boundary support `R_C(K)`.

## What This Does Not Prove

The obstruction only controls the support set `R_C(K)`, not the number of
edges from `K` to the third colour:

`|delta_G(K)| = |K cap N(v)| + e_H(K,C)`.

K6 requires:

- type `(1,1)`: `e_H(K,C) = 4`;
- type `(2,2)`: `e_H(K,C) = 2`.

Kempe-expansion allows:

- type `(1,1)`: `e_H(K,C) >= 6`;
- type `(2,2)`: `e_H(K,C) >= 4`.

The list obstruction sees only which vertices touch the third colour, not how
many third-colour edges leave those vertices.

## Abstract Countermodel

GPT Pro gave a quotient-level model, not an actual graph:

- colour classes all size 4;
- for each colour pair, two touched `(1,1)` components, each a single terminal
  edge with boundary 8;
- one untouched component with boundary 10;
- accounting: `8 + 8 + 10 = 26 = 6*4 + 2`.

This satisfies Kempe balance, Kempe accounting, Kempe-expansion, and the
boundary-support obstruction at quotient level, while having no boundary-6
touched component. It shows the current fixed-colouring constraints alone do
not logically force K6.

## New Missing Lemma

Support-to-multiplicity lemma:

> In a genuine 6-regular target, a touched Kempe component that is
> boundary-support-critical cannot have too many third-colour boundary edges.

Concrete version:

- if `K` has terminal type `(1,1)`, prove `e_H(K,C) <= 4`;
- if `K` has terminal type `(2,2)`, prove `e_H(K,C) <= 2`.

Together with edge-connectivity lower bound `|delta_G(K)| >= 6`, this would
force `|delta_G(K)| = 6` and prove K6.

## Weakest Point

Global `L_a`-criticality gives `L_a`-colourings of every `H-y`, but those
colourings need not be Kempe-reachable from the fixed colouring `phi|_{H-y}`.
The missing bridge is to connect one-deletion list-colourability back to the
Kempe components of the original colouring.
