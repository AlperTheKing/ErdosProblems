# Direct Route A: exact prefix recurrence and obstruction audit

## Source extraction

The primary source inspected was Tao, *Local Bernstein theory, and lower
bounds for Lebesgue constants*, arXiv:2603.21453v3.  The downloaded source is
in `tao_src/trunc_duffin_schaeffer.tex`.

- Theorem 1.10(i), source lines 341--355, gives
  \[
  \sup_{x\in I}L_n(x)\geq \frac{2}{\pi}\log n-O_I(1)
  \]
  for every fixed interval \(I\).
- Corollary 1.11, source lines 359--367, applies this to arbitrary triangular
  arrays of nodes, not only nested prefixes, and obtains the loss
  \(\omega(n)\to\infty\) by Baire category.
- Remark 1.12, source lines 371--373, identifies dependence of the error on
  the localization interval as the obstruction to replacing \(\omega(n)\)
  by a fixed constant.

Thus prefix nesting is genuinely additional information not used by the
existing Baire argument.

## Exact one-step identities

Let
\[
P_n(t)=\prod_{i=1}^n(t-x_i),\qquad a=x_{n+1},\qquad
q_a(t)=\frac{P_n(t)}{P_n(a)}=\ell_{n+1,n+1}(t).
\]
For \(k\leq n\),
\[
\ell_{k,n+1}(t)
=\frac{t-a}{x_k-a}\ell_{k,n}(t)
\tag{1}
\]
and, equivalently,
\[
\ell_{k,n}(t)
=\ell_{k,n+1}(t)+\ell_{k,n}(a)q_a(t).
\tag{2}
\]
Both formulas follow directly from the product definition.

Taking absolute values in (2) gives the true recurrence
\[
L_n(t)
\leq L_{n+1}(t)+(L_n(a)-1)|q_a(t)|
\leq L_n(a)L_{n+1}(t),
\tag{3}
\]
because \(L_n(a)\geq1\) and \(|q_a(t)|\leq L_{n+1}(t)\).  Hence
\[
L_{n+1}(t)\geq \frac{L_n(t)}{L_n(a)}.
\tag{4}
\]
This is multiplicative, not additive, and therefore does not preserve a
lower bound of size \((2/\pi)\log n-O(1)\) unless \(L_n(a)=1+O(1/\log n)\).

There is also an exact block version.  For \(m>n\), interpolation of the
degree-\((n-1)\) polynomial \(\ell_{k,n}\) at the first \(m\) nodes gives
\[
\ell_{k,n}(t)
=\ell_{k,m}(t)+
\sum_{j=n+1}^m\ell_{k,n}(x_j)\ell_{j,m}(t).
\tag{5}
\]
Consequently,
\[
L_n(t)\leq
\max\left(1,\max_{n<j\leq m}L_n(x_j)\right)L_m(t).
\tag{6}
\]
Formula (6) is the strongest direct prefix estimate obtained from the
interpolation identities alone.  Its loss is uncontrolled for an arbitrary
future node sequence.

## Quantitative reset lemma

**Lemma.**  Fix a prefix \(x_1,\ldots,x_n\), and let \(t\) not be one of its
nodes.  Put
\[
d_k=|t-x_k|,\quad d=\min_k d_k,\quad
S=\sum_{k=1}^n\frac1{d_k},\quad
B=\sum_{k=1}^n\frac{|\ell_{k,n}(t)|}{d_k}.
\]
If a new node \(a\) satisfies \(h=|a-t|<d/2\) and \(hS\leq1/4\), then
\[
1\leq L_{n+1}(t)\leq 1+(4S+2B)h.
\tag{7}
\]
In particular, \(L_{n+1}(t)\to1\) as \(a\to t\), even if \(L_n(t)\) is
arbitrarily large.

**Proof.**  Formula (1) gives
\[
L_{n+1}(t)
=\left|\frac{P_n(t)}{P_n(a)}\right|
+h\sum_{k=1}^n\frac{|\ell_{k,n}(t)|}{|x_k-a|}.
\]
Since \(|x_k-a|\geq d_k-h\geq d_k/2\), the second term is at most
\(2Bh\).  Also
\[
\left|\frac{P_n(t)}{P_n(a)}\right|
\leq\prod_{k=1}^n(1-h/d_k)^{-1}.
\]
Using \(-\log(1-u)\leq2u\) for \(0\leq u\leq1/2\), its logarithm is at most
\(2hS\leq1/2\).  Since \(e^v\leq1+2v\) for \(0\leq v\leq1\), this product is
at most \(1+4hS\).  Finally \(L_{n+1}(t)\geq1\) because the Lagrange basis
sums to \(1\).  This proves (7).

