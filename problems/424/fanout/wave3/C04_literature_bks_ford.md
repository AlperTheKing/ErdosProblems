# Primary-source audit: Bettin-Koukoulopoulos-Sanna and Ford

Scope: this note checks the two literature claims in `writeup/R1_GPTPRO56.md`
against the primary papers only. Here

\[
G_0=G\cap 3\mathbb N,\qquad
G_2=G\cap\{n:n\equiv2\pmod 3\},\qquad
A\cdot B=\{ab:a\in A,b\in B\}.
\]

## 1. Bettin-Koukoulopoulos-Sanna

### Bibliographic record

Sandro Bettin, Dimitris Koukoulopoulos, and Carlo Sanna, "A note on the
natural density of product sets," *Bulletin of the London Mathematical
Society* **53** (2021), no. 5, 1407-1413.

- DOI / version of record: <https://doi.org/10.1112/blms.12506>
- arXiv:2006.13356 [math.NT]: <https://arxiv.org/abs/2006.13356>
- Author-hosted paper: <https://dms.umontreal.ca/~koukoulo/documents/publications/Density_of_products.pdf>

The publisher records online publication on 7 May 2021 and issue publication
in October 2021.

### Exact theorem invoked

The paper defines natural density by

\[
\mathbf d(A)=\lim_{x\to\infty}\frac{\#(A\cap[1,x])}{x},
\]

when the limit exists. Below, \(\underline{\mathbf d}\) and
\(\overline{\mathbf d}\) denote the corresponding liminf and limsup
densities. The paper's **Theorem 1** states exactly:

> Let \(A,B\subseteq\mathbb N\). If \(\mathbf d(A)=\mathbf d(B)=1\), then
> \(\mathbf d(A\cdot B)=1\).

Thus the hypotheses are global natural density one for both sets. They are not
positive lower density, upper density one, logarithmic density one, or density
one relative to residue classes. The conclusion is global natural density one
of the unrestricted product set. The theorem imposes no distinct-factor
condition.

The immediately following corollary says that if \(\mathbf d(A)=1\), then
\(\mathbf d(A^k)=1\) for every integer \(k\ge2\).

The paper's **Theorem 2** gives the sharp density-only companion statement:

\[
\inf_{A\subseteq\mathbb N:\,\mathbf d(A)=\alpha}\mathbf d(A^2)
=
\begin{cases}
0,&0\le\alpha<1,\\
1,&\alpha=1.
\end{cases}
\]

For each fixed \(0<\alpha<1\) and each \(\varepsilon>0\), the proof constructs
a set \(A\) for which both displayed densities exist,
\(\mathbf d(A)=\alpha\), and \(\mathbf d(A^2)<\varepsilon\). This is an
infimum statement. It does **not** say that every set of density below one has
a zero-density square, or even that the infimum is attained. It rules out a
uniform positive quantitative lower bound for \(\mathbf d(A^2)\) based only on
a fixed density \(\alpha<1\). In fact, when \(\alpha>0\), zero cannot be
attained: for any fixed \(a\in A\), one has \(aA\subseteq A^2\), so
\(\underline{\mathbf d}(A^2)\ge \mathbf d(A)/a>0\). Thus "no \(c<1\)
suffices" is correct only if the desired conclusion is density one, or a
uniform lower bound depending on density alone. It is false if read as saying
that positive density of a particular nonempty factor cannot yield qualitative
positivity of its product set.

### Smooth/rough ingredients actually available

The proof of Theorem 1 uses the following two numbered lemmas.

- **Lemma 2.1.** If \(x\ge y>1\), then the count \(\Phi(x,y)\) of \(y\)-rough
  integers in \([1,x]\) satisfies \(\Phi(x,y)\ll x/\log y\).
- **Lemma 2.2.** Uniformly for \(x\ge y^2\ge1\) and \(u\ge1\),
  \[
  \#\{n\le x:\exists d\mid n,\ P^+(d)\le y^{1/u},\ d>y\}
  \ll x(e^{-u}+y^{-1/3}).
  \]

Consequently, the ambient factorization claim in R1 can be justified, but it
is a corollary of these lemmas rather than the statement of Theorem 1. Put

\[
u=(\log\log X)^{1/2},\quad y=e^{(\log X)^{1/2}},\quad
z=y^{1/u},\quad L=e^{(\log z)^{1/2}}.
\]

Write every \(n\) uniquely as \(n=sr\), where \(s\) is its \(z\)-smooth part
and \(r\) its \(z\)-rough part. Lemma 2.2 gives

\[
\#\{n\le X:s>y\}\ll X(e^{-u}+y^{-1/3})=o(X).
\]

Lemma 2.1 and a harmonic sum give

\[
\#\{n\le X:s<L\}
\le \sum_{\substack{s<L\\P^+(s)\le z}}\Phi(X/s,z)
\ll \frac{X\log L}{\log z}=o(X).
\]

The exceptional case \(r=1\) contributes at most \(y=o(X)\). Hence almost all
\(n\le X\) do have \(n=sr\) with \(L\le s\le y\), \(P^+(s)\le z\), and
\(P^-(r)>z\), in particular \(r>z\). This proves ambient supply only. It gives
no membership of \(s\) or \(r\) in sets derived from \(G\).

### What this does and does not imply for \(G_0\cdot G_2\)

1. **No direct application.** Since \(G_0\subseteq3\mathbb N\) and
   \(G_2\subseteq\{n:n\equiv2\pmod3\}\), each has natural upper density at
   most \(1/3\). Therefore neither can satisfy the density-one hypothesis of
   Theorem 1 as a subset of \(\mathbb N\).

2. **Relative density does not repair the hypothesis.** Even eventual or
   relative density one inside the two residue classes would give global
   density \(1/3\), not one. Writing \(G_0=3T\) preserves the cross-product
   up to the fixed scalar, \(G_0G_2=3(TG_2)\), but indexing \(G_2\) by
   \(3k+2\) is affine and does not preserve products.
   Applying Theorem 1 to normalized index sets therefore would not yield a
   theorem about \(G_0\cdot G_2\).

3. **The proof also does not transfer automatically.** Its two membership
   estimates use \(\#([1,t]\setminus A)=o(t)\) and
   \(\#([1,t]\setminus B)=o(t)\). For \(A=G_0\) or \(B=G_2\), the complements
   have density at least \(2/3\). The smooth/rough ambient decomposition remains
   valid, but the membership step is precisely missing.

4. **Theorem 2 is not a negative result about this particular cross-product.**
   It concerns self-products and an infimum over all sets of prescribed
   density. It neither proves nor disproves
   \(\underline{\mathbf d}(G_0\cdot G_2)>0\).
   More elementarily, since both channels are nonempty, positive lower density
   of either one would already imply positive lower density of the cross-product
   by fixing one element of the other channel. Establishing such density is the
   missing problem, not a consequence of BKS.

5. **Distinctness is not an obstacle in this cross-channel.** BKS allows
   equal factors, but \(G_0\cap G_2=\varnothing\), so factors selected one from
   each set are automatically distinct. This removes the mismatch without
   supplying the missing density hypotheses.

**Attribution verdict:** the density-one product theorem is correctly
attributed to Bettin-Koukoulopoulos-Sanna and is Theorem 1 of the cited paper.

## 2. Ford's multiplication-table estimate

### Bibliographic record

Kevin Ford, "The distribution of integers with a divisor in a given
interval," *Annals of Mathematics* (2) **168** (2008), no. 2, 367-433.

- DOI / journal page: <https://doi.org/10.4007/annals.2008.168.367>
- Official paper PDF: <https://annals.math.princeton.edu/wp-content/uploads/annals-v168-n2-p01.pdf>
- arXiv:math/0401223 [math.NT], final v5: <https://arxiv.org/abs/math/0401223>

### Exact result and exponent

On journal p. 372 Ford defines \(A(x)\) to be the number of positive integers
\(n\le x\) representable as \(n=m_1m_2\) with both \(m_i\le\sqrt{x}\).
**Corollary 3** on p. 373 states, as \(x\to\infty\),

\[
A(x)\asymp
\frac{x}{(\log x)^\delta(\log\log x)^{3/2}},
\qquad
\delta=1-\frac{1+\log\log2}{\log2}
=0.086071332055934\ldots .
\]

Ford defines \(f\asymp g\) to mean that each is bounded by an absolute
constant multiple of the other. Therefore this is an exact **order of
magnitude**, not an asymptotic equivalent with a leading constant.

If

\[
M(N)=\#\{ab:1\le a,b\le N\},
\]

then \(M(N)=A(N^2)\) exactly. Corollary 3 is equivalently

\[
M(N)\asymp
\frac{N^2}{(\log N)^\delta(\log\log N)^{3/2}}
=o(N^2).
\]

Corollary 3 is derived from Ford's **Theorem 1** on \(H(x,y,z)\), the number
of \(n\le x\) having a divisor in \((y,z]\), via the explicit inequalities
displayed immediately after the corollary. The dyadic special case also appears
in **Corollary 2**: for fixed \(c>1\), the count \(H(x,y,cy)\) has order

\[
\frac{x}{(\log Y)^\delta(\log\log Y)^{3/2}},
\qquad Y=\min(y,x/y)+3,
\]

uniformly in its stated range \(1/(c-1)\le y\le x/c\), with constants allowed
to depend on \(c\).

### Valid balanced-block consequence

For arbitrary \(U,V\subseteq[N,2N]\), Ford's corollary gives

\[
|U\cdot V|\le M(2N)
\ll \frac{N^2}{(\log N)^\delta(\log\log N)^{3/2}}
=o(N^2).
\]

Thus the R1 phrase "a balanced dyadic block covers \(o(X)\)" is valid after
setting \(X\asymp N^2\), but it is a derived containment corollary, not Ford's
verbatim theorem.

A slightly more invariant formulation is useful. For each fixed \(K\ge1\),
if \(ab\le X\) and \(K^{-1}\le a/b\le K\), then
\(a,b\le\sqrt{KX}\). Hence

\[
\#\{ab\le X:K^{-1}\le a/b\le K\}
\ll_K\frac{X}{(\log X)^\delta(\log\log X)^{3/2}}
=o_K(X).
\]

In particular, the comparable-factor part of \(G_0\cdot G_2\) has density
zero. The same containment plus Cauchy-Schwarz shows that a single nonempty
balanced block cannot have bounded normalized multiplicative energy of the R1
form: if \(X\asymp N^2\), then

\[
E_\times(U,V)\ge\frac{|U|^2|V|^2}{|U\cdot V|}
\quad\Longrightarrow\quad
\frac{E_\times(U,V)X}{|U|^2|V|^2}
\gg(\log N)^\delta(\log\log N)^{3/2}.
\]

### What Ford does not imply for \(G_0\cdot G_2\)

1. Ford does **not** prove \(\overline{\mathbf d}(G_0\cdot G_2)=0\). The full product
   permits factors on arbitrarily different scales, while \(M(N)\) controls a
   square box.

2. Ford does **not** require both factors to tend to infinity. For example,
   \(3\in G_0\), so \(3G_2\subseteq G_0\cdot G_2\) is a fixed-multiplier
   channel. If \(G_2\) had positive lower density, this channel alone would
   have lower density \(\underline{\mathbf d}(G_2)/3>0\). Ford's theorem says
   nothing against it.

3. Ford does show that no fixed bounded-ratio regime, nor any fixed finite
   union of such regimes, can supply positive density. A successful argument
   that excludes bounded multipliers would therefore need factor ratios that
   become unbounded. The stronger R1 wording that every proof "must use ...
   both [factors] tending to infinity" is not a consequence of Ford.

4. The estimate has no hypotheses involving membership recursion, congruence
   classes, or the closure defining \(G\). It supplies a universal obstruction
   for balanced boxes, not positive expansion for unbalanced subsets of
   \(G_0\times G_2\).

### Attribution corrections

- Ford is the correct source for the two-sided order of magnitude including
  the factor \((\log\log N)^{-3/2}\), specifically Corollary 3 of the 2008
  Annals paper.
- Calling this an "asymptotic" is inaccurate if that word means \(\sim\): the
  primary result is \(\asymp\), with no leading constant identified.
- Calling \(\delta\) itself "Ford's exponent" is historically imprecise.
  On p. 368 Ford explicitly records Erdos's 1960 estimate
  \(\varepsilon(y,2y)=(\log y)^{-\delta+o(1)}\) and defines the same
  \(\delta\) there. Ford's contribution cited here is the sharpened uniform
  divisor estimate and the resulting multiplication-table order, including
  the \((\log\log N)^{-3/2}\) factor.

## Bottom line for R1 route R-C

BKS supplies no theorem for \(G_0\cdot G_2\), because its global density-one
hypotheses fail; its smooth/rough lemmas verify only the ambient availability
of unbalanced factorizations. Ford rigorously kills a single balanced block
and, more generally, every fixed factor-comparability regime. It does not kill
the full cross-product, fixed-multiplier channels, or variable-scale
unbalanced reservoirs. Therefore neither citation proves
\(\underline{\mathbf d}(G_0\cdot G_2)>0\) or
\(\overline{\mathbf d}(G_0\cdot G_2)=0\); the R1 membership/energy frontier
remains genuinely additional.
