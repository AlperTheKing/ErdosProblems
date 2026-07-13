# C11: smooth/rough frontier for R-A3

Code: [audit_frontier.py](../../compute/wave3/C11_smooth_rough/audit_frontier.py)

Exact output: [result.json](../../compute/wave3/C11_smooth_rough/result.json)

## Verdict

The finite certificate behind (21) is valid, but there are two different
versions which must not be mixed.

1. The full version uses every canonical smooth part $s\leq y$, has only
   the high-smooth exception $s>y$, has rough cutoffs extending to $X$,
   and has the singleton correction $-1$.
2. The $L$-window version uses $L\leq s\leq y$ and $r>z$, has rough
   cutoffs only through $\lfloor X/L\rfloor$, and must add the ambient
   exceptions $s<L$, $s>y$, and $r=1$. It has no separate $-1$.

Thus the C03 interval

\[
[\lfloor X/y\rfloor,\lfloor X/L\rfloor]
\]

belongs to the second certificate, not to full (21). C03's finite
quantities are correct for their stated definitions; its gate-(32) product
is a sufficient upper bound for the windowed rough error only after the
ambient window error is included separately.

The immediate closure inequalities were tested first. The true seed-2
pullback and the true affine inclusion $4T-1\subseteq T$ do not yield a
contraction. Exact finite contraction candidates with coefficient at most
$4$ fail by wide margins. A seed-2 converse fails at $r=23$, and a
uniform many-witness lower bound fails at $r=19$.

No closure-specific inequality forcing (31) or (32) was found. The exact
remaining statements are weighted and sifted shifted-product theorems for
$G_2=G\cap\{2\pmod 3\}$, stated in Section 6 below.

## 1. Canonical factorization

Fix integers $X\geq1$ and $2\leq z<y\leq X$. Put

\[
P(z)=\prod_{p\leq z}p,
\qquad
S_z(n)=\prod_{p\leq z}p^{v_p(n)},
\qquad
R_z(n)=\frac{n}{S_z(n)}.
\]

Then $n=S_z(n)R_z(n)$ uniquely, $S_z(n)$ is $z$-smooth, and
$(R_z(n),P(z))=1$. Define

\[
\Phi_z(R)=\#\{r\leq R:(r,P(z))=1\},
\]

where $r=1$ is included, and

\[
M_z(R)=\#\{r\leq R:(r,P(z))=1, r\notin T\},
\qquad
D_z(R)=\frac{M_z(R)}{R}.
\]

Since $1\in T$, $M_z(R)$ is unchanged if it is written using C03's
condition $r>z$.

Let

\[
T^{(2)}=\{uv:u,v\in T, u\ne v\}.
\]

The canonical factors have disjoint prime support. Consequently
$S_z(n)=R_z(n)>1$ is impossible. If $n>1$, membership of both canonical
factors in $T$ therefore puts $n$ in $T^{(2)}$; the only equal-factor
case is $n=1=1\cdot1$.

## 2. Exact full certificate (21)

Define the following disjoint errors:

\[
\begin{aligned}
E_0(X;z,y)
 &=\#\{n\leq X:S_z(n)>y\},\\
E_s(X;z,y)
 &=\#\{n\leq X:S_z(n)\leq y, S_z(n)\notin T\},\\
E_r(X;z,y)
 &=\#\{n\leq X:S_z(n)\leq y, S_z(n)\in T,
                    R_z(n)\notin T\}.
\end{aligned}
\]

Every $n\leq X$ outside these three errors and outside $\{1\}$ is a
distinct product of two members of $T$. Hence the exact finite certificate
is

\[
\boxed{
|T^{(2)}\cap[1,X]|
\geq X-E_0(X;z,y)-E_s(X;z,y)-E_r(X;z,y)-1.}
\tag{21-full}
\]

There is no $s<L$ exception in this version. Its exact sum forms are

