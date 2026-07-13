# P09: unpaired residual reduction

## Verdict

There is a rigorous quantitative reduction, but inequality (19) does **not**
by itself prove that the unpaired residual is negligible.  Let \(e\) be the
unique repeated sum and write

\[
 C=A\cap(e-A),\qquad U=A\setminus C,
 \qquad A=C\mathbin{\dot\cup}U.
\]

If \(B=\{x\in C:2x<e\}\), \(p=|B|\), and

\[
 \delta=1_{\{e\ {\rm even},\ e/2\in A\}},
\]

then

\[
 C=B\mathbin{\dot\cup}(e-B)
   \mathbin{\dot\cup}(\{e/2\}\text{ if }\delta=1),
 \quad |C|=2p+\delta,
 \quad r_A(e)=p+\delta.                                    \tag{1}
\]

Every positive difference represented by a pair touching \(U\) is globally
unique and is disjoint from every difference represented inside \(C\).  This
gives the exact packing inequality

\[
 \boxed{p(p+\delta)+(2p+\delta)|U|+\binom{|U|}{2}
        \leq \max A-\min A.}                               \tag{2}
\]

Combining this with P02 (19) gives a second, scale-sensitive reduction in
which the right side depends only on the fully reflected core.  These are
necessary constraints, not a stability theorem.  A seven-point exact
witness above the finite \(2/\sqrt3\) normalization has a four-point core and
three unpaired points, and an infinite deletion family has both
\(|C|=\Theta(\sqrt N)\) and \(|U|=\Theta(\sqrt N)\).  The infinite family is
strictly below the threshold.  Thus the asymptotic assertion

\[
 |A|\geq(2/\sqrt3+\varepsilon)\sqrt N\quad\Longrightarrow
 \quad |U|=o(\sqrt N)                                      \tag{3}
\]

is neither proved nor disproved here.  What remains is a decorated
signed-ruler inequality, stated quantitatively in Section 6; assuming (3)
would simply assume the missing stability input.

## 1. The only open multiplicity regime

P02 proves that \(r_A(e)=o(\sqrt N)\) implies

\[
 |A|\leq(1+o(1))\sqrt N.
\]

It also proves the unconditional bound \(|A|=O(\sqrt N)\).  Therefore, for
every fixed \(\varepsilon>0\), any hypothetical family satisfying

\[
 |A|\geq(2/\sqrt3+\varepsilon)\sqrt N
\]

must have an exceptional sum and

\[
 r_A(e)=\Omega_\varepsilon(\sqrt N).
\]

On the other hand, (1) gives \(2r_A(e)-\delta=|C|\leq|A|\), so

\[
 \boxed{r_A(e)=\Theta_\varepsilon(\sqrt N)}.                \tag{4}
\]

This conclusion includes the midpoint correctly: a diagonal representation
\(e/2+e/2=e\) contributes one to \(r_A(e)\) and one element, not two, to
\(C\).

## 2. All residual differences and sums are unique

Put \(c=|C|=2p+\delta\), \(u=|U|\), and
\(L=\max A-\min A\).

### Difference packing

Suppose two distinct unordered pairs give the same positive difference,
after orienting both pairs from smaller to larger.  P02's reflection lemma
forces the second representation to be the reflection of the first about
\(e/2\).  In particular, every endpoint of both representations lies in
\(C\).  Consequently:

* the \(cu+\binom u2\) pairs having at least one endpoint in \(U\) give
  distinct positive differences;
* none of those differences occurs inside \(C\).

The number of distinct positive differences internal to \(C\) is

\[
 \binom c2-p(p-1+\delta)=p(p+\delta).                       \tag{5}
\]

All these labels lie in \([1,L]\), proving (2).  Solving its quadratic gives
the explicit bound

\[
 u\leq-{\left(c-\tfrac12\right)}+
 \sqrt{\left(c-\tfrac12\right)^2+2\left(L-p(p+\delta)\right)}. \tag{6}
\]

No parity term is hidden in (5): it is \(p^2\) when \(\delta=0\) and
\(p(p+1)\) when the midpoint is present.

### Sum packing, including diagonals

Every unordered pair touching \(U\), including every diagonal \(u+u\), has
a unique sum, and these sums are disjoint from \(C+C\).  Indeed, a collision
away from \(e\) is forbidden by admissibility.  A pair touching \(U\) cannot
sum to \(e\): if \(x+y=e\) with \(x,y\in A\), then both \(x,y\in C\).  This
also covers \(2u=e\), since then \(u=e/2\in C\).

The core has

\[
 |C+C|=\binom{c+1}{2}-(r_A(e)-1)=2p(p+\delta)+1.            \tag{7}
\]

