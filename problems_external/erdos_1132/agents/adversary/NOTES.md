# Adversarial audit of Erdős 1132, first question

## 1. Quantifier audit

The exact target fixed by the registry is
\[
\forall (x_i)_{i\geq 1}\ \exists x\in(-1,1)\ \exists C<\infty\
\forall N\ \exists n\geq N:\quad
L_n(x)>\frac2\pi\log n-C.
\]
Its negation is
\[
\exists (x_i)_{i\geq1}\ \forall x\in(-1,1)\ \forall C<\infty\
\exists N\ \forall n\geq N:\quad
L_n(x)\leq\frac2\pi\log n-C.
\]
Equivalently, for the defect
\[
d_n(x):=\frac2\pi\log n-L_n(x),
\]
the negation says \(d_n(x)\to+\infty\) for every \(x\in(-1,1)\).

The explanatory sentence in the initial registry saying that a proof of this
weak, point-dependent-\(C\) interpretation proves stronger uniform-\(C\)
interpretations is backwards.  A proof of the weak interpretation need not
prove a uniform version.  A counterexample to the weak interpretation would
also refute every stronger version.

## 2. What Tao's Baire argument actually supplies

For continuous defects \(d_n\), failure of the fixed-defect conclusion implies
that for every integer \(M\),
\[
[-1,1]=\bigcup_{N\geq1}
\{x:d_n(x)\geq M\text{ for every }n\geq N\}.
\]
Baire therefore gives an interval \(I_M\) and an \(N_M\) such that
\[
d_n(x)\geq M\qquad(x\in I_M,\ n\geq N_M).
\]
Tao's local theorem gives, for each fixed interval \(I\), a constant \(K(I)\)
such that
\[
\inf_{x\in I}d_n(x)\leq K(I)
\]
for all sufficiently large \(n\).  Applying it to \(I_M\) only yields
\[
M\leq K(I_M).
\]
There is no contradiction because the Baire interval depends on \(M\), and
its length can tend to zero while \(K(I_M)\) tends to infinity.  Thus a
fixed-defect conclusion cannot be extracted from the existing Baire step
unless one proves new quantitative persistence that controls the interval
selected by Baire.

## 3. Continuous moving-valley model: local sup bounds and Baire are insufficient

The following abstract construction rigorously realizes the preceding
failure mode.

Let \(X=[-1,1]\), and enumerate a basis of open rational intervals as
\((J_j)_{j\geq1}\).  For each fixed \(j\), choose pairwise disjoint open
intervals
\[
U_{j,n}\Subset J_j,\qquad n\geq j.
\]
The intervals only need to be pairwise disjoint as \(n\) varies with \(j\)
fixed; intervals belonging to different \(j\)'s may overlap.  Let
\(\psi_{j,n}:X\to[0,1]\) be continuous, equal to \(0\) at a point
\(c_{j,n}\in U_{j,n}\), and equal to \(1\) outside \(U_{j,n}\).  Define
\[
g_n(x):=\min\left(
n,\ \min_{1\leq j\leq n}\{j+(n-j)\psi_{j,n}(x)\}
\right).
\]
Then:

1. \(g_n\) is continuous.
2. If \(I\) is a nonempty open interval, choose \(J_j\Subset I\).  For every
   \(n\geq j\), \(g_n(c_{j,n})\leq j\), so
   \[
   \inf_{x\in I}g_n(x)\leq j
   \]
   with a constant depending only on \(I\).
3. For every fixed \(x\) and \(M\), the inequality \(g_n(x)<M\), once
   \(n\geq M\), forces \(x\in U_{j,n}\) for some \(j<M\).  For each such
   \(j\), pairwise disjointness permits this for at most one \(n\).  Hence it
   occurs for only finitely many \(n\), and \(g_n(x)\to+\infty\).

Consequently
\[
f_n(x):=\max\left(1,\frac2\pi\log n-g_n(x)\right)
\]
is a sequence of continuous nonnegative functions satisfying a Tao-shaped
local lower bound on every interval, but for which
\[
\frac2\pi\log n-f_n(x)\to+\infty
\]
at every fixed \(x\).  The supports can also be chosen to avoid any prescribed
finite set at stage \(n\), so the model can enforce \(f_n(q_k)=1\) for all
\(k\leq n\) along a prescribed countable set, mimicking the permanent identity
\(L_n(x_k)=1\).

This is not a Lagrange counterexample.  It is a rigorous obstruction showing
that continuity, local sup estimates with interval-dependent constants,
Baire category, and permanent low values at old nodes still do not close the
problem.  A successful proof must exploit an additional algebraic or
cross-scale property of actual nested Lagrange bases.

## 4. Exact nested rank-one recurrence

Let \(y=x_{n+1}\), let \(P_n(t)=\prod_{i=1}^n(t-x_i)\), and put
\[
b_y(x):=\ell_{n+1,n+1}(x)=\frac{P_n(x)}{P_n(y)}.
\]
For \(k\leq n\),
\[
\ell_{k,n+1}(x)
=\ell_{k,n}(x)\frac{x-y}{x_k-y}
=\ell_{k,n}(x)-\ell_{k,n}(y)b_y(x).
\]
Therefore the exact recurrence is
\[
L_{n+1}(x)
=\sum_{k=1}^n
\left|\ell_{k,n}(x)-b_y(x)\ell_{k,n}(y)\right|
+|b_y(x)|.
\]
It implies the valid but generally weak inequalities
\[
L_{n+1}(x)\geq
L_n(x)-|b_y(x)|(L_n(y)-1)
\]
and
\[
L_{n+1}(x)\geq
\frac{|x-y|}{2}L_n(x),
\]
the latter because \(|x_k-y|\leq2\).

