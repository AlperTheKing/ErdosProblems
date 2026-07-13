# P10: decorated signed-ruler gain

## Verdict

The target

\[
 L\geq {3\over4}(2p+u)^2-o(k^2)
\]

is not proved here.  There is, however, an exact decorated cutoff inequality
which simultaneously charges every core shifted-sum label, every residual
difference label, the coupling (22), and the autocorrelation of \(U\).  It is
a genuine extension of the fully reflected cutoff inequality.

There is also an exact obstruction to inserting the core deficit from P09
(11) as an additional residual weight.  That deficit is an upper bound on
the residual autocorrelation-scale term, whereas the cutoff inequality needs
a lower bound.  On P09's seven-point witness the valid cutoff is already an
equality, but the reversed substitution adds \(2/3\) to its left side.

## 1. Exact core and residual label partition

Let \(e\) be the unique repeated sum and put

\[
 C=A\cap(e-A),\qquad U=A\setminus C,\qquad u=|U|,
\]

\[
 B=\{x\in C:2x<e\},\qquad p=|B|,
 \qquad \delta=1_{\{e\ {\rm even},\ e/2\in A\}}.
\]

Thus \(|C|=2p+\delta\).  Write

\[
 x_0<\cdots <x_{p-1}
\]

for \(B\), and, when \(p\geq2\), define

\[
 W=x_{p-1}-x_0,\qquad
 Z=\{x_{p-1}-x:x\in B\}=\{0=z_0<\cdots<z_{p-1}=W\},
\]

\[
 G=e-2x_{p-1}>0.
\]

The distinct positive differences internal to \(C\) split as

\[
 D(Z),\qquad G+S(Z),\qquad
 G/2+Z\quad(\delta=1),                                  \tag{1}
\]

where

\[
 D(Z)=\{z_j-z_i:i<j\},\qquad
 S(Z)=\{z_i+z_j:i\leq j\}.
\]

The three sets in (1) are pairwise disjoint and have respective sizes

\[
 \binom p2,\qquad \binom{p+1}2,\qquad \delta p.          \tag{2}
\]

Indeed, the first family is represented on each reflected side, the second
is the family \(e-x_i-x_j\), and the third consists of the midpoint
distances \(e/2-x_i\).  A collision within or between these families would
give either a second nonexceptional sum or more than the two reflected
representations of a positive difference.  Their total size is therefore
\(p(p+\delta)\), agreeing with P09 (5).

Let

\[
 {\cal R}_U=\{|a-b|:a,b\in A,\ a<b,\ 
                    \{a,b\}\cap U\ne\varnothing\}.       \tag{3}
\]

P09's reflection lemma gives the exact disjointness

\[
 |{\cal R}_U|=(2p+\delta)u+\binom u2,
 \qquad
 {\cal R}_U\cap\bigl(D(Z)\cup(G+S(Z))
             \cup(G/2+Z)\bigr)=\varnothing.              \tag{4}
\]

The last family in (4) is present only when \(\delta=1\).

## 2. Decorated cutoff inequality

For \(1\leq r<p\), set

\[
 V_r=\{z_{i+j}-z_i:1\leq j\leq r,\ 0\leq i<p-j\},
\]

\[
 M_r=|V_r|=rp-{r(r+1)\over2},\qquad
 T_r=\sum_{d\in V_r}d.                                   \tag{5}
\]

For an integer \(h\geq1\), write \(f_h(t)=(h-t)_+\) and define

\[
 \Phi_h=\sum_{0\leq i\leq j<p}f_h(G+z_i+z_j),
\]

\[
 \Theta_h=\sum_{i=0}^{p-1}f_h(G/2+z_i),\qquad
 \Omega_h=\sum_{d\in{\cal R}_U}f_h(d).                   \tag{6}
\]

Here \(\Theta_h\) is used only when \(\delta=1\).

**Lemma 1 (exact decorated cutoff).**  For every \(r,h\),

\[
 \boxed{
 hM_r-\binom h2+\Phi_h+\delta\Theta_h+\Omega_h
 \ \leq\ T_r\ \leq\ \binom{r+1}{2}W.}                   \tag{7}
\]

**Proof.**  Since \(V_r\subseteq D(Z)\), all its labels are distinct.  Hence

\[
 T_r\geq hM_r-\sum_{d\in V_r}f_h(d).                     \tag{8}
\]

The total triangular weight of all positive integer labels below \(h\) is
\(\binom h2\).  Equations (1) and (4) show that the labels counted by
\(\Phi_h\), \(\delta\Theta_h\), and \(\Omega_h\) are mutually disjoint and
are all excluded from \(V_r\).  Therefore

\[
 \sum_{d\in V_r}f_h(d)
 \leq \binom h2-\Phi_h-\delta\Theta_h-\Omega_h.           \tag{9}
\]

This proves the lower bound.  Expanding the selected differences in the
consecutive gaps of \(Z\), a fixed gap is used at most \(j\) times at lag
\(j\).  Summing over \(1\leq j\leq r\) proves the upper bound.  QED.

Thus residual labels do not merely add the unweighted count in P09 (2):
each one removes its exact triangular weight from the core ruler's available
label capacity.

## 3. Charges forced by coupling and by \(U-U\)

The exact residual weight in (7) has two useful lower bounds.  First define

