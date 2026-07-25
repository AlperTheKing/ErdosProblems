# Nestedness resource audit for Erdős 1132

## Scope

Write \(a=2/\pi\).  This note tests a direct cross-time mechanism which is
specific to a nested interpolation sequence.  The mechanism is the norm of
the rank-one increment between two consecutive interpolation projections.
It gives a theorem-closing criterion, but an explicit
Chebyshev--Lobatto-type nested sequence falsifies the universal growth premise.

## 1. Exact rank-one increment

Let \(x_1,x_2,\ldots\) be distinct points of \([-1,1]\), and let
\(I_n\) be interpolation on the first \(n\) points.  Put
\[
 q_n(t)=\prod_{i<n}\frac{t-x_i}{x_n-x_i}
       =\ell_{n,n}(t)
\]
and
\[
 B_n=1+L_{n-1}(x_n).
\]
The usual insertion identity is
\[
 \ell_{k,n}(t)
 =\ell_{k,n-1}(t)-\ell_{k,n-1}(x_n)q_n(t)
 \quad(k<n).
\]
Consequently, the coefficient vector of the rank-one operator
\(I_n-I_{n-1}\), evaluated at \(t\), has \(\ell^1\)-norm
\[
 R_n(t):=B_n|q_n(t)|.
\tag{1}
\]
Since this coefficient vector is the difference of the coefficient vectors
of \(I_n\) and \(I_{n-1}\), the triangle inequality gives the exact
pointwise bridge
\[
 R_n(t)\le L_n(t)+L_{n-1}(t).
\tag{2}
\]

## 2. Remez turns exponential increment growth into a fixed point

The following lemma is the usable cross-time resource.

**Lemma (exponential rank-one increment criterion).**  If
\[
 \limsup_{n\to\infty}\frac1n
 \log\left(B_n\lVert q_n\rVert_{[-1,1]}\right)>0,
\tag{3}
\]
then there is a positive-measure set of \(t\in(-1,1)\) for which
\[
 L_m(t)>a\log m
\]
for infinitely many \(m\).  In particular, the first question of
Erdős 1132 holds for this node sequence, with \(C_t=0\).

**Proof.**  We use the sharp measurable-set form of the Remez inequality.
If \(p\) has degree at most \(d\), \(E\subset[-1,1]\) has measure \(m>0\),
and \(|p|\le T\) on \(E\), then
\[
 \lVert p\rVert_{[-1,1]}
 \le T\,T_d\left(\frac{4-m}{m}\right).
\tag{4}
\]
Let \(H=\{t:|p(t)|>T\}\), \(h=|H|\), and \(m=2-h\).  Since
\(T_d(z)\le \exp(d\operatorname{arcosh}z)\) for \(z\ge1\), (4) implies
\[
 \frac{\lVert p\rVert}{T}\ge e^{cd}
 \quad\Longrightarrow\quad
 h\ge 2\tanh^2(c/2).
\tag{5}
\]

Apply this to the degree-\((n-1)\) polynomial \(p_n=B_nq_n\), with
\(T_n=2a\log n\).  Condition (3), with the negligible factor \(T_n\),
supplies \(c>0\), an infinite subsequence \(n_j\), and a fixed
\(\delta>0\) such that
\[
 |\{t:R_{n_j}(t)>2a\log n_j\}|\ge\delta.
\tag{6}
\]
The limsup of the sets in (6) has measure at least \(\delta\): every tail
union has measure at least \(\delta\), and the tail unions decrease.
For every \(t\) in this limsup, (2) shows that either
\(L_{n_j}(t)>a\log n_j\) or
\(L_{n_j-1}(t)>a\log n_j\).  Infinitely many distinct indices occur because
one interpolation index can account for at most two consecutive increments.
This proves the lemma. \(\square\)

The same proof, applied to a single cardinal polynomial, gives another exact
necessary condition for a counterexample:
\[
 \limsup_{n\to\infty}\frac{\log\Lambda_n}{n}=0,
\qquad
\Lambda_n:=\sup_{[-1,1]}L_n.
\tag{7}
\]
Indeed, if \(\Lambda_n\) is exponentially large, one of the \(n\) cardinal
polynomials has exponentially large norm, and (5) again gives fixed positive
measure at the target threshold.

