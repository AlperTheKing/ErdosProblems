# C10: multi-star criterion and Ford obstruction audit

## Verdict

1. The uniform bounded-side theorem is **true**. It follows from Ford's
   divisor-in-an-interval estimate, including arbitrarily unbalanced
   rectangles. The rectangular multiplication-table estimate in R1 is a
   derived lemma, not a theorem stated verbatim by Ford.
2. The source range needed for the derivation is valid. The precise source is
   Ford, Corollary 2, with \(c=2\), not Corollary 3 alone.
3. The existential multi-star condition is **equivalent** to positive lower
   density of \(G_0G_2\). Given the latter, choose one edge over each distinct
   product; then the overlap parameter is \(L=0\). Thus it is not a weaker
   intermediate theorem for this actual closure.
4. The minimal noncircular repair in the second-moment lane is to forbid
   product-dependent thinning and use the full closure-forced relation in
   fixed product annuli. The exact aggregate condition is stated in Section 4.

## 1. Exact Ford source and range

Let

\[
 H(x,y,z)=\#\{n\le x:\text{ some divisor }d\mid n\text{ satisfies }y<d\le z\}
\]

and put

\[
 \delta=1-\frac{1+\log\log 2}{\log 2},\qquad
 F(t)=(\log(t+3))^\delta(\log\log(t+3))^{3/2}.
\]

