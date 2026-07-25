# Annular two-block obstruction for Erdős Problem 197

## Family under audit

Fix real numbers
\[
r>1,\qquad 1<\lambda<r,
\]
and define
\[
I_k=[\lceil r^k\rceil,\lceil \lambda r^k\rceil-1]\cap\mathbb Z,
\qquad
J_k=[\lceil \lambda r^k\rceil,\lceil r^{k+1}\rceil-1]\cap\mathbb Z.
\]
Colour \(I_k\) with colour \(0\) and \(J_k\) with colour \(1\).  In each
colour, concatenate the blocks in increasing order of \(k\), allowing an
arbitrary order inside each individual block.

Write
\[
B_{0,k}=I_k,\quad B_{1,k}=J_k,\qquad
\rho_0=\lambda,\quad \rho_1=\frac r\lambda.
\]
Thus \(\rho_c\) is the upper-to-lower endpoint ratio of a block of colour
\(c\), ignoring the bounded rounding errors.

## The three-distinct-block obstruction

### Lemma

Fix \(c\in\{0,1\}\).  If there are integers \(1\leq p<q\) such that
\[
\rho_c>
H_{p,q}(r):=
\max\left\{
\frac{1+r^q}{2r^p},
\frac{2r^p}{1+r^q}
\right\},
\tag{1}
\]
then, for every sufficiently large \(k\), there are
\[
x\in B_{c,k},\qquad
y\in B_{c,k+p},\qquad
z\in B_{c,k+q}
\]
with \(x+z=2y\).

Consequently, no ordering in this annular family can solve Problem 197.

### Proof

For colour \(c\), write its unrounded normalized block as
\([A r^j,B r^j)\), where \(B/A=\rho_c\).  The possible values of \(x+z\)
fill an integer interval whose endpoints are
\[
A(1+r^q)r^k+O(1)
\quad\hbox{and}\quad
B(1+r^q)r^k+O(1).
\]
The possible values of \(2y\) are the even integers in an interval whose
endpoints are
\[
2Ar^p r^k+O(1)
\quad\hbox{and}\quad
2Br^p r^k+O(1).
\]
Condition (1) is precisely the pair of strict inequalities
\[
A(1+r^q)<2Br^p,
\qquad
2Ar^p<B(1+r^q).
\]
Hence the two intervals overlap in an interval of length
\(\Omega(r^k)\).  For all sufficiently large \(k\), this overlap contains
an even integer \(2y\).  The sum of two integer intervals is an integer
interval, so \(2y=x+z\) for some \(x\in B_{c,k}\) and
\(z\in B_{c,k+q}\).

The three blocks are disjoint and increase with their indices, so
\(x<y<z\).  Block concatenation also places \(x\) before \(y\) before
\(z\) in the colour-\(c\) enumeration.  This is a forbidden monotone
three-term progression, independently of all internal block orders.
\(\square\)

## Exact survivor set of this obstruction

Define
\[
\mu(r)=
\min_{d\geq 1}
\max\left\{\frac{r^d}{2},\frac{2}{r^d}\right\}.
\tag{2}
\]
If \(\rho_c>\mu(r)\), choose a minimizing \(d\), put \(q=p+d\), and let
\(p\to\infty\).  Then
\[
H_{p,p+d}(r)\longrightarrow
\max\left\{\frac{r^d}{2},\frac{2}{r^d}\right\},
\]
so the lemma applies for some finite \(p\).

Let \(s=\log_r 2\).  Formula (2) can be written exactly as
\[
\mu(r)=r^{\operatorname{dist}(s,\mathbb N_{\geq1})}.
\tag{3}
\]
Since
\[
\rho_0\rho_1=r,
\]
at least one colour is obstructed whenever \(\mu(r)^2<r\).

