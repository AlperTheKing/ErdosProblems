# P17: amplification of finite compressed signed rulers

## Verdict

No finite compressed signed ruler was amplified into an infinite family in
this lane.  The natural product, mixed-radix, Costas-product, finite-type
graph-directed, and recursively guarded affine constructions all have exact
algebraic obstructions.  These obstructions occur already in the ordinary
Sidon condition, before the shifted-sum labels are considered.

There is one valid nontrivial *one-step* affine lift of the five-point seed,
but its exact span is

\[
 313>3\cdot 10^2.
\]

Thus it has already crossed to the non-counterexample side.  A standalone
Welch-Costas construction produces finite signed rulers below coefficient
three through order (18), but not at orders (22,28,30) in an exhaustive
radix sweep.  This is not an asymptotic theorem and is not an amplification
of a fixed seed.

The precise obstruction left by this report is:

> A disproof cannot be obtained by repeatedly inserting full affine copies
> of finitely many fixed blocks.  It would need a globally varying
> cross-fiber design, or an independently constructed infinite family of
> signed rulers.

All computations below use exact integers.  Reproducible code is in
`problems/864/compute/p17/amplification_audit.py`.

## 1. Signed-ruler normalization

Let

\[
 Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},\qquad G\ge 1.
\]

Write

\[
 D(Z)=\{z_j-z_i:i<j\},
 \qquad
 S(Z)=\{z_i+z_j:i\le j\}.
\]

The pair ((Z,G)) is a signed ruler when

\[
 |D(Z)|={p\choose2},\qquad
 |S(Z)|={p+1\choose2},\qquad
 D(Z)\cap(G+S(Z))=\varnothing.                 \tag{1}
\]

Its reflected admissible set has (2p) elements and span

\[
 L=G+2W.                                       \tag{2}
\]

Consequently an infinite family with (L/p^2<3-\delta) would disprove the
proposed constant in Problem 864.

## 2. Exact affine-fiber label formula

Let (X,Y\subseteq\mathbb Z_{\ge0}), let (c\ge1), and choose (T) so that
every point of (T+cY) is larger than every point of (X).  Put

\[
 Z'=X\mathbin{\dot\cup}(T+cY).
\]

The complete difference and sum labels are

