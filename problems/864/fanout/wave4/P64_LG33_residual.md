# P64: the LG33 residual already contains the sharp reflected-center theorem

## Verdict

No counterexample to the prescribed-scale P50 residual was found.  More
importantly, the remaining inequality is not a routine short-gap estimate.
On a separated reflected Sidon set it has the exact form in Theorem 2 below.
For asymptotically dense Sidon halves, that form forces the sharp
coefficient-three lower bound for the reflection center.  Thus a general
proof of the P50 residual would already prove the central unresolved
integer-carry statement on the principal reflected class.

This is a rigorous obstruction, not a finite-survival claim.  The exact
identity is proved below.  Its asymptotic consequence uses an elementary
sliding-window proof that dense Sidon rulers have maximal mesoscopic
short-difference weight.

An initially attractive strengthening,

\[
 \rho_H\le N(8S_H+A_H^{\rm dup}),                    \tag{1}
\]

where \(A_H^{\rm dup}\) is the weighted contribution of adjacent edges
whose difference is duplicated, survived the required exact audits.  It
does not simplify the hard case: on every separated reflected set,
\(A_H^{\rm dup}=S_H\), so (1) is exactly the original
\(\rho_H\le9NS_H\).  A still stronger version counting each touched
duplicate label only once is false on the stored \(N=4925\) witness.

## 1. P50 notation

Let

\[
 A=\{a_1<\cdots<a_k\}\subseteq[0,N-1],
 \qquad H=\lceil N^{2/3}\rceil .
\]

For \(d>0\), let \(\nu_A(d)\) be its positive-difference multiplicity and
put

\[
 \begin{aligned}
 D_H&=\sum_{\substack{d<H\\\nu_A(d)=2}}(H-d),
 &Q_H&=\sum_{\substack{d<H\\\nu_A(d)=0}}(H-d),\\
 Z_H&=D_H-Q_H,
 &M_H&=\left|A+[0,H-1]\right|,\\
 G_H&=N+H-1-M_H,
 &S_H&=kH-M_H.
 \end{aligned}
\]

P50 defines

\[
 E_H^\sharp=
 9N(N-1)-3H^3+12H^2+(12H^2-9N)G_H                 \tag{2}
\]

and

\[
 \rho_H=8NZ_H-E_H^\sharp.                            \tag{3}
\]

Its exact envelope identity says that, when \(\rho_H>0\), LG33 is
equivalent to

\[
                         \rho_H\le9NS_H.              \tag{4}
\]

## 2. Reflected Sidon specialization

Let

\[
 B=\{0=b_1<\cdots<b_p=W\}
\]

be Sidon, with diagonal pair sums included.  Write

\[
 \mathcal S(B)=\{b_i+b_j:i\le j\},\qquad
 \Delta(B)=\{b_j-b_i:i<j\}.
\]

Choose an integer center \(c>2W\) satisfying the literal hole condition

\[
                    c\notin\mathcal S(B)+\Delta(B),    \tag{5}
\]

and define

\[
 A=B\mathbin{\dot\cup}(c-B),\qquad N=c+1,
 \qquad \gamma=c-2W.                                  \tag{6}
\]

Condition (5) makes \(A\) admissible.  Indeed, sums internal to either
copy are unique by Sidonicity.  A cross-sum has the form
\(c+b_i-b_j\); all nonzero differences are unique, while the zero
difference gives the exceptional sum \(c\) with \(p\) representations.
A collision between an internal sum and a nonzero cross-sum is exactly an
identity \(c=s+d\) with \(s\in\mathcal S(B)\) and
\(d\in\Delta(B)\), forbidden by (5).  The lower and upper internal sum
ranges are disjoint because \(c>2W\).

Let the internal gaps of \(B\) be \(g_i=b_{i+1}-b_i\), and put

\[
 \mathcal E_H(B)=\sum_i(g_i-H)_+,
 \qquad
 \mathcal D_H(B)=\sum_{\substack{d\in\Delta(B)\\d<H}}(H-d). \tag{7}
\]

### Lemma 1 (separated reflected profiles)