## Explicit family with an arbitrarily large one-step drop

Let \(m\geq1\), \(n=m+1\), and take the prefix
\[
x_{j+1}=-1+\frac jm,\qquad 0\leq j\leq m.
\]
At \(t=1\), the absolute value of the basis polynomial belonging to the node
\(x_{m+1}=0\) is
\[
\left|\ell_{m+1,n}(1)\right|
=\prod_{j=0}^{m-1}\frac{2m-j}{m-j}
=\binom{2m}{m}.
\]
Thus
\[
L_n(1)\geq\binom{2m}{m}.
\tag{8}
\]
The quantities \(S\) and \(B\) in the reset lemma are rational for this
prefix.  For any rational \(\varepsilon>0\), choose a rational
\[
0<h<
\min\left(\frac12,\frac1{4S},
\frac{\varepsilon}{8(S+B)}\right)
\]
and append the distinct rational node \(a=1-h\).  Equation (7) then gives
\[
L_{n+1}(1)<1+\varepsilon.
\tag{9}
\]
Since \(\binom{2m}{m}\to\infty\), (8)--(9) disprove both of the following
possible prefix-persistence claims:

1. \(L_{n+1}(t)\geq L_n(t)-K\) for any universal finite \(K\);
2. \(L_{n+1}(t)\geq cL_n(t)\) for any universal \(c>0\).

An even stronger permanent reset is possible: if the next node is exactly
\(a=t\), then
\[
L_r(t)=1\qquad\text{for every }r\geq n+1.
\tag{10}
\]
The finite prefix can be continued by any enumeration of distinct unused
rationals, so (10) is compatible with one infinite nested node sequence.

For a small exact illustration, the prefix \((-1,0)\) has
\(L_2(1)=3\).  Appending \(a=9/10\) gives
\[
L_3(1)=\frac1{19}+\frac29+\frac{200}{171}
=\frac{247}{171}<\frac32.
\]
Appending \(a=1\) instead gives \(L_r(1)=1\) for every later prefix.

## Consequence for the direct route

Prefix nesting by itself provides no pointwise consecutive-time persistence,
no bounded additive recurrence, and no positive multiplicative recurrence.
Moreover, a high point supplied at stage \(n\) may be selected as a future
node and then be permanently annihilated.

This does **not** disprove Erdős 1132: a successful point may lie outside the
countable node set, and the argument above controls only a prescribed point.
It does show that a proof cannot close by following Tao's stagewise high
points or their cluster points.  A viable recurrence lemma must instead
control an insertion-robust set quantity (for example, a quantitatively thick
set of high points after excluding all future nodes).  No such set-level
inequality is supplied by (1)--(6), so the fixed-defect frontier remains open.

## The precise set-level lemma that would close the route

Fix a compact interval \(I\Subset(-1,1)\) and write
\[
H_n(C;I)=
\left\{t\in I:L_n(t)>
\frac{2}{\pi}\log n-C\right\}.
\]
The weakest directly checkable tail-thickness statement is:

> **Tail-thickness lemma.** There are \(I,C,\delta\), with
> \(\delta>0\), such that for every \(N\),
> \[
> \left|\bigcup_{n\geq N}H_n(C;I)\right|\geq\delta.
> \tag{11}
> \]

Indeed, the measurable tail unions in (11) decrease with \(N\). Continuity
of Lebesgue measure from above gives
\[
\left|\bigcap_N\bigcup_{n\geq N}H_n(C;I)\right|\geq\delta.
\]
The intersection is precisely the limsup of the high sets, so every point in
it proves the required fixed-defect conclusion. A convenient stronger
version of (11) would be a uniform marginal estimate
\[
\limsup_{n\to\infty}|H_n(C;I)|>0.
\tag{12}
\]

Tao's theorem and polynomial structure give only a summable marginal width,
as follows.

**Lemma (quantified width of one high set).** For every fixed
\(I\Subset(-1,1)\), there are \(C_I,c_I>0\) such that, for all sufficiently
large \(n\),
\[
|H_n(C_I;I)|\geq \frac{c_I}{n^2\log n}.
\tag{13}
\]

