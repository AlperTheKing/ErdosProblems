# P69: width-compensated curvature as a carry/Fourier dichotomy

## Verdict

The positive curvature defect

\[
 {\cal E}=3p^2-(G+2W)
\]

does not admit the first natural finite repair
\({\cal E}_+\leq2p^{3/2}\).  The exact P69 audit finds 2,145 failures among
6,852 valid pairs.  The clean Singer hole from P58 has

\[
 p=14,\quad (G,W)=(67,149),\quad {\cal E}=223,
 \qquad 223^2>4\cdot14^3.
\]

Local smoothing is also unavailable.  The P68 pair

\[
 Z=\{0,24,26,29,30\},\qquad G=7
\]

has a literal hole at every shift from 7 through 23.

There is, however, an exact global obstruction.  A positive
width-compensated defect forces either many modular folds of the two sparse
atom sets or a large nonzero Fourier coefficient of their four-point
incidence function.  Quantitatively, if \({\cal E}\geq\varepsilon p^2\),
then either the fold count is at least \(\varepsilon p^2/8\), or a nonzero
four-point coefficient is at least

\[
              {\varepsilon p^2\over256(2+H_{\lfloor h/2\rfloor})^5}.
\]

Thus a countersequence in the width-subcritical band must carry a genuinely
quadratic modular-fold obstruction or an almost-quadratic fourth-order
Fourier spike.  This is a proved reduction, not a proof of
\({\cal E}_+=o(p^2)\).

## 1. Normalization and exact defect

Let

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\}
\]

be Sidon, with diagonal sums included, and suppose

\[
 D^+(Z)\cap(G+S(Z))=\varnothing.                         \tag{1}
\]

We work in the only difficult range \(1\leq G<W\).  When \(G\geq W\),
the ordinary interval Sidon bound already gives
\(G+2W\geq3W=(3-o(1))p^2\).

Here \(S(Z)=\{z_i+z_j:i\leq j\}\).  Choose

\[
 b=\begin{cases}1,&G\text{ odd},\\2,&G\text{ even},\end{cases}
 \qquad \gamma={G-b\over2},\qquad h=\gamma+W+1,
 \qquad B=\gamma+Z.                                      \tag{2}
\]

Then \(B\subseteq\{0,\ldots,h-1\}\), and (1) is equivalent to

\[
                         -b\notin3B-B,                   \tag{3}
\]

with all repetitions allowed.  Put

\[
 \delta={3p^2-p+2\over2}-h.
\]

Since \(G+2W=2h+b-2\), there is the exact identity

\[
 \boxed{{\cal E}=3p^2-(G+2W)=2\delta+p-b.}               \tag{4}
\]

This is the width compensation missing from an unconditional inversion-span
bound.

## 2. Sparse atom folds and modular mass

Reduce the two literal support sets modulo \(h\).  Define

\[
 \overline S=\{x+y\pmod h:x,y\in B,\ x\leq y\},
 \qquad
 \overline D=\{x-y\pmod h:x,y\in B\},                  \tag{5}
\]

and their fold losses

\[
 C_S={p(p+1)\over2}-|\overline S|,
 \qquad
 C_D=p(p-1)+1-|\overline D|,
 \qquad C=C_S+C_D.                                      \tag{6}
\]

Integer Sidonicity makes the literal supports in (6) have the displayed
sizes before reduction.  Let

\[
 Q_b(B)=\#\{(x,y,z,w)\in B^4:
                   x+y+z+b\equiv w\pmod h\}.            \tag{7}
\]

### Lemma P69.1 (fold-to-modular-mass)

For every pair satisfying (1),

\[
 \boxed{Q_b(B)\geq\max\{\delta-C,0\}.}                  \tag{8}
\]

Consequently,

\[
 \boxed{{\cal E}\leq2Q_b(B)+2C+p-b.}                    \tag{9}
\]

### Proof

The two subsets

\[
                  \overline S,qquad -b+\overline D
\]

