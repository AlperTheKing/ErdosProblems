# P08: hybrid packing frontier

## Verdict

The uniform estimate

\[
 H(A):=|A+A|+|(A-A)_+|\leq N+O(N^{3/4})                 \tag{1}
\]

was not proved or disproved.  Two nontrivial subcases are proved below:

* (1) holds when the reflected core has size $q=O(\sqrt{k})$, where
  $k=|A|$;
* (1) holds for a fully reflected set whose two reflected blocks are
  range-separated.

The unresolved fully reflected case has an exact reformulation.  If
$B\subseteq[0,W]$ is a literal Sidon set, including diagonals, and
$M>2W$, then

\[
 A_0=B\cup(M-B)                                             \tag{2}
\]

is admissible exactly when

\[
 M\notin (B+B)_{\leq}+\Delta^+(B).                         \tag{3}
\]

Here $(B+B)_{\leq}$ denotes unordered sums with diagonals.  In that
case

\[
 H(A_0)=3|B|^2+1.                                           \tag{4}
\]

Consequently (1), already on the subclass (2), requires the concrete
hole theorem

\[
 M\geq3|B|^2-O(M^{3/4})                                    \tag{5}
\]

under (3).  Conversely, a sequence satisfying (3) and
$M\leq(3-\varepsilon)|B|^2$ would be a parametric obstruction to (1)
and an asymptotic disproof of Problem 864.  Exact tests found substantial
finite compression but no such sequence.  Thus raw interval support has
not closed the frontier; the missing input is the arithmetic assertion
(5), not reflection stability.

## 1. Exact value of $H$

Let the unique repeated unordered sum be $\sigma$, with multiplicity
$m\geq2$, and put

\[
 \delta={\bf1}_{\{\sigma/2\in A\}},\qquad
 P=A\cap(\sigma-A),\qquad q=|P|=2m-\delta.                  \tag{6}
\]

The $m-\delta$ off-diagonal exceptional pairs are disjoint, and the
possible midpoint contributes one point.  This proves the last equality
in (6) without imposing any bound on $m$.

There are \(\binom{k+1}{2}\) unordered pairs, including all $k$
diagonals.  Only the exceptional fibre is collapsed, from $m$ pairs to
one support value.  Hence

\[
 |A+A|=\binom{k+1}{2}-(m-1).                                \tag{7}
\]

For a positive difference, a second representation

\[
 x-y=u-v>0
\]

gives $x+v=u+y$.  The two unordered pairs are distinct, so their common
sum is $\sigma$, and the second representation is forced to be

\[
 (u,v)=(\sigma-y,\sigma-x).                                 \tag{8}
\]

Thus no positive difference has more than two representations.  Reflection
acts on the two-element subsets of $P$.  Of the \(\binom q2\) subsets,
exactly $m-\delta=(q-\delta)/2$ are fixed complementary pairs; all
remaining subsets form two-cycles.  Therefore the number of doubled
positive-difference values is

\[
 R=\frac12\left(\binom q2-\frac{q-\delta}{2}\right)
  =\frac{q^2-2q+\delta}{4}.                                 \tag{9}
\]

Since there are \(\binom k2\) positive-difference representations,

\[
 |(A-A)_+|=\binom k2-R.                                     \tag{10}
\]

Adding (7) and (10), substituting $m=(q+\delta)/2$, and retaining the
midpoint term gives the exact identity

\[
 \boxed{H(A)=k^2+1-\frac{q^2+3\delta}{4}.}                  \tag{11}
\]

If there is no repeated sum, every unordered sum and every positive
difference is unique, so the corresponding identity is $H(A)=k^2$.
This derivation uses unordered sums, includes every diagonal, and permits
arbitrary exceptional multiplicity.

## 2. A finite Sidon interval estimate

The following standard rank-window form records the error scale needed
later.  If

\[
 B=\{b_1<\cdots<b_p\}\subseteq[0,W]
\]

is Sidon, then

\[
 p^2\leq W+O(W^{3/4}).                                     \tag{12}
\]

For completeness, choose $1\leq r<p$ and take the

\[
 T=rp-\frac{r(r+1)}2
\]

differences $b_{i+h}-b_i$, $1\leq h\leq r$.  They are distinct:
equality of two positive differences rearranges to equality of two
unordered sums, and Sidonicity identifies the ordered edges.  Hence their
sum is at least $T(T+1)/2$.  In terms of the consecutive gaps, the same
sum is at most $r(r+1)W/2$.  Therefore

\[
 T(T+1)\leq r(r+1)W.                                       \tag{13}
\]

Taking $r=\lfloor\sqrt p\rfloor$ in (13) gives

