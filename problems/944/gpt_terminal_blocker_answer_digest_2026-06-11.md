# GPT Pro Terminal Blocker Answer Digest - 2026-06-11

Question asked: can the 6-vertex terminal list-critical blocker found in the
n=12 seed occur inside a genuine 6-regular `(4,1)` target under
Kempe-expansion?

Status: GPT Pro supplied a complete negative answer for the six-vertex blocker,
and in fact a stronger lemma.

## Verified Core Lemma

Let `G` be 4-vertex-critical. Fix `v in V(G)`, put `H = G - v`, and fix
`a in N(v)`. Define the terminal list assignment `L_a` on `H` by:

- `L_a(a) = {A,B,C}`;
- `L_a(x) = {B,C}` for `x in N(v) \ {a}`;
- `L_a(x) = {A,B,C}` otherwise.

Then every proper induced subgraph of `H` is `L_a`-colourable.

Proof sketch, independently checked:

Suppose `S` is a proper subset of `V(H)` and `H[S]` is not `L_a`-colourable.
Let `W = G[S union {v}]`. If `W` has a 3-colouring, rename colours so that
`v` has colour `A`; restricting to `S` gives an `L_a`-colouring of `H[S]`,
contradiction. Hence `W` is not 3-colourable. Since `S` is proper in `H`,
choose `y in V(H) \ S`. Then `W` is an induced subgraph of `G-y`, but
`G-y` is 3-colourable by vertex-criticality, contradiction.

Therefore every proper `S` is `L_a`-colourable.

## Consequence For Non-Critical Edges

If additionally `G - va` is not 3-colourable, then `H` is not
`L_a`-colourable. Combining with the core lemma, `H` itself is
inclusion-minimal `L_a`-uncolourable.

So in a genuine `(4,1)` target, terminal list blockers are global objects:
the only induced `L_a`-blocker is the whole vertex-deleted graph `G-v`.

## Consequence For The n=12 Seed

The extracted 6-vertex blockers cannot occur in any genuine vertex-critical
target. If such a blocker `Q` existed properly inside `H`, then
`G[Q union {v}]` would be a proper induced 4-chromatic subgraph, contradicting
vertex-criticality. This explains why the n=12 seed is not vertex-critical:
its small terminal blockers are exactly ordinary 4-chromatic witnesses after
adding back the deleted vertex.

## Corrected Next Target

The terminal-blocker method must now be global:

> Whole-H terminal blocker to K6 lemma. In a 6-regular `(4,1)` target, for
> every `v`, deleted-vertex colouring, and terminal `a`, the whole graph
> `H=G-v` is terminal-list-critical. Use this global minimality, together
> with Kempe balance/accounting, to force a touched two-colour Kempe component
> of boundary 6.

This replaces the earlier small-blocker classification target.
