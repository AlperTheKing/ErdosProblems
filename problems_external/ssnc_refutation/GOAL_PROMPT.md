# Goal Prompt - Seymour's Second-Neighborhood Conjecture

This is a neutral, target-specific adaptation of OpenAI's published Cycle
Double Cover multiagent-v2 prompt.

## Goal

Resolve Seymour's Second-Neighborhood Conjecture by producing either:

1. one explicit finite counterexample accepted by two independent exhaustive
   verifiers; or
2. a complete proof covering every finite oriented graph, with every
   load-bearing lemma independently audited and every feasible finite component
   replayed by proof-producing computation.

The first and primary attack is direct refutation. A proof route may be opened
only after its exact theorem-closing bridge, frontier lemma, next falsifiable
action, and exit condition are entered in `APPROACH_REGISTRY.md`.

## Problem

An oriented graph is a finite directed graph with no loops and no pair of
oppositely directed edges. For a vertex `v`, let `N+(v)` be its set of
out-neighbors. Let `N2+(v)` be the set of vertices `w` that are neither `v` nor
an out-neighbor of `v` and for which there is a vertex `u` with directed edges
`v -> u -> w`.

The conjecture states that every finite oriented graph has a vertex `v` with

`|N2+(v)| >= |N+(v)|`.

For a negative resolution, construct one explicit finite oriented graph `D`
such that

`|N2+(v)| < |N+(v)|` for every vertex `v`.

A complete counterexample deliverable consists of a canonical adjacency list,
a per-vertex first/second-neighborhood ledger, and two independently
implemented exhaustive verifiers that both accept the same certificate.

Partial progress is not a resolution. Bounded negative searches, timeouts,
unchecked UNSAT output, special classes, asymptotic estimates, equivalent
reformulations, or a candidate rejected by either verifier are insufficient.
A finite checked UNSAT certificate closes only the exact finite instance it
encodes unless a proved reduction closes the full conjecture.

## Dynamic multiagent protocol

Use multiagent reasoning aggressively and dynamically within the concurrency
available in the current environment. Recycle the available reasoning slots
through repeated independent rounds. Use up to 64 CPU workers only for search
engines that have passed calibration and adversarial audit.

- Begin with genuinely different mechanisms: exact SAT or CP-SAT synthesis,
  incremental local search, structural extremal analysis, algebraic or Boolean
  formulations, and adversarial certificate checking.
- Preserve independence during early rounds. Do not force all agents to inherit
  the favored encoding or incumbent construction.
- Maintain an explicit approach-family registry. Group related work by
  mathematical mechanism, not by wording.
- Require concrete adjacency data, equations, clauses, lemmas, source code, or
  counterexamples to proposed sublemmas. Reject vague status reports.
- A reformulation counts only if it creates a load-bearing lemma or a finite
  certificate with an explicit bridge to the full result.
- Mark theorem-strength gaps as blocked. Reopen them only after a materially new
  mechanism, invariant, or construction is proposed.
- Use adversarial agents throughout. Audit the definition of the new second
  neighborhood, exclusion of direct out-neighbors, loop and digon constraints,
  bidirectional SAT reification, strict cardinality inequalities, parser
  agreement, and verifier independence.
- The root agent repeatedly synthesizes, challenges, redirects, and launches new
  rounds. A favorable objective value is not a mathematical result.

Return a full resolution only after either an explicit graph survives both
independent verifiers or a complete global proof survives independent referee
review, followed in either case by a fresh current-status and novelty check.
Otherwise preserve the exact strongest derivation and state the remaining gap
without claiming a solution. Do not stop before the registered eight-hour
resource exit unless a rigorous falsifying fact triggers the registered
dead-end rule.