After translating \(A\) into \([0,L]\), all sums lie in \([0,2L]\).  Hence

\[
 \boxed{2p(p+\delta)+cu+\binom{u+1}{2}\leq2L.}             \tag{8}
\]

For a repeated exceptional fibre, (2) is at least as strong as (8), but (8)
records the full cross-sum and diagonal check rather than silently replacing
it by a difference assertion.

## 3. P02 (19) gives an exact core-deficit bound

For \(S\neq\varnothing\), put

\[
 M_h(S)=|S+\{0,\ldots,h-1\}|.
\]

All doubled differences of \(A\) are internal to \(C\), so the term
\(W_h(A,e)\) in P02 depends only on the reflected core.  Explicitly,

\[
\begin{split}
 W_h(C,e)={}&\sum_{x<y\atop x,y\in B}
 \left((h-y+x)_+ +(h-e+x+y)_+\right)\\
 &+\delta\sum_{x\in B}(h-e/2+x)_+.                         \tag{9}
\end{split}
\]

P02 (19) is therefore

\[
 {c^2h^2\over M_h(C)}+{u^2h^2\over M_h(U)}
 \leq (c+u)h+h(h-1)+2W_h(C,e),                             \tag{10}
\]

with the second term omitted when \(u=0\).  Since \(M_h(U)\leq L+h\), (10)
proves the exact residual reduction

\[
 \boxed{
 {u^2\over L+h}+{c^2\over M_h(C)}
 \leq 1-{1\over h}+{c+u\over h}+{2W_h(C,e)\over h^2}.}     \tag{11}
\]

Equivalently, if

\[
 \Psi_h(C;L,k)=1-{1\over h}+{k\over h}
 +{2W_h(C,e)\over h^2}-{c^2\over M_h(C)},                  \tag{12}
\]

then

\[
 \boxed{u^2\leq(L+h)\Psi_h(C;L,k).}                        \tag{13}
\]

Thus \(\Psi_h\geq0\) whenever a residual can be attached.  On a mesoscopic
scale \(k=o(h)\), \(h=o(L)\), this becomes

\[
 {u^2\over L}\leq
 1+{2W_h(C,e)\over h^2}-{c^2\over M_h(C)}+o(1).             \tag{14}
\]

In particular, \(u\geq\eta\sqrt L\) forces a core deficit of at least
\(\eta^2-o(1)\) in (14).  Conversely, saturation of the core inequality at
one mesoscopic scale forces \(u=o(\sqrt L)\).  This is the promised
quantitative reduction.  It does not prove that an above-threshold core must
saturate; that implication is exactly the missing stability statement.

## 4. Exact obstructions

### A finite over-threshold residual

Take

\[
 A=\{1,2,4,9,13,30,31\}\subseteq[31],\qquad e=32.
\]

Then

\[
 C=\{1,2,30,31\},\qquad U=\{4,9,13\},\qquad
 p=2,\quad\delta=0.
\]

The complete singleton-sum set is

\[
\begin{split}
 \{&2,3,4,5,6,8,10,11,13,14,15,17,18,22,26,31,\\
   &33,34,35,39,40,43,44,60,61,62\},
\end{split}
\]

and the only remaining sum is \(32\), represented exactly by
\(1+31=2+30\).  Thus all 28 unordered pairs, including the seven diagonals,
are certified.

The internal-core difference set and residual difference set are respectively

\[
 \{1,28,29,30\}
\]

and

\[
 \{2,3,4,5,7,8,9,11,12,17,18,21,22,26,27\};
\]

they are disjoint.  Here (2) reads \(4+12+3=19\leq30\).  Moreover,

\[
 {7\over\sqrt{31}}=1.257237\ldots>{2\over\sqrt3}.
\]

For this witness \(D=\{1,29\}\), so

\[
 W_h=(h-1)_++(h-29)_+,
\]

\[
 M_h(C)=
 \begin{cases}2h+2,&1\leq h\leq28,\\h+30,&h\geq29,
 \end{cases}
 \qquad
 M_h(U)=h+\min(h,5)+\min(h,4).
\]

Substitution verifies (10) and (11) for every \(1\leq h\leq31\).  Therefore
neither (19), cross-sum uniqueness, nor finite normalized excess forces a
small residual.

### An infinite positive-proportion residual

Let \(B_0\subseteq[1,L]\) be any genuine Sidon set, let \(P\subseteq B_0\),
put \(T=3L+1\), and define

\[
 A(B_0,P)=B_0\cup(T-P)\subseteq[1,3L].                     \tag{15}
\]