\[
E_s=\sum_{\substack{s\leq y\\P^+(s)\leq z\\s\notin T}}
       \Phi_z(\lfloor X/s\rfloor),
\tag{22}
\]

and

\[
E_r=\sum_{\substack{s\leq y\\P^+(s)\leq z\\s\in T}}
       M_z(\lfloor X/s\rfloor).
\tag{23}
\]

When $X/y\geq z$, the uniform rough-number upper bound gives

\[
E_s\ll \frac{X}{\log z}
\sum_{\substack{s\leq y\\P^+(s)\leq z\\s\notin T}}\frac1s.
\tag{24}
\]

Writing

\[
H_z(y)=\sum_{\substack{s\leq y\\P^+(s)\leq z}}\frac1s,
\]

Equation (23) gives the exact-range upper bound

\[
E_r\leq XH_z(y)
\sup_{\lfloor X/y\rfloor\leq R\leq X}D_z(R).
\tag{25}
\]

The supremum in (25) may be restricted to the actual cutoffs
$R=\lfloor X/s\rfloor$, but replacing its upper endpoint by
$\lfloor X/L\rfloor$ is not valid in the full certificate.

For the parameter recipe

\[
u=\sqrt{\log\log X},\quad
y=e^{\sqrt{\log X}},\quad
z=y^{1/u},\quad
L=e^{\sqrt{\log z}},
\tag{26}
\]

the primary-source audit in
[C04_literature_bks_ford.md](C04_literature_bks_ford.md) proves
$E_0=o(X)$. Therefore the two sufficient full-certificate gates are

\[
\boxed{
\sum_{\substack{s\leq y\\P^+(s)\leq z\\s\notin T}}\frac1s
=o(\log z)}
\tag{31}
\]

and

\[
\boxed{
H_z(y)\sup_{\lfloor X/y\rfloor\leq R\leq X}D_z(R)=o(1).}
\tag{32-full}
\]

Every $o(\cdot)$ here is as integer $X\to\infty$ along the coupled
parameters (26), and the supremum makes (32-full) uniform over every integer
cutoff in its displayed interval.

## 3. Exact $L$-window certificate measured by C03

If both canonical factors are required to be unbounded, define the ambient
exception as the union

\[
E_{\rm amb}
=\#\{n\leq X:S_z(n)<L\ \text{or}\ S_z(n)>y\ \text{or}\ R_z(n)=1\}.
\]

On its complement, $L\leq S_z(n)\leq y$ and $R_z(n)>z$. Define

\[
\begin{aligned}
E_{s,L}
 &=\#\{n\leq X:L\leq S_z(n)\leq y, R_z(n)>z,
                    S_z(n)\notin T\},\\
E_{r,L}
 &=\#\{n\leq X:L\leq S_z(n)\leq y, R_z(n)>z,
                    S_z(n)\in T, R_z(n)\notin T\}.
\end{aligned}
\]

Now the exact certificate is

\[
\boxed{
|T^{(2)}\cap[1,X]|
\geq X-E_{\rm amb}-E_{s,L}-E_{r,L}.}
\tag{21-window}
\]

There is no additional $-1$, since $n=1$ is already in
$E_{\rm amb}$. The ambient estimates in C04 give

\[
E_{\rm amb}
\ll X(e^{-u}+y^{-1/3})
   +X\frac{\log L}{\log z}+y
=o(X).
\tag{27}
\]

The rough error satisfies

\[
E_{r,L}\leq XH_z(y)
\sup_{\lfloor X/y\rfloor\leq R\leq\lfloor X/L\rfloor}D_z(R).
\tag{28}
\]

Using all of $H_z(y)$, rather than only reciprocal mass from
$T\cap[L,y]$, is a harmless overestimate. Equation (28) is exactly the
quantifier range in C03. The C03 product does not include $E_{\rm amb}$ or
$E_{s,L}$, so its finite decrease is not itself a finite density
certificate.