**Proof.** Let \(M=\sup_I L_n\), and choose \(t_*\in I\) attaining \(M\).
For each \(k\), choose \(s_k\in\{-1,1\}\) with
\(s_k\ell_{k,n}(t_*)=|\ell_{k,n}(t_*)|\), and put
\[
p(t)=\sum_{k=1}^n s_k\ell_{k,n}(t).
\]
Then \(p(t_*)=M\), while \(|p(t)|\leq L_n(t)\leq M\) on \(I\). The Markov
inequality on \(I\) gives
\[
\sup_I|p'|\leq \frac{2(n-1)^2}{|I|}M.
\tag{14}
\]
Take \(C_I\) to be Tao's interval constant plus \(2\). His Theorem 1.10(i)
then gives
\[
M\geq\frac{2}{\pi}\log n-C_I+2.
\]
Starting at \(t_*\) and moving into \(I\), (14) leaves a one-sided interval
of length
\[
\frac{|I|}{2(n-1)^2}
\frac{M-(2/\pi)\log n+C_I}{M}
\gg_I\frac1{n^2\log n}
\]
on which \(p\), and hence \(L_n\), is above the defining threshold of
\(H_n(C_I;I)\). This proves (13).

The series of lower bounds in (13) converges. Therefore (13) alone supplies
no positive lower bound for any tail union: measurable intervals with these
lengths can be placed so that their limsup is empty. Replacing the constant
by an unbounded loss enlarges the sets and recovers Tao's Baire argument, but
does not prove the fixed-defect target.

There is also no universal one-step measure persistence from a positive
measure high set. On \(I=[0,1]\), for the prefix \((-1,0)\),
\[
L_2(t)=1+2t.
\]
Thus \(\{t\in I:L_2(t)\geq2\}=[1/2,1]\), of measure \(1/2\). After appending
the node \(1\), direct calculation gives
\[
L_3(t)=1+t-t^2\leq\frac54
\qquad(0\leq t\leq1).
\]
Hence
\[
\{L_2\geq2\}\cap\{L_3\geq2\}=\varnothing,
\qquad
|\{L_3\geq2\}|=0.
\tag{15}
\]
This explicit prefix extension falsifies every universal insertion rule of
the form
\[
|\{L_{n+1}\geq T\}|\geq
f(|\{L_n\geq T\}|)
\]
with \(f(1/2)>0\), and even falsifies retention of a single old high point at
that threshold.

Thus the exact remaining requirement is cross-time information strong enough
to prove (11). Neither Tao's local theorem, the elementary Markov width (13),
nor the exact prefix identities provide such information; (15) shows that it
cannot be a universal one-step thickness recurrence.

## Two-prefix cumulative measure obstruction at fixed defect

A bounded-window cumulative measure inequality also fails at the actual
threshold. Let \(N\geq2\) and put
\[
y_j=\cos\frac{j\pi}{N},\qquad 0\leq j\leq N.
\]
Take as the \(N\)-node prefix \(y_1,\ldots,y_N\), and append \(y_0=1\).
Thus the second prefix is the full \((N+1)\)-point Chebyshev--Lobatto set.
Write \(L_N^-\) and \(L_{N+1}^{\rm CL}\) for the two Lebesgue functions.

For the full set, with \(x=\cos\theta\), the nodal polynomial is a constant
multiple of
\[
W(x)=(1-x^2)T_N'(x).
\]
The cardinal formula and the Chebyshev differential equation give
\[
|\ell_j(\cos\theta)|=
\frac{|\sin\theta\,\sin N\theta|}
     {c_jN|\cos\theta-\cos(j\pi/N)|},
\tag{16}
\]
where \(c_0=c_N=2\) and \(c_j=1\) otherwise.

For every fixed \(0<\eta<\pi/2\), (16) yields, uniformly for
\(\eta\leq\theta\leq\pi-\eta\),
\[
L_{N+1}^{\rm CL}(\cos\theta)
=\frac2\pi|\sin N\theta|\log N+O_\eta(1).
\tag{17}
\]
For completeness, separate the nearest angular grid point from the sum in
(16). Its contribution is \(O(1)\), because \(|\sin N\theta|\) cancels the
nearest denominator. For all other grid points,
\[
\frac{\sin\theta}{|\cos\theta-\cos\phi|}
=\frac1{|\theta-\phi|}+O_\eta(1)
\]
when \(\phi\) stays in the interior, while the endpoint ranges contribute
\(O_\eta(N)\). The two harmonic sums on either side of \(\theta\) equal
\((2N/\pi)\log N+O_\eta(N)\). Multiplication by
\(|\sin N\theta|/N\) proves (17), including grid points by continuity.