There is no pointwise monotonicity and no universal additive persistence:
take old nodes \(-1,-1+\varepsilon\) and evaluate at \(x=0\).  Then
\[
L_2(0)=\frac{2-\varepsilon}{\varepsilon}.
\]
Append the new node \(y=0\).  Since an interpolation node has Lebesgue
function exactly \(1\),
\[
L_3(0)=1.
\]
The one-step drop is arbitrarily large as \(\varepsilon\downarrow0\).
For a completely rational example away from the appended node, old nodes
\(-1,-3/4\), new node \(-1/4\), and evaluation point \(-1/2\) give
\[
L_2(-1/2)=3,\qquad L_3(-1/2)=5/3.
\]

Thus any proposed recurrence lemma must incorporate how often new nodes can
reset a fixed region; one-step comparison alone cannot prove recurrence.

## 5. Exact cluster-point obstruction using Chebyshev roots

Compactness of separately chosen high points is not enough even for genuine
Lebesgue functions.

Let \(n=2m+1\) and use the \(n\) roots
\[
t_{k,n}=\cos\frac{(2k-1)\pi}{2n}
\]
of \(T_n\).  Since \(0\) is one of these roots,
\[
L_n(0)=1.
\]
Set
\[
z_n=\sin\frac{\pi}{2n}.
\]
Then \(z_n\to0\), while the Chebyshev formula
\[
|\ell_{k,n}(x)|
=\frac{|T_n(x)|\sin\theta_{k,n}}
{n|x-\cos\theta_{k,n}|},
\qquad
\theta_{k,n}=\frac{(2k-1)\pi}{2n},
\]
and \(|T_n(z_n)|=1\) show that \(L_n(z_n)\) diverges at least
logarithmically.  Indeed, using the roots
\(\sin(r\pi/n)\), \(1\leq r\leq\lfloor n/4\rfloor\), gives
\[
L_n(z_n)
\geq \frac{\sqrt2}{2\pi}
\sum_{r=1}^{\lfloor n/4\rfloor}\frac1r.
\]
Hence high points can converge to a point where the same functions stay
identically low.  Any cluster-point transfer requires an \(n\)-dependent
modulus at a scale much smaller than compactness alone provides.

A general elementary bound illustrates the missing scale.  If
\(\Lambda_n=\sup_{[-1,1]}L_n\), Markov's inequality gives
\[
|L_n(x)-L_n(y)|
\leq n(n-1)^2\Lambda_n|x-y|.
\]
Thus transfer of a bounded additive defect may require
\(|x-y|=O((n^3\Lambda_n)^{-1})\); convergence of a subsequence gives no such
rate.

The Chebyshev arrays above are not prefixes of one infinite sequence, so they
do not refute the target.  They exactly refute the generic cluster-point
step that ignores prefix-specific cross-scale structure.

## 6. Referee verdict

- The existing local Bernstein plus Baire route is blocked exactly at the
  dependence \(K(I_M)\); the moving-valley construction proves that no purely
  topological repair using only continuity and local sup bounds can work.
- Cluster-point and derivative arguments without a prefix-specific
  cross-scale estimate are invalid; the Chebyshev example gives an actual
  Lagrange obstruction.
- Naive monotonicity or additive persistence across \(n\mapsto n+1\) is false;
  the exact rank-one recurrence identifies the cancellation term that must be
  controlled.
- The only still-direct proof route is to exploit the exact rank-one
  recurrence together with a global restriction on repeated spatial resets,
  or an equivalently strong potential/capacity statement special to one
  nested node sequence.  A route that only improves the interval dependence
  in Tao's theorem but does not link intervals across \(n\) remains a
  reformulation of the fixed-defect gap.

## 7. Exact potential obstruction for any counterexample

Fix an old node \(x_k\) and a point \(x\) which is not a node.  For \(n\geq k\),
\[
\log|\ell_{k,n}(x)|
=\sum_{\substack{i\leq n\\i\ne k}}
\left(\log|x-x_i|-\log|x_k-x_i|\right).
\]
If the target fails at \(x\), then \(L_n(x)\leq (2/\pi)\log n\) for all
sufficiently large \(n\).  Since \(|\ell_{k,n}(x)|\leq L_n(x)\), necessarily
\[
\limsup_{n\to\infty}\frac1n
\sum_{\substack{i\leq n\\i\ne k}}
\left(\log|x-x_i|-\log|x_k-x_i|\right)\leq0.
\]
Thus, in any counterexample, every fixed old node must asymptotically
maximize the leave-one-out discrete logarithmic potential against every
non-node \(x\).  Conversely, a fixed pair \((k,x)\) for which the displayed
limsup is positive immediately gives exponentially large \(L_n(x)\) along a
subsequence and proves the desired conclusion for that node sequence.  This
is a direct structural dichotomy, although handling the zero-limsup
(equilibrium-like) case remains the theorem-closing gap.

## 8. Audit of the registered diagonal-counterexample route

The prefix-extension lemma in DIRECT ROUTE B asks for uniform suppression on
entire protected rational intervals.  In that form it is already impossible.
For every fixed interval \(I\), Tao's local theorem gives a finite \(K(I)\)
such that, for every sufficiently large prefix,
\[
\sup_{x\in I}L_n(x)\geq\frac2\pi\log n-K(I).
\]
Therefore no extension can keep
\[
L_n(x)\leq\frac2\pi\log n-M\qquad\text{for every }x\in I
\]
through arbitrarily late prefixes once \(M>K(I)\).  This is exactly the exit
condition written for Route B, so that route is dead as currently formulated.
A genuine counterexample construction would have to let the compulsory high
point move inside every interval while ensuring that each individual point is
hit with bounded defect only finitely often.  The moving-valley model in
Section 3 shows the correct quantifier pattern, but does not realize it by
nested Lagrange bases.
