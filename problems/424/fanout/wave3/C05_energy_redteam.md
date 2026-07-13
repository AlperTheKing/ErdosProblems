# C05: red-team of the R-C multiplicative-energy route

## Verdict

The proposed finite Cauchy--Schwarz implication is correct at one scale, but
the intended Cartesian reservoir hypothesis is asymptotically impossible when
both factor scales tend to infinity. This is true for unbalanced as well as
balanced windows.

More precisely, let \(U_j,V_j\subset\mathbb N\) be nonempty and finite, put
\(Y_j=\max U_j\), \(Z_j=\max V_j\), and suppose \(Y_jZ_j\le X_j\). If

\[
  \min(Y_j,Z_j)\longrightarrow\infty,
\]

then

\[
 \boxed{\quad
 \frac{X_j E_\times(U_j,V_j)}{|U_j|^2|V_j|^2}
 \longrightarrow\infty.\quad}                                      \tag{1}
\]

Thus the bounded-\(\kappa\) target in R1 (48)--(51) and R-C (58)--(61), with a
single Cartesian product \(U_X\times V_X\) and all cross-products at most
\(X\), is falsified in its intended two-unbounded-factor form. The proof is a
short consequence of Ford's divisor-in-an-interval theorem; see below.

This does **not** say that \(G_0G_2\) has density zero. It says that this
particular finite certificate cannot prove otherwise. A non-Cartesian,
scale-correlated edge set remains viable.

## 1. Exact normalization audit

For

\[
 r(n)=|\{(u,v)\in U\times V:uv=n\}|,
 \qquad N=|U||V|,
\]

write

\[
 E=\sum_n r(n)^2,
 \quad D=\frac{E}{N},
 \quad \rho=\frac{N}{X},
 \quad \kappa_X=\frac{EX}{N^2}.
\]

There is an exact identity

\[
                 \boxed{\kappa_X=\frac{D}{\rho}}.                   \tag{2}
\]

Here \(D\ge1\) is the collision ratio and \(\rho\) is the pair mass at scale
\(X\). Consequently, near-diagonal energy \(D=1+o(1)\) says nothing about
bounded \(\kappa\) unless \(N\gg X\) is proved separately. The diagonal terms
alone give the necessary condition

\[
 E\ge N,
 \qquad E\le K\frac{N^2}{X}
 \quad\Longrightarrow\quad N\ge \frac X K.                          \tag{3}
\]

Cauchy--Schwarz gives the other exact relation

\[
 E|UV|\ge N^2,
 \qquad |UV|\ge\frac{X}{\kappa_X}.                                  \tag{4}
\]

The probe was rerun unchanged on 2026-07-13: \(B=10^6\), ten window pairs,
and product cap \(4\cdot10^8\). It reproduced

\[
 |G|=457599,\quad |G_0|=192451,\quad |G_2|=265148
\]

and SHA-256
9462e017bf46fc5b08a1267987b4fa4c037daebdc4892a2cfa666fb5780d5258.
For example, at \((Y,Z)=(10^4,10^6)\),

\[
 |U|=712,\quad |V|=136590,\quad E=106256268,
 \quad D=1.0926,\quad \kappa_X=112.346.
\]

So the computation itself is already a finite counterexample to
"near-diagonal energy implies small \(\kappa\)": the missing quantity is
\(\rho\).

For the full dyadic windows define their relative occupancies by

\[
 \lambda_0(Y)=\frac{2|G_0\cap(Y/2,Y]|}{Y},\qquad
 \lambda_2(Z)=\frac{2|G_2\cap(Z/2,Z]|}{Z}.
\]

With \(X=YZ\), (2) becomes

\[
             \kappa_X=\frac{4D}{\lambda_0(Y)\lambda_2(Z)}.          \tag{5}
\]

Hence extrapolating bounded \(\kappa\) from the displayed full-window table
already extrapolates positive local density for both colors. Since
\(G_0,G_2\subset G\), that density input is at least as difficult as the
requested conclusion.

## 2. Ford obstruction, including unbalanced windows

