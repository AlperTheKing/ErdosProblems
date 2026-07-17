# Adversarial formal referee report: WOWII / Graffiti.pc 143

Date: 2026-07-17
Verdict: ACCEPT on mathematical correctness and target equivalence; PR integration and status metadata remain separate tasks.

## 1. Exact invariant and target

- degreeSequence sorts the multiset of all vertex degrees and retains multiplicity
  (formal-conjectures-w143/FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Degrees.lean,
  lines 37-43).
- secondSmallestDegree is degreeSequence.getD 1 0, so index 1 is the second entry,
  not the second distinct degree (same file, lines 85-91).
- The independent computations use the same convention, namely sorted(degrees)[1]
  (atlas_check.py, lines 74-87; atlas_check_independent.py, lines 165-170).
- The extraction lemma proves that secondSmallestDegree G = 1 gives two distinct
  degree-one vertices in a nontrivial preconnected graph (Degrees.lean, lines 94-141).
  This is exactly the bridge required by PROOF.md, lines 74-80.

No second-smallest/second-distinct or multiplicity mismatch was found.

## 2. Scope and statement equivalence

The repository target quantifies over a finite type with decidable equality and at
least two vertices, a SimpleGraph, decidable adjacency, connectedness, and positive
second-smallest degree; its conclusion is the real-valued denominator-free inequality
(GraphConjecture143.lean, lines 30 and 44-46).

ExactConjecture.lean, lines 11-16, has the same binders and conclusion, modulo
hypothesis names and namespace. It compiled with exit 0 and no output; SHA-256 begins
5AF1E7C9.

- Finiteness is supplied by [Fintype alpha].
- Simplicity is built into SimpleGraph.
- Connectedness is the exact target hypothesis.
- [Nontrivial alpha] removes the order-zero/order-one case in which the second entry is
  unavailable.
- hSigma : 0 < secondSmallestDegree G makes multiplication by the denominator equivalent
  to the quotient formulation. It is redundant for a connected nontrivial finite graph,
  but it does not remove an intended graph.

Thus the compiled theorem is not merely a restricted variant of the formal target.

## 3. Tree/girth convention

The informal main statement is correctly restricted to cyclic/non-tree graphs
(PROOF.md, lines 8-18). The current formal target also includes trees because Mathlib
sets the natural-valued girth of an acyclic graph to zero.

The addendum explicitly records this convention (PROOF.md, lines 82-90). The exact
Lean assembly handles it at ExactConjecture.lean, lines 19-28: girth rewrites to zero,
one_le_largestInducedTreeSize supplies a nonempty induced tree, and positive sigma
makes the product positive.

This is correct for the formal target. A paper should keep the cyclic theorem as the
primary statement and label the tree case as a convention-dependent formal extension;
it must not silently identify Mathlib girth zero with the usual extended girth infinity.

## 4. Informal two-leaf argument

No gap was found.

- A shortest leaf-to-leaf path supplies a nonempty family of induced trees
  (PROOF.md, line 36); the Lean geodesic lemma formalizes the chord-shortening step
  (LargestInducedTree.lean, lines 149-198).
- A largest member exists by finiteness, and it is proper because a spanning member
  would make the cyclic graph a tree (PROOF.md, lines 36-38;
  TwoLeaf.lean, lines 227-252).
- Connectedness supplies a boundary edge. If the outside endpoint has a unique neighbor
  in the tree, inserting it gives a larger induced tree (PROOF.md, lines 38-40;
  LargestInducedTree.lean, lines 79-144 and 288-328).
- Two distinct neighbors and their unique tree path form a simple cycle even if the
  outside vertex has extra chords (PROOF.md, lines 42-46).
- Every vertex of that path has two distinct neighbors in the ambient graph, so neither
  degree-one vertex is on it (PROOF.md, lines 48-51). The Lean proof implements the
  same exclusion through subsingleton neighbor sets (TwoLeaf.lean, lines 178-220).
- Erasing the two leaves from the maximum tree yields the exact cardinal inequality.
  The full wrapper compiled warning-free, exit 0, SHA-256 255ADA10
  (TwoLeaf.lean, lines 221-259).

## 5. Girth branch and exact case split

The girth helper uses a girth-realizing cycle and the walk c.tail.dropLast, whose
support has girth - 1 vertices. It proves connectedness from the remaining path and
acyclicity because any induced cycle would have length at most girth - 1, contradicting
minimality (LargestInducedTree.lean, lines 201-254). This is stronger and safer than
relying on an informal chordless-cycle API. It compiled with no warnings or banned
shortcuts.

The exact assembly then splits:

1. acyclic: girth zero and a singleton induced tree;
2. cyclic with sigma one: the degree-order lemma plus the two-leaf bound;
3. cyclic with sigma at least two: the girth-minus-one bound and
   2(g-1) >= g+1 for g >= 3.

These are exhaustive under positive sigma (ExactConjecture.lean, lines 17-47).

## 6. Remaining non-mathematical items

- At the time of this review, the clean target problem file still ends the theorem with
  sorry and remains tagged research open (GraphConjecture143.lean, lines 43-47).
  The compiled body still has to be inserted and built in that exact file.
- Repository status should not be changed silently. CONTRIBUTING.md, lines 76-80 and
  212-218, governs the research solved and formal_proof metadata.
- The helper diff is large (about 463 inserted ForMathlib lines). The repository's
  25-50-line limit exempts FormalConjecturesForMathlib (CONTRIBUTING.md, lines 57-66),
  so this is not a rule violation, but maintainers may request API splitting or upstreaming.
- git diff --check is clean. The current integrated helper source builds with exit 0
  and contains no sorry or native_decide. A final lake --wfail build is still required
  after the target body and metadata are finalized.

No correctness blocker or definitional mismatch was found.
