# Erdős Problem 742 — Approach Registry

## Exact target

Let \(G\) be a finite simple graph of order \(n\). Call \(G\) diameter-2
edge-critical (D2C) when \(\operatorname{diam}(G)=2\) and
\(\operatorname{diam}(G-e)>2\) for every edge \(e\).

The Murty–Simon conjecture asserts
\[
  |E(G)|\le \left\lfloor n^2/4\right\rfloor
\]
for every D2C graph \(G\), with equality only for the balanced complete
bipartite graph.

Fan proved the bound for \(n\le 24\) and \(n=26\); Füredi proved it for all
sufficiently large \(n\). The first unresolved order is therefore \(n=25\).

## DIRECT ROUTE R1 — explicit order-25 refutation

1. **Exact final deliverable.** A canonical adjacency list of a simple
   25-vertex graph with at least 157 edges, together with a complete
   per-edge criticality ledger and acceptance by two independently
   implemented exhaustive verifiers.
2. **Current frontier certificate.** One graph \(G\) on vertices
   \(0,\ldots,24\) with \(|E(G)|\ge157\), diameter exactly 2, and a
   distance-\(>2\) witness after deletion of every edge.
3. **Logical bridge.** Since
   \(\lfloor25^2/4\rfloor=156\), that certificate is a direct
   counterexample to the universal Murty–Simon conjecture.
4. **Next falsifiable action.** Independently implement the certificate
   semantics, calibrate both verifiers on positive and deliberately corrupted
   graphs, then run a diverse native C++/exact-SAT portfolio for the frontier
   certificate.
5. **Exit condition.** A graph is accepted only after raw-adjacency replay by
   both verifiers. Verifier disagreement, an unsound encoding, or failed
   calibration kills the affected lane. Bounded NO_HIT, timeout, or unchecked
   UNSAT closes only the attempted search and is not a proof.

## DIRECT ROUTE R2 — structural edge bound

1. **Exact final deliverable.** A complete proof that every D2C graph has at
   most \(\lfloor n^2/4\rfloor\) edges, including the equality case.
2. **Current frontier lemma.** Derive an injective charging map from every edge
   of a non-bipartite D2C graph into the cross-pairs of a certified bipartition,
   with all uncharged defects bounded strongly enough to give
   \(|E(G)|\le\lfloor n^2/4\rfloor\).
3. **Logical bridge.** Such a charging inequality is exactly the conjectured
   global bound; equality analysis identifies balanced complete bipartite
   graphs.
4. **Next falsifiable action.** Enumerate small D2C graphs and search for
   counterexamples to each proposed local charging rule before using it.
5. **Exit condition.** Kill the route when the claimed charging map fails on a
   verified D2C graph or when the frontier merely restates the conjecture
   without a strictly simpler local lemma.

## Audit contract

- Simple graph: no loops, no duplicate or directed edges.
- Diameter exactly 2: connected, not complete, every nonedge has a common
  neighbor.
- Edge criticality: for every edge \(e\), recompute all-pairs distances in
  \(G-e\); at least one unordered pair must have distance greater than 2.
- Threshold at \(n=25\): at least 157 edges, not 156.
- No symmetry breaker may exclude a valid isomorphism class unless its
  soundness is separately proved.
- A solver objective, approximate graph, or bounded NO_HIT is not a result.

## Route status — 2026-07-23

- **R1 halted.** The calibrated 64-thread native search completed
  3,600,239 restarts without a 157-edge certificate; the exact SMS route is
  not production-ready at order 25 because its audited degree-sequence driver
  is missing; and 186,971,232 audited one-level twin substitutions through
  order-7 D2C bases attained at most 156 edges. These are bounded negative
  results, not a proof of the conjecture.
- **R2 dead.** The proposed maximum-cut charging rule has a verified
  order-8 D2C counterexample. The valid true-twin transfer lemma does not
  bridge to the global bound because the required density-sensitive
  cloneability statement is unproved, while its unrestricted low-degree
  version has a verified order-12 counterexample.
- **Dead-end record.** `DEAD: reformulation maze — no proven bridge from
  bounded family exclusions or density-sensitive cloneability to the
  universal edge bound.`

