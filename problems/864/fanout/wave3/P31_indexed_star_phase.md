# P31: indexed-star phase across moduli

## Verdict

For

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\},\qquad G>0,
\]

write

\[
 D=\{z_j-z_i:i<j\},\qquad
 C_i=\{G+z_i+z_j:i\leq j<p\}.
\]

This note proves an indexed, phase-sensitive sandwich for the cross-colour
congruence load. It retains the lower endpoint index \(i\), the relative
position of the residue supports, and all moduli simultaneously. For every
modulus \(m\), its central term is

\[
 H_{m,i}
 =|\operatorname{supp}(D\bmod m)
   \cap\operatorname{supp}(C_i\bmod m)|.
\]

Under \(D\cap\bigcup_i C_i=\varnothing\), every such shared residue must be
covered by a nonzero integer wrap. The resulting weighted divisor-cover
inequality is exact and is not a restatement of the forbidden zero layer.

The weaker attempt that keeps only the two indexed support cardinalities is
dead. There is an exact strict-subcritical twin at

\[
 p=4,\qquad G=2,\qquad W=20,\qquad L=42<3p^2=48:
\]

\[
 Z_+=\{0,3,19,20\},\qquad Z_-=\{0,1,17,20\}=20-Z_+.
\]

Both are Sidon and have the same positive-difference set. For every
\(4\leq m\leq16\) and every index \(i\), they have the same cardinalities
\(|D\bmod m|\) and \(|C_i\bmod m|\). Nevertheless \(Z_+\) is valid and
\(Z_-\) has three difference/sum collisions. Thus indexing stars without
retaining their translated support phase does not repair the P16 marginal
residue loss.

The relative-support vector \(H_{m,i}\) distinguishes this twin. An exact
search found no valid/invalid equal-span twin preserving all \(H_{m,i}\) on
390,396 strict-subcritical candidates with \(p=4,5\), \(W\leq35\), and
\(G\leq35\). This is a finite gate, not an asymptotic theorem. The
remaining obstruction is precise: the proved lower load still fits inside
the available nonzero wrap capacity on every known witness. A completion
requires a coherent across-modulus lower bound on \(H_{m,i}\) or its
multiplicity refinement, not another bound on support sizes.

## 1. Indexed stars

Put

\[
 e_i=G+2z_i,\qquad
 D_i=\{z_j-z_i:i<j<p\}.
\]

Then the off-diagonal part of the \(i\)-th shifted-sum star is an exact
translate:

\[
 \boxed{C_i=\{e_i\}\mathbin{\dot\cup}(e_i+D_i).}          \tag{1}
\]

The \(C_i\) partition \(C=G+S(Z)\), while the \(D_i\) partition \(D\).
There is also an upper-index form. For \(i<j\), set

\[
 d_{ij}=z_j-z_i,\qquad c_{ij}=G+z_i+z_j.
\]

Then

\[
 \boxed{c_{ij}-d_{ij}=e_i,\qquad c_{ij}+d_{ij}=e_j.}     \tag{2}
\]

Thus each edge retains both endpoint labels. Equation (1), rather than a
global residue histogram, is the phase datum used below.

## 2. Indexed relative-support lemma

For a modulus \(m\geq1\) and \(r\in\mathbb Z/m\mathbb Z\), define

\[
 d_m(r)=|\{d\in D:d\equiv r\pmod m\}|,
\]

\[
 c_{m,i}(r)=|\{c\in C_i:c\equiv r\pmod m\}|.
\]

Let

\[
 A_m=\operatorname{supp}d_m,\qquad
 B_{m,i}=\operatorname{supp}c_{m,i},
\]

\[
 a_m=|A_m|,\qquad b_{m,i}=|B_{m,i}|,\qquad
 H_{m,i}=|A_m\cap B_{m,i}|,
\]

and let the multiplicity-sensitive cross load be

\[
 K_{m,i}=\sum_{r\bmod m}d_m(r)c_{m,i}(r).                \tag{3}
\]

For \(c>0\), write \(\rho_m(c)\in\{1,\ldots,m\}\) for its least positive
residue, and put

\[
 u_m(c)=
 \left(1+\left\lfloor{W-\rho_m(c)\over m}\right\rfloor\right)_+
 -\mathbf 1_{c\leq W},                                  \tag{4}
\]

\[
 U_{m,i}=\sum_{c\in C_i}u_m(c).                          \tag{5}
\]