If \(\gamma\ge H\), then

\[
 \boxed{
 \begin{aligned}
 G_H&=\gamma-H+2\mathcal E_H(B),\\
 S_H&=2\bigl((p-1)H-W+\mathcal E_H(B)\bigr),\\
 Z_H&=2\mathcal D_H(B)-\binom H2.
 \end{aligned}}                                       \tag{8}
\]

Moreover every short adjacent edge has a duplicated difference, and hence

\[
                         A_H^{\rm dup}=S_H.             \tag{9}
\]

#### Proof

The thickening of one copy of \(B\) has size

\[
 H+\sum_i\min(g_i,H)=W+H-\mathcal E_H(B).
\]

The two thickenings are separated when \(\gamma\ge H\).  Subtracting
twice the displayed size from the ambient length \(c+H\) proves the first
line of (8).  The support-defect identity gives the second line.

Every cross difference is \(c-b_i-b_j\ge c-2W=\gamma\), so no cross
difference is below \(H\).  Each difference of \(B\) occurs once in each
reflected copy and every other label below \(H\) is missing.  Therefore

\[
 Z_H=\mathcal D_H(B)-
 \left(\binom H2-\mathcal D_H(B)\right),
\]

which is the last line of (8).  Finally, every short internal adjacent gap
appears in both reflected copies and has difference multiplicity two; the
central gap is not short.  This proves (9).  QED.

### Theorem 2 (exact reflected LG33 identity)

Under the hypotheses of Lemma 1, the LG33 slack is exactly

\[
\boxed{
\begin{aligned}
 \operatorname{RHS}(\mathrm{LG33})-8NZ_H
={}&-16N\mathcal D_H(B)-15H^3+4NH^2\\
 &+12H^2\gamma+24H^2\mathcal E_H(B)+12H^2\\
 &+18HNp-13HN .
\end{aligned}}                                         \tag{10}
\]

Consequently LG33 implies the exact finite lower bound

\[
\boxed{
 \frac{\gamma+2\mathcal E_H(B)}N
 \ge
 \frac43\frac{\mathcal D_H(B)}{H^2}
 +\frac54\frac HN-\frac13-\frac1N
 -\frac32\frac pH+\frac{13}{12H}.}                    \tag{11}
\]

#### Proof

Substitute (8) and \(k=2p\) into

\[
12H^2G_H-3H^3+12H^2+9N(k-1)H-8NZ_H.
\]

Collecting terms gives (10).  Moving all terms except
\(12H^2(\gamma+2\mathcal E_H(B))\) to the other side and dividing by
\(12H^2N\) gives (11).  QED.

Equation (9) also proves that the candidate (1) is identical to (4) on
this class.  It is therefore not a route around Theorem 2.

## 3. Dense-ruler barrier

The short-difference term in (11) is asymptotically maximal for every
asymptotically optimal Sidon ruler; this does not require an external
equidistribution theorem.

### Lemma 3 (sliding-window short differences)

For every Sidon \(B\subseteq[0,W]\) of size \(p\),

\[
\boxed{
 \frac12\left(\frac{p^2H^2}{W+H}-pH\right)
 \le\mathcal D_H(B)\le\frac{H(H-1)}2.}                 \tag{12}
\]

#### Proof

For \(0\le y\le W+H-1\), let

\[
 q_y=|B\cap[y-H+1,y]|.
\]

Each mark lies in exactly \(H\) of these windows, so
\(\sum_yq_y=pH\).  A pair at distance \(d<H\) lies in exactly
\(H-d\) windows.  Hence

\[
 \sum_y\binom{q_y}{2}=\mathcal D_H(B).
\]

Cauchy--Schwarz over the \(W+H\) windows gives the lower bound in (12).
The positive differences of a Sidon set are distinct, so at most one can
occupy each label \(1,\ldots,H-1\); summing the available triangular
weights gives the upper bound.  QED.

### Corollary 4 (coefficient-three barrier)

Consider a sequence of data from (5)-(7) with

