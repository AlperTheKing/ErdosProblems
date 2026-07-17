# Erdős Problem 128 — Adversarial audit of the n=20 route

Audit date: 2026-07-13.

## Verdict

- **Direct certificate bridge: PASS.** A simple triangle-free graph on vertices
  0,...,19 whose every induced 10-set has at least 9 edges is a literal
  counterexample to the stated universal assertion.
- **One-shot n=20 attack: GO.** The declared SAT/CP-SAT experiment has a direct
  bridge and a hard exit; it is not an asymptotic reformulation.
- **Claim that Problem 128 is resolved: NO-GO at this audit.** No adjacency-list
  witness was available. A solver timeout, a heuristic lower bound, or an
  uncheckable UNSAT status does not resolve the problem.
- **Novelty gate: conditional PASS.** The primary results checked below do not
  contain a theorem covering every residual n=20 candidate. This is a search
  audit, not a guarantee that no uncatalogued result exists.

## 1. Certificate bridge

For n=20, the formal antecedent for a set V' is

    2 * |V'| + 1 >= 20,

which over natural-number cardinalities is equivalent to |V'| >= 10.
The edge inequality is

    50 * e(G[V']) > 20^2 = 400,

which over integers is equivalent to e(G[V']) >= 9. There is no rounding
ambiguity: 8 edges gives equality, not strict inequality.

Checking only 10-sets is sufficient. If W has at least 10 vertices, choose
a 10-subset S of W. Every edge of G[S] is also an edge of G[W], so
e(G[W]) >= e(G[S]) >= 9. This covers all sizes 10 through 20, including
the whole graph.

The official discussion confirms both the floor convention and that
“subgraph” means induced subgraph:
<https://www.erdosproblems.com/forum/thread/128>. The local Lean statement
uses the same integer condition. A finite witness proves that the mathematical
answer is “no”; in Lean one would instantiate the right-hand universal
implication and refute it with the witness.

## 2. Audit of SEARCH_LEMMAS.md

### Lemma 1 — PASS

The ten-set monotonicity argument above is exact.

### Lemma 2 — PASS

Fixing v, there are

- C(19,10) = 92378 ten-subsets of V(G) \ {v}; and
- each edge not incident with v occurs in C(17,8) = 24310 of them.

Thus

    (e-d(v)) * 24310 >= 9 * 92378

and e-d(v) >= 171/5. Integrality gives e-d(v) >= 35.
Summing over all 20 vertices is legitimate because

    sum_v (e-d(v)) = 20e - sum_v d(v) = 18e.

Hence 18e >= 700, so e >= 39. No divisibility or strictness error was
found.

### Lemma 3 — PASS

For a nonedge uv, adding uv preserves triangle-freeness exactly when
u,v have no common neighbour. Adding an edge can only increase induced
edge counts. Iteration terminates after at most 190 additions, so restricting
an existence search to maximal triangle-free graphs is lossless.

The current CP-SAT encoding was also checked: its auxiliary variable for a
potential common neighbour is constrained to be exactly the AND of the two
incident edges, and every pair is required to be either an edge or to have
such a witness. This matches maximal triangle-freeness.

### Lemma 4 — PASS, with a composition caveat

Relabelling vertices in non-increasing degree order preserves every
isomorphism class, so the displayed degree inequalities alone are safe.
They remain safe with relabelling-invariant constraints. They must be
re-audited if combined with an additional labelled choice such as fixing an
arbitrary specific edge. The current CP-SAT file contains no such extra
labelled fixing.

## 3. Primary-result overlap at n=20

The checked results do not close the full n=20 case.

- Erdős–Faudree–Rousseau–Schelp's general result uses the stronger local
  threshold n^2/16 = 25 at n=20, so it does not exclude minimum 9.
- Krivelevich's bound n^2/36 = 100/9 only guarantees a 10-set with at most
  11 edges at this order, not at most 8:
  <https://doi.org/10.1006/jctb.1995.1018>.
- Keevash–Sudakov prove the conjecture for total edge count at most
  n^2/12 and at least n^2/5:
  <https://doi.org/10.1016/j.jctb.2005.11.003>. At n=20, Lemma 2 already
  forces e>=39, outside the sparse range. Their dense theorem excludes a
  strict candidate with e>=80, leaving 39<=e<=79.
- Norin–Yepremyan prove it when minimum degree is at least 5n/14, and in
  further dense/stability regimes:
  <https://arxiv.org/abs/1311.5818>. Consequently a candidate must have
  minimum degree at most 7, but their theorem does not cover all remaining
  graphs.
- Razborov's universal bound is 27n^2/1024 = 10.546875 at n=20, which
  only forces an integral half with at most 10 edges. His exact-class
  theorems imply that a candidate must have independence number at most 7,
  must contain a 4-cycle, and cannot be strongly regular:
  <https://arxiv.org/abs/2104.09406>.
- The later signless-Laplacian theorem explicitly describes Brandt's
  spectral conjecture as a subproblem/relaxation of the sparse-half
  conjecture, not a proof of it:
  <https://arxiv.org/abs/2204.00093>.
- Since alpha(G)<=7, a candidate is also a (3,8;20)-Ramsey graph. The
  McKay–Zhang theorem R(3,8)=28 and its modern certificate concern
  nonexistence at order 28. The historical computation generated about
  5.2 million (3,7)-graphs at orders 20–22 as an intermediate step, not an
  exhaustive sparse-half theorem for (3,8;20):
  <https://doi.org/10.1002/jgt.3190160111> and
  <https://cs.uwaterloo.ca/~cbright/group/research_paper_conor_duggan.pdf>.
  The public McKay catalogue supplies all largest (3,8;27)-graphs, not all
  order-20 graphs:
  <https://users.cecs.anu.edu.au/~bdm/data/ramsey.html>.

The official page still lists the problem as open and records no claimed
solution:
<https://www.erdosproblems.com/128>. Searches for the exact sparse-half
phrase, small-order computations, and n=20 produced no primary theorem
enumerating or excluding all 20-vertex candidates.

Therefore any witness returned by the search must lie in this residual
profile:

    39 <= e <= 79, alpha(G) <= 7, delta(G) <= 7, girth 4,
    and G is not strongly regular.

These are consequences for auditing a candidate; they are not additional
assumptions needed by the finite verifier.

## 4. Independent exact verifier

verify/audit_verify.py accepts either JSON adjacency data or plain lines of
the form v: neighbours. It rejects missing rows, loops, duplicate neighbours,
out-of-range labels, and asymmetric declarations. It then independently:

1. enumerates all C(20,3)=1140 triples and counts triangles;
2. enumerates all C(20,10)=184756 ten-sets;
3. counts each induced edge by direct unordered-pair membership;
4. reports the exact histogram, minimum, minimizers, and canonical
   adjacency SHA-256; and
5. accepts only if the triangle count is zero and the minimum is at least 9.

It imports no solver and shares no SAT representation.

verify/audit_selftest.py gave the following exact outcomes:

| Graph | Edges | Triangles | Minimum on 10 vertices | Sets below 9 | Expected |
|---|---:|---:|---:|---:|---|
| empty graph | 0 | 0 | 0 | 184756 | reject |
| complete graph K20 | 190 | 1140 | 45 | 0 | reject: triangles |
| balanced C5 blow-up by 4 | 80 | 0 | 8 | 60 | reject: strict threshold |
| Petersen blow-up by 2 | 60 | 0 | 8 | 540 | reject: strict threshold |

An asymmetric adjacency declaration was also rejected. The complete log is
verify/audit_test.log.

SHA-256:

- audit_verify.py:
  fb8bbfaf5d81a6cbd6e869624d21fded74bd63263eb4cc53ecabf22d0ad13cbc
- audit_selftest.py:
  044962512ec6845be1cee76c80c9d2fbfb44d4407eef280514848679c0871116
- audit_test.log:
  5b1371bb3dfbf68303a5764ed9f900a47d50c337b28f03761079a1c4cc723f2a

## 5. Acceptance decision

A candidate is **GO** only after this verifier and a separately implemented
verifier both accept the same hashed adjacency list. Until then the project
has only a well-posed direct experiment, not a counterexample and not a proof.

An UNKNOWN or timed-out solver result is **NO-GO** for any mathematical
claim. A genuine UNSAT conclusion is usable only with a replayable proof
certificate; even then it kills only the declared n=20 route and does not
prove the original universal statement.

