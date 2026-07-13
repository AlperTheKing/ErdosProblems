# P15: mixed Fourier phase for the signed ruler

## Verdict

The unit-lattice exclusion has two exact polynomial forms.  It gives a
nontrivial natural-modulus phase-defect identity, but that identity does not
by itself imply

\[
  G+2W\ge (3-o(1))p^2.
\]

More strongly, there is an infinite family of **exact cyclic phase
countermodels** of modulus

\[
  2(p^2-p+1)=(2+o(1))p^2.
\]

They come from Singer perfect difference sets.  They preserve the same
Newman-polynomial factorization, cyclic Sidonicity, the diagonal terms, the
coefficientwise difference/sum exclusion, and every root-of-unity mixed
correlation.  Thus no argument using only cyclic Fourier phase can recover
the coefficient (3).

The information not preserved by these models is now precise: an integer
signed ruler is supported in a one-sided arc ([0,W]) with
(2W<L:=G+2W), and the root filter must distinguish the zero-winding and
one-winding coefficients of one Laurent polynomial.  A radial (off-unit-
circle) identity records that distinction exactly.  This arc/winding datum,
not another unit-circle moment, is the next missing invariant.

## 1. Exact Laurent-polynomial identities

Let

\[
 Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},\qquad G>0,
\]

and assume the exact signed-ruler condition

\[
 D(Z)\cap (G+S(Z))=\varnothing,                         \tag{1}
\]

where

\[
 D(Z)=\{z_j-z_i:i<j\},\qquad
 S(Z)=\{z_i+z_j:i\le j\}.
\]

The ordinary Sidon condition, including diagonal sums, is also assumed.
Put

\[
 P(z)=\sum_{x\in Z}z^x,
 \qquad
 Q(z)=\frac{P(z)^2+P(z^2)}2.
\]

Sidonicity gives the coefficient identities

\[
 P(z)P(z^{-1})
 =p+\sum_{d\in D(Z)}(z^d+z^{-d}),                       \tag{2}
\]

and

\[
 Q(z)=\sum_{0\le i\le j<p}z^{z_i+z_j}.                 \tag{3}
\]

In particular, (3) retains every diagonal (2z_i) with coefficient one.
Since all exponents in (z^GQ(z)) are positive, (1) is exactly

\[
 \boxed{
 \operatorname{CT}\!\left[
 (P(z)P(z^{-1})-p)z^{-G}Q(z^{-1})
 \right]=0.}                                             \tag{4}
\]

There is no hidden cancellation in (4): its constant term is precisely

\[
 |D(Z)\cap(G+S(Z))|.
\]

On the unit circle, (4) becomes

\[
 \frac1{2\pi}\int_0^{2\pi}
 (|P(e^{i\theta})|^2-p)e^{-iG\theta}
 \frac{\overline{P(e^{i\theta})}^{\,2}
       +\overline{P(e^{2i\theta})}}2\,d\theta=0.        \tag{5}
\]

An even cleaner ordered form is

\[
 \boxed{
 \operatorname{CT}\!\left[z^G P(z)^3P(z^{-1})\right]=0.} \tag{6}
\]

Indeed, the constant term in (6) counts ordered quadruples satisfying

\[
 z_j=G+z_i+z_a+z_b.                                     \tag{7}
\]

Such a quadruple is exactly a collision
(z_j-z_i=G+z_a+z_b).  Conversely every collision gives one or two
ordered quadruples according as (a=b) or (a\ne b).  Thus (6) is
equivalent to (1), rather than merely necessary for it.  Its unit-circle
form is

\[
 \frac1{2\pi}\int_0^{2\pi}
 e^{iG\theta}P(e^{i\theta})^2|P(e^{i\theta})|^2
 \,d\theta=0.                                           \tag{8}
\]

## 2. The natural-modulus residue identity

Set

\[
 L=G+2W,\qquad \omega=e^{2\pi i/L},\qquad P_r=P(\omega^r).
\]

Root-of-unity filtering in (6) gives

\[
 \frac1L\sum_{r=0}^{L-1}
 \omega^{Gr}P_r^3\overline{P_r}
 =\#\{(j,i,a,b):z_j-z_i-z_a-z_b\equiv G\pmod L\}.       \tag{9}
\]

The integer on the right of (9) has a special no-wrap interpretation.  The
expression (z_j-z_i-z_a-z_b) lies in ([-3W,W]).  Among integers in that
interval congruent to (G) modulo (L=G+2W), only

\[
 G\quad\hbox{and}\quad G-L=-2W
\]

can occur.  The first is excluded by (1).  Reverse the ruler,

\[
 X=W-Z.
\]

The second equation becomes

\[
 x_i+x_a+x_b=x_j.
\]

Consequently, if

\[
 T_3(X)=\#\{(i,a,b,j):x_i+x_a+x_b=x_j\},                \tag{10}
\]

then

\[
 \boxed{
 \sum_{r=0}^{L-1}\omega^{Gr}P_r^3\overline{P_r}
 =L T_3(X).}                                             \tag{11}
\]

