# P56: reflected core, residual labels, and completion defect

## Verdict

There is an exact, noncircular reduction to a fully reflected admissible
set, but it requires a collision defect. Let $A$ be admissible with
exceptional sum $\sigma$, and write

\[
 P=A\cap(\sigma-A),\qquad R=A\setminus P,
\]

\[
 |P|=c=2p+\delta,\qquad |R|=u,\qquad |A|=k=c+u,
\]

where $\delta=1$ exactly when $\sigma/2\in A$. Reflect $R$ virtually and put

\[
 F=A\cup(\sigma-R),\qquad
 Q=\bigl\{|r_i+r_j-\sigma|:1\leq i\leq j\leq u\bigr\}
\]

as a multiset. If $D^+(X)$ denotes the support of the positive differences
of $X$, define

\[
 \boxed{\beta=(p+u)(p+u+\delta)-|D^+(F)|.}                 \tag{1}
\]

Then $\beta\geq0$, and it is exactly the collision excess of the virtual
labels $Q$ against each other and against $D^+(A)$. There is a set
$X\subseteq R$ with

\[
 |X|\leq\min(u,\beta)                                    \tag{2}
\]

such that

\[
 F_X=P\cup(R\setminus X)\cup(\sigma-(R\setminus X))       \tag{3}
\]

is fully reflected and admissible. Thus one collision excess costs at most
one residual reflection-pair, with constant exactly $1$.

Let

\[
 \tau=|\sigma-\min A-\max A|,
\]

and let $H_\delta(q)$ be the minimum span of a fully reflected admissible
set with $q$ off-diagonal reflected pairs and midpoint flag $\delta$.
Writing $b=\min(u,\beta)$, the exact reduction is

\[
 \boxed{
   \operatorname{span}(A)+\tau
   \ \geq\ H_\delta(p+u-b).
 }                                                         \tag{4}
\]

No hypothesis on $u/k$ occurs. If the fully reflected hard regime is
available in the quantified form

\[
 H_\delta(q)\geq {3\over4}(2q+\delta)^2-E_\delta(q),       \tag{5}
\]

then (4) gives

\[
 \boxed{
 \operatorname{span}(A)
 \geq {3\over4}(k+u-2b)^2
      -E_\delta(p+u-b)-\tau.
 }                                                         \tag{6}
\]

The explicit residual credit over the desired $\tfrac34k^2$ is therefore

\[
 {3\over4}\bigl((k+u-2b)^2-k^2\bigr)
 ={3\over4}(u-2b)(2k+u-2b).                              \tag{7}
\]

Consequently the fully reflected theorem proves the general sharp bound
whenever this credit pays the reflection shift and the error in (5). The
remaining structural frontier is now explicit: too many completion blockers
($b>u/2$) or a large shift $\tau$, rather than an unjustified claim that
$u=o(k)$.

The natural stronger candidate $\beta=0$, even when $\tau=0$, is false. The
smallest exact falsifier is

\[
 A=\{0,2,3,6\},\qquad \sigma=6,\qquad
 P=\{0,3,6\},\quad R=\{2\}.                              \tag{8}
\]

Here the sole virtual label is $|2+2-6|=2\in D^+(A)$, so $\beta=1$. The
completion $\{0,2,3,4,6\}$ has repeated sums $4,6,8$. Exhaustive enumeration
proves that no endpoint-normalized example of smaller span has a blocked
completion.

## 1. Exact residual sum and difference accounting

Let $S_P$ be the support of unordered sums represented inside $P$, and let
$S_R$ be the support of unordered sums whose pair touches $R$. Diagonals are
included. Define $D_P,D_R$ analogously for positive differences, with
diagonals omitted.

Every sum represented by a pair touching $R$ is unique, and no such sum lies
in $S_P$. Indeed, a pair touching $R$ cannot sum to $\sigma$, since both
endpoints would then have partners and belong to $P$. Any other collision is
forbidden by admissibility.

Every positive difference represented by a pair touching $R$ is also
globally unique and lies outside $D_P$. If

\[
 x-y=v-w>0
\]

are distinct representations, then $x+w=v+y$. Admissibility forces this
common sum to be $\sigma$, so

\[
 (v,w)=(\sigma-y,\sigma-x).
\]

All four endpoints therefore lie in $P$. This is impossible if either
difference pair touches $R$.

It follows, with no asymptotic error, that

