# P24: ordered endpoint-shadow packing for three-free Sidon sets

## Verdict

Write $3E=E+E+E$, with repetitions allowed.  The exact reformulation used
throughout this lane is:

> A positive integer set $E$ of size $q$ is valid signed-ruler data if and
> only if (i) all elements have one parity, (ii) $E$ is Sidon including
> diagonals, and (iii) $E\cap3E=\varnothing$, repetitions allowed.

The sharp target is

\[
                     \max E\geq(3-o(1))q^2.                 \tag{P24.1}
\]

This note proves a new necessary inequality in the current #864 dossier.  It
uses the actual order on $[1,\max E]$: every sufficiently low pair sum
translates both endpoints of a represented difference to a pair of holes.
The translation is injective, distance by distance.  This gives an exact
upper bound by the autocorrelation of the holes, not by scalar interval
occupation.

The inequality does not by itself prove (P24.1).  It gives a concrete new
frontier: lower-bound the resulting ordered pair-sum count for a dense Sidon
ruler in the overlap regime $G<W$.  An exhaustive exact audit passed all
2,861 signed rulers with $W\leq14$, $G\leq15$, and $2\leq q\leq6$, as
well as the known witnesses through $q=12$.

## 1. Notation

Let

\[
 E=\{e_1<e_2<\cdots<e_q=M\}
\]

satisfy the three conditions above, and let

\[
 \epsilon=M\pmod 2,\qquad
 \mathcal P_M=\{n\in[1,M]:n\equiv\epsilon\pmod2\},
 \qquad R=|\mathcal P_M|=\frac{M+\epsilon}{2}.           \tag{P24.2}
\]

The available holes and the low triple-sum shadow are

\[
 H=\mathcal P_M\setminus E,
 \qquad T=3E\cap[1,M].                                  \tag{P24.3}
\]

The parity and three-free hypotheses give $T\subseteq H$, and

\[
 |H|=R-q.                                                \tag{P24.4}
\]

For real $t$, put

\[
 F(t)=|E\cap[1,t]|,
 \qquad
 B(t)=\#\{(a,b):a,b\in E,\ a\leq b,\ a+b\leq t\}.       \tag{P24.5}
\]

Thus diagonals are included in $B(t)$.  For an even positive integer $d$,
define

\[
 h(d)=|\{u:u,u+d\in H\}|,
 \qquad
 \tau(d)=|\{u:u,u+d\in T\}|.                           \tag{P24.6}
\]

## 2. The endpoint-shadow inequality

**Theorem 1 (exact represented-distance capacity).**  For every
$1\leq i<j\leq q$, with $d=e_j-e_i$,

\[
 \boxed{
 B(M-e_j)\leq \tau(d)\leq h(d)
 =R-\frac d2-F(M-d)-q+F(d)+1.}                          \tag{P24.7}
\]

Consequently, if

\[
 Q(E)=\sum_{1\leq i<j\leq q}B(M-e_j)
     =\sum_{j=2}^q(j-1)B(M-e_j),                        \tag{P24.8}
\]

then, writing $D(E)=\{e_j-e_i:i<j\}$,

\[
 \boxed{
 Q(E)\leq\sum_{d\in D(E)}\tau(d)
 \leq
 \min\left\{\binom{|T|}{2},\ \sum_{d\in D(E)}h(d)\right\}
 \leq\binom{R-q}{2}.}                                  \tag{P24.9}
\]

In particular the triple-sum shadow itself obeys

\[
 |T|\geq
 \left\lceil\frac{1+\sqrt{1+8Q(E)}}2\right\rceil.      \tag{P24.10}
\]

More generally, every nonnegative weight $w:D(E)\to\mathbb R_{\geq0}$
gives the distance-sensitive inequality

\[
 \sum_{i<j}w(e_j-e_i)B(M-e_j)
 \leq\sum_{i<j}w(e_j-e_i)h(e_j-e_i).                   \tag{P24.11}
\]

### Proof

Sidonicity, including diagonals, has two consequences used below.

First, all unordered pair sums $a+b$, $a\leq b$, are distinct.  Second,
every positive difference has a unique ordered endpoint pair.  Indeed, if

\[
 y-x=v-u>0,
\]

then $y+u=v+x$; Sidonicity identifies the two unordered pairs, and the
positive orientation gives $(x,y)=(u,v)$.

Fix $i<j$, put $d=e_j-e_i$, and take an unordered pair $a\leq b$ from
$E$ with

\[
 s=a+b\leq M-e_j.                                      \tag{P24.12}
\]

Map it to the two-point set

\[
 \{e_i+s,e_j+s\}.                                      \tag{P24.13}
\]

