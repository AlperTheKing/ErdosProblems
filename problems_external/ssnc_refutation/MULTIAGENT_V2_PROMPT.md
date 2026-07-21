# Counterexample Prompt - Seymour's Second-Neighborhood Conjecture

This is a neutral, target-specific adaptation of OpenAI's published Cycle
Double Cover multiagent-v2 prompt. It directs the method toward refutation
without assuming that a counterexample exists.

## Current task statement

An oriented graph is a finite directed graph with no loops and no pair of
oppositely directed edges. For a vertex `v`, let `N+(v)` be its set of
out-neighbors. Let `N2+(v)` be the set of vertices `w` that are not `v` or an
out-neighbor of `v` and for which there is a vertex `u` with directed edges
`v -> u -> w`.

Search for a complete negative resolution of Seymour's Second-Neighborhood
Conjecture by constructing one finite oriented graph `D` such that

`|N2+(v)| < |N+(v)|` for every vertex `v`.

A complete result must include the explicit adjacency list and two independent
exhaustive verifiers. The verifiers must agree on the oriented-graph axioms,
the exact first and new second out-neighborhoods, and the strict inequality at
every vertex.

Partial progress does not count as a resolution. In particular, bounded
negative searches, solver timeouts, unchecked UNSAT output, special graph
classes, asymptotic estimates, equivalent reformulations, or a candidate that
fails either verifier are insufficient.

## Dynamic multiagent protocol

Use the available reasoning agents aggressively and dynamically. The current
environment exposes four concurrent reasoning slots; recycle them through
many independent rounds rather than treating the first four assignments as
the whole search. Use up to 64 CPU workers only for validated computational
search engines.

- Begin with a genuinely diverse portfolio: exact SAT/CP-SAT synthesis,
  incremental local search, structural extremal analysis, algebraic/Boolean
  formulations, and adversarial certificate checking.
- Preserve independence in early rounds. Do not tell every agent the favored
  encoding or incumbent construction.
- Maintain an explicit approach-family registry. Group work by mathematical
  mechanism, not wording. Redirect agents when one family dominates.
- A reformulation is not progress unless it produces a load-bearing lemma or
  an explicit graph certificate with a stated bridge to full refutation.
- Mark theorem-strength gaps as blocked. Reopen them only after a materially
  new mechanism, invariant, or construction is proposed.
- Require concrete adjacency data, equations, clauses, lemmas, code, or
  counterexamples to proposed sublemmas. Reject vague status reports.
- Use adversarial agents throughout. Audit the definition of the new second
  neighborhood, exclusion of direct neighbors, loop/digon constraints,
  bidirectional SAT reification, strict cardinality inequalities, parser
  agreement, and independence of the two verifiers.
- The root agent repeatedly synthesizes, challenges, redirects, and launches
  new rounds. A promising score is not a result.

Return a full refutation only after one explicit graph survives both independent
verifiers and a fresh current-status/novelty check. Otherwise preserve the
exact strongest derivation and state the remaining gap without claiming a
solution. Do not consider giving up before the registered eight-hour resource
exit, unless a rigorous falsifying fact triggers the registered dead-end rule.