of \(\mathbb Z/h\mathbb Z\) have intersection at least

\[
\begin{aligned}
 |\overline S|+|\overline D|-h
 &= {p(p+1)\over2}+p(p-1)+1-h-C\\
 &=\delta-C.                                             \tag{10}
\end{aligned}
\]

Every residue in the intersection supplies a choice of
\(x,y,z,w\in B\) with
\(x+y+z+b\equiv w\pmod h\).  This proves (8).  Combining (8) with (4)
gives (9).  QED.

Both sparse atom sets are essential in (10).  Dropping either \(C_S\) or
\(C_D\) is invalid; the exact carry audits already contain collision-only
profiles.

## 3. The Fourier forcing lemma

For a function on \((\mathbb Z/h\mathbb Z)^3\), use the unnormalized
Fourier transform

\[
 \widehat F(\xi)=\sum_x F(x)e^{-2\pi i\langle\xi,x\rangle/h}.
\]

Put \(d=h-b\), \(f=1_B\), and define

\[
 {cal G}_d(x,y,z)
 =f(x)f(y)f(z)f(x+y+z-d\pmod h).                         \tag{11}
\]

Then \(\widehat{{\cal G}_d}(0)=Q_b(B)\).  Let

\[
 \Lambda(B,h,b)=
 \max_{\xi\ne0}|\widehat{{\cal G}_d}(\xi)|,
 \qquad
 L_h=2+H_{\lfloor h/2\rfloor}.                          \tag{12}
\]

### Lemma P69.2 (literal-hole Fourier forcing)

Under (3),

\[
 \boxed{
 \Lambda(B,h,b)
 \geq {Q_b(B)\binom{h-b+2}{3}\over4h^3L_h^5}.}          \tag{13}
\]

Equivalently,

\[
 \boxed{
 {\cal E}\leq
 2C+p-b+
 {8h^3L_h^5\over\binom{h-b+2}{3}}\Lambda(B,h,b).}       \tag{14}
\]

### Proof

Let

\[
 T_d=\{(x,y,z)\in\{0,\ldots,h-1\}^3:x+y+z<d\}.         \tag{15}
\]

If \({\cal G}_d(x,y,z)=1\) on \(T_d\), then
\(x+y+z+b<h\), and the fourth element in (11) is literally
\(x+y+z+b\).  This contradicts (3).  Hence

\[
                 \sum_x{\cal G}_d(x)1_{T_d}(x)=0.       \tag{16}
\]

We record the required Fourier-algebra estimate.  A cyclic interval has
normalized Fourier algebra norm at most \(L_h\).  Indeed, the geometric-sum
formula and
\(\sin(\pi r/h)\geq2r/h\) for \(1\leq r\leq h/2\) give the harmonic sum in
(12); the extra 1 makes the bound uniform for even \(h\).

Under the invertible linear change

\[
               (a,c,e)=(x,x+y,x+y+z),                   \tag{17}
\]

the tetrahedron becomes \(0\leq a\leq c\leq e<d\).  Split
\([0,d-1]\) into two consecutive blocks, each of length at most \(h/2\).
The four possible nondecreasing block patterns are

\[
                         000,\quad001,\quad011,\quad111.
\]

Within one block, order is the pullback of a cyclic interval under a
difference map.  Thus the first and last patterns are products of five
interval pullbacks, and the middle two are products of four.  The Fourier
algebra norm is submultiplicative, so

\[
                 \|1_{T_d}\|_A\leq2L_h^5+2L_h^4
                                  \leq4L_h^5.            \tag{18}
\]

Fourier inversion in (16), separating the zero frequency, now gives

\[
 {Q_b(B)|T_d|\over h^3}
 \leq \Lambda(B,h,b)\|1_{T_d}\|_A.                      \tag{19}
\]

Finally,

\[
                         |T_d|=\binom{d+2}{3}.
\]

