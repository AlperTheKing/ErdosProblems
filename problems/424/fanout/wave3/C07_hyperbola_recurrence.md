# C07: hyperbola support recursion and divisor-ratio gate

## Verdict

There is an exact scale recursion, but its required collision estimate is
open.  Put

\[
 S=G_0G_2,\qquad Q(X)=|S\cap[1,X]|.
\]

The full closure, not merely the frozen \(\{2,3,5\}\) subsystem, gives

\[
 P(4X)\ge 2Q(X)\ge \frac{2P(X)^2}{E(X)}.                 \tag{1}
\]

More generally, every \(n\in S\) generates an affine family inside \(S\).
Using the 23 certified elements of \(G\) through 100 as multipliers, the
inverse-slope weight of this family is the exact number

\[
 W=\frac{12246282477409697}{11187720423079200}
  =1.094618207668720\ldots>1.                                  \tag{2}
\]

This yields a rigorous positive-density bootstrap if a critical affine-image
collision excess is summable across dyadic scales.  The zero-error version of
that collision bound is already false at \(X=10^3,10^4,10^5\): an exact
replay gives affine energy ratios \(1.35398,1.25037,1.29936\), all larger
than \(W\).  These finite failures do not disprove the summable-excess
version.

For the original hyperbola energy there is also an exact reduced-divisor
identity.  It isolates a second, independent missing inequality: a uniform
bound on simultaneous dilation correlations in the two colors.  The JSON
does not establish this bound.  In fact, its normalized off-diagonal term
increases from \(0.780437\) to \(3.477069\) over the six checkpoints, while
the diagonal term decreases; the near-constant total \(\kappa\) is therefore
not evidence for either term being uniformly bounded.

## 1. Definitions and the first exact recursion

For \(m\ge1\), let

\[
 r(m)=|\{(a,b)\in G_0\times G_2:ab=m\}|,
\]

so that

\[
 P(X)=\sum_{m\le X}r(m),\qquad
 E(X)=\sum_{m\le X}r(m)^2,\qquad
 Q(X)=|\{m\le X:r(m)>0\}|.                                  \tag{3}
\]

Cauchy--Schwarz gives the exact finite inequality

\[
 Q(X)E(X)\ge P(X)^2.                                          \tag{4}
\]

**Lemma 1 (bounded-ratio closure recursion).**  For every integer \(X\ge6\),

\[
 \boxed{P(4X)\ge2Q(X)\ge 2P(X)^2/E(X).}                       \tag{5}
\]

More generally, for every integer \(Y\ge24\),

\[
 P(Y)\ge2Q(\lfloor Y/4\rfloor).                               \tag{6}
\]

**Proof.**  Take \(n\in S\cap[1,X]\).  Some automatically distinct
\(a\in G_0,b\in G_2\) satisfy \(n=ab\), so full closure gives

\[
 x=n-1\in G_2.
\]

Here \(n\ge3\cdot2=6\), hence \(x\ge5\) and \(x\ne2\).  The fixed seed
2 therefore gives

\[
 2x-1=2n-3\in G_0.
\]

Consequently the two colored pairs

\[
 (3,n-1),\qquad (2n-3,2)                                     \tag{7}
\]

are counted by \(P(4X)\); their products are at most \(3X-3\) and
\(4X-6\).  Distinct \(n\)'s give distinct pairs, and the two displayed
families cannot meet because the first has first coordinate 3 and second
coordinate at least 5, whereas the second has second coordinate 2 and first
coordinate at least 9.  This proves the first inequality in (5).  Equation
(4) proves the second.  Replacing \(X\) by \(\lfloor Y/4\rfloor\) proves
(6).  QED.

The same argument with two source cutoffs gives

\[
 P((2U-3)(V-1))\ge Q(U)Q(V)
 \ge\frac{P(U)^2}{E(U)}\frac{P(V)^2}{E(V)},                    \tag{8}
\]

because \(\{2n-3:n\in S\cap[1,U]\}\subset G_0\) and
\(\{m-1:m\in S\cap[1,V]\}\subset G_2\).  Unlike (5), (8) moves to a
squared scale and is less useful for lower density.

## 2. The full support-affine recursion

**Lemma 2 (support maps).**  If \(n\in S\), then

\[
 F_a(n)=a(n-1)\in S\quad(a\in G_0),                            \tag{9}
\]

and

\[
 H_b(n)=b(2n-3)\in S\quad(b\in G_2).                          \tag{10}
\]

**Proof.**  The proof of Lemma 1 gives \(n-1\in G_2\) and
\(2n-3\in G_0\).  Equations (9) and (10) are then products of one element
of each color.  QED.