This is a subset of the standard admissible reflected set
\(B_0\cup(T-B_0)\), so it is admissible.  If \(|P|\geq2\), its only repeated
sum is \(T\), with exactly \(|P|\) representations, and

\[
 C=P\cup(T-P),\qquad U=B_0\setminus P.                      \tag{16}
\]

Take dense Sidon sets with \(|B_0|=(1+o(1))\sqrt L\), fix
\(0<\alpha<1\), and choose \(|P|=(\alpha+o(1))|B_0|\).  Then, with \(N=3L\),

\[
 |C|\sim{2\alpha\over\sqrt3}\sqrt N,qquad
 |U|\sim{1-\alpha\over\sqrt3}\sqrt N,qquad
 r_A(T)\sim{\alpha\over\sqrt3}\sqrt N,                   \tag{17}
\]

while

\[
 {|A|\over\sqrt N}\longrightarrow{1+\alpha\over\sqrt3}
 <{2\over\sqrt3}.                                          \tag{18}
\]

Thus a linear-size reflected core and a nonnegligible residual coexist in an
exact infinite family, even in the regime \(r_A(e)=\Theta(\sqrt N)\).  The
strict density loss in (18) is why this construction does not disprove (3).
It does disprove any unconditional core-to-residual stability claim.

## 5. Midpoint and parity audit

There are three distinct cases, and none may be merged with another:

1. \(e\) odd, necessarily \(\delta=0\);
2. \(e\) even but \(e/2\notin A\), again \(\delta=0\);
3. \(e\) even and \(e/2\in A\), so \(\delta=1\).

The finite obstruction above tests case 2.  Case 1 is tested by

\[
 \{1,2,5,6\},\quad e=7,\quad B=\{1,2\},\quad D=\{1,4\},
\]

for which \(|D|=p(p-1)=2\).  Case 3 is tested by

\[
 \{1,2,4,6,7\},\quad e=8,\quad B=\{1,2\},\quad D=\{1,2,3,5\},
\]

for which \(|D|=p^2=4\).  The collision
\(1+7=2+6=4+4\) shows why the midpoint contributes to \(r_A(e)\) but does not
create a second element in a reflected pair.

As a computational guardrail, all 3,489 admissible subsets with a repeated
sum through \(N=14\) were exhaustively checked: 2,016 had a midpoint and
1,473 did not.  For every set the check verified (1), (2), (5), (7), (8),
the injectivity and disjointness of all residual sums and differences, (10)
for every \(1\leq h\leq N\), and the derived inequality (11).

## 6. Corrected frontier

P03 already proves, in the notation above and with parity contributing only
\(O(k)\),

\[
 L\geq2p^2+2pu+u^2-o(k^2).                                 \tag{19}
\]

The target is

\[
 L\geq{3\over4}(2p+u)^2-o(k^2)
  =3p^2+3pu+{3\over4}u^2-o(k^2).                            \tag{20}
\]

Thus the exact missing gain over the accepted rank-window bound is

\[
 \boxed{p^2+pu-{u^2\over4}.}                                \tag{21}
\]

It is positive precisely when

\[
 {u\over p}<2+2\sqrt2,
\]

which is asymptotically equivalent to P03's only unresolved regime

\[
 {|C|\over|A|}>1-{1\over\sqrt2}.
\]

At \(u=0\), (21) is the missing \(p^2\) in the fully reflected signed-ruler
bound \(L\geq(3-o(1))p^2\).  For \(u>0\), the residual cannot simply be
discarded.  Its labels form a disjoint forbidden set of size

\[
 cu+\binom u2
\]

inside \([1,L]\), and (11) forces it to consume a quantified amount of the
core's occupied-thickening slack.  There is also an exact coupling: for every
\(x\in B\), writing \(\bar x=e-x\), and every \(v\in U\),

\[
 \begin{cases}
 |v-x|+|v-\bar x|=e-2x,&x<v<\bar x,\\
 \big||v-x|-|v-\bar x|\big|=e-2x,&v<x\text{ or }v>\bar x.
 \end{cases}                                                \tag{22}
\]

All distances on the left are residual labels; \(e-2x\) is a singleton core
difference.  When \(\delta=1\), the additional \(u\) distances to \(e/2\)
are also unique and disjoint, exactly accounting for the \(\delta u\) term
in (2).

The corrected frontier is therefore to prove (20), equivalently the gain
(21), for this **decorated signed ruler** using the disjoint residual labels,
the coupling (22), and the core-deficit constraint (11).  A theorem only for
the bare fully reflected set \(U=\varnothing\) is insufficient, while a
theorem asserting \(u=o(\sqrt N)\) is the desired stability conclusion and
cannot be used as an input.
