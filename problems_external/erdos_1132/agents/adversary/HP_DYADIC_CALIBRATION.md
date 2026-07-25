# Route D calibration on a canonical nested near-arcsine sequence

## Sequence

Enumerate the Chebyshev--Lobatto grids in dyadic levels:
\[
\mathcal X_m=\left\{\cos\frac{j\pi}{2^m}:0\leq j\leq2^m\right\},
\qquad
\mathcal X_m\subset\mathcal X_{m+1}.
\]
At each level append the points with odd numerator.  The terminal prefix at
level \(m\) has \(n=2^m+1\) nodes and is exactly \(\mathcal X_m\).

This file proves that the harmonic-profile condition (HP) does occur at
infinitely many terminal prefixes for an explicit fixed non-node.  It is a
calibration of Route D, not a proof for arbitrary nested sequences.

## Uniform sorted-profile estimate

Let \(N=2^m\), let \(x=\cos\theta\), and assume
\[
\eta\leq\theta\leq\pi-\eta
\]
for a fixed \(\eta>0\).  Put
\[
s_N=|\sin N\theta|.
\]
For the \(N+1\)-point Lobatto grid, equation (16) in the recurrence audit is
\[
|\ell_j(\cos\theta)|
=\frac{s_N\sin\theta}
{c_jN|\cos\theta-\cos(j\pi/N)|}.
\tag{1}
\]
Sort these \(N+1\) magnitudes as
\[
w_{1,N}(\theta)\geq\cdots\geq w_{N+1,N}(\theta).
\]

**Lemma.** There are \(\beta_\eta>0\) and \(C_\eta<\infty\) such that,
uniformly in \(N\) and \(\theta\in[\eta,\pi-\eta]\),
\[
\sum_{r=1}^{\lfloor\beta_\eta N\rfloor}
\left(\frac{2}{\pi r}-w_{r,N}(\theta)\right)_+
\leq
\frac2\pi(1-s_N)H_{\lfloor\beta_\eta N\rfloor}+C_\eta.
\tag{2}
\]

**Proof.** Write \(h=\pi/N\).  The \(r\)-th closest angular grid point to
\(\theta\) has distance at most
\[
\delta_r\leq\frac{(r+1)h}{2}.
\tag{3}
\]
Choose \(\beta_\eta>0\) small enough that all the first
\(\lfloor\beta_\eta N\rfloor\) closest grid points remain in
\([\eta/2,\pi-\eta/2]\).  They are therefore non-endpoints.  If
\(\phi=j\pi/N\) is one of them and
\(\delta=|\theta-\phi|\), then
\[
\begin{aligned}
\frac{\sin\theta}{|\cos\theta-\cos\phi|}
&=\frac{\sin\theta}
{2|\sin((\theta+\phi)/2)\sin((\theta-\phi)/2)|}\\
&\geq \frac{1-C_\eta\delta}{\delta}.
\end{aligned}
\tag{4}
\]
Equations (1), (3), and (4) imply
\[
w_{r,N}(\theta)
\geq s_N\left(\frac{2}{\pi(r+1)}-\frac{C_\eta}{N}\right)
\qquad
(1\leq r\leq\beta_\eta N).
\tag{5}
\]
Consequently,
\[
\begin{aligned}
\left(\frac{2}{\pi r}-w_{r,N}(\theta)\right)_+
&\leq
\frac2\pi\frac{1-s_N}{r}
+\frac2\pi\left(\frac1r-\frac1{r+1}\right)
+\frac{C_\eta}{N}.
\end{aligned}
\]
Summation telescopes the middle term and proves (2).

Thus any subsequence for which
\[
(1-|\sin N\theta|)\log N=O(1)
\tag{6}
\]
satisfies (HP) with a bounded constant.

## One explicit fixed non-node

Let
\[
m_s=2^{s+1}\quad(s\geq1),\qquad
\alpha=\frac14+\sum_{s=1}^{\infty}2^{-(m_s+1)},
\qquad
\theta=\pi\alpha.
\tag{7}
\]
The number \(\alpha\) is not dyadic, so
\[
x_*=\cos(\pi\alpha)
\]
is never a node of a dyadic Lobatto grid.  It is also a fixed interior point.

At \(N_s=2^{m_s}\), all terms in (7) preceding the \(s\)-th tail become
integers after multiplication by \(N_s\), and
\[
\{N_s\alpha\}=\frac12+\varepsilon_s,
\qquad
0<\varepsilon_s
=\sum_{t>s}2^{m_s-m_t-1}
\leq 2^{-m_s}
\tag{8}
\]
for all sufficiently large \(s\).  Hence
\[
\begin{aligned}
1-|\sin(N_s\theta)|
&=1-\cos(\pi\varepsilon_s)\\
&\leq\frac{\pi^2}{2}\varepsilon_s^2
\leq\frac{\pi^2}{2}4^{-m_s}.
\end{aligned}
\tag{9}
\]
Since \(\log N_s=m_s\log2\), equations (6) and (9) give
\[
(1-|\sin(N_s\theta)|)\log N_s\longrightarrow0.
\]
Combining this with (2) proves (HP) at the fixed point \(x_*\) for the
infinite terminal-prefix subsequence \(n_s=N_s+1\).

It also gives the fixed-defect conclusion directly:
\[
L_{N_s+1}(x_*)\geq\frac2\pi\log N_s-O_\alpha(1).
\]

## Exact computational audit

`hp_dyadic_scan.cpp` implements the exact magnitude form of the rank-one
update
\[
\log|\ell_{k,n+1}(x)|
=\log|\ell_{k,n}(x)|
+\log|x-x_{n+1}|-\log|x_k-x_{n+1}|
\tag{10}
\]
and
\[
\log|\ell_{n+1,n+1}(x)|
=\sum_{i=1}^n
\left(\log|x-x_i|-\log|x_{n+1}-x_i|\right).
\tag{11}
\]
The program independently recomputes every product through level \(7\);
the maximum reported log-weight disagreement was zero at printed precision.
The level-\(12\), four-thread run completed with 4097-node terminal prefixes.

For the fixed phase \(\alpha=1/3\),
\(|\sin(2^m\pi\alpha)|=\sqrt3/2\) at every level, and the measured
positive-profile defect grows by approximately \(0.0586\) per level, as
predicted by the first term on the right of (2).  Irrational samples whose
doubling orbit approaches \(1/2\) show bounded or near-zero deficits along
the corresponding terminal subsequences.

## Scope and Route D gap

This calculation verifies that (HP) has the correct constant and rank scale
for a canonical nested equilibrium sequence.  It does not derive a fixed
point from condition (R).  Condition (R) is only a first-order statement
\(\Phi_{k,n}(x)=o(n)\) from above, whereas (2) requires a bounded
second-order cumulative defect.  No implication from (R) to (6), or to an
analogous bounded multiscale defect, follows from the rank-one identities.