It follows that the three-distinct-block lemma eliminates every parameter
pair except the following set:
\[
\boxed{
\left\{(r,\lambda):r>4,\ 2\leq\lambda\leq\frac r2\right\}
\ \cup\
\left\{
\left(2^{2/(2m+1)},\,2^{1/(2m+1)}\right):m\geq0
\right\}.}
\tag{4}
\]
Here “except” means only “not eliminated by the preceding lemma,” not that
the remaining pairs work.

Indeed, if \(1<r\leq4\), then \(s\geq1/2\), and the distance in (3) is
strictly less than \(1/2\) unless \(s=m+1/2\).  In the equality case,
\(\mu(r)=\sqrt r\), and both block ratios can fail to exceed \(\mu(r)\)
only when
\[
\lambda=\frac r\lambda=\sqrt r.
\]
This gives the discrete pairs in (4).  If \(r>4\), then \(s<1/2\),
the closest positive integer is \(1\), and
\[
\mu(r)=\frac r2.
\]
Thus \(\lambda<2\) obstructs colour \(1\), while
\(\lambda>r/2\) obstructs colour \(0\), leaving only the interval in
(4).

## A forced two-block cycle inside the survivor set

The survivor set in (4) is not merely an artefact of the
three-distinct-block test.  The parameter pair
\[
r=6,\qquad \lambda=\frac{12}{5}
\]
lies in its continuous part, but is impossible by a finite forced-order
cycle.

For this pair,
\[
I_0=\{1,2\},\qquad I_1=\{6,7,\ldots,14\}.
\]
Write \(u\prec v\) when \(u\) occurs before \(v\) in the colour-\(0\)
enumeration.  Since all of \(I_0\) precedes all of \(I_1\), the four
crossing progressions
\[
(2,6,10),\quad (2,7,12),\quad
(2,8,14),\quad (1,6,11)
\]
force
\[
10\prec6,\qquad
12\prec7,\qquad
14\prec8,\qquad
11\prec6.
\tag{5}
\]

For an internal progression \(x<y<z\), validity says that \(y\) is
either before both endpoints or after both endpoints.  In particular,
\[
y\prec x\Longrightarrow y\prec z,
\qquad
x\prec y\Longrightarrow z\prec y,
\tag{6}
\]
and the symmetric versions of these implications also hold.

Using only (5), (6), transitivity, and internal progressions in \(I_1\):

1. From \(10\prec6\) and \((6,10,14)\), obtain \(10\prec14\), hence
   \(10\prec8\).
2. From \((8,10,12)\), obtain \(10\prec12\), hence \(10\prec7\).
   From \((7,10,13)\), obtain \(10\prec13\).
3. From \(10\prec8\) and \((6,8,10)\), obtain \(6\prec8\).
   Thus \(11\prec8\), and \((8,11,14)\) gives \(11\prec14\).
4. From \(10\prec12\) and \((10,12,14)\), obtain \(14\prec12\).
   Hence \(11\prec12\), and \((10,11,12)\) gives \(11\prec10\).
5. Therefore \(11\prec10\prec13\), and \((9,11,13)\) gives
   \(11\prec9\).
6. On the other hand, \(11\prec10\) and \((9,10,11)\) give
   \(9\prec10\).  Since \(10\prec7\), the progression \((7,9,11)\)
   gives \(9\prec11\).

Thus both \(11\prec9\) and \(9\prec11\), a contradiction.  No choice of
the internal order of \(I_1\) can repair this parameter pair.

## Audit disposition

The three-distinct-block lemma gives a uniform necessary obstruction and
the \(r=6,\lambda=12/5\) certificate gives a genuine finite forced cycle
inside the residual region.  However, (4) still contains a continuum of
parameter pairs and a discrete self-dual family.  No invariant or uniform
forced-cycle argument presently covers that survivor set.

Therefore this annular two-block family currently has no theorem-closing
bridge.  Continuing with isolated parameter exclusions would be a bounded
family cascade rather than a proof of Problem 197.

Suggested route status:

`DEAD: annular geometric-block family — exact three-block obstruction leaves
the survivor set (4), and the available two-block forced cycle is not uniform
over that set.`