Equations (18)-(19) prove (13).  Inequalities (8), (4), and (13) give
(14).  QED.

## 4. Quantified obstruction to a countersequence

### Corollary P69.3 (fold-or-Fourier dichotomy)

Let \(\varepsilon>0\), suppose \(p\geq4/\varepsilon\), \(h\geq4\), and

\[
                         {\cal E}\geq\varepsilon p^2.
\]

Then at least one of the following holds:

\[
 \boxed{C_S+C_D\geq{\varepsilon p^2\over8},}            \tag{20}
\]

or

\[
 \boxed{
 \Lambda(B,h,b)\geq
 {\varepsilon p^2\over256L_h^5}.}                       \tag{21}
\]

### Proof

By (4),

\[
 \delta={{\cal E}-p+b\over2}\geq{3\varepsilon p^2\over8}.
\]

If (20) fails, (8) gives \(Q_b(B)\geq\varepsilon p^2/4\).  For
\(b\in\{1,2\}\) and \(h\geq4\),

\[
 {\binom{h-b+2}{3}\over h^3}\geq{1\over16}.
\]

Substitution in (13) proves (21).  QED.

Since \(L_h=O(\log h)\), any countersequence with
\({\cal E}\geq\varepsilon p^2\) and \(h=O(p^2)\) must therefore have

\[
 C_S+C_D=\Omega_\varepsilon(p^2)
 \quad\text{or}\quad
 \Lambda=\Omega_\varepsilon(p^2/\log^5p).               \tag{22}
\]

In particular, the desired conclusion \({\cal E}_+=o(p^2)\) follows on
any family for which

\[
 C_S+C_D=o(p^2),
 \qquad L_h^5\Lambda=o(p^2).                             \tag{23}
\]

The Singer Fourier estimates in P29--P35 fit the second condition and
explain their drift to coefficient 3.  Establishing (23) for arbitrary
dense integer Sidon rulers is still open.

## 5. Exact finite audit and guardrails

The checker is

```text
problems/864/compute/p69/audit_width_compensated.py
```

Run

```powershell
python -m py_compile problems/864/compute/p69/audit_width_compensated.py
python -B problems/864/compute/p69/audit_width_compensated.py --max-width 18
```

It uses integer arithmetic for every decision and rational arithmetic for
reported ratios.  It checks:

1. all 6,783 valid pairs from the endpoint-normalized census through
   width 18;
2. every dangerous shift of the five stored P60 rulers;
3. the doubled Erdos--Turan rulers at
   \(p=3,5,7,11,13,17,19,23\);
4. the P68 long-hole profile; and
5. the clean P58 Singer hole.

There are 6,852 records in total.  Every record verifies (4), (8), (9),
the zero literal tetrahedron count, and the elementary overlap capacity

\[
 |D^+(Z)\cap[G,W]|+|S(Z)\cap[0,W-G]|\leq W-G+1.          \tag{24}
\]

The finite square candidate

\[
                         {\cal E}_+^2\leq4p^3
\]

fails 2,145 times.  The relaxed constant 25 has no failure in this finite
corpus; its largest ratio is

\[
 {29584\over1331}
\]

at the stored \(p=11\) pair.  This is only a finite statistic and is not
promoted to a conjecture.

For the doubled Erdos--Turan guardrails, \({\cal E}<0\) at every tested
parameter, so the one-sided theorem imposes no false span constraint.  For
P68, the 17-shift missing run coexists with \(C_S+C_D=6\), showing why a
neighboring-shift proof cannot replace the global dichotomy.  For P58,
\(C_S=C_D=0\), \(Q_b=222\), and \({\cal E}=223\); this is the finite clean
Fourier-forcing case.

The machine-readable output is

```text
problems/864/compute/p69/audit_results.json
```

The result is deliberately scoped.  P69 proves that the remaining
width-subcritical obstruction is fourth-order (or quadratically folded);
it does not bound either term in (22) for every Sidon ruler and therefore
does not resolve Problem 864.