**Lemma IS1 (indexed support and nonzero-wrap capacity).** If \(Z\) is
Sidon and \(D\cap C=\varnothing\), then for every \(m\) and \(i\),

\[
 \boxed{
 (a_m+b_{m,i}-m)_+
 \leq H_{m,i}
 \leq K_{m,i}
 \leq U_{m,i}.}                                         \tag{6}
\]

Moreover, for any finite set of moduli \(\mathcal M\) and nonnegative
weights \(w_{m,i}\),

\[
 \boxed{
 \sum_{m\in\mathcal M}\sum_i w_{m,i}H_{m,i}
 \leq
 \sum_i\sum_{d\in D}\sum_{c\in C_i}
 \sum_{\substack{m\in\mathcal M\\m\mid d-c}}w_{m,i}.}   \tag{7}
\]

All divisors on the right of (7) divide a nonzero integer.

### Proof

Support inclusion-exclusion in the \(m\) residue classes gives

\[
 |A_m\cap B_{m,i}|\geq a_m+b_{m,i}-m.
\]

Every residue in the intersection has \(d_m(r)\geq1\) and
\(c_{m,i}(r)\geq1\), proving the first two inequalities in (6).

Expanding (3) gives the exact labelled identity

\[
 K_{m,i}
 =|\{(d,c)\in D\times C_i:m\mid d-c\}|.                 \tag{8}
\]

Validity makes \(d-c\ne0\). For fixed \(c\), all possible \(d\)'s lie in
\([1,W]\), are congruent to \(c\) modulo \(m\), and cannot equal \(c\).
The number of integers with those three properties is exactly (4).
Since \(D\) is a set, summing over \(c\in C_i\) proves \(K_{m,i}\leq
U_{m,i}\).

Finally, multiply \(H_{m,i}\leq K_{m,i}\) by \(w_{m,i}\), use (8), and
exchange the finite sums. This proves (7). QED.

The point of (7) is its coherence: one pair \((d,c)\) can cover only the
moduli dividing its one fixed nonzero difference. The support-size lower
bound in (6) does not retain this divisor assignment; \(H_{m,i}\) does.

## 3. Why indexed support sizes still erase phase

There is an exact identity

\[
 \boxed{
 b_{m,i}
 =|\{z_i,z_{i+1},\ldots,z_{p-1}\}\bmod m|.}             \tag{9}
\]

Indeed,

\[
 C_i=(G+z_i)+\{z_i,z_{i+1},\ldots,z_{p-1}\},
\]

and translation does not change support cardinality. Similarly, for the
off-diagonal star,

\[
 |\,(C_i\setminus\{e_i\})\bmod m\,|
 =|\{z_{i+1},\ldots,z_{p-1}\}\bmod m|.                  \tag{10}
\]

Thus \(b_{m,i}\) remembers the index and the tail occupation, but it erases
the translation \(G+z_i\). In contrast, \(H_{m,i}\) compares the translated
tail with \(D\bmod m\) and therefore retains relative phase.

## 4. Exact strict-subcritical support twin

Take \(p=4,G=2,W=20,L=42\) and

\[
 Z_+=\{0,3,19,20\},\qquad Z_-=\{0,1,17,20\}.            \tag{11}
\]

Both rulers have the same six distinct positive differences,

\[
 D_+=D_-=\{1,3,16,17,19,20\},                           \tag{12}
\]

so both are Sidon, including diagonal sums. Their shifted-sum stars are

\[
 \begin{array}{c|c|c}
 i&C_i(Z_+)&C_i(Z_-)\\ \hline
 0&\{2,5,21,22\}&\{2,3,19,22\}\\
 1&\{8,24,25\}&\{4,20,23\}\\
 2&\{40,41\}&\{36,39\}\\
 3&\{42\}&\{42\}.
 \end{array}                                             \tag{13}
\]

Consequently,

\[
 D_+\cap C(Z_+)=\varnothing,                             \tag{14}
\]

whereas

\[
 D_-\cap C(Z_-)=\{3,19,20\}.                            \tag{15}
\]

Equivalently,

\[
 E_+=2+2Z_+=\{2,8,40,42\}
\]

is same-parity Sidon with \(E_+\cap3E_+=\varnothing\), while

\[
 E_-=2+2Z_-=\{2,4,36,42\},\qquad
 42=2+4+36.                                             \tag{16}
\]

