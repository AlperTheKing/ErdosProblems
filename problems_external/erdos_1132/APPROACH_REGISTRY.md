# Erdős Problem 1132 — Approach Registry

## Exact target

For every infinite sequence of pairwise distinct nodes
\[
x_1,x_2,\ldots\in[-1,1],
\]
write
\[
\ell_{k,n}(x)=\prod_{\substack{1\le i\le n\\i\ne k}}
\frac{x-x_i}{x_k-x_i},
\qquad
L_n(x)=\sum_{k=1}^n|\ell_{k,n}(x)|.
\]
Resolve whether there must exist \(x\in(-1,1)\) and a finite constant
\(C_x\) such that
\[
L_n(x)>\frac{2}{\pi}\log n-C_x
\]
for infinitely many \(n\).

The constant is allowed to depend on the node sequence and on \(x\). This is
the weakest natural interpretation mentioned in the current literature. A
proof resolves this weakest reading only; a counterexample to it also refutes
every stronger uniform-constant reading.

## DIRECT ROUTE A — fixed-defect recurrence

1. **Exact final deliverable.** A theorem proving the target statement above
   for every infinite node sequence.
2. **Current frontier lemma or certificate.** Prove a fixed-defect recurrence
   lemma: for every node sequence there are a compact interval
   \(I\Subset(-1,1)\) and \(C<\infty\) for which
   \[
   \limsup_{n\to\infty}
   \{x\in I:L_n(x)\ge (2/\pi)\log n-C\}\ne\varnothing.
   \]
   The proof must use a quantitative persistence or cross-scale relation
   special to nested Lagrange node sets; non-emptiness of each high set is
   insufficient.
3. **Logical bridge.** Any point in that limsup belongs to the displayed high
   set for infinitely many \(n\), which is exactly the required point \(x\)
   and constant \(C\).
4. **Next falsifiable action.** Extract Tao's local lower bound with all
   interval dependence explicit, then test whether the Lagrange basis
   supplies a cross-scale persistence inequality strong enough to keep the
   defect bounded. Produce either the exact inequality with proof or an
   explicit nested node family falsifying it.
5. **Exit condition.** Stop this route if every proposed persistence
   inequality is falsified by an explicit node family or if the argument
   requires replacing a fixed \(C\) by any unbounded function of \(n\).

## DIRECT ROUTE B — diagonal counterexample

**Status: DEAD.** Tao's Theorem 1.10(i) supplies, for every fixed nontrivial
interval \(I\), constants \(K_I,N_I\) uniform over all node sets such that
\[
\sup_{x\in I}L_n(x)\ge(2/\pi)\log n-K_I
\]
for \(n\ge N_I\). Taking a protected-interval budget \(B>K_I\) contradicts
the registered prefix-extension lemma already at one terminal prefix. This
kills this interval-uniform construction mechanism, not all possible
pointwise counterexamples.

1. **Exact final deliverable.** One explicit infinite pairwise-distinct node
   sequence for which, for every \(x\in(-1,1)\) and every \(C<\infty\), only
   finitely many \(n\) satisfy
   \[
   L_n(x)>(2/\pi)\log n-C.
   \]
2. **Current frontier lemma or certificate.** A prefix-extension lemma that,
   from any finite node prefix and any finite family of rational intervals
   with assigned defect budgets, appends a finite block of nodes so that all
   later prefix Lebesgue functions in the block stay below the corresponding
   thresholds on those intervals, without invalidating earlier requirements.
3. **Logical bridge.** Apply the extension lemma to a countable basis of
   rational intervals and integer defect budgets by diagonalization. Every
   \(x\) and every finite \(C\) is eventually covered, giving the explicit
   counterexample required above.
4. **Next falsifiable action.** Attempt the extension lemma first for one
   closed interval and one budget using clustered Chebyshev-like blocks;
   compute exact symbolic or interval-certified examples and derive the
   governing inequality.
5. **Exit condition.** Stop this route if a proved universal local lower bound
   forces a fixed-defect high point inside every protected interval for every
   extension, or if the construction only controls a non-nested triangular
   array rather than one infinite prefix sequence.

## DIRECT ROUTE C — moving microscopic high sets

1. **Exact final deliverable.** An explicit nested node sequence for which
   \(d_n(x)=(2/\pi)\log n-L_n(x)\to+\infty\) for every \(x\in(-1,1)\).
2. **Current frontier lemma or finite certificate.** Prove a stage-localization
   lemma: construct explicit \(N_s\) and finite rational-open sets
   \(U_{s,q}\), \(1\le q\le s\), such that
   \[
   \{x:L_n(x)>(2/\pi)\log n-q\}\subset U_{s,q}
   \]
   for every \(N_s\le n<N_{s+1}\), while for each fixed \(q\) the family
   \((U_{s,q})_{s\ge q}\) is point-finite.
