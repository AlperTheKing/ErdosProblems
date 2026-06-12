# GPT Pro Kempe-Expansion Answer Digest - 2026-06-11

Question context: can the proposed A/B/C route prove Erdős #944 by forcing a
small nontrivial 6-edge-cut in any 6-regular `(4,1)` target?

Status: GPT Pro did not supply a complete proof of A/B/C. The answer is useful
as a route correction and as a sharper formulation of the next lemma.

## Main Corrections

1. Lemma B is not a useful intermediate target. In a vertex-critical graph, the
   forced `(2,2,2)` neighbourhood condition in every deleted-vertex
   3-colouring is essentially equivalent to no incident edge being critical.
   Therefore proving B would mostly restate the no-critical-edge hypothesis in
   colouring language.

2. Attacking the full small-shore claim A directly is probably too large. The
   smaller target is first to force a nontrivial 6-edge-cut via a touched
   two-colour Kempe component.

3. The exact bounded-shore strengthening `min(|K|, |V\K|) <= 14` is the least
   trustworthy part. Large Kempe 6-poles may exist abstractly, so any K14-type
   lemma likely needs minimality or additional irreducibility.

## Verified / Already-Used Lemmas

For a target `G`, fixed `v`, and a 3-colouring `phi` of `G-v` with colour
classes `A,B,C`:

- Local multiplicity: each colour occurs exactly twice in `N(v)`.
- Kempe balance: for every `(A,B)`-Kempe component `K`, if
  `a_K = |K cap A cap N(v)|` and `b_K = |K cap B cap N(v)|`, then
  `a_K = b_K`. Otherwise swapping colours on `K` would produce a deleted
  colouring violating local multiplicity.
- Component accounting:
  `sum_{K in K_AB} |delta_G(K)| = 6|C| + 2`, and cyclically.

These are solid; the missing step is global, not local.

## Next Lemma Formulation

K6 / Kempe-expansion contradiction:

> In a minimal 6-regular `(4,1)` target, for some deleted vertex `v`, some
> 3-colouring of `G-v`, and some colour pair, there is a non-singleton touched
> two-colour Kempe component `K` with `|delta_G(K)| = 6`.

Equivalently, no target is Kempe-expanding, where every non-singleton
two-colour Kempe component touching `N(v)` has boundary at least 8.

The suggested pressure lemma is a trichotomy:

> If every touched two-colour Kempe component has boundary at least 8, then
> either a nontrivial 6-edge-cut already exists, or there is a comparable
> same-colour non-neighbour, or there is a bounded reducible atom around `v`.

In a genuine vertex-critical target, the latter two alternatives should be
impossible by already-verified reducibility/minimality lemmas, so this would
force K6.

## Weak Point

One-pair accounting is too weak: a single large touched component can absorb
the boundary budget. Any proof must use all three colour-pair decompositions
simultaneously, probably together with global terminal-list-criticality.

Potential pressure point: singleton components in a two-colour graph correspond
to vertices pure toward the third colour, and each colour-pair decomposition
has only one unit of slack beyond the singleton baseline. The missing proof is
to turn this three-pair budget into either a 6-cut or a forbidden reducible
configuration.

## Integration With Terminal-List Lemma

This answer does not supersede the global terminal blocker lemma. The best
current target is:

> Combine whole-`H` terminal-list-criticality for every non-critical edge
> `va` with the three Kempe balance/accounting identities to prove that
> Kempe-expansion is impossible.

No complete proof is known in the current workspace.
