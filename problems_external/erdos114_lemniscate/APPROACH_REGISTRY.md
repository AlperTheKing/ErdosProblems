# Erdős Problem 114 — Approach Registry

## Problem

For every integer \(n\ge 1\) and every monic polynomial
\(p\in\mathbb C[z]\) of degree \(n\), prove
\[
\mathcal H^1\{z\in\mathbb C:|p(z)|=1\}
\le
\mathcal H^1\{z\in\mathbb C:|z^n-1|=1\}.
\]

## DIRECT ROUTE: make the high-degree theorem effective and close the finite gap

1. **Exact final deliverable.** A complete proof for every \(n\ge1\), consisting
   of (a) a fully explicit degree threshold \(N_0\) extracted without changing
   any hypothesis from Tao's high-degree proof, and (b) independently replayable
   rigorous certificates for every remaining degree \(15\le n<N_0\), together
   with the published proofs/certificates for the already covered degrees.

2. **Current frontier lemma or finite certificate.** Determine from the cited
   high-degree proof a numerical \(N_0\) and a finite list of explicit
   inequalities whose simultaneous verification implies the theorem for every
   \(n\ge N_0\).

3. **Logical bridge to the final deliverable.** Tao proves the conjecture for
   all sufficiently large \(n\). Existing rigorous results cover \(1\le n\le14\).
   Therefore an audited explicit \(N_0\), plus rigorous verification of the
   finite interval \(15\le n<N_0\), covers every positive integer degree.

4. **Next falsifiable action.** Three independent readers extract every
   quantitative dependency in Tao's proof and report either the same explicit
   threshold/inequality ledger or the first genuinely ineffective dependency.
   A referee then checks their ledgers directly against the source.

5. **Exit condition.** Exit this route immediately if the high-degree proof
   contains an ineffective constant, if the extracted threshold leaves a finite
   interval for which no direct rigorous certification method with stated
   completeness exists, or if the existing \(n\le14\) certificates do not
   replay. Record the precise missing bridge; do not replace it with another
   asymptotic reformulation.

## Novelty gate snapshot

- The official problem page was still marked open when checked on 2026-07-23.
- Tao's arXiv:2512.12455 covers all sufficiently large degrees, not an explicit
  all-degree statement.
- The problem thread records a claimed interval certificate through degree 14,
  explicitly described as a finite complement rather than a full solution.
- No complete all-degree proof was found in the live status/forum check.
