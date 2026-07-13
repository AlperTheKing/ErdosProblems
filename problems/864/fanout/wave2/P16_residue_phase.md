# P16: residue phase and wrap layers

## Verdict

The residue attack does not prove

\[
G+2W\geq(3-o(1))p^2.
\]

It does identify the missing discrete state exactly.  Residue histograms
determine the **total** number of congruent difference/shifted-sum label
pairs, while admissibility removes one specified integer wrap layer from
that total.  Averaging over (p\leq m\leq p^2) gives an exact divisor
identity, but still does not isolate the forbidden layer.

This loss is genuine.  There are subcritical valid/invalid integer Sidon
rulers with the same single-modulus point and label histograms and the same
cross-wrap moments through degree three.  A second subcritical pair has the
same first three polynomially weighted averages over **all** moduli in the
assigned range.  Thus marginal residues, aggregate wraps, fixed low-order
wrap moments, and low-degree averaged-modulus moments cannot close the
coefficient (3).

The surviving residue frontier is a coherent quotient-layer theorem across
moduli, or an equivalent indexed-star phase theorem.  Merely retaining the
complete quotient vector and restating that its zero layer is empty would be
equivalent to the original signed-ruler condition.

## 1. Exact residue identities, including diagonals

Let

\[
Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},\qquad G>0,
\]

and put

\[
D=\{z_j-z_i:i<j\},\qquad
C=\{G+z_i+z_j:i\leq j\}.                                \tag{1}
\]

The fully reflected core is valid exactly when (Z) is Sidon, with
diagonals included, and

\[
D\cap C=\varnothing.                                      \tag{2}
\]

Thus (|D|=\binom p2), (|C|=\binom{p+1}2), and the union has
exactly (p^2) labels in ([1,L]), where (L=G+2W).

Fix a modulus (m\).  Define

\[
n_m(a)=\#\{i:z_i\equiv a\pmod m\},
\]

\[
d_m(r)=\#\{(i,j):i<j, z_j-z_i\equiv r\pmod m\},
\]

\[
c_m(r)=\#\{(i,j):i\leq j, G+z_i+z_j\equiv r\pmod m\}.
\]

If

\[
\Delta_m(t)=\#\{i:2z_i\equiv t\pmod m\},
\]

then the exact unordered-sum formula is

\[
\boxed{
c_m(G+t)=\frac12\left(\sum_a n_m(a)n_m(t-a)+\Delta_m(t)\right).}
\tag{3}
\]

The diagonal correction is essential: the ordered convolution counts an
off-diagonal pair twice and a diagonal once, while (Delta_m) supplies the
second diagonal copy.

The positive-difference orientation is not determined by (n_m), but its
symmetrization is:

\[
\boxed{
d_m(r)+d_m(-r)=
\sum_a n_m(a)n_m(a+r)-p\mathbf1_{r=0}.}                   \tag{4}
\]

This also covers (r=0), and (r=m/2) for even (m): in either
self-inverse residue the left side is (2d_m(r)).

There is a useful point-residue rigidity consequence.  Every pair of points
in one residue class has a distinct positive difference among
(m,2m,\ldots,\lfloor W/m\rfloor m).  Hence

\[
\boxed{
\sum_{r\bmod m}\binom{n_m(r)}2\leq\left\lfloor\frac Wm\right\rfloor.}
\tag{5}
\]

In particular, at (m=p^2), under (W<3p^2/2), at most one pair of ruler
points shares a residue.  This is genuine microscopic rigidity, but the
countermodels below show that it does not by itself locate the forbidden
label layer.

## 2. Exact quotient layers

For (q\in\mathbb Z), define

\[
X_m(q)=\#\{(d,c)\in D\times C:d-c=qm\}.                  \tag{6}
\]

Every congruent pair has a unique integer quotient, so

\[
\boxed{
\sum_{r\bmod m}d_m(r)c_m(r)=\sum_qX_m(q).}               \tag{7}
\]

Condition (2) is precisely

\[
\boxed{X_m(0)=0.}                                        \tag{8}
\]

The residue histograms determine the left side of (7), but not the
distribution of its mass among (q).  This is the phase erased by weak
occupation and ordinary modular counting.

The internal wrap identities are

\[
\sum_r\binom{d_m(r)}2
=\sum_{q\geq1}|D\cap(D+qm)|,                              \tag{9}
\]

\[
\sum_r\binom{c_m(r)}2
=\sum_{q\geq1}|C\cap(C+qm)|.                              \tag{10}
\]

Consequently aggregate internal and cross wrap counts add no state beyond
the residue histograms.  Only quotient-resolved counts see (8).

There is one exact indexed contribution.  Pair

\[
d_{ij}=z_j-z_i,\qquad c_{ij}=G+z_i+z_j\quad(i<j).
\]