This is a genuine residue restriction: the mixed phase sum is not free and
is not zero after reduction modulo the natural span.

There is an exact combinatorial formula for the wrap count.  Let

\[
 S_{\rm off}(X)=\{x_a+x_b:a<b\},\qquad 2X=\{2x:x\in X\}.
\]

Since (X) is Sidon, every positive difference and every unordered sum has
a unique representing pair.  Separating (x_j-x_i=0), off-diagonal sums,
and diagonal sums gives

\[
 \boxed{
 T_3(X)=p
   +2|D(X)\cap S_{\rm off}(X)|
   +|D(X)\cap 2X|.}                                     \tag{12}
\]

Every positive (x\in X) lies in the first intersection via
(x=x-0=x+0).  Also a positive difference receives weight at most two.
Therefore

\[
 \boxed{3p-2\le T_3(X)\le p^2.}                         \tag{13}
\]

The fourth Fourier moment is exact as well.  Since (2W<L), equality of
two sums modulo (L) is equality over the integers.  Sidonicity therefore
gives

\[
 \sum_{r=0}^{L-1}|P_r|^4=L(2p^2-p).                     \tag{14}
\]

For (P_r\ne0), define

\[
 u_r=\omega^{Gr}\frac{P_r^2}{|P_r|^2},
\]

and put (u_r=1) when (P_r=0).  Equations (11) and (14) yield the exact
phase-defect identity

\[
 \boxed{
 \sum_{r=0}^{L-1}|P_r|^4(1-\operatorname{Re}u_r)
 =L(2p^2-p-T_3(X)).}                                    \tag{15}
\]

In particular,

\[
 L(p^2-p)
 \le \sum_r|P_r|^4(1-\operatorname{Re}u_r)
 \le 2L(p-1)^2.                                         \tag{16}
\]

Thus a valid signed ruler forces order-(Lp^2) nontrivial phase
dispersion.  However, the triangle inequality applied to (11) and (14)
only gives

\[
 L\ge
 \frac{2p^4}{2p^2-p+T_3(X)}
 \ge \frac{2p^4}{3p^2-p}
 =\left(\frac23+o(1)\right)p^2,                         \tag{17}
\]

which is weaker than the elementary label count (L\ge p^2).  The exact
phase budget alone does not approach the coefficient three.

## 3. Exact finite audit

The two compressed rulers from P07 give the following integer checks.

\[
\begin{array}{c|c|c|c|c|c}
p&W&G&L&T_3(X)&2p^2-p-T_3(X)\\ \hline
5&12&6&30&20&25\\
9&49&18&116&44&109
\end{array}                                              \tag{18}
\]

For the first row,

\[
 Z=\{0,4,9,11,12\};
\]

for the second,

\[
 Z=\{0,6,13,29,34,38,46,48,49\}.
\]

Direct integer enumeration gives zero solutions to (7), respectively
20 and 44 natural-modulus wrap solutions, and verifies (12)--(16) without
floating-point arithmetic.  In particular, substantial phase defect is
already compatible with (L/p^2=30/25) and (116/81) at finite size.

As a separate exhaustive gate, all signed rulers with
\(W\le14\), \(2\le p\le6\), and \(1\le G\le15\) were enumerated.  All
2,861 valid triples \((Z,G,L)\) passed (9)--(16) and the winding check in
Section 5 using integer coefficient counts only.

## 4. Infinite exact cyclic phase countermodels

The preceding identities suggest retaining all phases at roots of unity.
That relaxation still cannot prove the target.

Let (r) be a prime power, put

\[
 p=r+1,\qquad q=r^2+r+1=p^2-p+1,\qquad m=2q.
\]

By the Singer perfect-difference-set theorem there is

\[
 \mathcal D\subseteq\mathbb Z/q\mathbb Z,\qquad
 |\mathcal D|=p,
\]

such that every nonzero residue has exactly one ordered representation
(d-d') with (d,d'\in\mathcal D).  As (q) is odd, the Chinese
remainder map

\[
 \mathbb Z/m\mathbb Z\simeq
 \mathbb Z/2\mathbb Z\times\mathbb Z/q\mathbb Z
\]

is an isomorphism.  For each (d\in\mathcal D), let \(\widetilde d\)
be the unique **even** residue modulo (m) reducing to (d) modulo (q),
and set

\[
 \widetilde Z=\{\widetilde d:d\in\mathcal D\},
 \qquad \widetilde G=q.
\]

This construction has four exact properties.

1.  All (p(p-1)) ordered nonzero differences of \(\widetilde Z\) are
    distinct modulo (m).  Equality modulo (m) would imply equality
    modulo (q), where the perfect-difference property fixes the ordered
    pair.

2.  All \(\binom{p+1}{2}\) unordered sums, including diagonals, are
    distinct modulo (m).  Indeed, an equality of two sums modulo (q)
    rearranges to an equality of two differences; perfection makes the
    unordered pairs equal.  Since (q) is odd, the diagonal case causes no
    exception.

