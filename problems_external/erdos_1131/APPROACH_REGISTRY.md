# Erdős Problem 1131 — Approach Registry

## Statement

For distinct \(x_1,\ldots,x_n\in[-1,1]\), let \(l_k\) be the associated
Lagrange cardinal polynomials and
\[
I(x_1,\ldots,x_n)=\int_{-1}^{1}\sum_{k=1}^n |l_k(x)|^2\,dx.
\]
The principal explicit question asks whether
\[
\min I=2-\frac{1+o(1)}{n}.
\]

## DIRECT ROUTE R1 — Jacobi–Lobatto asymptotic counterexample

1. **Exact final deliverable.** An explicit constant \(\delta>0\) and, for
   every sufficiently large \(n\), explicit distinct nodes
   \(X_n\subset[-1,1]\) satisfying
   \[
   I(X_n)\le 2-\frac{1+\delta+o(1)}{n}.
   \]
   This gives a negative answer to the displayed asymptotic conjecture.
2. **Current frontier lemma or finite certificate.** For \(X_n\) consisting
   of \(\pm1\) and the zeros of
   \(P_{n-2}^{(5/4,5/4)}\), prove that
   \[
   \lim_{n\to\infty} n(2-I(X_n))=C_{1/4}
   \]
   for an explicit \(C_{1/4}>1\).
3. **Logical bridge.** Since \(\min I\le I(X_n)\),
   \[
   n(2-\min I)\ge n(2-I(X_n))\to C_{1/4}>1.
   \]
   The proposed formula would instead force
   \(n(2-\min I)\to1\), a contradiction.
4. **Next falsifiable action.** Derive an exact finite-\(n\) expression for
   \(I(X_n)\) from Jacobi recurrence and norm identities, obtain its
   asymptotic expansion, and independently replay numerical values from the
   raw nodes and exact polynomial coefficients.
5. **Exit condition.** Succeed only with a complete derivation of an explicit
   limit \(C_{1/4}>1\) and two independent checks. Exit as
   `DEAD: Jacobi–Lobatto route — no proved asymptotic coefficient above 1`
   if the limit is at most \(1\), fails to exist, or the derivation requires an
   unproved asymptotic principle of comparable strength.

## Prohibited substitutes

- Numerical optimization without an analytic bound.
- A fixed-\(n\) improvement over Legendre–Lobatto nodes.
- A claimed limit without uniform error control.
- A lower or upper bound that does not separate the coefficient from \(1\).
- A reformulation as optimal design without proving the frontier lemma.