Then

\[
d_{ij}-c_{ij}=-(G+2z_i),                                  \tag{11}
\]

and therefore

\[
\boxed{
\sum_qX_m(q)\geq
\sum_{i=0}^{p-2}(p-1-i)\mathbf1_{m\mid G+2z_i}.}         \tag{12}
\]

The right side is the exact same-pair self-fibre contribution.  It can be a
small fraction of the total modular cross count; it may not be treated as an
equality.

Finally, if

\[
I_D(m)=\sum_r\binom{d_m(r)}2,\qquad
I_C(m)=\sum_r\binom{c_m(r)}2,
\]

then support inclusion-exclusion gives

\[
\boxed{
\sum_qX_m(q)\geq
\bigl(p^2-m-I_D(m)-I_C(m)\bigr)_+.}                       \tag{13}
\]

Indeed, the supports of (d_m,c_m) have sizes at least
(|D|-I_D(m)), (|C|-I_C(m)), respectively.  Equation (13) is the
cross-colour form of pigeonhole packing; it still does not distinguish
(q=0) from (q\ne0).

## 3. Averaging moduli gives divisor sums

Write

\[
\tau_{[p,p^2]}(n)=\#\{m:p\leq m\leq p^2,\ m\mid n\}.
\]

Since (D\cap C=\varnothing), summing (7) gives

\[
\boxed{
\sum_{m=p}^{p^2}\sum_qX_m(q)
=\sum_{d\in D}\sum_{c\in C}\tau_{[p,p^2]}(|d-c|).}      \tag{14}
\]

More generally, for any weight (w(m)), the weighted left side equals

\[
\sum_{d,c}\sum_{\substack{p\leq m\leq p^2\\m\mid d-c}}w(m).
\tag{15}
\]

These are exact divisor transforms of already nonzero label differences.
They contain no preference for the absent layer (q=0).

If (Lambda=D\mathbin{\dot\cup}C), then the full residue collision count

\[
E_m=\sum_r\binom{|\Lambda\cap(r+m\mathbb Z)|}{2}
\]

satisfies

\[
E_m\geq p^2-m\qquad(m\leq p^2),                           \tag{16}
\]

and

\[
\sum_{m=p}^{p^2}E_m
=\sum_{\{x,y\}\subset\Lambda}\tau_{[p,p^2]}(|x-y|).      \tag{17}
\]

Equations (16)--(17) hold for every (p^2)-element set of distinct integer
labels.  Thus the strongest universal total-colour residue packing still
forgets that the labels come from one ruler and cannot yield the coefficient
(3) without additional phase information.

## 4. Equivalent center-layer statement

Let (Y\subset[0,W]) be the unreversed lower ruler, with (0\in Y), and
let the center be (L>2W).  The same validity condition is

\[
Y\text{ is Sidon},\qquad L\notin3Y-Y.                     \tag{18}
\]

For (L=r_m+q_m m), (0\leq r_m<m), put

\[
T_m(q)=\#\{(a,b,c,d)\in Y^4:a+b+c-d=r_m+qm\}.            \tag{19}
\]

The point residue histogram determines only

\[
\sum_qT_m(q)
=(N_m*N_m*N_m*\widetilde N_m)(r_m),                       \tag{20}
\]

whereas (18) removes the specified layer

\[
\boxed{T_m(q_m)=0.}                                      \tag{21}
\]

At (m=L), the range

\[
-W<a+b+c-d<3W<3L/2
\]

shows that all center-congruence solutions lie in the exact-zero layer; the
(L)-layer is absent.  The zero-layer solutions need not be trivial.  The
five-point witness below has 20, not (3p-2=13).  Hence (Y) is not a
4-independent cyclic set, and importing a 4-independence bound would be
invalid.

## 5. Subcritical single-modulus phase twin

Take

\[
p=5,\quad G=3,\quad W=22,\quad L=47<3p^2=75,\quad m=9.
\]

The two integer Sidon rulers

\[
Z_{\rm good}=\{0,2,8,18,22\},\qquad
Z_{\rm bad}=\{0,2,8,9,22\}                               \tag{22}
\]

have identical point, difference-label, and shifted-sum-label residue
histograms modulo (9).  Therefore they also have identical aggregate
internal and cross wrap counts.  The good ruler has

\[
D_{\rm good}\cap C_{\rm good}=\varnothing,
\]

while the bad ruler has

\[
D_{\rm bad}\cap C_{\rm bad}=\{7,13,14,20\}.              \tag{23}
\]

Their quotient distributions are

\[
X_9^{\rm good}:\{-5:1,-3:4,-1:7,1:4\},                  \tag{24}
\]

\[
X_9^{\rm bad}:\{-5:1,-3:3,-2:4,-1:1,0:4,1:3\}.          \tag{25}
\]