Fix finite nonempty sets \(A\subset G_0\), \(B\subset G_2\), and define

\[
 W(A,B)=\sum_{a\in A}\frac1a+\sum_{b\in B}\frac1{2b}.         \tag{11}
\]

For \(X\ge1\), let \(R_{A,B;X}(m)\) be the number of labeled edges
\((F_a,n)\) and \((H_b,n)\), with \(n\in S\), whose image is \(m\le X\).
Write

\[
 M_{A,B}(X)=\sum_mR_{A,B;X}(m),\quad
 \mathcal E_{A,B}(X)=\sum_mR_{A,B;X}(m)^2,                     \tag{12}
\]

and let \(U_{A,B}(X)=|\{m:R_{A,B;X}(m)>0\}|\).  Direct inversion of the
affine maps gives the exact parent mass

\[
\begin{split}
 M_{A,B}(X)
  ={}&\sum_{a\in A}Q(\lfloor X/a\rfloor+1)\\
    &+\sum_{b\in B}Q(\lfloor X/(2b)+3/2\rfloor).               \tag{13}
\end{split}
\]

All image points lie in \(S\cap[1,X]\).  Hence

\[
 \boxed{
 Q(X)\ge U_{A,B}(X)
      \ge\frac{M_{A,B}(X)^2}{\mathcal E_{A,B}(X)}.}             \tag{14}
\]

Equivalently, with the exact collision tax

\[
 \Delta_{A,B}(X)=M_{A,B}(X)-U_{A,B}(X),                         \tag{15}
\]

one has \(Q(X)\ge M_{A,B}(X)-\Delta_{A,B}(X)\).

### A precise sufficient collision inequality

**Lemma 3 (critical affine bootstrap).**  Suppose \(W=W(A,B)>1\).  For
\(2^j\le X<2^{j+1}\), let \(\varepsilon_j\ge0\).  Either one of the
following hypotheses, uniformly for every sufficiently large \(X\), implies
\(\liminf_XQ(X)/X>0\):

\[
 \mathcal E_{A,B}(X)\le(W+\varepsilon_j)M_{A,B}(X),
 \qquad \sum_j\varepsilon_j<\infty;                            \tag{AE}
\]

or the weaker direct-overlap bound

\[
 \Delta_{A,B}(X)
 \le\left(1-\frac1W+\varepsilon_j\right)M_{A,B}(X),
 \qquad \sum_j\varepsilon_j<\infty,                           \tag{AC}
\]

where eventually \(W\varepsilon_j<1\).

**Proof.**  Every parent cutoff in (13) is below the current dyadic layer
once \(X\) is large.  Moreover,

\[
 \sum_{a\in A}(\lfloor X/a\rfloor+1)
 +\sum_{b\in B}\lfloor X/(2b)+3/2\rfloor\ge WX.               \tag{16}
\]

If all preceding layers satisfy \(Q(t)\ge c_jt\), then (13) and (16) give
\(M_{A,B}(X)\ge c_jWX\).  Under (AE), equation (14) gives

\[
 Q(X)\ge c_j\frac{W}{W+\varepsilon_j}X.                        \tag{17}
\]

The product of the factors \(W/(W+\varepsilon_j)\) is positive when
\(\sum_j\varepsilon_j<\infty\).  A finite initial range supplies a positive
base constant because \(6\in S\).  This proves the claim under (AE).

Under (AC), equations (15)--(16) instead give

\[
 Q(X)\ge c_j(1-W\varepsilon_j)X,                               \tag{18}
\]

and the corresponding infinite product is again positive.  QED.

Since \(P(X)\ge Q(X)\), either missing inequality would prove
\(P(X)\ge cX\), and \(S-1\subset G_2\) would prove positive lower density
for \(G\).

## 3. Fixed \(\{2,3,5\}\) versus full \(G\)

Using only 2, 3, and 5 as operands in Lemma 2 gives exactly

\[
 F_3(n)=3n-3,\qquad H_2(n)=4n-6,\qquad H_5(n)=10n-15.          \tag{19}
\]

Their exponent-one weight is

\[
 \frac13+\frac14+\frac1{10}=\frac{41}{60}<1.                 \tag{20}
\]

Thus even disjoint images from these three induced support maps do not close
a linear induction.  More strongly, an orbit of finitely many support seeds
under (19) is \(O(X^\sigma)\) for some \(\sigma<1\).  Indeed, by continuity
one can choose \(\sigma<1\) with
\(3^{-\sigma}+4^{-\sigma}+10^{-\sigma}<1\).  For \(n\ge6\), after shifting
by 3, each map in (19) grows \(n-3\) by at least its slope.  Summing
\(\lambda_w^{-\sigma}\) over words then gives the standard convergent
geometric bound.