\[
\begin{aligned}
 |S_P|&=2p(p+\delta)+1,
 &|S_R|&=cu+\binom{u+1}{2},\\
 |D_P|&=p(p+\delta),
 &|D_R|&=cu+\binom u2.                                  \tag{9}
\end{aligned}
\]

The two entries in each row are disjoint. The core counts follow by counting
its unordered pairs and removing the $p+\delta-1$ excess representations of
$\sigma$, or by counting the reflected difference orbits. The residual
counts are simply the numbers of pairs touching $R$, since the maps to
labels are injective.

If $L=\max A-\min A$, all sums occupy an interval of $2L+1$ integers and all
positive differences lie in $[1,L]$. Hence (9) gives both exact packing
inequalities

\[
 \boxed{
  2p(p+\delta)+cu+\binom{u+1}{2}\leq2L,
 }                                                        \tag{10}
\]

\[
 \boxed{
  p(p+\delta)+cu+\binom u2\leq L.
 }                                                        \tag{11}
\]

There is also an exact coupling between the cross sums and cross
differences. Reflection permutes $P$, so as multisets

\[
 \boxed{
 \{|r+x-\sigma|:r\in R,x\in P\}
 =\{|r-x|:r\in R,x\in P\}.
 }                                                        \tag{12}
\]

Both sides consist of $cu$ distinct positive labels. Thus the $P+R$ sum
labels do not provide an independent second penalty after folding; the
genuinely new completion data are the $R+R$ labels in $Q$.

## 2. Virtual completion criterion

The reflected set $\sigma-R$ is disjoint from $A$, by the definition of
$R$. Every positive difference in

\[
 F=P\mathbin{\dot\cup}R\mathbin{\dot\cup}(\sigma-R)
\]

has one of four endpoint types.

* Differences inside $A$ give $D^+(A)$.
* Differences inside $\sigma-R$ reflect differences inside $R$.
* Differences between $P$ and $\sigma-R$ reflect differences between $P$
  and $R$.
* A difference between $r_i$ and $\sigma-r_j$ is
  $|r_i+r_j-\sigma|$. Reflection swaps $i,j$, so these new reflection orbits
  are indexed by unordered pairs $i\leq j$.

Therefore

\[
 \boxed{D^+(F)=D^+(A)\cup\operatorname{supp}Q.}          \tag{13}
\]

The union in (13) need not be disjoint. The old orbit labels are already
distinct by admissibility of $A$, while the number of old and virtual orbit
classes is

\[
\begin{aligned}
 |D^+(A)|+\binom{u+1}{2}
 &=p(p+\delta)+cu+\binom u2+\binom{u+1}{2}\\
 &=(p+u)(p+u+\delta).                                   \tag{14}
\end{aligned}
\]

For $d>0$, let

\[
 a_d=1_{\{d\in D^+(A)\}},\qquad
 q_d=\#\{\{i,j\}:i\leq j,\ |r_i+r_j-\sigma|=d\}.
\]

Equations (1), (13), and (14) give the equivalent exact formulas

\[
 \boxed{
 \beta=\sum_{d>0}(a_d+q_d-1)_+
 =\binom{u+1}{2}
  -|\operatorname{supp}Q\setminus D^+(A)|.
 }                                                        \tag{15}
\]

Because $F$ is fully reflected, its positive-difference representations are
partitioned into reflection orbits. It is admissible exactly when no two
different orbits have the same label. By (13), this is equivalent to

\[
 q_d\leq1\quad\hbox{and}\quad a_dq_d=0
 \qquad(d>0).                                             \tag{16}
\]

Thus

\[
 \boxed{F\text{ is admissible}\quad\Longleftrightarrow\quad\beta=0.}
                                                                  \tag{17}
\]

This criterion includes the diagonal virtual pairs $i=j$. Their labels
$|2r_i-\sigma|$ are positive because a residual point cannot be the
exceptional midpoint.

## 3. Collision-repair lemma

**Lemma P56.1 (unit-cost reflected repair).** With the notation above, there
exists $X\subseteq R$ satisfying (2) such that $F_X$ in (3) is fully
reflected and admissible.

**Proof.** For each label $d$, inspect the $q_d$ virtual unordered pairs
which give $d$.

* If $a_d=1$, mark all $q_d$ virtual pairs.
* If $a_d=0$, leave one virtual pair unmarked and mark the remaining
  $(q_d-1)_+$.