Despite the four forbidden zero-layer collisions in (25),

\[
\boxed{
\sum_q q^jX_9^{\rm good}(q)
=\sum_q q^jX_9^{\rm bad}(q)
\quad(0\leq j\leq3),}                                   \tag{26}
\]

with common values

\[
(16,-20,72,-236).                                         \tag{27}
\]

Thus the failure occurs inside the target's subcritical region, not merely
for a very long ruler.

There is also an abstract all-orders obstruction.  For every fixed (K),
partition (0,1,\ldots,2^{K+1}-1) according to the parity of the binary
digit sum.  If the even and odd parts are (P_K,Q_K), then

\[
0\in P_K,\qquad0\notin Q_K,
\]

but

\[
\sum_{q\in P_K}q^j=\sum_{q\in Q_K}q^j\quad(0\leq j\leq K).
\tag{28}
\]

Indeed,

\[
\sum_n(-1)^{s_2(n)}e^{nt}
=\prod_{i=0}^{K}(1-e^{2^it})
\]

has a zero of order (K+1) at (t=0).  Hence no fixed finite list of
quotient power moments can identify an atom at zero in an abstract layer
model.  Equations (22)--(27) realize this obstruction inside genuine
subcritical Sidon rulers through degree three.

## 6. Subcritical all-moduli average twin

Take

\[
p=5,\quad G=6,\quad W=27,\quad L=60<75.
\]

The rulers

\[
Z_{\rm good}=\{0,14,24,25,27\},\qquad
Z_{\rm bad}=\{0,4,5,13,27\}                              \tag{29}
\]

are Sidon.  The first is valid; the second has

\[
D_{\rm bad}\cap C_{\rm bad}=\{14,23\}.                  \tag{30}
\]

For (A_m(Z)=\sum_qX_m(q)), exact enumeration over every
(5\leq m\leq25) nevertheless gives

\[
\boxed{
\sum_{m=5}^{25}m^jA_m(Z_{\rm good})
=\sum_{m=5}^{25}m^jA_m(Z_{\rm bad})
\quad(j=0,1,2),}                                         \tag{31}
\]

with common values

\[
(232,2718,39570).                                         \tag{32}
\]

So unweighted, linear-weighted, and quadratic-weighted averaged-modulus
collision totals do not distinguish validity even under (L<3p^2).  The
individual modulus vectors differ; an across-modulus theorem may still use
that coherent vector rather than only finitely many averages.

## 7. Audit on the supplied witnesses

Every identity above was checked with exact integers for every modulus
(p\leq m\leq p^2) on the five supplied witnesses.  Here “cross” is
(\sum_m\sum_qX_m(q)), “self” is the summed right side of (12), and
(T_L(0)) is the exact-zero center-layer count.

\[
\begin{array}{c|c|c|c|c|c|c}
p&L&W&G&\text{cross}&\text{self}&T_L(0)\\ \hline
5&30&12&6&223&20&20\\
9&116&49&18&3332&88&44\\
10&152&55&42&5655&172&58\\
11&191&84&23&8101&52&67\\
12&238&107&24&12100&234&69
\end{array}                                               \tag{33}
\]

The self-fibre contribution can be far below the whole cross average
(notably (52/8101) at (p=11)), so (12) cannot be promoted to an
asymptotic equality without a new argument.

Reproduction commands:

```text
python problems/864/compute/p16/residue_phase_audit.py
python problems/864/compute/p16/verify_p16.py
python problems/864/compute/p16/find_moment_collision.py \
  --p 5 --max-width 35 --max-gap 5 --degree 3
python problems/864/compute/p16/find_average_collision.py \
  --p 5 --max-width 35 --max-gap 20 --degree 2 --subcritical
```

The independent verifier checks (3)--(5), (7)--(14), (18)--(21), both
twins, and the Prouhet identity through degree ten.  It uses no
floating-point arithmetic.

## 8. Corrected frontier

A successful residue proof must distinguish (24) from (25), and the two
vectors underlying (31), using coherent same-ruler information.  The
smallest visible coherence is the indexed-star translation

\[
\{G+z_i+z_j:j>i\}
\equiv\{z_j-z_i:j>i\}+(G+2z_i)\pmod m.                   \tag{34}
\]

The precise surviving target is therefore:

> Under (L\leq(3-\varepsilon)p^2), prove that the permitted nonzero
> quotient layers cannot absorb all congruent pairs in (7), using the same
> indexed stars coherently for many moduli.

Any argument using only (n_m,d_m,c_m), aggregate collision counts, a fixed
number of quotient moments, or a fixed number of polynomial averages over
the moduli is ruled out at the indicated level by the exact subcritical
twins.  The complete quotient vectors or an equivalent phase-sensitive
state remain viable, but no inequality forcing the missing zero layer was
obtained here.
