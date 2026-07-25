# Erdős Problem 602 - Approach Registry

Live audit date: 2026-07-23.

## Exact target

Let \(\mathcal A=(A_i)_{i\in I}\) be a family of countably infinite sets.
Assume that, for distinct \(i,j\), the intersection \(A_i\cap A_j\) is
finite and never has size one. Prove in ZFC that
\(\bigcup_i A_i\) has a 2-colouring under which every \(A_i\) meets both
colour classes, or give an explicit ZFC counterexample.

## DIRECT ROUTE R1 - limit-stable greedy repair

### 1. Exact final deliverable

A ZFC proof of Property B for every family in the exact target. It is enough
to give a transfinite repair construction and prove that every repaired set
has two permanently opposite-coloured witnesses at every limit stage.

### 2. Current frontier lemma

**Protected-zero selection lemma.** Well-order the family and start with all
points coloured zero. Whenever the current set is monochromatic, flip one of
its points from zero to one. There is a choice of flip points (allowing finite
injury and protected witnesses) such that:

1. no point is flipped more than once; and
2. every \(A_i\) contains a point which is never flipped.

The local no-singleton-intersection lemma ensures that a successor flip never
makes another currently split set monochromatic. The second clause is the
missing limit-stage assertion.

### 3. Explicit logical bridge

At the stage when \(A_i\) is processed, either it already contains a flipped
point or one of its points is flipped. Hence it contains a final colour-one
point. The frontier lemma supplies a never-flipped colour-zero point in the
same \(A_i\). Therefore every \(A_i\) meets both final colour classes, which
is exactly Property B.

### 4. Next falsifiable action

First falsify the published unrestricted instruction "choose any point" by
an explicit \(\omega\)-stage family satisfying the exact intersection
hypotheses whose legal repair run makes an earlier set monochromatic at the
limit. Then test whether protecting one zero witness per processed set always
admits the next repair. Compare this extension assertion with Miller's
non-2-colourable almost-disjoint construction, Miller's bounded-intersection
theorem, Komjáth's essential-disjointness theorem, and the set-theoretic
splitting literature.

### 5. Exit condition

Exit R1 if the protected-zero selection lemma is false, is equivalent to the
original Property B assertion, or requires an unproved uniform bound on
intersection sizes. A counterexample only to one greedy schedule kills that
schedule, not Problem 602. Do not substitute finite-uniform extremal bounds:
they bridge to the target only if they yield the protected-zero lemma for an
arbitrary transfinite family.

## Audit constraints

- Preserve the distinction between successor-stage invariance and
  limit-stage invariance.
- Every alleged counterexample must have countably infinite edges and
  pairwise intersections finite and in \(\{0,2,3,\ldots\}\).
- Pairwise finite intersections without the no-singleton condition are known
  not to imply Property B.
- A theorem assuming one fixed finite upper bound on all intersections proves
  only the strongly almost-disjoint special case.