By (15), exactly $\beta$ virtual pairs are marked. From each marked pair
choose one of its residual endpoints, and let $X$ be the union of the chosen
endpoints. Then $|X|\leq\beta$, and of course $|X|\leq u$.

After deleting $X$ and its reflections, every surviving virtual pair was
unmarked. At most one survives at each label, and its label is outside
$D^+(A)$. The old difference orbits of the remaining set form a subset of
the old orbits of $A$, so they remain collision-free. Criterion (16) now
proves that $F_X$ is admissible. It is fully reflected by its definition.
QED.

The coefficient $1$ in (2) is attained by (8): $\beta=u=1$, and the only
repair obtained by this construction deletes the residual point.

## 4. Reduction to the hard regime

Put $a=\min A$ and $z=\max A$. The interval containing the reflection
$\sigma-A$ is $[\sigma-z,\sigma-a]$, a translate of $[a,z]$ by
$\sigma-a-z$. Hence

\[
 \boxed{
 \operatorname{span}(A\cup(\sigma-A))
 =L+|\sigma-a-z|=L+\tau.
 }                                                        \tag{18}
\]

The function $H_\delta(q)$ is nondecreasing in $q$: deleting a complete
off-diagonal reflected pair preserves admissibility and the midpoint flag
and cannot increase span. Lemma P56.1 leaves
$q'=p+u-|X|\geq p+u-b$ reflected pairs. Since $F_X\subseteq F$,

\[
 L+\tau\geq\operatorname{span}(F_X)
 \geq H_\delta(q')\geq H_\delta(p+u-b),
\]

which proves (4). Substitution of (5), followed by

\[
 2(p+u-b)+\delta=k+u-2b,
\]

proves (6). This uses only the fully reflected estimate (5), the explicit
integer defect $\beta$, and the exact geometry (18); it does not assume the
desired general bound or any smallness of $R$.

## 5. Smallest completion falsifier

For (8), the unordered sum fibres of $A$ are singletons except

\[
 0+6=3+3=6.
\]

Thus $A$ is admissible, with $p=1,\delta=1,c=3,u=1$. Its positive
difference support is

\[
 D^+(A)=\{1,2,3,4,6\}.
\]

The missing reflection of $2$ is $4$, and the virtual self-pair has label

\[
 |2-(6-2)|=|2+2-6|=2.
\]

This collides with the existing difference $2-0=2$, so (15) gives
$\beta=1$. In the same-span completion

\[
 F=\{0,2,3,4,6\}
\]

the repeated fibres are exactly

\[
 0+4=2+2=4,
\]

\[
 0+6=2+4=3+3=6,
\]

\[
 2+6=4+4=8.
\]

So admissibility of $A$ does not license even one same-span reflected
completion. The repair lemma deletes $2$ and returns the fully reflected
core $\{0,3,6\}$.

## 6. Exact computation

The auditor is

~~~text
problems/864/compute/p56/audit_reflected_residual.py
~~~

and the exhaustive command is

~~~text
python -B problems/864/compute/p56/audit_reflected_residual.py \
  --max-n 22 \
  --output problems/864/compute/p56/census_N22.json
~~~

It enumerates every endpoint-normalized subset
$A\subseteq[0,N-1]$ with both endpoints present for $2\leq N\leq22$:

\[
 \sum_{N=2}^{22}2^{N-2}=2,097,151
\]

subsets. Exact incremental sum counting found $11,969$ admissible sets. Of
these, $8,458$ have a repeated exceptional sum and $u>0$. The completion
split is

\[
\begin{array}{c|r}
\text{class}&\text{count}\\ \hline
\beta=0&5,582\\
\beta>0&2,876\\
\tau=0&2,136\\
\tau=0,\ \beta>0&982
\end{array}
\]

For every one of the $8,458$ records, the program independently rebuilds
all unordered sums and positive differences and checks (9), (12)--(18), the
completion criterion, and the repaired set produced in Lemma P56.1. All
checks use integer arithmetic. The first blocked record is (8); all
endpoint-normalized sets with $N\leq6$ were exhausted before it. Since every
finite integer set translates into this normalization, (8) is the
smallest-span exact falsifier to collision-free virtual completion.

The machine-readable certificate, including every blocking label for the
extremal records and the repeated fibres of their completions, is

~~~text
problems/864/compute/p56/census_N22.json
~~~