3. **Logical bridge.** Given \(x\) and a finite \(C\), choose an integer
   \(q\ge C\). Point-finiteness makes \(x\notin U_{s,q}\) for all large
   \(s\), so every later \(n\) has
   \(L_n(x)\le(2/\pi)\log n-q\le(2/\pi)\log n-C\). This is the required
   counterexample.
4. **Next falsifiable action.** Test whether point-finite schedules can meet
   every interval-intersection forced by Tao's theorem, then derive the exact
   block-update objective for every intermediate prefix, not only terminal
   prefixes.
5. **Exit condition.** Stop if Tao or an insertion-robust capacity theorem
   forces \(\limsup_s U_{s,q}\ne\varnothing\) for some fixed \(q\), if prefix
   extension cannot localize every intermediate high set, or if the mechanism
   works only for independent triangular arrays.
## DIRECT ROUTE D — leave-one-out potential rigidity

1. **Exact final deliverable.** Prove the target for every node sequence, or
   turn a falsifier of the frontier below into a complete explicit
   counterexample.
2. **Current frontier lemma or finite certificate.** Put
   \[
   \Phi_{k,n}(x)=\log|\ell_{k,n}(x)|
   =\sum_{\substack{i\le n\\i\ne k}}
   \log\frac{|x-x_i|}{|x_k-x_i|}.
   \]
   In the rigidity class
   \[
   \limsup_n\Phi_{k,n}(x)/n\le0
   \tag{R}
   \]
   for every fixed \(k\) and every non-node \(x\), sort
   \(e^{\Phi_{k,n}(x)}\) as \(w_{1,n}(x)\ge\cdots\ge w_{n,n}(x)\).
   Prove that some \(x_*\), \(\beta>0\), \(B<\infty\), and infinitely many
   \(n\) satisfy
   \[
   \sum_{r\le\beta n}
   \left(\frac{2}{\pi r}-w_{r,n}(x_*)\right)_+\le B.
   \tag{HP}
   \]
3. **Logical bridge.** If (R) fails, one fixed basis term is exponentially
   large along a subsequence, proving the target. If (R) holds, (HP) gives
   \[
   L_n(x_*)\ge\sum_{r\le\beta n}w_{r,n}(x_*)
   \ge(2/\pi)H_{\lfloor\beta n\rfloor}-B
   =(2/\pi)\log n-O_{\beta,B}(1).
   \]
4. **Next falsifiable action.** Derive or refute (HP) using the exact nested
   rank-one update. A negative test must give an explicit nested sequence and
   exact indices, then test the full sum \(L_n=\sum_k e^{\Phi_{k,n}}\) to
   distinguish failure of (HP) from a genuine counterexample.
5. **Exit condition.** Stop if (HP) fails and no positive-density rank range
   has bounded total defect, if only weak-* arcsine convergence or an
   \(o(n)\) potential statement remains, if any loss is unbounded in \(n\),
   or if the falsifier uses non-nested triangular arrays. Record
   `DEAD: potential rigidity lacks a fixed-point second-order bridge`.
## Known result and non-results

- Tao's current theorem gives, for every \(\omega(n)\to\infty\), a dense set
  of \(x\) with
  \[
  L_n(x)\ge(2/\pi)\log n-\omega(n)
  \]
  infinitely often.
- Replacing \(C\) by any unbounded \(\omega(n)\) does not resolve the target.
- A high point \(x_n\) for each \(n\), a convergent subsequence of such
  points, or a Baire-category statement with interval-dependent constants
  does not by itself give a fixed \(x\) and fixed \(C\).
- Results for Chebyshev nodes, separated nodes, random nodes, or a
  non-nested triangular array do not cover an arbitrary infinite node
  sequence.

## Adversarial checks

- Keep the prefix dependence of \(\ell_{k,n}\) explicit.
- Do not transfer a bound from \(x_n\) to a limit point without a quantitative
  modulus valid for that same \(n\).
- Audit strict versus non-strict inequalities; an additive adjustment of one
  is harmless only when stated.
- Track whether constants depend on the interval, node sequence, point, or
  \(n\).
- Reject any argument whose closing step silently changes a fixed constant
  into \(o(\log n)\) or \(\omega(n)\).




## Route closure audit — 2026-07-23

- **Route A: DEAD.** Exact insertion permits one-step resets, Lobatto pairs have vanishing two-prefix high-set measure, and Re-Leja has only polynomial increments. The missing second-order correlation is the original gap.
- **Route C: DEAD.** An m-node epsilon-cluster forces off-cluster growth of order epsilon^{-(m-1)}. No distributed block yields the registered localization certificate; optimizing arbitrary blocks merely restates it.
- **Route D: DEAD.** First-order potential rigidity does not imply a fixed-point harmonic profile. Re-Leja explicitly kills the universal exponential-increment premise.

No registered direct route remains. Continuing would be a reformulation maze; no proof or disproof of Problem 1132 was obtained.
