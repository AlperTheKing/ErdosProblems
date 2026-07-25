# Erdős Problem 602: limit-stage and literature audit

Audit date: 2026-07-23.

## Verdict

The proposed one-pass greedy proof is false.  Its successor-step invariant is
correct, but it does not survive a limit ordinal.  The failure already occurs
at stage omega in an explicit family satisfying every hypothesis of Problem
602.

The stronger `Protected-zero selection lemma` in `APPROACH_REGISTRY.md` would
repair the proof, but it is exactly equivalent to Property B for the original
family.  It is therefore not an isolated residual lemma and triggers the
registry's exit condition.

The literature checked below neither supplies that selection lemma nor gives a
ZFC counterexample satisfying the no-singleton condition.  The official page
still marks [Problem 602 as open](https://www.erdosproblems.com/forum/thread/602?order=oldest).

## 1. Exact omega-limit counterexample to the greedy run

Take pairwise distinct points

\[
  a_0,a_1,\ldots;\qquad u_0,u_1,\ldots;
\]

and pairwise disjoint countably infinite private sets

\[
  P_n=\{p_{n,k}:k<\omega\},
\]

also disjoint from all `a`- and `u`-points.  Define

\[
  A=\{a_n:n<\omega\}
\]

and, for each `n < omega`,

\[
 B_n=\{a_{n+1},a_{n+2},u_n\}\cup P_n
      \cup\begin{cases}\varnothing,&n=0,\\
                        \{u_{n-1}\},&n>0.
          \end{cases}
\]

Every edge is countably infinite.  The complete intersection table is

\[
 |A\cap B_n|=2,
 \qquad |B_n\cap B_{n+1}|=2,
 \qquad B_n\cap B_m=\varnothing\quad(|n-m|\ge 2).
\]

Indeed, `A cap B_n` consists of `a_(n+1),a_(n+2)`, while consecutive
`B`-edges share exactly `a_(n+2),u_n`.  Thus all distinct-edge
intersections are finite and have size zero or two, never one.

Start with every point coloured zero and process the edges in the order

\[
  A,B_0,B_1,B_2,\ldots.
\]

Use the following choices, all legal under the proposed instruction "choose
any point of the currently monochromatic edge":

* at `A`, flip `a_0` to one;
* at `B_n`, flip `a_(n+1)` to one.

Inductively, immediately before processing `B_n`, precisely
`a_0,...,a_n` among the `a`-points have been flipped.  None belongs to
`B_n`, so `B_n` is still all zero and the prescribed flip is legal.  Each
point is flipped at most once.

After every finite stage, `A` contains both a flipped point and infinitely
many unflipped points.  At the limit stage omega, however, every `a_n` has
been flipped, so `A` is all one.  No successor step made `A` monochromatic;
monochromaticity appeared only in the pointwise limit.

This proves exactly:

> The local rule "repair a monochromatic edge by flipping any one of its
> points" plus the fact that each point flips at most once does not imply
> limit-stage preservation, even under the exact hypotheses of Problem 602.

It does **not** prove that this family lacks Property B.  It only falsifies the
claimed arbitrary-choice greedy construction.
Indeed, Bernstein's lemma guarantees Property B here because the displayed
family itself is countable.

## 2. Why the successor argument itself is valid

Suppose an all-zero edge `E` is repaired by flipping `x in E`.  If another
edge `F` was already split and became all one after this single flip, then `x`
would have been its unique zero.  Because every other point of `E` is still
zero, `E cap F` would have to equal `{x}`.  The hypothesis rules this out.

The all-one case is symmetric; the explicit run in Section 1 uses only
zero-to-one flips.
The counterexample above therefore does not exploit a successor error.  It
isolates the missing implication

\[
  \text{split at every earlier stage}\ \not\Longrightarrow\
  \text{split at a limit stage}.
\]

## 3. The protected-zero lemma is equivalent to the target

One direction is the bridge already recorded in the registry: if the greedy
run gives every edge a flipped point and a never-flipped point, then final
colour one for flipped points and zero otherwise splits every edge.

Conversely, suppose a Property B colouring already exists and let `R` be its
colour-one class.  Process the edges in any well-order.  Whenever the current
edge has no previously flipped point, flip any point in its nonempty
intersection with `R`.  All flips lie in `R`; hence every edge eventually has
a flipped point.  Every edge also has a point outside `R`, and that point is
never flipped.  Thus the protected-zero lemma follows from Property B.

Consequently,

\[
  \text{Protected-zero selection}\quad\Longleftrightarrow\quad
  \text{Problem 602 has a positive answer}.
\]

Calling the choice scheme "finite injury" does not reduce this equivalence.
A genuine repair still needs a new structural theorem ensuring globally
compatible permanent witnesses.

## 4. A smaller obstruction to naive no-injury protection

The following example explains why simply reserving one arbitrary zero per
processed edge is insufficient.  Let

\[
 C=\{h_0,h_1\}\cup\{a_n:n<\omega\}.
\]

Put `c_0=h_0`, `c_1=h_1`, and `c_(n+2)=a_n`, and define

\[
 D_n=\{h_0,h_1,c_n\}\cup P_n.
\]

Here `|C cap D_n|=2` for `n=0,1`, `|C cap D_n|=3` for `n>=2`, and
`D_n cap D_m={h_0,h_1}` whenever `n != m`.  Process all `D_n` before `C`,
flip a private point of each `D_n`, and reserve `c_n` as its zero witness.
Every reservation is legal because `c_n in D_n`.  At the limit every point
of `C` is reserved zero, so `C` is monochromatic and cannot be repaired
without injury.

This does not refute a globally informed protection strategy: one could have
reserved private points instead.  It only rules out arbitrary permanent
reservations and identifies the global bookkeeping burden.

## 5. What arXiv:2408.00484 proves

Danila Cherkashin's [On set systems without singleton intersections](https://arxiv.org/abs/2408.00484)
is a finite extremal theorem.  For `k > 1`, it determines the maximum size of
a family of `k`-subsets of a fixed `(k^2-k+1)`-element ground set with no
pair intersecting in exactly one point:

\[
  \binom{k^2-k-1}{k-2}.
\]

It does not discuss Property B, countably infinite edges, transfinite
recursion, protected witnesses, or limit stages.  No implication from that
finite cardinality bound to the required infinite splitting theorem is given.
It therefore does not repair the gap.

## 6. Exact literature boundary

* [P. L. Erdős (1999)](https://www.renyi.hu/~elp/Splitting/Erdos-AoC99.pdf)
  records Bernstein's lemma: every **countable family** of infinite sets has
  Property B.  It also records Lovász's theorem for a **finite ground set**
  with no singleton edge intersections.
* Hajnal, Juhász and Shelah's
  [Splitting strongly almost disjoint families](https://shelah.logic.at/files/95149/249.pdf)
  records Miller's ZFC theorem when one finite bound uniformly controls every
  pairwise intersection.  Corollary 2.5 gives essential disjointness in that
  uniformly bounded setting.
* The same paper, Theorem 4.3 and Corollary 4.4, gives in ZFC an almost-disjoint
  subfamily of `[omega]^omega` with no Property B.  Enumerate all subsets
  `X_alpha` of omega and thin an almost-disjoint `A_alpha` inside either
  `X_alpha` or its complement; the member indexed by any proposed colour
  class is monochromatic.  This construction guarantees only finite
  intersections and may produce intersections of size one, so it is not a
  counterexample to Problem 602.

Lovász's finite result does not pass through ordinary compactness here.  For
an infinite edge, "contains a zero and a one" is an infinitary existential
condition (an open, not closed, subset of the Cantor cube of colourings).
Finite restrictions can lose one of the two required colours at a limit.

## Direct-route decision

`DEAD: limit-stage repair — successor safety supplies no permanent witness,
and the proposed protected-witness frontier is equivalent to the original
Property B assertion.`

The exact new fact from this audit is the family in Section 1, which falsifies
the generated proof's unrestricted-choice and limit-induction steps.  The
scope is deliberately limited: Problem 602 itself remains open.