The C11 audit independently partitioned all integers at the three C03
scales. Every row below sums exactly to $X$.

| $X$ | $E_0$ | $E_s$ | $E_r$ | singleton | certified by (21-full) |
|---:|---:|---:|---:|---:|---:|
| $10^6$ | 161,964 | 484,718 | 37,286 | 1 | 316,031 |
| $10^7$ | 1,688,750 | 4,847,398 | 227,390 | 1 | 3,236,461 |
| 33,333,333 | 5,171,866 | 16,615,290 | 604,091 | 1 | 10,942,085 |

| $X$ | $E_{\rm amb}$ | $E_{s,L}$ | $E_{r,L}$ | certified by (21-window) |
|---:|---:|---:|---:|---:|
| $10^6$ | 638,177 | 313,271 | 8,453 | 40,099 |
| $10^7$ | 6,017,787 | 3,288,929 | 67,163 | 626,121 |
| 33,333,333 | 19,601,916 | 11,420,454 | 171,416 | 2,139,547 |

These are lower-bound certificate counts, not exact counts of
$T^{(2)}\cap[1,X]$: an integer in an error class can still have a different
factorization through $T$.

## 4. Closure contractions tested and falsified

### 4.1 The affine map $t\mapsto4t-1$

For every $t\in T$, the distinct-input closure gives

\[
3t\in G
\Longrightarrow 6t-1=2(3t)-1\in G
\Longrightarrow 3(4t-1)=2(6t-1)-1\in G.
\]

Thus

\[
t\in T\Longrightarrow4t-1\in T,
\qquad
4t-1\notin T\Longrightarrow t\notin T.
\tag{29}
\]

For the smooth gate, let $C_z^{\rm sm}(Y)$ be the reciprocal mass of
missing $z$-smooth $m\leq Y$ such that

\[
m\equiv3\pmod4,
\qquad
t=(m+1)/4\ \text{is also }z\text{-smooth}.
\]

The parent $t$ is missing by (29), and $t\geq2$. Hence

\[
C_z^{\rm sm}(Y)
\leq\sum_{\substack{t\leq(Y+1)/4\\P^+(t)\leq z\\t\notin T}}
\frac1{4t-1}
\leq\frac27W_z((Y+1)/4),
\tag{30}
\]

where $W_z(Y)$ denotes the left side of (31) with $y=Y$. A uniform
inequality

\[
W_z(Y)\leq B_z(Y)+3C_z^{\rm sm}(Y)
\tag{S-aff}
\]

with $B_z(Y)=o(\log z)$ uniformly down the descendant scales would give a
$6/7$ contraction and force (31).

The zero-residual candidate is exactly false. In fact the census falsifies
even $W_z(y)\leq4C_z^{\rm sm}(y)$:

| $X$ | $W_z(y)$ | recursive children | $C_z^{\rm sm}(y)$ | $W_z(y)-4C_z^{\rm sm}(y)$ |
|---:|---:|---|---:|---:|
| $10^6$ | $35627/16800$ | 7, 15 | $22/105$ | $21547/16800$ |
| $10^7$ | $27159509/11642400$ | 7, 15, 55 | $263/1155$ | $16555349/11642400$ |
| 33,333,333 | $55856323/23284800$ | 7, 15, 55, 63 | $844/3465$ | $33169603/23284800$ |

Thus almost all measured missing reciprocal mass lies outside the only
immediate smooth-preserving affine descent. The data do not disprove an
asymptotic estimate for the residual $B_z$; proving that estimate is the
missing theorem, not a consequence of (29).

For the rough gate, let $C_z^{\rm rough}(R)$ count missing $z$-rough
$m\leq R$ of the form $m=4t-1$ with $t$ also $z$-rough. Then (29)
gives

\[
C_z^{\rm rough}(R)\leq M_z(\lfloor(R+1)/4\rfloor).
\tag{33}
\]

A uniform inequality