## 3. Immediate Chebyshev--Lobatto test

Let
\[
 y_j=\cos(j\pi/N),\qquad 0\le j\le N,
\]
take the \(N\)-point prefix \(y_1,\ldots,y_N\), and append \(y_0=1\).
The new cardinal polynomial is
\[
 q_{N+1}(\cos\theta)
 =\frac{\cos(\theta/2)\sin(N\theta)}
        {2N\sin(\theta/2)}.
\tag{8}
\]
Equivalently,
\[
 q_{N+1}(x)=\frac{(1+x)U_{N-1}(x)}{2N}.
\]
The elementary inequality
\(|U_{N-1}(\cos\theta)|\le N\) gives
\[
 \lVert q_{N+1}\rVert_{[-1,1]}=1.
\tag{9}
\]
The old Lebesgue value at the appended endpoint is exactly
\[
 L_N^-(1)=2N-1.
\tag{10}
\]
Thus the full rank-one increment norm for this update is
\[
 B_{N+1}\lVert q_{N+1}\rVert=2N,
\qquad
\frac{\log(2N)}{N+1}\longrightarrow0.
\tag{11}
\]
So even the strengthened resource \(B_n\lVert q_n\rVert\), not merely the
new-cardinal norm, has only polynomial size on this exact nested update.
The exponential criterion correctly remains silent.

There is also an infinite, rather than two-prefix, falsifier of a universal
version of (3).  For the real projections \(R\) of the standard binary Leja
sequence on the unit circle, the sections are nested
Chebyshev--Lobatto-type sets.  Chkifa records for their difference
operators the bound
\[
 \lVert I_{R_{k+1}}-I_{R_k}\rVert\le(1+k)^2.
\tag{12}
\]
By (1), the left side is exactly \(B_{k+1}\lVert q_{k+1}\rVert\).
Hence (3) fails along the entire explicit nested sequence.  See
Chkifa, *New bounds on the Lebesgue constants of Leja sequences on the
unit disc and on \(\Re\)-Leja sequences*, arXiv:1503.01731, equation (4.4).
More generally, Lebesgue constants of genuine Leja sequences on
\([-1,1]\) are subexponential (and currently have polynomial upper bounds);
see arXiv:2607.01836.

## 4. Energy consequence and precise exit

Condition (7) has a concrete potential-theoretic consequence.  If
\[
 V(X_n)=\prod_{1\le i<j\le n}|x_i-x_j|
\]
and \(V_n^*\) is the maximum \(n\)-point Vandermonde product on
\([-1,1]\), interpolation of a Fekete set \(Y_n\) in the nodes \(X_n\)
gives
\[
 \frac{V_n^*}{V(X_n)}
 =\left|\det(\ell_{j,n}(y_i))_{i,j=1}^n\right|
 \le\Lambda_n^n.
\tag{13}
\]
Thus every counterexample must satisfy
\[
 \log V_n^*-\log V(X_n)=o(n^2),
\tag{14}
\]
so its prefixes are asymptotically Fekete and their empirical measures have
the arcsine limit.  This is a genuine structural reduction, but it does not
close the fixed additive defect.

The hoped-for universal nestedness statement (3) is false by (12).  Replacing
exponential growth in (3) by unspecified subexponential growth destroys the
positive-measure conclusion in (5); the guaranteed measure then tends to
zero.  An additional assertion that these shrinking Remez high sets have a
nonempty limsup is exactly the unresolved cross-time correlation problem,
not a derived resource.

**Exit.**  The rank-one-increment/Remez mechanism proves the target for every
sequence with positive exponential increment rate and forces any
counterexample into the asymptotically Fekete, subexponential class.  It
cannot be a complete route: the explicit nested \(\Re\)-Leja sequence has
only polynomial difference-operator norms.  Continuing by merely postulating
correlation of the remaining shrinking high sets would be a reformulation
maze.  No proof or disproof of Erdős 1132 is obtained here.