This statement concerns the support maps (19).  It does not prove that the
frozen \(\{2,3,5\}\) subsystem itself has density zero; that subsystem uses
the maps \(x\mapsto2x-1,3x-1,5x-1\), whose density remains unresolved.

The following 23 values are certified by those frozen maps:

\[
 D_{100}=\{2,3,5,9,14,17,26,27,33,41,44,50,51,53,
 65,69,77,80,81,84,87,98,99\}.                                \tag{21}
\]

For example, after \(5=2\cdot3-1\), the chain uses

\[
\begin{gathered}
9=2\cdot5-1,\ 14=3\cdot5-1,\ 17=2\cdot9-1,\ 26=3\cdot9-1,\
27=2\cdot14-1,\ 33=2\cdot17-1,\ 41=3\cdot14-1,\ 44=5\cdot9-1,\\
50=3\cdot17-1,\ 51=2\cdot26-1,\ 53=2\cdot27-1,\ 65=2\cdot33-1,\\
69=5\cdot14-1,\ 77=3\cdot26-1,\ 80=3\cdot27-1,\ 81=2\cdot41-1,\\
84=5\cdot17-1,\ 87=2\cdot44-1,\ 98=3\cdot33-1,\ 99=2\cdot50-1.
\end{gathered}                                                   \tag{22}
\]

Take

\[
\begin{split}
 A={}&\{3,9,27,33,51,69,81,84,87,99\},\\
 B={}&\{2,5,14,17,26,41,44,50,53,65,77,80,98\}.
\end{split}                                                       \tag{23}
\]

Then (11) is exactly (2).  Although the constants in (23) are already
certified by the frozen subsystem, using every one of them as a multiplier
in (9)--(10) uses the full closure rule.  The load-bearing step
\(n\in G_0G_2\Rightarrow n-1\in G_2\) also uses an arbitrary cross-color
pair and is not a closure rule of the frozen subsystem.

## 4. Exact tests against `result_1e8.json`

### The bounded-ratio recursion

For consecutive decimal checkpoints, monotonicity and Lemma 1 give

\[
 P(10X)\ge P(4X)\ge2Q(X)\ge2\lceil P(X)^2/E(X)\rceil.
\]

Every entry below is exact.

| \(X\) | \(2\lceil P^2/E\rceil\) | \(2Q(X)\) | \(P(10X)\) |
|---:|---:|---:|---:|
| \(10^3\) | 228 | 236 | 1,856 |
| \(10^4\) | 2,848 | 3,182 | 27,214 |
| \(10^5\) | 34,562 | 40,782 | 370,812 |
| \(10^6\) | 383,962 | 478,390 | 4,787,694 |
| \(10^7\) | 3,958,726 | 5,235,768 | 59,668,569 |

Thus (5) passes every comparison available from the JSON.  The slack is
large, so the table gives no asymptotic estimate for (5).

### The 23-map critical collision gate

An exact replay of the accepted ascending divisor recurrence through
\(10^5\) reproduced the JSON triples

\[
 (P,Q,E)=(124,118,136),(1856,1591,2420),(27214,20391,42858).
\]

Applying (9)--(12) with (23) gave:

| \(X\) | \(M\) | \(U\) | \(\Delta=M-U\) | \(\mathcal E\) | \(\mathcal E/M\) | \(\Delta/M\) |
|---:|---:|---:|---:|---:|---:|---:|
| \(10^3\) | 113 | 93 | 20 | 153 | 1.353982300885 | 0.176991150442 |
| \(10^4\) | 1,350 | 1,188 | 162 | 1,688 | 1.250370370370 | 0.120000000000 |
| \(10^5\) | 17,905 | 15,367 | 2,538 | 23,265 | 1.299357721307 | 0.141748115052 |

The critical collision-tax ratio in (AC) with zero excess is

\[
 1-1/W=0.086439460814593\ldots.                                \tag{24}
\]

Hence both zero-excess bounds \(\mathcal E\le WM\) and
\(\Delta\le(1-1/W)M\) are counterexampled at all three tested cutoffs.
The required energy excesses \(\mathcal E/M-W\) are respectively

\[
 0.259364093216,quad0.155752162702,quad0.204739513638.         \tag{25}
\]

This does not counterexample (AE) or (AC), which permit arbitrary finite
initial errors and ask only for a summable tail.

## 5. Exact divisor-ratio identity for the original energy

