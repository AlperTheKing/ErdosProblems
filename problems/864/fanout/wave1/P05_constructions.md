# P05: disproof-construction lane

## Verdict

No infinite admissible family with

\[
\limsup \frac{|A_N|}{\sqrt N}>\frac2{\sqrt3}
\]

was obtained.  This is not evidence that the conjecture is true.  The search
gave rigorous obstructions to the range-separated unbalanced/reflected class
and to mixed-radix Cartesian products, plus finite exact falsifiers for naive
algebraic lifts and conic stacking.  It also gave an exact
necessary-and-sufficient gate for compressed reflections.

There is a genuine finite over-constant example:

\[
A=\{1,3,4,8,17,23,32,36,37,39\}\subseteq[39].
\]

It is admissible, its sole repeated sum is

\[
40=1+39=3+37=4+36=8+32=17+23,
\]

and $10/\sqrt{39}>2/\sqrt3$.  Thus finite normalized excess cannot be used
as evidence for either asymptotic verdict.  The product obstruction below
shows why the most direct attempt to amplify this finite seed fails.

## 1. Exact gate for a compressed reflection

Let $B\subseteq[0,L]$, with $0,L\in B$, and let $M>2L$.  Put

\[
A_0=B\cup(M-B),\qquad
S(B)=\{b+b':b,b'\in B,\ b\leq b'\},
\]

and let

\[
\Delta^+(B)=\{b'-b:b,b'\in B,\ b<b'\}.
\]

### Reflection criterion

$A_0$ is admissible if and only if

1. $B$ is a Sidon set for literal unordered sums, including diagonals; and
2. $M\notin S(B)+\Delta^+(B)$.

When these conditions hold, the only possibly repeated sum is $M$, with
exactly $|B|$ representations $b+(M-b)$.  It is the sole repeated sum when
$|B|\geq2$.

**Proof.**  The three types of sums are

\[
S(B),\qquad M+(B-B),\qquad 2M-S(B).
\]

If a sum in $S(B)$ repeats, its reflected sum in $2M-S(B)$ also repeats.
They lie on opposite sides of $M$, so $A_0$ would have at least two
exceptional values.  Hence $B$ must be Sidon.  Sidonicity also says that
every nonzero signed difference of $B$ has one ordered representation;
therefore every cross sum except $M$ is unique, while difference zero gives
the $|B|$ central representations.

Because $M>2L$, a low sum and a high sum cannot coincide.  A low sum
$s\in S(B)$ equals a cross sum precisely when

\[
s=M+b-c,
\]

or equivalently $M=s+(c-b)\in S(B)+\Delta^+(B)$.  Such a collision at
$s<M$ reflects to a second collision at $2M-s>M$.  Thus no such collision
is allowable.  Conversely, if the displayed sumset misses $M$, all
noncentral sums are unique.  Diagonal pairs occur only inside the two copies
of $B$, and they were included in the Sidon check.  This proves the claim.

Equivalently, a compressed reflected disproof must produce Sidon sets $B_j$
of size $k_j\to\infty$ and centers $M_j>2\max B_j$ such that

\[
M_j\notin 3B_j-B_j
\quad\text{and}\quad
\limsup_j\frac{M_j}{k_j^2}<3.
\]

The first condition is literal: because $M_j>2\max B_j$, membership in
$3B_j-B_j$ is exactly membership in $S(B_j)+\Delta^+(B_j)$.  This is the
remaining reflected construction target; it is not resolved here.

### Exact finite survivor

Take

\[
B=\{0,2,3,7,16\},\quad L=16,\quad M=38.
\]

Its 15 unordered sums, diagonals included, are

\[
S(B)=\{0,2,3,4,5,6,7,9,10,14,16,18,19,23,32\},
\]

and its ten positive differences are

\[
\Delta^+(B)=\{1,2,3,4,5,7,9,13,14,16\}.
\]

Both lists have the required cardinalities, so $B$ is Sidon.  Moreover

\[
38-\Delta^+(B)=
\{22,24,25,29,31,33,34,35,36,37\},
\]

which is disjoint from $S(B)$.  The criterion proves that
$B\cup(38-B)$ is admissible.  Translating it by $1$ gives the set in the
verdict, and translation changes every pair sum by $2$, so its exception is
exactly $40$.  This proof includes the five diagonal sums of each reflected
Sidon block.

### Exact falsifier for over-compression

The same seed with $M=33$ gives, after translation by $1$,

\[
A=\{1,3,4,8,17,18,27,31,32,34\}\subseteq[34].
\]

It has at least the two distinct repeated sums

\[
21=3+18=4+17,
\qquad
34=3+31=17+17.
\]

The second collision contains a diagonal.  Thus this candidate fails the
literal convention, independently of any asymptotic estimate.

## 2. Range-separated and unbalanced reflected blocks

Let $X\subseteq[0,L_X]$ and $Y\subseteq[0,L_Y]$ be genuine Sidon sets and
consider

\[
A_0=X\cup(M-Y).
\]

The standard range-separated template assumes

\[
M>\max(2L_X+L_Y,\ L_X+2L_Y).
\tag{1}
\]

Indeed, its sum bands are

\[
X+X\subseteq[0,2L_X],
\]

\[
X+(M-Y)\subseteq[M-L_Y,M+L_X],
\]

and

\[
(M-Y)+(M-Y)\subseteq[2M-2L_Y,2M].
\]

Condition (1) makes these bands pairwise disjoint.  Cross-sum admissibility
can only impose additional restrictions, so it may be ignored for an upper
bound on the size of this construction class.

The interval Sidon bound, with diagonals included, gives uniformly

\[
|X|\leq(1+o(1))\sqrt{L_X},\qquad
|Y|\leq(1+o(1))\sqrt{L_Y}.
\]

After translating $A_0\subseteq[0,M]$ into $[M+1]$, (1) yields

\[
\frac{|A_0|}{\sqrt{M+1}}
\leq
\frac{\sqrt{L_X}+\sqrt{L_Y}+o(\sqrt M)}
{\sqrt{\max(2L_X+L_Y,L_X+2L_Y)}}
\leq \frac2{\sqrt3}+o(1).
\tag{2}
\]

For the last inequality assume $L_X\geq L_Y$ and put
$t=\sqrt{L_Y/L_X}\in[0,1]$.  Squaring (2) reduces to

\[
\frac{(1+t)^2}{2+t^2}\leq\frac43,
\]

which follows exactly from

\[
4(2+t^2)-3(1+t)^2=(1-t)(5-t)\geq0.
\]

Equality requires asymptotic balance $L_X/L_Y\to1$.  Therefore unbalancing
the two separated Sidon blocks cannot beat $2/\sqrt3$.

This includes the literal nested reflected family.  If $C\subseteq B$,
$B\subseteq[0,L]$ is Sidon, and $M>3L$, then

\[
B\cup(M-C)
\]

is admissible: nonzero cross differences are unique because all elements lie
in the Sidon set $B$, while difference zero gives the sole sum $M$, with
$|C|$ representations.  Both within-block diagonal conventions are covered
by Sidonicity.  Since $|C|\leq|B|$, the balanced choice $C=B$ is already
best in this entire nested class.

This obstruction is intentionally scoped to the two-Sidon-block template,
where the exception is the repeated cross sum.  Allowing an internally
exceptional block recursively restores Problem 864 inside the construction
and is not claimed to be settled by (2).

## 3. Algebraic attempts

### 3.1 Compact finite-field parabola: exact carry falsifier

For an odd prime $p$, a tempting integer lift of the finite-field parabola is

\[
P_p=\{1+x+p[x^2]_p:0\leq x<p\},
\]

where $[z]_p\in\{0,\ldots,p-1\}$ is the least residue.  Equality modulo $p$
would make the parabola Sidon, but base-$p$ carries couple the two coordinates.
At $p=7$ the literal set is

\[
P_7=\{1,9,14,18,19,31,34\},
\]

and it has the two distinct repeated sums

\[
28=9+19=14+14,
\qquad
32=1+31=14+18.
\]

The first collision contains a diagonal.  Thus this compact algebraic lift is
not even admissible for all primes, and it cannot serve as a reflected Sidon
block.  Using radix $2p$ removes carries and repairs Sidonicity, but doubles
the ambient scale and loses rather than gains in the normalized constant.

### 3.2 A carry-free inverse-conic family

There is a clean infinite algebraic family, but its constant is too small.
For an odd prime $p$, let $x^{-1}\in\{1,\ldots,p-1\}$ denote the inverse of
$x\pmod p$, and set

\[
H_p=\{x+2p x^{-1}:1\leq x<p\}.
\]

Then

\[
H_p\subseteq[1,2p^2-p-1],\qquad |H_p|=p-1.
\]

This family is literally admissible.  Suppose

\[
x+2p x^{-1}+y+2p y^{-1}
=u+2p u^{-1}+v+2p v^{-1}.
\]

All low-coordinate sums lie strictly between $0$ and $2p$, so equality
forces $x+y=u+v$ as integers and then
$x^{-1}+y^{-1}=u^{-1}+v^{-1}$.  Modulo $p$, if
$s=x+y\ne0$, then

\[
x^{-1}+y^{-1}=\frac{s}{xy}
\]

determines $xy$; hence the quadratic with roots $(x,y)$ also determines the
unordered pair.  If $s=0$, then $y=p-x$, and every such complementary pair
has the same literal sum

\[
E_p=p+2p^2.
\]

It has exactly $(p-1)/2$ unordered representations.  No diagonal occurs at
$E_p$, since $p$ is odd, and the preceding quadratic argument includes and
proves uniqueness of every other diagonal.  Therefore

\[
\frac{|H_p|}{\sqrt{2p^2-p-1}}\longrightarrow\frac1{\sqrt2},
\]

so this one-conic algebraic class is a rigorous sub-threshold family.

### 3.3 Stacking conics: exact falsifier

The direct attempt to gain cardinality by taking two inverse conics already
fails without carries.  With $p=5$, radix $2p=10$, and conic parameters
$c=1,2$, the union

\[
A=\{x+10[cx^{-1}]_5:c\in\{1,2\},\ 1\leq x<5\}
=\{11,12,21,23,32,34,43,44\}
\]

has the distinct repeated sums

\[
44=12+32=21+23,
\qquad
46=12+34=23+23.
\]

Again the second collision is diagonal.  Hence stacking full conics does not
produce a one-exception family; a restricted multi-conic construction would
need a genuinely new cross-conic design.

## 4. Product constructions

Let $X\subseteq[0,L]$, let $Y\subseteq\mathbb Z_{\geq0}$, and choose
$Q>2L$.  The carry-free Cartesian product is

\[
X\otimes_QY=\{x+Qy:x\in X,\ y\in Y\}.
\]

For every $x_0<x_1$ in $X$ and $y_0<y_1$ in $Y$, there is a rectangle
collision

\[
(x_0+Qy_0)+(x_1+Qy_1)
=(x_0+Qy_1)+(x_1+Qy_0).
\tag{3}
\]

The two unordered pairs in (3) are distinct.  Since $Q>2L$, different
coordinate-sum pairs give different integer sums.

More precisely, let

\[
T_X=\{x+x':x,x'\in X,\ x<x'\},
\qquad
T_Y=\{y+y':y,y'\in Y,\ y<y'\}.
\]

Then (3) produces at least $|T_X||T_Y|$ distinct repeated sum values.  If
$X$ is itself admissible and $|X|=m\geq2$, at most one off-diagonal sum can
repeat, and one fixed sum has at most $\lfloor m/2\rfloor$ disjoint
off-diagonal representations.  Consequently

\[
|T_X|\geq {m\choose2}-\left\lfloor\frac m2\right\rfloor+1,
\]

and analogously for $Y$.  Thus a product of two admissible factors has at
most one rectangle sum only when one factor is a singleton or both factors
have size $2$.  The $2$-by-$2$ product gives one finite rectangle
exception, but no product with two nontrivial growing factors, and no
nontrivial iterated product, can remain admissible.

The smallest useful exact falsifier is obtained from
$X=\{0,1\}$, $Y=\{0,1,3\}$, and $Q=3$.  After translation by $1$,

\[
A=\{1,2,4,5,10,11\}\subseteq[11]
\]

has exactly the three repeated sums

\[
6=1+5=2+4,
\]

\[
12=1+11=2+10,
\]

\[
15=4+11=5+10.
\]

All diagonal pairs were included in this enumeration and create no additional
collision.  This rules out mixed-radix Cartesian amplification of the finite
compressed-reflection survivor.

## 5. Construction frontier left by this lane

The searched classes therefore leave one precise non-product route to a
disproof.  It is enough to construct Sidon sets $B_j\subseteq[0,L_j]$ with
$|B_j|\to\infty$ and centers $M_j>2L_j$ for which

\[
M_j\notin S(B_j)+\Delta^+(B_j)
\]

and, for some fixed $\delta>0$,

\[
M_j\leq(3-\delta)|B_j|^2
\]

infinitely often.  The ten-element example proves that compression can happen
at finite scale.  The separated-block inequality and the product rectangle
theorem prove that neither unbalancing the known three-band construction nor
tensoring a finite compressed seed supplies the required asymptotic family.
No claim is made that a non-Cartesian algebraic or compressed reflected family
cannot do so.