\[
 \boxed{
 D(Z')=D(X)\mathbin{\dot\cup}cD(Y)
       \mathbin{\dot\cup}\{T+cy-x:x\in X,y\in Y\},}       \tag{3}
\]

and

\[
 \boxed{
 S(Z')=S(X)\mathbin{\dot\cup}
       \{T+x+cy:x\in X,y\in Y\}
       \mathbin{\dot\cup}(2T+cS(Y)).}                    \tag{4}
\]

The dots in (3)-(4) are requirements, not automatic assertions.  In
particular, two cross labels coincide exactly when

\[
 c(y-y')=x-x'.                                  \tag{5}
\]

Thus a necessary condition for either cross-label family to be injective is

\[
 D(X)\cap cD(Y)=\varnothing.                    \tag{6}
\]

Condition (6) is also necessary because (D(X)) and (cD(Y)) themselves
occur as internal differences in (3).  Translation guards (T) and the new
gap (G') cannot repair a failure of (6).  After (3)-(4) are disjoint
internally, the remaining signed-ruler test is the literal condition

\[
 D(Z')\cap(G'+S(Z'))=\varnothing.               \tag{7}
\]

Equations (3)-(7) are the full cross-fiber gate used in the computation.

## 3. Cartesian products and mixed-radix powers

Let (X,Y) each contain two distinct points and use an injective radix
encoding

\[
 P=X+QY=\{x+Qy:x\in X,y\in Y\}.
\]

Choose (x_0<x_1) and (y_0<y_1).  Then

\[
 \begin{aligned}
 &(x_0+Qy_0)+(x_1+Qy_1)\\
 &\qquad=(x_0+Qy_1)+(x_1+Qy_0).                 \tag{8}
 \end{aligned}
\]

The two unordered pairs are distinct.  Equivalently, the positive
difference (Q(y_1-y_0)) occurs once in the (x_0)-fiber and once in the
(x_1)-fiber.  Hence (P) is not Sidon, independently of carries, guards,
or (G).

This proves that every nontrivial Cartesian product and every digitwise
mixed-radix power of a fixed seed fails.  For the five-point seed and radix
100, the exact script returns the collision

\[
 0+404=4+400.                                   \tag{9}
\]

## 4. Guarded affine concatenation

Consider the five-point compressed seed

\[
 Z_5=\{0,4,9,11,12\},\qquad G=6.               \tag{10}
\]

Its difference set is

\[
 D(Z_5)=\{1,2,3,4,5,7,8,9,11,12\}.             \tag{11}
\]

For a two-copy lift

\[
 Z'=Z_5\cup(T+cZ_5)
\]

or the version with the upper copy reversed, (6) forces (c\ge10).  Indeed,
for (c=1,2,3,4,5,7,8,9), the number (c=c\cdot1) lies in both internal
difference sets, while for (c=6),

\[
 12=6\cdot2
\]

lies in both.  Thus every (c<10) is impossible before (T) is chosen.

The exact exhaustive search over (c=10,11,12), both orientations, and all
translations capable of beating the displayed answer gives the unique
minimum span

\[
 \begin{aligned}
 Z_{10}={}&\{0,4,9,11,12,25,65,115,135,145\},\\
 G_{10}={}&23,\\
 L_{10}={}&23+2\cdot145=313.                    \tag{12}
 \end{aligned}
\]

The literal certificate is

\[
 |D(Z_{10})|=45,qquad |S(Z_{10})|=55,qquad
 D(Z_{10})\cap(23+S(Z_{10}))=\varnothing.       \tag{13}
\]

For (c\ge13), even the smallest separated translation gives

\[
 G'+2\max Z'\ge1+2(13+13\cdot12)=339>313.       \tag{14}
\]

For (c=10,11,12), any translation beyond the enumerated range is already
larger than 313 by the same monotonic width bound.  Therefore (12) is the
global optimum among separated two-affine-copy lifts of this seed.  Since

\[
 313>3\cdot10^2,                                \tag{15}
\]

even the first valid lift does not disprove the target.

As an exact diagnostic, the least positive scale (c) satisfying the
translation-independent condition (D(Z)\cap cD(Z)=\varnothing) is

\[
 \begin{array}{c|ccc}
 Z&Z_5&Z_9&Z_{10}\\ \hline
 \min c&10&22&32,
 \end{array}                                    \tag{16}
\]

where (Z_9) is the optimal nine-point ruler in P07.  This explains the
rapid deterioration of a second guarded lift.

## 5. Recursive affine copies cannot amplify a seed

The preceding finite calculation has a general explanation.

### Theorem 1 (binary affine recursion obstruction)

Let (C\subset\mathbb Z) contain at least two points.  At level (j), use
two full-copy branches with absolute scales (1) and (q_j\ge2), allowing
arbitrary translations and reflections.  Suppose that after (n) levels
the (2^n) terminal copies are pairwise disjoint, so the resulting union has

\[
 p_n=2^n|C|
\]

points.  If the union is Sidon, then all subset products

\[
 \prod_{j\in I}q_j,\qquad I\subseteq\{1,\ldots,n\},        \tag{17}
\]

are distinct.  Consequently

\[
 \frac{L_n}{p_n^2}
 \ge
 \frac{2\operatorname{width}(C)(n+1)!}
      {4^n|C|^2}longrightarrow\infty.           \tag{18}
\]

#### Proof

Each leaf is a translated or reflected copy of (C) with absolute scale
equal to one subset product in (17).  If two leaves had the same absolute
scale, any fixed positive difference of (C) would occur in both leaves.
The leaves are disjoint, so these are distinct realizing pairs, contradicting
Sidonicity.  Hence all subset products are distinct.

In particular the singleton products (q_1,\ldots,q_n) are distinct
integers at least two.  After sorting them,

\[
 q_j\ge j+1,qquad \prod_{j=1}^nq_j\ge(n+1)!.     \tag{19}
\]

The all-scaled leaf has width

\[
 \operatorname{width}(C)\prod_jq_j.
\]

Translations can only make the width of the whole union at least this leaf
width.  Since every signed-ruler span is at least twice its ruler width,
(18) follows.  QED.

Thus choosing bounded scales repeats a leaf scale and immediately creates a
difference collision.  Choosing enough distinct scales to avoid that
collision makes the span factorially larger than the square of the number of
points.  Guards do not enter either conclusion.

### Corollary 2 (finite-type graph-directed obstruction)

Consider a graph-directed affine substitution with finitely many terminal
block types and a finite alphabet of nonzero integer scales.  Include
orientation in the block type.  If the number of disjoint terminal copies at
depth (n) grows exponentially, then the union is not Sidon for all large
(n).

Indeed, with (r) absolute scale values, a length-(n) path has a total
scale determined by a multiplicity vector of size (r).  There are at most

\[
 {n+r-1\choose r-1}                            \tag{20}
\]

such vectors.  Multiplying by the finite number of terminal types still
gives only polynomially many type-scale pairs.  Exponentially many leaves
therefore contain two translated copies of the same type at the same scale,
which duplicate an internal difference.

This covers fixed finite substitution systems.  A scheme with globally new
block types or scales at every level is not covered, but then it is no longer
an amplification of a fixed finite compressed ruler.

## 6. Costas and permutation compositions

One-point-per-fiber constructions avoid the Cartesian rectangle, but the
standard Kronecker composition of two permutations does not.

Let (pi) have order (m\ge2), let (	au) have order (n\ge2), and set

\[
 \rho(in+j)=n\pi(i)+\tau(j).                    \tag{21}
\]

For any (j<k), the displacement

\[
 (k-j,\tau(k)-\tau(j))                          \tag{22}
\]

occurs inside every coarse block (i).  Thus (ho) is not Costas.  Under
any integer flattening (a\mapsto a+Q\rho(a)), the literal positive
difference

\[
 (k-j)+Q(\tau(k)-\tau(j))                       \tag{23}
\]

is repeated.  The transposed block composition has the same obstruction.
This kills Costas tensoring and permutation block substitution of a fixed
seed.

A single Welch permutation is a different construction, not a composition.
For context, the exact script checked every primitive root, cyclic shift,
both coordinate flattenings, and every integer radix (1\le Q\le3p) for
prime orders through (31).  The best valid signed rulers at each available
order were:

\[
\begin{array}{c|rrrrrrrrrr}
p&2&4&6&10&12&16&18&22&28&30\\ \hline
L&4&20&62&213&368&691&935&1455&2634&3156.
\end{array}                                     \tag{24}
\]

This radix range includes every candidate capable of (L<3p^2).  Indeed,
because a permutation uses both ordinates (0) and (p-1), its flattened
width is at least

\[
 (Q-1)(p-1),                                    \tag{25}
\]

so larger (Q) already forces (2W+1\ge3p^2).

The exact ratios in the last four relevant cases are

\[
 \frac{935}{324}<3,qquad
 \frac{1455}{484}>3,qquad
 \frac{2634}{784}>3,qquad
 \frac{3156}{900}>3.                            \tag{26}
\]

Equation (24) is finite evidence only.  It neither proves that Welch rulers
eventually stay above three nor excludes a later sub-three subsequence.  It
does show that the finite compressed seed is not being amplified by the
permutation-product mechanism.

## 7. Scope of the negative result

The exact collision mechanisms are now separated:

1. Cartesian and mixed-radix powers fail by the rectangle identity (8).
2. Repeated translated fibers fail because internal differences ignore
   guards.
3. Distinct-scale binary recursion either repeats a total scale or has the
   factorial lower bound (18).
4. Finite-type graph-directed systems repeat a type-scale pair by (20).
5. Kronecker Costas/permutation composition repeats the displacement (22).
6. The best possible one-step affine lift of the (p=5) seed is the valid
   but supercritical ruler (12).

Therefore none of these natural amplification mechanisms supplies an
infinite family with

\[
 \liminf\frac{G+2W}{p^2}<3.
\]

This does **not** prove the Problem 864 upper bound.  A negative resolution
could still come from a new algebraic family whose fibers vary globally with
the order, or from a non-affine construction.  Such a family would need its
cross-fiber labels designed simultaneously; it cannot inherit validity from
a fixed finite seed by any composition covered above.

## 8. Reproduction commands

The principal exact audit is

```text
python problems/864/compute/p17/amplification_audit.py \
  --max-prime 31 --radix-factor 3 \
  --max-scale 12 --translation-factor 8
```

The literal certificate for (12) returns

```text
45 45 55 55 0 313
```

meaning 45 distinct differences, 55 distinct unordered sums including
diagonals, zero intersections with (23+S(Z_{10})), and span 313.