\[
 p\to\infty,qquad W=(1+o(1))p^2,qquad c=O(W),
 \qquad \gamma\ge H,qquad \mathcal E_H(B)=o(N),        \tag{13}
\]

where \(N=c+1\) and \(H=\lceil N^{2/3}\rceil\).  If LG33 holds along
this sequence, then

\[
                         c\ge(3-o(1))p^2.               \tag{14}
\]

#### Proof

From (13), \(N=\Theta(W)\), so

\[
 H/W\to0,\qquad p/H\to0,qquad H/N\to0.
\]

Lemma 3 and \(W=(1+o(1))p^2\) give

\[
                 \mathcal D_H(B)/H^2\to1/2.
\]

Thus (11), together with \(\mathcal E_H(B)=o(N)\), gives

\[
                         \gamma/N\ge1/3-o(1).           \tag{15}
\]

Since \(N=2W+\gamma+1\), equation (15) implies
\(\gamma\ge W-o(W)\).  Therefore

\[
 c=2W+\gamma\ge3W-o(W)=(3-o(1))p^2.
\]

This proves (14).  QED.

For the reflected admissible set \(|A|=2p\), (14) is precisely

\[
 |A|\le\left(\frac2{\sqrt3}+o(1)\right)\sqrt N.
\]

Hence proving the P50 residual in general necessarily proves the sharp
reflected-center theorem at least for the dense, unfragmented class (13).
The residual has not reduced that arithmetic barrier to a generic local
gap estimate.

## 4. Exact falsifier to the one-label bridge

Let

\[
 T_H^{\rm touch}=
 \sum_{\substack{d<H,\ \nu_A(d)=2\\
                  \text{some adjacent edge has difference }d}}(H-d),
\]

counting each difference label once.  The stronger proposal

\[
                    \rho_H\le N(8S_H+T_H^{\rm touch}) \tag{16}
\]

is false.  The stored sample `ruzsa-9ab2ac138632` has

\[
\begin{gathered}
 (N,H,p,W,c,\gamma)=(4925,290,46,2127,4924,670),\\
 \mathcal E_H(B)=0,\quad
 \mathcal D_H(B)=39066,\quad
 S_H=A_H^{\rm dup}=21846,\quad
 T_H^{\rm touch}=10923,\\
 \rho_H=914592800.
\end{gathered}
\]

But

\[
 N(8S_H+T_H^{\rm touch})=914528175,
\]

so (16) fails by exactly \(64625\).  The true LG33 rescue is
\(9NS_H=968323950\), leaving exact slack \(53731150\).

## 5. Exact computation

The integer-only verifier is reproduced by

```powershell
python -B problems/864/compute/p64/audit_residual_bridges.py --max-n 24
python -B problems/864/compute/p64/audit_reflected_reduction.py --max-width 18
```

The first command checked all `21,674` endpoint-normalized admissible sets
through `N=24` and all `193` prescribed P20 profiles.  There were `78` and
`151` positive-residual rows respectively.  LG33 and (1) had zero failures;
(16) had the single P20 failure above.

The second command checked all `6,783` literal reflected holes from the
`1,340` endpoint-normalized Sidon rulers through width `18`, the hard P20
sample, and the independent Bose `q=128` sample.  It found no LG33
counterexample.  Formulae (8)-(11) were checked on all `1,837` separated
small rows and on both larger witnesses, for `1,839` exact identity checks.

Generated certificates are

```text
problems/864/compute/p64/audit_results.json
problems/864/compute/p64/reflected_reduction.json
```

These finite checks validate the identities and falsify (16); they are not
used to prove Theorem 2, Lemma 3, or Corollary 4.

## 6. Claim boundary

P64 does **not** prove LG33 and does not give a counterexample to it.  It
proves the exact reflected reduction (10), the finite lower bound (11), and
the coefficient-three barrier (14).  Therefore the P50 residual remains
open, but its obstruction is now explicit: on dense reflected rulers, one
must prove either a center gap of asymptotic size `N/3` or a macroscopic
internal gap defect.  That is the sharp arithmetic content, not an omitted
constant-factor charging argument.