\[
M_z(R)\leq E_z(R)+3C_z^{\rm rough}(R),
\qquad E_z(R)=o(R/\log z),
\tag{R-aff}
\]

would give a $3/4$ density contraction and force the rough gate. The exact
zero-residual inequality fails at every C03 right endpoint, again even with
coefficient $4$:

| $X$ | $z$ | $R=\lfloor X/L\rfloor$ | $M_z(R)$ | $C_z^{\rm rough}(R)$ | $M_z(R)-4C_z^{\rm rough}(R)$ |
|---:|---:|---:|---:|---:|---:|
| $10^6$ | 9 | 200,000 | 5,911 | 87 | 5,563 |
| $10^7$ | 11 | 2,000,000 | 31,059 | 160 | 30,419 |
| 33,333,333 | 11 | 6,666,666 | 81,685 | 196 | 80,901 |

### 4.2 The seed-2 pullback

Every $z$-rough $r$ is odd when $z\geq2$. Put

\[
h(r)=\frac{3r+1}{2}.
\]

If $h(r)\in G$, then $h(r)\ne2$, and closure with the seed $2$ gives
$2h(r)-1=3r\in G$. Therefore

\[
r\notin T\Longrightarrow h(r)\notin G.
\tag{34}
\]

This is a genuine closure-specific injection, but its right side is an
uncontrolled affine trace of $G^c$. At the C03 right endpoints it gives:

| $X$ | $R$ | rough $T$-misses | rough $r$ with $h(r)\notin G$ | extra unresolved $T$-members |
|---:|---:|---:|---:|---:|
| $10^6$ | 200,000 | 5,911 | 12,471 | 6,560 |
| $10^7$ | 2,000,000 | 31,059 | 83,320 | 52,261 |
| 33,333,333 | 6,666,666 | 81,685 | 245,141 | 163,456 |

There were zero violations of (34). Its converse is exactly false at
$r=23$:

\[
3r+1=70=5\cdot14,
\qquad 5,14\in G_2,
\]

so $23\in T$, while $h(23)=35\notin G$. Thus replacing the full divisor
recursion by the seed-2 branch loses real rough members.

### 4.3 No pointwise many-witness inequality

The $11$-rough value $r=19$ is missing from $T$, and

\[
3r+1=58=2\cdot29
\]

has exactly one nontrivial distinct factor pair; $2\in G$ and
$29\notin G$. Hence no closure descent can assign two distinct divisor
trials to every rough input. Conversely, $r=17\in T$ and
$3r+1=52$ has exactly one admissible $G_2$-pair, $2\cdot26$.
Thus even present rough members need not have redundant closure witnesses.

## 5. Quantifier audit for (31) and (32)

The following points are load-bearing.

1. $T$, $G$, and the distinct-input convention are fixed before $X$.
2. The little-$o$ statements run only along the coupled functions in
   (26); the three C03 rows cannot establish or refute them.
3. Equation (31) is a reciprocal-mass assertion, not a counting-density
   assertion for smooth values.
4. Equation (32) uses $M_z(R)/R$, not the conditional fraction
   $M_z(R)/\Phi_z(R)$.
5. The supremum is uniform over all displayed integer cutoffs. Checking only
   $R=\lfloor X/s\rfloor$ is enough for the exact error, but any broader
   interval bound must contain every such cutoff.
6. Full (21) requires the upper endpoint $X$. The C03 upper endpoint
   $\lfloor X/L\rfloor$ requires (21-window) and its ambient error.
7. In the full certificate the $-1$ is exactly the forbidden product
   $1\cdot1$. In the window certificate $r=1$ is already ambient and no
   $-1$ remains.
8. Directed integer rounding changes finite endpoints but not the logical
   form: $L=\lceil L_{\mathbb R}\rceil$,
   $y=\lfloor y_{\mathbb R}\rfloor$, and
   $z=\lfloor z_{\mathbb R}\rfloor$.

## 6. Rigorous theorem-strength reduction

