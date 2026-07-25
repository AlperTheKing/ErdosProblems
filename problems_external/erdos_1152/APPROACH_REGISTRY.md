# Erdős Problem 1152 — Approach Registry

## Exact statement

For every triangular array of distinct nodes
\[
X_n=\{x_{1n},\ldots,x_{nn}\}\subset[-1,1]
\]
and every positive sequence \(\epsilon_n\to0\), determine whether there is
\(f\in C[-1,1]\) such that every sequence of polynomials \(p_n\) satisfying
\[
\deg p_n<(1+\epsilon_n)n,\qquad
p_n(x_{kn})=f(x_{kn})\quad(1\le k\le n)
\]
fails to converge to \(f\) for almost every \(x\in[-1,1]\).

## DIRECT ROUTE R1 — robust Erdős–Vértesi resonance

1. **Exact final deliverable.** A proof of the statement above. It is enough
   to prove the stronger conclusion that one can choose \(f\) and an
   increasing subsequence \(n_j\) such that every admissible sequence obeys
   \[
   |p_{n_j}(x)-f(x)|\longrightarrow\infty
   \quad\text{for almost every }x.
   \]
2. **Current frontier lemma or finite certificate.** Put
   \[
   \omega_n(x)=\prod_{k=1}^n(x-x_{kn}),\quad
   d_n=\lceil(1+\epsilon_n)n\rceil-1,\quad s_n=d_n-n=o(n),
   \]
   and let \(L_n\) be ordinary degree-\((n-1)\) Lagrange interpolation on
   \(X_n\). Prove the following robust finite-stage resonance lemma:

   For every \(h\in C[-1,1]\), \(\rho,A,\eta>0\), and \(N\), there are
   \(n\ge N\), \(g\in C[-1,1]\), and \(\tau>0\), with
   \(\|g-h\|_\infty<\rho\), such that for every
   \(\|g'-g\|_\infty<\tau\) and every \(q\in\mathcal P_{s_n}\),
   \[
   \mu\{x:\ |L_ng'(x)+\omega_n(x)q(x)-g'(x)|\le A\}<\eta.
   \]
3. **Explicit logical bridge.** Every admissible interpolant has the unique
   form \(p_n=L_nf+\omega_nq_n\), with \(\deg q_n\le s_n\). The frontier
   lemma makes, for each \(j,N\), the union of its witnessing balls with
   \(A=j\) and \(\eta=2^{-j}\) open and dense in \(C[-1,1]\). Baire category
   supplies one \(f\) in all these sets and an increasing \(n_j\).
   Borel–Cantelli then gives
   \(|p_{n_j}(x)-f(x)|>j\) eventually for almost every \(x\), uniformly over
   the arbitrary choices \(q_{n_j}\).
4. **Next falsifiable action.** Reconstruct the short/long-interval
   resonance mechanism in Erdős–Vértesi (1980), and prove or refute the
   exact insertion claim that a multiplier of degree \(s_n=o(n)\) can
   destroy only \(O(s_n)\) of the alternating resonance blocks used at one
   finite stage.
5. **Exit condition.** Exit this route as
   `DEAD: robust resonance — an o(n)-degree multiplier cancels the
   Erdős–Vértesi stage on positive measure without exceeding its
   zero/sign-change budget`
   if an explicit admissible correction survives on a fixed positive-measure
   portion of the resonance set, or if the open-neighborhood finite-stage
   statement fails. Do not replace the route by bounded-node experiments or
   by a weaker positive-measure divergence statement.

## Adversarial checks required

- Preserve the strict degree inequality when defining \(d_n\) and \(s_n\).
- Quantify over every \(q\in\mathcal P_{s_n}\); a bound for one selected
  extension is insufficient.
- Prove that the finite-stage witnesses are stable in the uniform norm.
- Track whether the sign-change argument applies to
  \(\omega_n q\), to its quotient by a fixed factor, or only to \(q\).
- Do not infer an almost-everywhere conclusion from density alone; the
  exceptional measures must be summable.
- Treat the 1980 ordinary-interpolation theorem and the fixed-positive-excess
  1989 result as inputs, not as solutions of the vanishing-excess problem.

## Prohibited substitutes

- A reformulation without the robust finite-stage lemma.
- A result for one node family or one rate \(\epsilon_n\).
- Divergence for one chosen admissible interpolating sequence.
- Divergence on merely positive measure.
- Numerical evidence, solver timeout, or a bounded finite verification.

## Route closure

**R1 status: DEAD.** In the actual Erdős–Vértesi stage the large raw sign alternation is supplied by `omega_n`; after division the quotient has constant sign. A degree-zero correction can cancel a fixed positive-measure large-error test exactly. The required weighted anti-approximation theorem is not supplied by the scaffold, so continuing would replace the problem by an equivalent-strength conjecture.
