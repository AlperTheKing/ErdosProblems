You are tasked with resolving the Murty–Simon conjecture on
diameter-2 edge-critical graphs.

A finite simple graph \(G\) is diameter-2 edge-critical (D2C) if its diameter
is exactly 2 and deleting any edge increases its diameter beyond 2. The
conjecture states that every D2C graph of order \(n\) has at most
\(\lfloor n^2/4\rfloor\) edges, with equality only for the balanced complete
bipartite graph.

A complete resolution must be either:

1. a complete proof for every finite simple graph; or
2. one explicit D2C graph on \(n\) vertices with more than
   \(\lfloor n^2/4\rfloor\) edges.

Prioritize direct refutation at the first unresolved order \(n=25\), where a
counterexample has at least 157 edges. A valid counterexample must include a
canonical adjacency list, a complete per-edge criticality ledger, and
acceptance by two independently implemented exhaustive verifiers.

Begin with genuinely independent approaches: exact SAT synthesis, native C++
local or stochastic search, structural extremal analysis, complement/total-
domination formulations, and adversarial encoding audit. Preserve independence
during early rounds. Require concrete graphs, clauses, equations, local
lemmas, counterexamples to proposed lemmas, or exact failure certificates.

Audit the graph convention, diameter exactly 2, edge deletion rather than
vertex deletion, strict threshold 157, witness reification in both directions,
symmetry-breaking soundness, parser agreement, and raw-certificate replay.

A bounded NO_HIT, timeout, approximate objective, unchecked UNSAT output,
restricted-family theorem, reformulation, or partial lemma does not resolve
the conjecture. Do not cascade automatically through orders or constrained
families. A finite UNSAT result closes only its exact instance unless it has an
independently checked proof certificate and a proved bridge to the universal
statement.

If a raw counterexample appears, stop its searches, replay it through both
verifiers, emit the full ledger, and repeat the live novelty check before any
discovery claim. If a proof route appears, independently referee every
load-bearing lemma and computationally falsify all feasible local claims.