\[
 \Gamma_h=
 \sum_{v\in U}\ \sum_{\substack{x\in B\\x<v<e-x}}
       (2h-(e-2x))_+.                                     \tag{10}
\]

For every summand, P09 (22) gives

\[
 (v-x)+(e-x-v)=e-2x.
\]

Both distances are distinct labels in \({\cal R}_U\), and

\[
 f_h(v-x)+f_h(e-x-v)\geq(2h-(e-2x))_+.                   \tag{11}
\]

Second, put

\[
 Q_h(U)=\sum_{v<w\atop v,w\in U}f_h(w-v),\qquad
 M_h(U)=|U+\{0,\ldots,h-1\}|.
\]

When \(u>0\), the sliding-window identity and Cauchy give

\[
 uh+2Q_h(U)\geq {u^2h^2\over M_h(U)}.
\]

Since \(M_h(U)\leq L+h\),

\[
 Q_h(U)\geq {1\over2}
 \left({u^2h^2\over L+h}-uh\right)_+.                    \tag{12}
\]

For \(u=0\), both sides of (12) are zero.  The labels used in (10) are
\(C-U\) labels, while those in (12) are \(U-U\) labels.  They are disjoint
by (4).  Consequently (7) implies the fully explicit inequality

\[
 \boxed{
 hM_r-\binom h2+\Phi_h+\delta\Theta_h+\Gamma_h
 +{1\over2}\left({u^2h^2\over L+h}-uh\right)_+
 \leq \binom{r+1}{2}W.}                                  \tag{13}
\]

No range separation and no assumption on the size or location of \(U\) is
used in (13).  Residual points outside a reflected interval contribute zero
to (10), as required by the difference form of P09 (22).

## 4. Exact obstruction to charging the core deficit

Put \(c=2p+\delta\), \(k=c+u\), and denote the right side of P09 (11),
after removing its core term, by

\[
 \Delta_h=
 1-{1\over h}+{k\over h}+{2W_h(C,e)\over h^2}
       -{c^2\over M_h(C)}.                                \tag{14}
\]

P09 (11) says

\[
 {u^2\over L+h}\leq\Delta_h.                              \tag{15}
\]

The residual autocorrelation charge in (13), however, needs the left side
of (15) as a lower contribution.  The tempting substitution

\[
 {1\over2}\left(h^2\Delta_h-uh\right)_+                  \tag{16}
\]

for the last term in (13) is false.

Use P09's exact admissible set

\[
 A=\{1,2,4,9,13,30,31\},\qquad e=32.
\]

Then

\[
 B=\{1,2\},\quad C=\{1,2,30,31\},\quad
 U=\{4,9,13\},\quad p=2,\quad u=3,\quad\delta=0,
\]

and \(L=30\).  In the normalization above,

\[
 Z=\{0,1\},\quad W=1,\quad G=28.
\]

Take \(r=1\) and \(h=2\).  Then \(M_r=T_r=W=1\), while every label in
\(G+S(Z)\) and every residual label is at least \(2\).  Also every term in
\(\Gamma_2\) vanishes.  Thus the valid decorated inequality (7) is exactly

\[
 2-1=1\leq1.                                               \tag{17}
\]

On the other hand,

\[
 M_2(C)=6,\qquad W_2(C,e)=1,
\]

so (14) gives

\[
 \Delta_2={1\over2}+{7\over2}+{1\over2}-{16\over6}
          ={11\over6},
 \qquad {u^2\over L+h}={9\over32}.                        \tag{18}
\]

The proposed charge (16) is

\[
 {1\over2}\left(4\cdot{11\over6}-6\right)={2\over3}.
\]

It would change (17) into \(5/3\leq1\).  This is an exact falsifier: the
slack in \(\Delta_h\) need not be occupied by residual labels at cutoff
\(h\).  Hence (11) and (13) may be imposed simultaneously, but their left
sides cannot be added by replacing \(u^2/(L+h)\) with \(\Delta_h\).

## 5. Midpoint, parity, and finite audit

If \(e\) is odd, or if \(e\) is even with \(e/2\notin A\), then
\(\delta=0\) and no \(G/2+Z\) label is present.  If \(e/2\in A\), then
\(e\) and \(G=e-2x_{p-1}\) are even, so every label in \(G/2+Z\) is an
integer.  These \(p\) midpoint-core labels are charged by \(\Theta_h\).
The additional \(u\) distances from \(U\) to \(e/2\) are part of
\({\cal R}_U\), accounting exactly for the \(\delta u\) term in (4); they
are retained in \(\Omega_h\) and merely discarded from the coarser bound
(13).

An exhaustive enumeration of all subsets of \([1,14]\) having exactly one
repeated unordered sum, with diagonals included, found 1,373 sets.  Of
these, 750 contain the exceptional midpoint and 623 do not.  For every set
with \(p\geq2\), every \(1\leq r<p\), and every \(1\leq h\leq L+1\), direct
integer evaluation verified (1)--(7), (10)--(13), and all disjointness and
cardinality claims in (2) and (4), for 8,044 cutoff instances.

The new inequality (13) does not supply the missing gain
\(p^2+pu-u^2/4\).  The exact obstruction (17)--(18) identifies the failed
bridge: P09 (11) controls how large the residual term may be from above,
while a weighted packing proof needs a lower relation tying the core deficit
to actual low residual labels.
