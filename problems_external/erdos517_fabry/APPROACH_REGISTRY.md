# Erdős Problem 517 — Approach Registry

## Status

Selected for a direct literature-to-certificate audit on 2026-07-23.

## DIRECT ROUTE A — Murai finite-zero construction

1. **Exact final deliverable.** A self-contained disproof of Erdős Problem
   517: an entire function
   \[
     f(z)=\sum_{k\geq 1} a_k z^{n_k},\qquad a_k\ne 0,\qquad n_k/k\to\infty,
   \]
   and a complex value assumed by \(f\) only finitely many times.

2. **Current frontier lemma or finite certificate.** Extract and independently
   verify from Section 5 of Murai (1983) the following stronger construction
   lemma: there is a nonzero entire function \(g\) whose nonzero Taylor
   exponents \(m_k\) satisfy \(k/m_k\to0\), and whose total number of zeros in
   \(\mathbb C\), counted with multiplicity, is bounded by one fixed integer
   \(d_1\).

3. **Explicit logical bridge.** Set \(f(z)=z\,g(z)\). Its nonzero Taylor
   exponents are \(n_k=m_k+1\), hence \(n_k/k\to\infty\). Its zeros are the
   zeros of \(g\), together with the origin, so \(f\) assumes \(0\) only
   finitely many times. This directly negates the universal assertion in
   Problem 517.

4. **Next falsifiable action.** Audit every dependency of Murai's equations
   (28)--(35): local-uniform convergence to a nonzero entire \(g\), the support
   counting estimate giving \(k/m_k\to0\), and the uniform-in-\(r\) zero-count
   bound. Reproduce these implications in a source-indexed proof and have an
   independent referee try to find a quantifier or Hurwitz/Rouché error.

5. **Exit condition.** Kill this route immediately if the zero bound depends
   on the disk radius, the limiting function may be identically zero, the
   Taylor support is not Fabry, or the construction only proves deficiency
   \(1\) without a finite global zero bound. Also kill the novelty claim if a
   source already states this exact finite-zero corollary, while retaining the
   prior-art correction as a database result.

## DIRECT ROUTE B — independent reconstruction

1. **Exact final deliverable.** The same explicit disproof, reconstructed
   without relying on an unstated strengthening of Murai's theorem.

2. **Current frontier lemma or finite certificate.** Construct locally
   uniformly convergent entire functions \(g_j\) with stabilized zeros and
   increasingly sparse disjoint Taylor blocks, with quantitative tail bounds
   on every disk.

3. **Explicit logical bridge.** Stabilized finite zeros plus Fabry support
   gives the \(g\) required by Route A, and multiplication by \(z\) closes the
   problem.

4. **Next falsifiable action.** Translate Murai's recursive definitions into
   an explicit induction lemma and test its first two stages symbolically.

5. **Exit condition.** Stop if the induction requires an unproved
   approximation theorem of comparable strength or if zero stabilization and
   Taylor sparsity cannot be imposed simultaneously.