For completeness, the common vector
\((a_m,b_{m,0},b_{m,1},b_{m,2},b_{m,3})\) is

\[
\begin{array}{c|c@{\qquad}c|c}
m&\text{common vector}&m&\text{common vector}\\ \hline
4 &(3,2,2,2,1)&11&(6,4,3,2,1)\\
5 &(5,3,3,2,1)&12&(6,4,3,2,1)\\
6 &(5,4,3,2,1)&13&(5,4,3,2,1)\\
7 &(5,4,3,2,1)&14&(5,4,3,2,1)\\
8 &(4,3,2,2,1)&15&(5,4,3,2,1)\\
9 &(5,4,3,2,1)&16&(4,3,2,2,1)\\
10&(6,3,3,2,1)&&
\end{array}                                              \tag{17}
\]

Thus every inequality formed from all indexed cardinalities
\(a_m,b_{m,i}\), even using the full vector over \(4\leq m\leq16\), has
the same input on a valid and an invalid ruler of the same \(p,G,W,L\).
This is an exact falsifier, not an asymptotic comparison.

Relative phase sees the difference. At \(m=6\),

\[
 (H_{6,0},H_{6,1},H_{6,2},H_{6,3})(Z_+)=(4,2,2,0),
\]

\[
 (H_{6,0},H_{6,1},H_{6,2},H_{6,3})(Z_-)=(4,3,1,0).     \tag{18}
\]

## 5. Quantitative audit and precise obstruction

Summing (6) over \(p\leq m\leq p^2\), write

\[
 \mathrm{LB}=\sum_{m,i}(a_m+b_{m,i}-m)_+,\quad
 \mathrm{H}=\sum_{m,i}H_{m,i},
\]

\[
 \mathrm{K}=\sum_{m,i}K_{m,i},\quad
 \mathrm{U}=\sum_{m,i}U_{m,i}.
\]

Exact audits on three stored valid witnesses give

\[
\begin{array}{c|c|c|c|c|c|c|c}
p&W&G&L&\mathrm{LB}&\mathrm H&\mathrm K&\mathrm U\\ \hline
5&12&6&30&72&178&223&267\\
9&49&18&116&706&2092&3332&4448\\
11&84&23&191&1558&4783&8101&12276
\end{array}                                              \tag{19}
\]

Thus retaining relative supports recovers a substantial part of the erased
phase, but the valid witnesses still have strict room

\[
 \mathrm H<\mathrm K<\mathrm U.                         \tag{20}
\]

The exact remaining task in this lane is now narrower than P16's quotient
atom statement:

> Under \(L\leq(3-\varepsilon)p^2\), lower-bound a weighted version of
> \(\sum H_{m,i}\), or of \(\sum K_{m,i}\), beyond the weighted nonzero
> divisor capacity in (7), using the common indexed translations (1).

This is not equivalent to declaring the zero quotient layer empty or
nonempty. It asks for an inequality between an observable relative-support
load and a nonzero-divisor cover. What is presently missing is a
same-ruler coherence bound on that cover. Treating the \(C_i\) independently
reduces (7) to \(K_{m,i}\leq U_{m,i}\), and (19) proves that this independent
capacity has enough room on every audited witness. Therefore no
coefficient-three conclusion follows from Lemma IS1 alone.

## 6. Reproduction

All computations use exact integers.

~~~text
python problems/864/compute/p31/search_support_twins.py \
  --p-min 4 --p-max 5 --max-width 35 --max-gap 35 \
  --output problems/864/compute/p31/support_twins_p4_p5.json

python problems/864/compute/p31/search_intersection_twins.py \
  --p-min 4 --p-max 5 --max-width 35 --max-gap 35 \
  --output problems/864/compute/p31/intersection_twins_p4_p5.json

python problems/864/compute/p31/search_indexed_twins.py \
  --p-min 4 --p-max 5 --max-width 35 --max-gap 35 \
  --output problems/864/compute/p31/indexed_twins_p4_p5.json

python problems/864/compute/p31/audit_indexed_phase.py
python problems/864/compute/p31/verify_p31.py
~~~

The support search found both an off-diagonal and a full-star twin. The
relative-support and multiplicity-sensitive searches each exhausted 28,160
Sidon rulers and 390,396 strict-subcritical \((Z,G)\) candidates without an
equal-span valid/invalid twin. These negative finite searches are reported
only as gates; Lemma IS1 and the twin (11)--(18) are the proved statements.
