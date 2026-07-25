# Independent referee audit of the Chebyshev--Lobatto nested pair

This audits equations (16)--(22) in
`agents/recurrence/RECURRENCE_AUDIT.md`.

## Verdict

Equations (16)--(22) are correct.  The asymptotic formula (17) is uniform in
the full \(N\)-dependent angular range
\[
\eta\leq\theta\leq\pi-\eta
\]
for every fixed \(\eta\in(0,\pi/2)\), including points whose distance from a
Lobatto grid point tends to zero and the grid points themselves (interpreted
by continuity).  The implied constant may depend on \(\eta\), but not on
\(N\) or \(\theta\).  This is exactly the uniformity needed for (21)--(22).

## Formula checks

For
\[
W(x)=(1-x^2)T_N'(x)
\]
and \(y_j=\cos(j\pi/N)\), direct differentiation gives
\[
|W'(y_j)|=c_jN^2,\qquad
c_0=c_N=2,\quad c_j=1\ (0<j<N).
\]
Also
\[
|W(\cos\theta)|=N|\sin\theta\,\sin N\theta|.
\]
Thus
\[
|\ell_j(\cos\theta)|
=\frac{|\sin\theta\,\sin N\theta|}
{c_jN|\cos\theta-\cos(j\pi/N)|},
\]
which verifies (16), including the endpoint factor \(c_0=c_N=2\).

The appended-node cardinal polynomial is
\[
\begin{aligned}
q_N(\cos\theta)
&=\frac{(1+\cos\theta)U_{N-1}(\cos\theta)}{2N}\\
&=\frac{2\cos^2(\theta/2)}{2N}
  \frac{\sin N\theta}{2\sin(\theta/2)\cos(\theta/2)}\\
&=\frac{\cos(\theta/2)\sin N\theta}
{2N\sin(\theta/2)},
\end{aligned}
\]
so (18) is correct.

For the \(N\)-node prefix \(y_1,\ldots,y_N\), the alternating-sign
interpolant on the extrapolation interval is
\[
U_{N-1}(x)+U_{N-2}(x).
\]
At \(x=1\) its value is \(N+(N-1)=2N-1\), verifying (19).

The exact update
\[
\ell_{j,N}^{-}(x)
=\ell_{j,N+1}^{\rm CL}(x)
+\ell_{j,N}^{-}(1)q_N(x)
\]
gives
\[
\begin{aligned}
L_N^-(x)
&\leq
\sum_{j=1}^N|\ell_{j,N+1}^{\rm CL}(x)|
+L_N^-(1)|q_N(x)|\\
&=L_{N+1}^{\rm CL}(x)-|q_N(x)|
+(2N-1)|q_N(x)|\\
&=L_{N+1}^{\rm CL}(x)+(2N-2)|q_N(x)|,
\end{aligned}
\]
which verifies (20) with the exact coefficient.

## Uniformity in (17)

Put \(h=\pi/N\), \(\phi_j=jh\), and choose a closest grid index \(j_*\).
When \(\theta,\phi_j\) remain in a fixed compact subinterval of \((0,\pi)\),
\[
\frac{\sin\theta}{|\cos\theta-\cos\phi_j|}
=\frac1{|\theta-\phi_j|}+O_\eta(1)
\]
uniformly for \(j\ne j_*\).  Summing the \(O_\eta(1)\) errors over \(O(N)\)
indices and dividing by \(N\) contributes \(O_\eta(1)\).

The grid points outside a slightly larger compact interior range have
denominator bounded below in terms of \(\eta\); their total contribution
after the \(1/N\) factor is also \(O_\eta(1)\).  The two remaining harmonic
sums satisfy, uniformly in the offset of \(\theta\) within its grid cell,
\[
\frac1N\sum_{j\ne j_*}\frac1{|\theta-jh|}
=\frac2\pi\log N+O_\eta(1).
\]

The omitted nearest term is uniformly \(O_\eta(1)\) after multiplication by
\(|\sin N\theta|\), since, with
\(\delta=\theta-\phi_{j_*}\),
\[
|\sin N\theta|=|\sin(N\delta)|\leq N|\delta|
\]
and
\[
|\cos\theta-\cos\phi_{j_*}|\gg_\eta|\delta|.
\]
At \(\delta=0\), the removable value is the cardinal value \(1\).  Therefore
\[
L_{N+1}^{\rm CL}(\cos\theta)
=\frac2\pi|\sin N\theta|\log N+O_\eta(1)
\]
uniformly for every \(\eta\leq\theta\leq\pi-\eta\), proving (17) with the
claimed uniformity.

## Consequences (21)--(22)

On the same compact angular interval, (18) gives
\[
(2N-2)|q_N(\cos\theta)|
=\left(1-\frac1N\right)
|\cot(\theta/2)\sin N\theta|
=O_\eta(1).
\]
Hence (17) and (20) imply for both prefixes that the fixed-defect inequality
can hold only if
\[
1-|\sin N\theta|
\leq\frac{K_{\eta,C}}{\log N},
\]
which is (21).

Near each maximum of \(|\sin u|\),
\[
1-|\sin u|\asymp {\rm dist}
\left(u,\frac\pi2+\pi\mathbb Z\right)^2.
\]
Thus the set in (21) has relative length
\(O_{\eta,C}((\log N)^{-1/2})\) in every period.  Its total interior angular
measure, and hence its \(x\)-measure, tends to zero.

The omitted endpoint angular pieces have total \(x\)-measure
\[
2(1-\cos\eta).
\]
First sending \(N\to\infty\) for fixed \(\eta\), then
\(\eta\downarrow0\), proves (22).  Replacing \(\log N\) by
\(\log(N+1)\) changes the threshold by \(O(1/N)\), which is absorbed in the
fixed error.

No error was found in the two-prefix union-measure conclusion.  Its scope is
exactly one nested Chebyshev--Lobatto update; it does not establish an
unbounded-window or tail-union estimate.