The original \(E(X)\) has a useful exact parametrization.  For coprime
integers \(1\le u<v\) with \(u\equiv v\pmod3\), define

\[
\begin{split}
 C_{u,v}(X)=\#\{(h,w):{}&\ 3\mid h,\ 3\nmid uvw,\ huv w\le X,\\
 &hu,hv\in G_0,\quad uw,vw\in G_2\}.
\end{split}                                                       \tag{26}
\]

**Lemma 4 (reduced-ratio decomposition).**  For every \(X\),

\[
 \boxed{
 E(X)=P(X)+2
 \sum_{\substack{1\le u<v\\(u,v)=1\\u\equiv v\ (3)}}
 C_{u,v}(X).}                                                    \tag{27}
\]

**Proof.**  Given two representations \(ab=a'b'\), put
\(h=(a,a')\), \(a=hu\), and \(a'=hv\), with \((u,v)=1\).  Equality forces
\(b=vw\), \(b'=uw\) for a unique \(w\).  Since \(b,b'\in G_2\), none of
\(u,v,w\) is divisible by 3 and \(u\equiv v\pmod3\); since
\(a,a'\in G_0\), one has \(3\mid h\).  The case \(u=v\) forces
\(u=v=1\) and contributes exactly \(P(X)\).  The two orders of every
\(u<v\) term give the factor 2.  The construction is reversible.  QED.

At \(X=1000\), the six nontrivial products are exactly

\[
\begin{array}{lll}
402=3\cdot134=201\cdot2,&474=3\cdot158=237\cdot2,&
690=3\cdot230=345\cdot2,\\
726=3\cdot242=363\cdot2,&882=9\cdot98=441\cdot2,&
966=69\cdot14=483\cdot2.
\end{array}                                                       \tag{28}
\]

Each has multiplicity 2, so (27) gives \(E-P=2\cdot6=12\) and
\(E=124+12=136\), exactly the first JSON row.

### Precise remaining divisor-sieve inequality

Once (AE) or (AC) proves \(P(X)\ge cX\), the following single uniform
inequality would prove the requested energy estimate:

\[
 \boxed{
 2\sum_{\substack{1\le u<v\\(u,v)=1\\u\equiv v\ (3)}}
 C_{u,v}(X)
 \le K\frac{P(X)^2}{X}
 \quad\text{for every sufficiently large }X.}                  \tag{DS}
\]

Indeed, \(P(X)\ge cX\) implies
\(P(X)\le c^{-1}P(X)^2/X\), so (27) and (DS) give

\[
 E(X)\le(c^{-1}+K)\frac{P(X)^2}{X}.                            \tag{29}
\]

Condition (DS) is a simultaneous divisor-correlation sieve: it must control
the events \(hu,hv\in G_0\) and \(uw,vw\in G_2\) after summing over every
reduced dilation ratio \(u/v\).  Neither membership of a multiple nor the
closure operation descends to membership of its divisors, so Lemmas 1--3 do
not imply (DS).

The exact JSON decomposition

\[
 \frac{E(X)X}{P(X)^2}
 =\frac{X}{P(X)}+\frac{(E(X)-P(X))X}{P(X)^2}                   \tag{30}
\]

is:

| \(X\) | diagonal \(X/P\) | off-diagonal \((E-P)X/P^2\) | total \(EX/P^2\) |
|---:|---:|---:|---:|
| \(10^3\) | 8.064516129 | 0.780437045 | 8.844953174 |
| \(10^4\) | 5.387931034 | 1.637280767 | 7.025211801 |
| \(10^5\) | 3.674579261 | 2.112336222 | 5.786915483 |
| \(10^6\) | 2.696784354 | 2.512073695 | 5.208858049 |
| \(10^7\) | 2.088688208 | 2.963442937 | 5.052131144 |
| \(10^8\) | 1.675924221 | 3.477068514 | 5.152992735 |

Thus the supplied finite values neither prove nor counterexample (DS).  They
show that the apparent stabilization of total \(\kappa\) comes from a falling
diagonal contribution and a rising off-diagonal contribution.  No finite
extrapolation is used here.

## Frontier

The proved route is now a two-inequality lemma tree:

\[
 \text{summable affine overlap (AE) or (AC)}
 \Longrightarrow Q(X),P(X)\gg X,
\]

followed by

\[
 \text{reduced-ratio sieve (DS)}
 \Longrightarrow E(X)\ll P(X)^2/X.
\]

The first zero-excess affine estimate has exact finite counterexamples.  The
summable affine excess and the full divisor-ratio sieve are the precise
missing inequalities; neither follows from the frozen \(\{2,3,5\}\) affine
subsystem.