The cardinal polynomial of the appended endpoint is
\[
q_N(\cos\theta)
=\frac{(1+\cos\theta)U_{N-1}(\cos\theta)}{2N}
=\frac{\cos(\theta/2)\sin N\theta}
       {2N\sin(\theta/2)}.
\tag{18}
\]
Moreover,
\[
L_N^-(1)=2N-1.
\tag{19}
\]
To verify (19), on the extrapolation interval the alternating-sign
interpolant is
\[
U_{N-1}(x)+U_{N-2}(x),
\]
which takes the appropriate signs at \(y_1,\ldots,y_N\), and its value at
\(1\) is \(N+(N-1)\).

Applying the exact update identity (2) and summing absolute values gives
\[
L_N^-(x)\leq
L_{N+1}^{\rm CL}(x)+(2N-2)|q_N(x)|.
\tag{20}
\]
On \(\eta\leq\theta\leq\pi-\eta\), (18) makes the second term in (20)
\(O_\eta(1)\). Combining (17) and (20), for either of the two prefixes,
\[
L(\cos\theta)\geq\frac2\pi\log N-C
\]
can hold in this compact angular interval only if
\[
1-|\sin N\theta|=O_{\eta,C}(1/\log N).
\tag{21}
\]
Within each period, the set in (21) has relative angular length
\(O_{\eta,C}(1/\sqrt{\log N})\). Hence its total angular, and therefore
\(x\)-measure, tends to zero.

The two omitted endpoint angular intervals have total \(x\)-measure
\(2(1-\cos\eta)\). Letting first \(N\to\infty\) and then \(\eta\to0\)
proves, for every fixed finite \(C\),
\[
\left|
H_N^-(C;[-1,1])\cup
H_{N+1}^{\rm CL}(C;[-1,1])
\right|\longrightarrow0.
\tag{22}
\]
(The replacement of \(\log N\) by \(\log(N+1)\) for the second prefix is
an \(o(1)\) threshold change.)

Thus no rank-one argument can supply a universal positive cumulative
Lebesgue-measure resource over one update, or over any fixed window merely by
iterating such a bound: the explicit nested pair above makes the combined
fixed-defect high-set measure arbitrarily small. This does not rule out an
unbounded-block estimate or a genuine cross-time correlation inequality;
those are exactly what would still be needed for (11).

## Cross-time second-moment criterion and route exit

A genuinely cross-time resource can be stated without disguising the target
as another limsup assertion. For a finite block \(B\) of indices, define
\[
V_B(t)=\sum_{n\in B}\mathbf 1_{H_n(C;I)}(t),
\quad
S_1(B)=\int_I V_B(t)\,dt,
\quad
S_2(B)=\int_I V_B(t)^2\,dt.
\]
Cauchy--Schwarz on the support of \(V_B\) gives the exact inequality
\[
\left|\bigcup_{n\in B}H_n(C;I)\right|
\geq \frac{S_1(B)^2}{S_2(B)}.
\tag{23}
\]
Consequently, disjoint blocks \(B_j\) escaping to infinity and a fixed
\(\delta>0\) with
\[
S_1(B_j)^2\geq\delta S_2(B_j)
\tag{24}
\]
would prove the tail-thickness lemma (11), and hence the original target.
This is a concrete first/second-moment bridge: (24) requires both cumulative
high-set mass and a bound on repeated concentration.

The available inputs do not establish either side of (24). The Tao--Markov
bound (13) only gives
\[
\sum_{n\geq N}|H_n(C_I;I)|
\geq c_I\sum_{n\geq N}\frac1{n^2\log n},
\]
whose guaranteed right-hand side tends to zero; it supplies no nonvanishing
block first moment. The rank-one formulas (1)--(6) give pointwise values but
no upper bound for the intersections appearing in \(S_2\). The reset lemma
shows why: a high region may be moved or erased by the next node. Finally,
the nested Chebyshev--Lobatto pair (22) gives
\[
S_1(\{N,N+1\})\longrightarrow0
\]
for every fixed defect \(C\), so no iteration of a positive bounded-window
first-moment inequality is possible.

**Dead-end statement for Direct Route A's rank-one mechanism.** Exact prefix
identities plus Tao's one-time local theorem yield only the summable width
(13). Pointwise persistence, one-step set persistence, and positive
bounded-window cumulative measure are all falsified by explicit nested
prefixes in (8)--(10), (15), and (22). The remaining sufficient estimate
(24) is an unbounded-block correlation estimate not controlled by any of
those inputs. Continuing to restate (24), tail thickness, or a capacity
analogue would merely rename the fixed-defect gap. Therefore the
rank-one/local-width branch exits here; no proof or disproof of Problem 1132
has been obtained.