Both points are at most $M$, have the common parity of $E$, and belong to
$3E$.  Since $E\cap3E=\varnothing$, both lie in $T\subseteq H$.  Their
difference is exactly $d$.

The map is globally injective.  A target pair $\{u,v\}$ with $u<v$ first determines
$d=v-u$.  Uniqueness of positive differences recovers $(e_i,e_j)$; then
$s=u-e_i$.  Uniqueness of unordered pair sums then recovers $\{a,b\}$.
This proves the first two inequalities in (P24.7), and summing the injection
over all represented differences proves the first parts of (P24.9).

It remains to calculate $h(d)$.  There are exactly $R-d/2$ pairs
$(u,u+d)$ in the parity progression $\mathcal P_M$.  Of these,

\[
 F(M-d)
\]

have $u\in E$, while

\[
 q-F(d)
\]

have $u+d\in E$.  Their intersection consists of the unique pair of
elements of $E$ at difference $d$.  Inclusion-exclusion therefore gives

\[
 h(d)=R-\frac d2-F(M-d)-(q-F(d))+1,                    \tag{P24.14}
\]

which is (P24.7).  Distinct values of $d$ classify disjoint sets of hole
pairs, so their total is at most $\binom{|H|}{2}$.  The same statement for
$T$, followed by $T\subseteq H$, completes (P24.9).  Solving
$\binom{|T|}{2}\geq Q(E)$ gives (P24.10), and multiplying each separate
inequality by $w(d)\geq0$ gives (P24.11).  QED.

## 3. An interval-slice corollary

Theorem 1 immediately gives a form involving only ordered prefix counts.  For
every real $0\leq t\leq M$,

\[
 \boxed{
 \binom{F(M-t)}2 B(t)
 \leq
 \sum_{\substack{i<j\\e_j\leq M-t}}h(e_j-e_i).}        \tag{P24.15}
\]

Indeed, there are $\binom{F(M-t)}2$ endpoint pairs with
$e_j\leq M-t$, and each has $B(M-e_j)\geq B(t)$.

All pair sums formed from $E\cap[1,t/2]$, including diagonals, are counted
by $B(t)$.  Hence the fully explicit slice inequality is

\[
 \boxed{
 \binom{F(M-t)}2
 \binom{F(t/2)+1}{2}
 \leq
 \sum_{\substack{i<j\\e_j\leq M-t}}h(e_j-e_i)
 \leq\binom{R-q}{2}.}                                  \tag{P24.16}
\]

Unlike a scalar cutoff occupation bound, the middle term retains each
represented distance and the autocorrelation of the complement of $E$ at
that distance.

## 4. Exact signed-ruler form

Return to

\[
 Z=\{0=z_0<z_1<\cdots<z_{q-1}=W\},\qquad
 E=G+2Z,\qquad M=G+2W.                                 \tag{P24.17}
\]

Put

\[
 K=W-G,
 \qquad
 B_Z(u)=\#\{(a,b):0\leq a\leq b<q,\ z_a+z_b\leq u\}.  \tag{P24.18}
\]

A direct calculation gives

\[
 \begin{aligned}
 B_E(M-e_j)
 &=\#\{a\leq b:2G+2z_a+2z_b\leq2W-2z_j\}\\
 &=B_Z(K-z_j).
 \end{aligned}                                         \tag{P24.19}
\]

Thus the ordered shadow charge is exactly

\[
 \boxed{Q(E)=\sum_{j=1}^{q-1}j\,B_Z(K-z_j).}           \tag{P24.20}
\]

This exhibits the one-sided datum.  The left side counts precisely the
configurations

\[
 z_a+z_b+z_j\leq W-G.                                  \tag{P24.21}
\]

If $G\geq W$, it vanishes; this is the range-separated regime.  If $G<W$,
it measures the actual nonwrapping triple-sum shadow entering below the right
endpoint $M$.

For completeness, the right side also has a ruler-coordinate formula.  Let
$b=1$ when $G$ is odd and $b=2$ when $G$ is even, and put

\[
 \gamma=\frac{G-b}{2},\qquad R=\gamma+W+1.             \tag{P24.22}
\]

The parity slots identify with $[0,R-1]$, while $E$ identifies with
$\gamma+Z$.  If $\delta=z_j-z_i$, then

\[
 \boxed{
 B_Z(K-z_j)\leq
 R-\delta
 -|Z\cap[0,W-\delta]|
 -|Z\cap[\delta-\gamma,W]|+1.}                         \tag{P24.23}
\]

Equation (P24.23) is (P24.7) after dividing the represented difference by
two.  It is an endpoint inequality for the same ruler $Z$, not an
independent density relaxation.

## 5. Why the known barriers do not subsume it

P13's coefficient-two countermodel retains weak occupation of difference and
shifted-sum labels.  It does not retain the two-point complement correlation