The exact result used here is Corollary 2 on journal p. 372 of Kevin Ford,
"The distribution of integers with a divisor in a given interval," *Annals
of Mathematics* 168 (2008), 367-433
([official PDF](https://annals.math.princeton.edu/wp-content/uploads/annals-v168-n2-p01.pdf),
[journal page](https://annals.math.princeton.edu/2008/168-2/p01)). It states
that, for fixed \(c>1\),

\[
 \frac1{c-1}\le y\le\frac{x}{c}
 \quad\Longrightarrow\quad
 H(x,y,cy)\asymp_c
 \frac{x}{(\log Y)^\delta(\log\log Y)^{3/2}},
 \qquad Y=\min(y,x/y)+3.                                      \tag{1}
\]

Ford specifies on journal p. 371 that the constants are absolute unless a
subscript is shown; hence the constants in (1) depend only on \(c\). Taking
\(c=2\) gives one absolute upper constant \(K_F\).

C05's displayed specialization

\[
 H(x,y,2y)\asymp \frac{x}{(\log y)^\delta(\log\log y)^{3/2}}
 \quad(3\le y\le\sqrt x)                                      \tag{2}
\]

is valid: in this range \(Y=y+3\), and replacing \(y+3\) by \(y\) only
changes absolute constants. It is not Ford's exact stated range. Ford's
actual range for \(c=2\) is \(1\le y\le x/2\), with the symmetric parameter
\(\min(y,x/y)+3\). Corollary 3 on journal p. 373 concerns only the square
multiplication table; by itself it does not give uniformity for \(m\le n\).

## 2. Uniform rectangular theorem

For integers \(1\le m\le n\), write

\[
 T(m,n)=\#\{ab:1\le a\le m,\ 1\le b\le n\}.
\]

**Lemma.** Uniformly in \(n\ge m\),

\[
 \frac{T(m,n)}{mn}\longrightarrow0\qquad(m\to\infty).          \tag{3}
\]

More precisely, for all sufficiently large \(m\),

\[
 T(m,n)\le
 \left(\frac{2}{\sqrt m}+\frac{2K_F}{F(\sqrt m)}\right)mn.      \tag{4}
\]

**Proof.** Put \(s=\sqrt m\). For every \(j\ge0\) such that

\[
 y_j=\frac{m}{2^{j+1}}\ge s,
\]

consider factors \(a\in(y_j,2y_j]\). Their products with \(b\le n\) are at
most

\[
 x_j=2y_jn=\frac{mn}{2^j}
\]

and have a divisor in \((y_j,2y_j]\). The exact hypotheses of (1) hold:

\[
 1\le y_j\le x_j/2,\qquad
 \min(y_j,x_j/y_j)+3=\min(y_j,2n)+3=y_j+3.                    \tag{5}
\]

Therefore this block contributes at most \(K_Fx_j/F(y_j)\), and this is at
most \(K_Fx_j/F(s)\). The selected dyadic blocks cover every \(a>2s\);
the remaining factors give at most \(2sn\) distinct products. Since
\(\sum_{j\ge0}x_j<2mn\), (4) follows. Both terms in its parenthesis tend to
zero, proving (3). Notice that no upper bound on \(n/m\) was used. QED.

Since \(F(\sqrt m)\asymp F(m)\), (4) also proves R1's asserted form

\[
 T(m,n)\le K_0\frac{mn}{(\log m)^\delta(\log\log m)^{3/2}}
 \quad(n\ge m\ge m_0)                                         \tag{6}
\]

after choosing absolute \(K_0,m_0\). These constants exist, but Ford's
corollary does not print numerical values for them. Consequently R1's
formula for \(B(c,C)\) is valid only symbolically after \(K_0,m_0\) have
been defined from this derivation; it is not a numerical explicit bound
supplied by the citation.

**Cartesian reservoir theorem.** Fix \(c,C>0\). Let
\(U,V\subset\mathbb N\) be finite and nonempty, set \(P=|U||V|\), and
suppose

\[
 uv\le X\quad(u\in U,v\in V),\qquad P\ge cX,\qquad
 E_\times(U,V)\le CP.                                         \tag{7}
\]

Then

\[
 \min(\max U,\max V)\le B(c,C)                                \tag{8}
\]

for a constant independent of \(X,U,V\).

**Proof.** Let \(M=\max U\), \(N=\max V\), \(m=\min(M,N)\), and
\(n=\max(M,N)\). The maximum pair occurs, so \(mn=MN\le X\). By
Cauchy--Schwarz and (7),

\[
 |UV|\ge\frac{P^2}{E_\times(U,V)}\ge\frac{P}{C}
 \ge\frac{cX}{C}\ge\frac{c}{C}mn.                             \tag{9}
\]

On the other hand, \(|UV|\le T(m,n)\). Equations (3) and (9) are
incompatible once \(m\) exceeds a constant depending only on \(c,C\). For
example, one may choose \(B\) so large that the parenthesis in (4) is less
than \(c/C\) for every \(m>B\). QED.

The density-scale hypothesis in R1_audit,

\[
 E_\times(U,V)\le C\frac{P^2}{X},                              \tag{10}
\]

also implies the energy hypothesis in (7), since \(P\le MN\le X\).
If \(m\le B\), the set on the bounded side has at most \(B\) elements, so
the opposite side has at least \(cX/B\) elements. Thus the correct resulting
density constant is \(c/B\), whether the bounded side alternates with \(X\)
or not.

Finally, the stronger sequential claim in C05 is valid. If \(U_j,V_j\) have
maxima \(m_j\le n_j\), \(m_jn_j\le X_j\), and \(m_j\to\infty\), then

\[
 \frac{X_jE_\times(U_j,V_j)}{|U_j|^2|V_j|^2}
 \ge\frac{X_j}{|U_jV_j|}
 \ge\frac{m_jn_j}{T(m_j,n_j)}\longrightarrow\infty.           \tag{11}
\]

Thus C05's qualitative Ford obstruction is confirmed, including unbounded
aspect ratios. Its equation (8) should be read with \(F(\sqrt Y)\) (up to
absolute constants); the unexplained \(c\sqrt Y\) there is only a notation
defect.

## 3. Multi-stars are exactly product density

The equivalence does not use closure. Let \(A,B\subset\mathbb N\), and put

\[
 Q_X=|AB\cap[1,X]|.
\]

**Proposition.** The following are equivalent.

1. There are fixed \(\eta>0,L<\infty\) such that, for every sufficiently
   large \(X\), there are finite \(D_X\subset A\) and
   \(V_{d,X}\subset B\cap[1,\lfloor X/d\rfloor]\) with

   \[
   M_X=\sum_{d\in D_X}|V_{d,X}|\ge\eta X,
   \qquad
   S_X=\sum_{\substack{d,e\in D_X\\d\ne e}}
       |dV_{d,X}\cap eV_{e,X}|\le L M_X,                       \tag{12}
   \]

   where the second sum is ordered.
2. \(\liminf_{X\to\infty}Q_X/X>0\).

**Proof of 1 implies 2.** Let

\[
 r_X(n)=\#\{d\in D_X:n\in dV_{d,X}\}.
\]

Then \(\sum_n r_X(n)=M_X\) and, exactly,

\[
 \sum_n r_X(n)^2=M_X+S_X\le(1+L)M_X.
\]

Cauchy--Schwarz gives

\[
 Q_X\ge|\operatorname{supp}r_X|
 \ge\frac{M_X^2}{M_X+S_X}
 \ge\frac{\eta}{1+L}X.                                       \tag{13}
\]

**Proof of 2 implies 1.** Choose \(\eta>0\) below the positive liminf. For
each \(n\in AB\cap[1,X]\), choose exactly one factorization \(n=d_nb_n\),
with \(d_n\in A,b_n\in B\). Set

\[
 D_X=\{d_n:n\in AB\cap[1,X]\},\qquad
 V_{d,X}=\{b_n:d_n=d\}.
\]

There is one selected edge per product, so

\[
 M_X=Q_X\ge\eta X,\qquad dV_{d,X}\cap eV_{e,X}=\varnothing
 \quad(d\ne e).                                                \tag{14}
\]

Thus (12) holds with \(L=0\). QED.

Apply the proposition to \(A=G_0\), \(B=G_2\). These colors are disjoint,
so every represented \(n=db\) satisfies \(n-1\in G_2\). Hence the
multi-star theorem is precisely a relabeling of positive lower density of
\(G_0G_2\), followed by the already-known closure map \(n\mapsto n-1\).

The raw R1 example proves only that a multi-star edge set need not contain a
large Cartesian subrectangle in an artificial residue-compatible ambient
set. It does not prove weaker theorem-strength for subsets of this fixed
closure. The same defect affects C05's arbitrary correlated-edge condition:
from \(Q_X\ge\eta X\), the one-edge-per-product relation has \(M_X=E_X=Q_X\)
and satisfies \(E_X\le\eta^{-1}M_X^2/X\).

## 4. Minimal noncircular repair

The edge family must be fixed before products are deduplicated. The weakest
canonical second-moment condition is obtained from the full, unthinned
closure incidence in fixed product annuli. For

\[
 I_k=(2^{k-1},2^k]\cap\mathbb N
\]

define

\[
 \mathcal R_k=\{(a,b)\in G_0\times G_2:ab\in I_k\},\qquad
 r_k(n)=\#\{(a,b)\in\mathcal R_k:ab=n\},
\]

\[
 M_k=|\mathcal R_k|,\qquad E_k=\sum_{n\in I_k}r_k(n)^2,
 \qquad M_k^2/E_k:=0\text{ if }M_k=0.                           \tag{15}
\]

The noncircular structural target is

\[
 \boxed{\quad
 \liminf_{K\to\infty}2^{-K}
 \sum_{k\le K}\frac{M_k^2}{E_k}>0.
 \quad}                                                        \tag{16}
\]

This condition uses every closure-forced cross-color pair in each annulus;
there is no selectable \(V_{d,X}\) in which to hide a transversal of the
already-known products. It is weaker than requiring linear pair mass and
\(O(\text{pair mass})\) energy separately in every annulus.

It is sufficient because Cauchy--Schwarz gives at least \(M_k^2/E_k\)
distinct products in \(I_k\). The annuli are disjoint, and translation by
\(-1\) puts all these products into disjoint members of \(G_2\). If the
liminf in (16) is \(\Delta>0\), then

\[
 |G\cap[1,2^K-1]|\ge(\Delta-o(1))2^K,
\]

and monotonicity between consecutive dyadic cutoffs gives

\[
 \underline d(G)\ge\Delta/2>0.                                \tag{17}
\]

Condition (16) is genuinely extra multiplicative structure, not product
density in disguise. For a residue-compatible counterexample, take
\(A=3\mathbb N\) and \(B=\{b:b\equiv2\pmod 3\}\). Then \(AB\) contains
\(6\mathbb N\), so it has positive lower density. For the full annular
relation at scale \(X=2^k\), harmonic summation gives \(M_k=O(X\log X)\),
whereas

\[
 E_k\gg X(\log X)^3.                                          \tag{18}
\]

For completeness, (18) follows by counting the distinct collision
parameters

\[
 (a,b,a',b')=(3gr,sh,3gs,rh),\qquad (r,s)=1,\quad
 r\equiv s\equiv1\pmod 3,\quad h\equiv2\pmod 3,
\]

with \(X/2<3grsh\le X\) and \(r,s\le X^{1/8}\). For each \(r,s\), harmonic
summation over \(g\) gives \(\gg X\log X/(rs)\) choices of \(g,h\); Moebius
inversion gives

\[
 \sum_{\substack{r,s\le X^{1/8}\\ (r,s)=1\\r\equiv s\equiv1\ (3)}}
 \frac1{rs}\gg(\log X)^2.
\]

Thus \(M_k^2/E_k=O(X/\log X)\), and the normalized sum in (16) is
\(O(1/K)\to0\). Positive product density therefore does not imply (16),
even under the same two residue restrictions.

The actual closure-specific frontier is exactly (16), or a still more
explicit sufficient estimate for its fixed raw incidences. Proving it may
use derivation trees, least generated divisors, or scale recurrences, but it
may not choose edges after the product support has been exposed.