\[
 W\geq p^2-O(p^{3/2}).                                     \tag{14}
\]

The same inequality first gives $W\gg p^2$, so
$p^{3/2}=O(W^{3/4})$, proving (12).  Small $p$ are absorbed by the
absolute constant.  No diagonal was dropped: diagonals enter the Sidon
hypothesis which makes the positive differences distinct.

## 3. Proved low-reflection regime

Suppose $q\leq C_0\sqrt{k}$.  Let $L=\max A-\min A\leq N-1$, take
$r=\lfloor\sqrt{k}\rfloor$, and use the lag-$r$ window from P03.  It
contains

\[
 T=rk-\frac{r(r+1)}2                                       \tag{15}
\]

edges.  If $Q$ of its difference labels are doubled, every doubled label
uses two reflected $P$-$P$ edges.  There are at most (rq) selected
$P$-$P$ edges, so

\[
 Q\leq\frac{rq}{2}.                                        \tag{16}
\]

The least possible sum of the selected differences, with (T-Q) labels
used once and $Q$ labels used twice, is

\[
 \binom{T-Q+1}{2}+\binom{Q+1}{2}.                           \tag{17}
\]

The function in (17) decreases for $0\leq Q\leq T/2$.  For large $k$,
(16) is in that range.  On the other hand the gap expansion bounds the same
sum by $r(r+1)L/2$.  Consequently

\[
 L\geq \frac{r}{r+1}
 \left[
 \left(k-\frac{r+1}{2}-\frac q2\right)^2+left(\frac q2\right)^2
 \right]
 =k^2-O_{C_0}(k^{3/2}).                                    \tag{18}
\]

Equation (9) and $|(A-A)_+|\leq N-1$ also give $k=O_{C_0}(\sqrt N)$.
Using $H(A)\leq k^2+1$ in (18) now proves

\[
 \boxed{H(A)\leq N+O_{C_0}(N^{3/4})}                       \tag{19}
\]

whenever $q=O(\sqrt k)$.  The same calculation with $q=o(k)$ gives the
weaker but useful $H(A)\leq N+o(N)$.  It does not handle $q=\Theta(k)$:
the loss (kq) in (18) is then of leading order.

## 4. Fully reflected reduction

It is enough to expose the obstruction in the no-midpoint subclass.  After
translation, any fully reflected set of even size can be written as (2),
where $0\in B\subseteq[0,W]$, $M>2W$, and $p=|B|\geq2$.  Its three sum
types are

\[
 S(B),\qquad M+(B-B),\qquad 2M-S(B),                        \tag{20}
\]

where $S(B)$ contains the unordered diagonal sums $2b$.

If $B$ is not Sidon, both its low collision and its reflected high
collision are repeated sums different from $M$.  Thus admissibility forces
literal Sidonicity.  Conversely, Sidonicity makes every nonzero difference
of $B$ unique, because

\[
 b-c=b'-c'\quad\Longrightarrow\quad b+c'=b'+c.              \tag{21}
\]

Therefore every cross sum in (20) except $M$ is unique, while $M$ has
exactly the $p$ unrestricted representations

\[
 b+(M-b)=M\qquad(b\in B).                                   \tag{22}
\]

Since $M>2W$, low and high sums cannot meet each other.  A low sum
$s\in S(B)$ meets a cross sum precisely when

\[
 s=M+b-c
 \quad\Longleftrightarrow\quad
 M=s+(c-b)\in S(B)+\Delta^+(B).                             \tag{23}
\]

Such a collision reflects to a high collision.  This proves the exact
criterion (3), in both directions, with all diagonals in $S(B)$.

For an admissible (2), (6) has $k=q=2p$, $m=p$, and $\delta=0$.
Equation (11) gives (4); equivalently, the two supports have the exact sizes

\[
 |A_0+A_0|=2p^2+1,\qquad |(A_0-A_0)_+|=p^2.                 \tag{24}
\]

After translating $A_0\subseteq[0,M]$ into $[M+1]$, (1) is exactly
(5), up to the harmless endpoint $N=M+1$.

This also proves (1) in the range-separated case $M>3W$: by (12),

\[
 H(A_0)=3p^2+1\leq3W+O(W^{3/4})\leq M+O(M^{3/4}).           \tag{25}
\]

If the fully reflected set also contains the midpoint, write its core as

\[
 B\mathbin{\dot\cup}(M-B)\mathbin{\dot\cup}\{M/2\},
 \qquad |B|=p.
\]

Then (11), now with $q=2p+1$ and $\delta=1$, gives

\[
 H=3p^2+3p+1.                                               \tag{26}
\]