3.  Every difference is even modulo (m), while every residue in
    \(\widetilde G+S(\widetilde Z)\) is odd.  Hence

    \[
    (\widetilde Z-\widetilde Z)\setminus\{0\}
    \quad\hbox{and}\quad
    \widetilde G+S(\widetilde Z)
    \]

    are coefficientwise disjoint.  This is stronger than excluding only
    one orientation of each difference.

4.  If

    \[
    \widetilde P(z)=\sum_{x\in\widetilde Z}z^x
    \quad\text{in }\mathbb Z[z,z^{-1}]/(z^m-1),
    \]

    and write \(\widetilde P^*(z)=\widetilde P(z^{-1})\), then parity gives
    the exact cyclic identities

    \[
    \operatorname{CT}_m
    \left[(\widetilde P\widetilde P^*-p)
    z^{-\widetilde G}
    \frac{(\widetilde P^*)^2+\widetilde P(z^{-2})}{2}
    \right]=0,                                           \tag{19}
    \]

    and

    \[
    \boxed{
    \operatorname{CT}_m
    \left[z^{\widetilde G}\widetilde P(z)^3
    \widetilde P(z^{-1})\right]=0.}                      \tag{20}
    \]

    Equivalently, (19)--(20) hold after the exact average over all (m)-th
    roots of unity.  There is no numerical approximation and no loss of
    the common polynomial \(\widetilde P\).

The modulus is

\[
 \boxed{m=2(p^2-p+1)=(2+o(1))p^2.}                      \tag{21}
\]

Thus even the full cyclic polynomial phase, including the same-(P)
factorization and all residues simultaneously, admits coefficient two.

Small exact instances are

\[
\begin{array}{c|c|c|c|c}
p&q&m&\mathcal D&\widetilde Z\\ \hline
3&7&14&\{0,1,3\}&\{0,8,10\}\\
4&13&26&\{0,1,3,9\}&\{0,14,16,22\}\\
6&31&62&\{0,1,4,10,12,17\}&\{0,32,4,10,12,48\}
\end{array}                                              \tag{22}
\]

with shifts (7,13,31), respectively.  Direct residue enumeration gives
difference counts (6,12,30), sum counts (6,10,21), zero overlap, and
zero quartic mixed count.

These are not integer counterexamples to Problem 864.  Their exponents wind
around the cyclic group.  In particular they do not obey the one-sided
support relation

\[
 \widetilde Z\subseteq[0,W],\qquad 2W<m,\qquad
 m=\widetilde G+2W.                                     \tag{23}
\]

That failure is exactly why the cyclic quartic count in (20) can be zero,
whereas an integer ruler reduced modulo its natural span has the unavoidable
wrap count (T_3(X)\ge3p-2) in (11).

## 5. The precise missing invariant: winding separation

The order information can be written without approximation.  Put

\[
 R(z)=\sum_{x\in X}z^x=z^W P(z^{-1}).
\]

Then

\[
 F(z)=R(z)^3R(z^{-1})
 =\sum_{a,b,c,d\in X}z^{a+b+c-d}.
\]

Its exponents lie in ([-W,3W]).  Since (2W<L), the root filter at
modulus (L) can see only the zero-winding and one-winding coefficients:

\[
 \frac1L\sum_{j=0}^{L-1}F(\rho\omega^j)
 =[z^0]F+\rho^L[z^L]F                                  \tag{24}
\]

for every real \(\rho>0\).  Here

\[
 [z^0]F=T_3(X),
\]

while

\[
 [z^L]F
 =\#\{a,b,c,d\in X:a+b+c-d=L\}.                         \tag{25}
\]

Under the reversal (X=W-Z), (25) is exactly the forbidden mixed
difference/sum collision.  Hence an integer signed ruler satisfies the
off-unit-circle identity

\[
 \boxed{
 \frac1L\sum_{j=0}^{L-1}
 R(\rho\omega^j)^3R(\rho^{-1}\omega^{-j})
 =T_3(X)\quad(\rho>0).}                                 \tag{26}
\]

Unlike the unit-circle equation, (26) separates the two winding numbers:
varying \(\rho\) would expose a nonzero coefficient (25).  The Singer
models satisfy every cyclic identity at \(\rho=1\), but they have no
one-sided lift satisfying (23), so they do not satisfy this radial
zero/one-winding separation with modulus (m).

Therefore the next viable Fourier target is not another scalar moment or
another root-of-unity constraint.  It must combine

* the exact same-(P) phase relation;
* support in an arc of length (W<L/2); and
* quantitative separation of the coefficients ([z^0]F) and ([z^L]F),
  for example through the radial family (26).

Any argument that first passes to a cyclic quotient and then uses only
unit-circle data is ruled out by (21).  The unresolved step is an
arc-sensitive or radial inequality for Newman polynomials with Sidon
coefficients; proving such an inequality strong enough to force
(L\ge(3-o(1))p^2) remains open.
