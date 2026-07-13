# R2 audit: finite-state strict-gap theorem

## Verdict

Accepted after notation repair. The response proves a genuine obstruction:

> Any fixed finite congruence partition, fixed finite family of nonempty affine
> words \(F_e(x)=a_ex-b_e\) built from \(T_d(x)=dx-1\) with
> \(d\in G_0\), and any fixed pointwise fractional packing of their images,
> has linear density-transfer spectral radius strictly below one.

Therefore no proof using only such a fixed finite monotone renewal system,
finite initial data, and cell capacities can force positive lower density of
\(G_2\). This does not prove that \(G_2\) has zero density. It identifies
unbounded scale-dependent complexity as necessary within this proof class.

The browser rendering dropped fraction bars. The repaired matrix definitions
used in the proof are

\[
M_{ji}=\sum_{\substack{e:s(e)=i\\t(e)=j}}{\lambda_e\over a_e},
\qquad
M(\sigma)_{ji}=
\sum_{\substack{e:s(e)=i\\t(e)=j}}{\lambda_e\over a_e^\sigma}.
\]

These are forced by the averaging and counting equations and make every
displayed step dimensionally consistent.

## Proof audit

1. Every nonempty word has \(F(x)=ax-b\) with
   \(a\ge3\) and \(1\le b\le a-2\). Its only real fixed point
   \(b/(a-1)\) lies strictly between zero and one, so no integer is fixed.
2. Averaging the pointwise packing over a common period gives
   \(\sum_iM_{ji}\le1\); hence \(M\) is row-substochastic.
3. If \(\rho(M)=1\), a maximal-coordinate Perron class has row sums exactly
   one. Equality in the periodic packing then covers every integer in those
   cells by a backward image from the same cells.
4. Repeated backward selection remains in a bounded integer interval because
   every inverse branch contracts by at least \(1/3\). A repeated integer
   yields a nonempty word with an integer fixed point, contradicting step 1.
   Hence \(\rho(M)<1\).
5. For fixed architecture the feasible weight polytope is compact, so the
   spectral gap is uniform over all admissible weights.
6. Continuity gives some \(\sigma<1\) with \(\rho(M(\sigma))<1\).
   The exact shift inequality
   \[
   \left({X+b_e\over a_e}-1\right)_+^\sigma
   \le a_e^{-\sigma}(X-1)_+^\sigma
   \]
   constructs an \(O(X^\sigma)\) numerical supersolution dominating any
   finite initial data. Thus the finite renewal inequalities themselves are
   compatible with sublinear growth.

## Scale-dependent replacement

The response also proves a sufficient nonstationary theorem. At scales
\(X_k\), let \(L_k\) be the finite count-transfer matrices of pointwise
packings, and suppose bounded positive potentials \(p_k\) satisfy

\[
p_{k+1}^TL_k\ge\gamma_kp_k^T.
\]

If \(X_{k+1}/X_k\le R\) and

\[
\inf_n\prod_{k<n}\theta_k>0,
\qquad
\theta_k=\gamma_k{X_k\over X_{k+1}},
\]

then the generated set has positive lower density, quantitatively at least

\[
{m\over MR}{A(X_0)\over X_0}
\inf_n\prod_{k<n}\theta_k,
\]

where \(m\le p_{k,i}\le M\). After normalizing \(0<\theta_k\le1\), this is
equivalent to the summable-loss condition
\(\sum_k(1-\theta_k)<\infty\).

This replacement is rigorous but not yet instantiated for Problem 424.
Producing the scale-dependent packings and summable loss remains an open
load-bearing lemma.

## Scope

- Kills: every fixed finite congruence-state, fixed-word, pointwise-packing
  renewal proof for \(G_2\).
- Does not kill: changing moduli, multipliers, words, or noncongruence
  partitions with scale; correlated hyperbola arguments; missing-hole
  contractions.
- Does not solve Problem 424.