The lower block is still Sidon.  Thus the same proof gives (25), with the
$3p$ term absorbed by $O(W^{3/4})$, whenever $M>3W$.  The midpoint is
counted once in $q$, and its diagonal is one of the unrestricted
representations of the exception.

## 5. Exact tests

### Exhaustive small sets

Direct enumeration of every subset for $1\leq N\leq16$ tested 131070
sets.  For each set it formed all unordered sums with `i <= j`, rejected a
set when more than one sum had multiplicity at least two, and formed all
positive differences.  The largest value of

\[
 \frac{H(A)-N}{N^{3/4}}
\]

in this exhaustive range was $2.8864\ldots$, at

\[
 N=15,\qquad A=\{1,3,4,8,12,13,15\},\qquad H(A)=37.          \tag{27}
\]

The certified-extremizer records in `census_cpsat.jsonl` contain one
admissible cardinality maximizer for each $1\leq N\leq55$.  Recomputing
both supports directly, rather than trusting stored multiplicities, gave a
maximum scaled excess $3.4252418\ldots$, at

\[
 N=31,\qquad
 A=\{1,2,4,9,13,19,23,28,30,31\},\qquad H(A)=76.            \tag{28}
\]

Its only repeated sum is $32$, with five off-diagonal representations.
Thus $k=q=10$, $\delta=0$, and (11) independently gives
$H=100+1-25=76$.  These large finite excesses rule out an exact injection
of the two supports into $[N]$, but they do not refute an $O(N^{3/4})$
error.

### Compressed reflected centers

For each listed Sidon ruler $B\subseteq[0,W]$, the following table gives
the first $M>2W$ satisfying (3).  The last two columns use
$N=M+1$ and $H=3p^2+1$.

\[
\begin{array}{c|r|r|c|r|c}
p& W&M&M/p^2&H-N&(H-N)/N^{3/4}\\ \hline
2& 1& 4&1.0000&  8&2.3926\\
3& 3&10&1.1111& 17&2.8145\\
4& 6&19&1.1875& 29&3.0664\\
5&11&34&1.3600& 41&2.8493\\
6&17&48&1.3333& 60&3.2397\\
7&25&76&1.5510& 71&2.7314\\
8&34&103&1.6094&89&2.7328\\
9&44&130&1.6049&113&2.9183\\
10&55&152&1.5200&148&3.4021
\end{array}                                                     \tag{29}
\]

The exact test uses these rulers, in table order:

```python
rulers = [
    [0, 1], [0, 1, 3], [0, 1, 4, 6], [0, 1, 4, 9, 11],
    [0, 1, 4, 10, 12, 17],
    [0, 1, 4, 10, 18, 23, 25],
    [0, 1, 4, 9, 15, 22, 32, 34],
    [0, 1, 5, 12, 25, 27, 35, 41, 44],
    [0, 1, 6, 10, 23, 26, 34, 41, 53, 55],
]
```

For each `B` in `rulers`, put `p = len(B)` and `W = max(B)`, then run:

```python
S = {B[i] + B[j] for i in range(p) for j in range(i, p)}
D = {B[j] - B[i] for i in range(p) for j in range(i + 1, p)}
assert len(S) == p * (p + 1) // 2       # diagonals included
assert len(D) == p * (p - 1) // 2
bad = {s + d for s in S for d in D}    # unrestricted reuse allowed
M = next(x for x in range(2 * W + 1, 3 * W + 2) if x not in bad)
A0 = set(B) | {M - b for b in B}
```

The upper endpoint $3W+1$ is always legal by strict range separation.
For every row, direct unordered-sum enumeration of `A0` finds exactly one
repeated value, namely $M$, with multiplicity $p$.  Hence the table is
not a relaxation.  It shows that finite compression below $3p^2$ is
substantial, but its nine rows are not a parametric obstruction and cannot
be amplified by assertion.

## 6. Remaining lemma

The attempt leaves two coupled tasks, neither of which follows from raw
support cardinalities:

1. Prove the hole estimate (5), equivalently show that a dense Sidon ruler
   cannot keep $M$ out of $S(B)+\Delta^+(B)$ far below $3p^2$.
2. Control the unpaired residual $A\setminus P$ when $q=\Theta(k)$.
   Every difference involving an unpaired point is globally unique by (8),
   but the difference count alone does not pay for the missing sum support.

No reflection closure of $A$ was used.  In particular, adjoining missing
partners is not licensed by any argument above: it can create new low-cross
and high-cross collisions of exactly the form (23).  No uniform proof of
(1), and no infinite admissible family violating it, is claimed.
