# GPT Pro K6 Consult Digest - 2026-06-11

Question asked: can full vertex-criticality rule out the n=12
no-critical-edge/Kempe-expanding seed pattern, or prove the proposed K6/triple
pressure lemma?

Status: no complete proof of K6 was supplied.

Main answer:

- The ordinary "proper induced 4-critical atom" obstruction is exactly the
  failure of vertex-criticality. In a genuine 4-vertex-critical graph every
  proper induced subgraph is 3-colourable; if a graph is not vertex-critical,
  a failed vertex deletion contains an inclusion-minimal induced 4-critical
  subgraph.
- Comparable non-neighbours are impossible in a vertex-critical graph by the
  standard extension argument already formalized locally.
- Therefore the previous trichotomy
  `proper induced 4-critical atom OR comparable non-neighbour OR K6` becomes
  essentially circular on genuine targets: the first two alternatives are
  forbidden, so proving the trichotomy is basically proving K6.
- The local Kempe balance/accounting lemmas remain sound, but do not by
  themselves force a boundary-6 Kempe component.
- A useful replacement obstruction is a terminal list-critical blocker
  attached to a non-critical incident edge.

Terminal list-critical blocker setup:

- Let `G` be a 6-regular `(4,1)` target.
- Fix a vertex `v` and a 3-colouring `phi` of `H = G - v`.
- Suppose colour `A` appears on exactly two neighbours of `v`, call them
  `a,a'`.
- Since `va` is not critical, `G - va` is not 3-colourable.
- Define a list assignment `L_a` on `H`:
  - `L_a(a) = {A,B,C}`;
  - `L_a(x) = {B,C}` for `x in N(v) \ {a}`;
  - `L_a(x) = {A,B,C}` otherwise.
- Then `H` is not `L_a`-colourable: otherwise colour `v` by `A` in `G-va`.
- But `H-a` is `L_a`-colourable, using a 3-colouring of `G-a` and permuting
  colours so that `v` receives colour `A`.
- Hence an inclusion-minimal induced `L_a`-uncolourable blocker `Q_a` exists.
- Any such blocker contains both terminals `a` and `a'`; the original colouring
  `phi` satisfies all lists except at `a'`.

New target proposed by GPT Pro:

> Terminal-blocker-to-K6 lemma. In a 6-regular `(4,1)` target, the minimal
> `L_a`-critical blocker `Q_a` forced by any terminal pair `a,a'` should imply
> either a touched two-colour Kempe component of boundary 6, or an impossible
> structural form.

Weakest step:

- Prove that a minimal terminal list-critical blocker forces a small-boundary
  two-colour Kempe component. Ordinary one-pair Kempe accounting does not
  supply this.

Actionable next work:

1. Build a C++ exact list-colouring/blocker finder for the existing n=10/n=12
   no-critical-edge seeds, to understand the terminal blocker shapes.
2. Ask GPT Pro a sharper follow-up only after local blocker data is available:
   classify minimal `L_a` blockers under degree-6/Kempe-expansion hypotheses.
3. Consider Lean-formalizing the terminal blocker existence lemma separately
   from any unproved blocker-to-K6 step.