Let

\[
G_2=G\cap\{n:n\equiv2\pmod3\}.
\]

Induction from the seeds shows $G\subseteq\{0,2\pmod3\}$. For $n\geq2$,
the exact well-founded membership recursion gives

\[
\boxed{
n\in T
\quad\Longleftrightarrow\quad
3n+1=ab\ \text{for some }2\leq a<b, a,b\in G_2.}
\tag{35}
\]

Indeed, $3n$ is not a seed, so membership supplies a distinct factor pair
of $3n+1$. Its product is $1\pmod3$, forcing both factors to be
$2\pmod3$. The converse is the closure rule. The excluded value $n=1$
is exactly the seed/equal-factor exception $4=2^2$.

Write

\[
\mathcal W(n)=
\{(a,b):2\leq a<b, a,b\in G_2, ab=3n+1\}.
\]

Then (31) is exactly the shifted smooth theorem

\[
\sum_{\substack{2\leq s\leq y\\P^+(s)\leq z\\
                  \mathcal W(s)=\varnothing}}
\frac1s=o(\log z),
\tag{SR-S}
\]

and, using (36), the windowed rough gate is equivalent to the uniform
shifted sifted theorem

\[
\sup_{\lfloor X/y\rfloor\leq R\leq\lfloor X/L\rfloor}
\frac{\log z}{R}
\#\{2\leq r\leq R:(r,P(z))=1,
                  \mathcal W(r)=\varnothing\}
=o(1).
\tag{SR-R}
\]

Along (26), a standard Mertens-product argument gives

\[
H_z(y)\sim e^\gamma\log z.
\tag{36}
\]

For completeness, truncation at $y=z^u$ loses $o(\log z)$: Markov's
inequality under reciprocal Euler-product weights bounds the tail by

\[
\frac1{u\log z}
\prod_{p\leq z}(1-p^{-1})^{-1}
\sum_{p\leq z}\frac{\log p}{p-1}
=O(\log z/u).
\]

Thus (SR-S) says that $T$ has relative harmonic density one among the
relevant smooth numbers. Likewise, the standard uniform rough-number
asymptotic in this range turns (SR-R) into relative density one of $T$
among $z$-rough integers, uniformly over the cutoff interval.

This identifies the obstruction precisely. Closure proves (35), but (35)
does not estimate how often the shifted integer $3n+1$ has a distinct
$G_2$-factor pair. Proving either gate requires new distributional control
of those recursively defined factors. It is not a consequence of the unary
maps (29), the seed pullback (34), raw density of $T$, or pointwise divisor
multiplicity.

The rough theorem is an almost-all factorization statement, not the prime
theorem isolated for eventual coverage: primes contribute
$O(R/\log R)=o(R/\log z)$ in the present parameter range, so (SR-R) can
hold even if every relevant prime is absent from $T$.

## 7. Reproduction boundary

Run from the repository root:

```powershell
python problems/424/compute/wave3/C11_smooth_rough/audit_frontier.py `
  --limit 100000000 `
  --x-values 1000000 10000000 33333333 `
  --output problems/424/compute/wave3/C11_smooth_rough/result.json
```

The run rebuilt the exact $G[0..10^8]$ bitmap and obtained 51,899,129
members, matching C03. It used the recorded integer triples
$(5,41,9)$, $(5,55,11)$, and $(5,64,11)$ directly; no floating calculation
selects a mathematical parameter. All certificate partitions, closure
implications, and fractions were asserted in code. The JSON is deterministic
under a repeated run. The recorded artifacts have SHA-256 values

```text
audit_frontier.py  bff586abeb493843080641a9f4790541abcc8c3615d069e6837692d4626e7495
result.json        7534b4a4752dde8a67f1483ac6e5c6e7278b4c0ff156bef0ea2827f6e9d1b3c9
```

The hashes certify this finite run only. None of the finite residuals is
extrapolated to an asymptotic claim.