Let \(H(x,y,2y)\) count integers at most \(x\) having a divisor in
\((y,2y]\). Ford proved, uniformly for \(3\le y\le\sqrt x\),

\[
 H(x,y,2y)\asymp
 \frac{x}{(\log y)^\delta(\log\log y)^{3/2}},
 \qquad
 \delta=1-\frac{1+\log\log2}{\log2}=0.086071332\ldots.              \tag{6}
\]

Sources: [Ford's author synopsis](https://ford126.web.illinois.edu/papers-ann.html)
and the [Annals paper](https://annals.math.princeton.edu/2008/168-2/p01).

### A single dyadic block

Suppose \(U\subset(Y/2,Y]\), \(V\subset(Z/2,Z]\), \(Y\le Z\), and \(X=YZ\).
Every member of \(UV\) is at most \(X\) and has a divisor in \((Y/2,Y]\).
Thus (6) and (4) imply

\[
 |UV|\le H(X,Y/2,Y)
 \ll \frac{X}{(\log Y)^\delta(\log\log Y)^{3/2}},
\]

\[
 \boxed{\quad
 \kappa_X\gg(\log Y)^\delta(\log\log Y)^{3/2}\longrightarrow\infty.
 \quad}                                                             \tag{7}
\]

Only the smaller scale matters. An arbitrary ratio \(Z/Y\to\infty\) does
not evade (7) if \(Y\to\infty\). Therefore the claim that sufficiently
unbalanced dyadic windows might have bounded \(\kappa\) is exactly false.

### Any Cartesian factor box

The same obstruction is not limited to dyadic windows. Let

\[
 \mathcal M(Y,Z)=\{uv:1\le u\le Y,\ 1\le v\le Z\},\qquad 3\le Y\le Z.
\]

Put \(X_0=YZ\). Split \(u>\sqrt Y\) into
\((Y/2^{j+1},Y/2^j]\). Products from this block are at most \(X_0/2^j\)
and have a divisor in that block. Applying (6) to each block and summing
the geometric factor \(2^{-j}\), while treating \(u\le\sqrt Y\) trivially,
gives

\[
 |\mathcal M(Y,Z)|
 \ll \frac{X_0}{\sqrt Y}
   +\frac{X_0}
   {(\log(c\sqrt Y))^\delta(\log\log(c\sqrt Y))^{3/2}}
 =o(X_0).                                                           \tag{8}
\]

This proves (1): after swapping \(Y_j,Z_j\) if needed,

\[
 \kappa_{X_j}\ge\frac{X_j}{|U_jV_j|}
 \ge\frac{Y_jZ_j}{|\mathcal M(Y_j,Z_j)|}\longrightarrow\infty.     \tag{9}
\]

There is a useful dichotomy behind (9). If \(N=o(X)\), then even diagonal
energy makes \(\kappa\) diverge by (2). If \(N\gg X\), Ford forces
\(|UV|=o(X)\), so Cauchy--Schwarz makes the collision ratio \(D\) diverge.
No choice of subsets inside one Cartesian box avoids both alternatives.

### The bounded-factor escape is circular

Suppose instead that \(\kappa\) is bounded and, at a given scale, say
\(\max U_X\le C\). From (3),

\[
 |V_X|\ge\frac{X}{KC}.
\]

Since \(V_X\subset G_2\cap[1,X]\), this gives a linear-size subset of \(G\)
at that scale. Quantitatively, (8)--(9) show that bounded \(\kappa\) forces
the smaller factor maximum to remain uniformly bounded. If the bounded side
is eventually fixed, the opposite color has positive lower density. Even if
the bounded side alternates, at every large scale one of \(U_X,V_X\) has at
most \(C\) elements and (3) puts at least \(X/(KC)\) elements of the other
side in \(G\cap[1,X]\). Thus the only Cartesian escape directly assumes the
desired positive-density conclusion.

## 3. Exact artificial countermodels

These models are **not** claims about the actual generated set \(G\). They
show exactly which inferences are unavailable from the recorded data.

### 3.1 Full finite-census twin with zero-density products

Fix \(B=10^6\), and let

\[
 F_i=G_i\cap[1,B]\quad(i=0,2)
\]

be the exact sets produced by the verified truncated closure. Let

\[
 \mathcal P_1=\{p>B:p\text{ prime},\ p\equiv1\pmod3\},\qquad
 \mathcal P_2=\{q>B:q\text{ prime},\ q\equiv2\pmod3\},
\]

and define the deterministic artificial pair

\[
 A_0=F_0\cup3\mathcal P_1,
 \qquad A_2=F_2\cup\mathcal P_2.                                   \tag{10}
\]

It has all of the following properties.

1. \(A_i\cap[1,B]=G_i\cap[1,B]\). It therefore reproduces every finite
   density, every dyadic window, and every energy entry in the probe, not
   merely the three total counts.
2. It obeys the exact color restrictions \(A_0\subset3\mathbb N\) and
   \(A_2\subset\{n:n\equiv2\pmod3\}\).
3. In large windows,

   \[
   U_Y=A_0\cap(Y/2,Y]=\{3p:Y/6<p\le Y/3,\ p\equiv1\pmod3\},
   \]

   \[
   V_Z=A_2\cap(Z/2,Z]=\{q:Z/2<q\le Z,\ q\equiv2\pmod3\}.
   \]

   Unique factorization and the different residue classes give
   \(E_\times(U_Y,V_Z)=|U_Y||V_Z|\) exactly. The prime number theorem in
   progressions gives

   \[
   |U_Y|\sim\frac{Y}{12\log Y},\qquad
   |V_Z|\sim\frac{Z}{4\log Z},\qquad
   \kappa_{YZ}\sim48\log Y\log Z\longrightarrow\infty.              \tag{11}
   \]

   Thus even exact diagonal energy in every sufficiently large nonempty
   dyadic window does not give bounded \(\kappa\).
4. \(A_0A_2\) has upper density zero. Apart from a finite set, its elements
   are fixed multiples of one prime or numbers \(3pq\). Standard elementary
   prime bounds give

   \[
   |A_0A_2\cap[1,X]|
   =O_{F_0,F_2}\!\left(\frac{X\log\log X}{\log X}\right)=o(X).       \tag{12}
   \]

This is an exact countermodel to every inference based only on the known
finite census, the observed decreasing \(\kappa\) values, the color
restrictions, and near-diagonal energy.

There cannot be a version of (10) in which either artificial color has
genuine positive lower density while the product has density zero. For any
\(a\in A\),

\[
 |AB\cap[1,X]|\ge |B\cap[1,X/a]|,
 \qquad \underline d(AB)\ge\frac{\underline d(B)}a.                \tag{13}
\]

Thus only *finite empirical* densities can be matched by a zero-density
product model. This is exactly the status of the \(10^6\) census.

If full local residue support is also desired, enumerate every compatible
pair \((M,r)\) with \(3\mid M\) and \(r\equiv0\) or \(2\pmod3\). Recursively
adjoin the least representative \(d_t\equiv r_t\pmod {M_t}\) above
\(\max(B,d_{t-1}^2)\) to the corresponding color. The added sets have
count \(O(\log\log X)\) and summable reciprocals. They leave the finite
census unchanged, meet every allowed residue modulo every \(3q\), and their
products with (10) still contribute \(o(X)\). Hence even saturation of all
finite modular supports does not repair the inference. This strengthened
model is still not closed under \(xy-1\).

### 3.2 Cross-closure alone

Set

\[
 C_0=\{3\},\qquad
 b_n=\frac{3^{n+1}+1}{2},\qquad
 C_2=\{b_n:n\ge0\}.
\]

Then \(b_0=2\), every \(b_n\equiv2\pmod3\), and

\[
 3b_n-1=b_{n+1},
 \qquad C_0C_2-1=C_2\setminus\{2\}.                                \tag{14}
\]

So (14) satisfies exactly the R-C cross-closure rule, and in fact this
affine orbit lies inside the actual \(G\). Nevertheless

\[
 |C_0C_2\cap[1,X]|=O(\log X).
\]

It is not a model of all of \(G\), nor is it closed under every allowed pair.
It is an exact witness that the one-sided inclusion
\(G_0G_2-1\subset G_2\), by itself, contains no density amplification.

## 4. Correct energy-to-density quantifiers

### Cartesian statement

At a single scale the exact valid lemma is:

> If nonempty finite \(U\subset A\), \(V\subset B\) satisfy \(uv\le X\) for
> every \((u,v)\in U\times V\), and
>
> \[
> E_\times(U,V)\le K\frac{|U|^2|V|^2}{X},
> \]
>
> then \(|AB\cap[1,X]|\ge X/K\).

The asymptotic conclusions require the following exact scale quantifiers.

- If the lemma holds for every sufficiently large \(X\) with one fixed \(K\),
  then \(\underline d(AB)\ge1/K\).
- If it holds only at \(X_j\to\infty\), then only
  \(\overline d(AB)\ge1/K\) follows.
- If additionally \(X_{j+1}/X_j\le L\), then
  \(\underline d(AB)\ge1/(LK)\). For \(X_{j+1}/X_j\to1\), the bound is
  \(1/K\). If the \(\alpha\) in "\(\alpha/\kappa\)" is intended to encode
  scale coverage, its corrected value here is \(\alpha=1/L\); no asymptotic
  \(\alpha\) follows from the one-scale Cauchy--Schwarz lemma alone.
- Finitely many tested scales imply no asymptotic density statement.

For \(T^{(2)}\), one must also impose \(U\cap V=\varnothing\), or otherwise
remove the forbidden equal-value pairs. For \(G_0\times G_2\), the residue
classes make distinctness automatic.

### Surviving non-Cartesian theorem

The Ford obstruction targets a full Cartesian cross-product. The corrected
route is allowed to correlate factor scales. For every sufficiently large
\(X\), let

\[
 \mathcal E_X\subset\{(a,b)\in G_0\times G_2:ab\le X\}
\]

be an arbitrary finite edge set, not necessarily \(U_X\times V_X\), and put

\[
 R_X(n)=|\{(a,b)\in\mathcal E_X:ab=n\}|,
 \qquad M_X=|\mathcal E_X|.
\]

Then the following is a valid narrowed target:

\[
 \boxed{\quad
 \sum_n R_X(n)^2\le K\frac{M_X^2}{X}
 \quad\text{for every sufficiently large }X.
 \quad}                                                             \tag{15}
\]

Cauchy--Schwarz gives at least \(X/K\) distinct products, hence

\[
 \underline d(G_0G_2)\ge\frac1K,
 \qquad
 \underline d(G)\ge \underline d(G_0)+\frac1K,                    \tag{16}
\]

where the second inequality uses
\(G_0G_2-1\subset G_2\subset G\), the shift by one, and disjointness from
\(G_0\).

Condition (15), or its bounded-ratio-scale version with the \(1/L\) loss, is
the surviving energy theorem. It can combine many unbalanced blocks while
omitting the cross-pairs between incompatible scales. This escape is possible
only because the maxima of the two coordinate projections may have product
much larger than \(X\); completing the edge set to a Cartesian product would
insert inadmissible cross-scale pairs. Proving (15) still requires an
unconditional supply of \(M_X\gg X\) with sufficiently few repeated products;
neither the finite census nor closure supplies that.

## Route decision

- **FALSIFIED:** bounded \(\kappa\) from a balanced dyadic block.
- **FALSIFIED:** bounded \(\kappa\) from an unbalanced dyadic block when both
  scales tend to infinity.
- **FALSIFIED:** bounded \(\kappa\) from any Cartesian factor box with both
  maxima tending to infinity.
- **FALSIFIED AS AN INFERENCE:** finite densities, decreasing finite
  \(\kappa\), near-diagonal energy, modular support, or cross-closure alone.
- **SURVIVES:** a correlated edge family satisfying (15) at every large scale
  (or bounded-ratio scales with the exact loss), equivalently a genuine
  multi-scale smooth--rough covering certificate.