\[
                    h(d)=|H\cap(H-d)|                  \tag{P24.24}
\]

at each difference generated by the same endpoint pair.  The map (P24.13)
uses exactly that missing coupling.

P15's Singer models retain cyclic phase at modulus about $2q^2$, but they
wind around the modulus.  Conditions (P24.12) and (P24.21) use the literal
right endpoint and have no wrapped interpretation.  Thus (P24.7) is
one-sided interval data rather than another cyclic Fourier constraint.

The local novelty claim is deliberately limited.  No version of
(P24.7)--(P24.23) occurs in the existing P01--P21 lanes, and P14's audited
mixed-$B(3,1)$, Sidon-sumset, and (3B-B)-hole sources do not state this
represented-distance shadow injection.  This note does not claim a global
literature first beyond that audited corpus.

## 6. Equality and exact falsifiers to stronger guesses

The set

\[
                         E=\{2,4,14\}                   \tag{P24.25}
\]

is valid.  Its unordered pair sums, including diagonals, are

\[
 \{4,6,8,16,18,28\},                                   \tag{P24.26}
\]

and

\[
 3E\cap[1,14]=H=\{6,8,10,12\}.                         \tag{P24.27}
\]

For the endpoint pair $(2,4)$, the three sums $4,6,8\leq14-4$ map to

\[
 \{6,8\},\quad\{8,10\},\quad\{10,12\}.               \tag{P24.28}
\]

They exhaust the hole pairs at represented difference $2$.  The other two
represented differences have zero source and zero capacity.  Therefore

\[
             Q(E)=\sum_{d\in D(E)}h(d)=3.              \tag{P24.29}
\]

So no universal positive slack can be added to Theorem 1.

The tempting stronger assertion that the truncated translates

\[
 (E+s)\cap[1,M],\qquad s\in E+E,                       \tag{P24.30}
\]

are disjoint is false.  For the valid set $E=\{1,7,11\}$, the distinct pair
sums $2$ and $8$ give

\[
 (E+2)\cap[1,11]=\{3,9\},\qquad
 (E+8)\cap[1,11]=\{9\}.                               \tag{P24.31}
\]

Their intersection is exactly $\{9\}$.  The proof of Theorem 1 needs only
that two translates cannot share a *pair* of points, which follows from
difference uniqueness.

Nor may low triple sums be treated as uniquely represented.  The valid set

\[
 E=\{1,7,19,23\}                                      \tag{P24.32}
\]

has the exact collision

\[
                   21=1+1+19=7+7+7.                   \tag{P24.33}
\]

The endpoint-shadow injection survives both falsifiers because it records
two-point translated edges, not isolated triple-sum values.

## 7. Exact computational audit

The standalone verifier is

```text
problems/864/compute/p24/verify_endpoint_shadow.py
```

It uses integer arithmetic only.  It enumerates every

\[
 0=z_0<\cdots<z_{q-1}=W,\qquad
 1\leq W\leq14,\qquad1\leq G\leq15,\qquad2\leq q\leq6,
\]

checks Sidonicity including diagonals and

\[
 D(Z)\cap(G+S(Z))=\varnothing,
\]

then independently checks:

1. the exact reformulation for $E=G+2Z$, including repeated summands in
   $3E$;
2. every per-distance inequality and the exact formula (P24.7);
3. every integer instance of the slice inequality (P24.15);
4. the equality and falsifier certificates above;
5. the known signed-ruler witnesses for $q=2,\ldots,12$.

Reproduction command and output:

```text
> python problems/864/compute/p24/verify_endpoint_shadow.py
PASS: ordered endpoint-shadow audit
small signed rulers: 2861
represented differences: 14405
integer interval slices: 93494
equality: E=(2, 4, 14), Q=3, hole-edge capacity=3
translate collision: [3, 9] intersect [9] = [9]
repeated shadow: 21 = 1+1+19 = 7+7+7
known signed-ruler witnesses: q=2..12
```

## 8. Remaining frontier

For a Sidon ruler $Z\subseteq[0,W]$, the classical asymptotic interval
bound is $W\geq(1-o(1))q^2$.  Hence $G\geq W$ already gives

\[
 M=G+2W\geq3W\geq(3-o(1))q^2.                          \tag{P24.34}
\]

Only $K=W-G>0$ remains.  In this regime (P24.20) gives an exact ordered
quantity that must fit into the represented-distance autocorrelation of the
holes.  A completion along this lane would prove that any fixed quadratic
overlap $K\geq\eta q^2$, together with near-minimal Sidon span, makes some
weighted version of (P24.11) impossible.  No such distribution lower bound
is proved here, so (P24.1) remains open.
