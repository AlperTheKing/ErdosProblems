# P48: recursive constructions and separated-scale obstruction

## Verdict

No explicit infinite family of positive same-parity Sidon sets $E$ with

\[
 E\cap3E=\varnothing,\qquad
 \liminf {\max E\over |E|^2}<3
\]

was obtained. Sidonicity includes diagonal pair sums, and $3E$ allows
repeated summands.

There is a rigorous obstruction for a broad construction class. The two
component rulers may vary arbitrarily with the parameter; they need not be
copies of one seed, algebraic, balanced, or individually three-sum-free.

> **Fully range-guarded heterogeneous-union obstruction.** Let
> $X\subseteq[0,U]$ and $Y\subseteq[0,V]$, with both minima zero and both
> displayed endpoints attained. Put
> \[
> Z=X\mathbin{\dot\cup}(T+Y),\qquad E=G+2Z,
> \]
> where
> \[
> G>\max(U,V),\qquad T>G+3U.                    \tag{1}
> \]
> If $E$ is Sidon and $p=|E|\to\infty$, then
> \[
> E\cap3E=\varnothing,\qquad
> \liminf {\max E\over p^2}\ge5.                \tag{2}
> \]

The proof combines disjoint internal differences with a heterogeneous
short-lag packing inequality:

\[
 U+V\ge(1-o(1))(|X|+|Y|)^2,\qquad
 \max E>5(U+V).                                  \tag{3}
\]

Thus no binary Golomb-ruler recursion whose root certifies all
one-versus-three relations only by the range guards (1) can approach
coefficient $3$, even when both children are redesigned at every order.
The missing short-lag proof and its exact hypotheses are supplied by the
independent companion audit `P55_P48_audit.md`, Theorem (4). In particular,
cross-disjointness alone is insufficient; both component rulers must be
internally Sidon, as already required by the validity gate below.

Tiny guarded examples can have excellent ratios. For example,
$E=\{3,5,17,21\}$ is valid and has $\max E/|E|^2=21/16$. Finite records do
not evade the asymptotic difference-packing cost.

Exact scans were also run for full tensors, separable deterministic carries,
Kronecker Costas compositions, compact parabola lifts with affine step
carries, all affine Bose-Chowla cuts through prime $13$, natural Ruzsa cuts
through prime $43$, and selected Welch flattenings through prime $31$.
These produced finite records but no parameter-uniform infinite family.

## 1. Exact normalization

Let

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\},\qquad G\ge1,
 \qquad E=G+2Z.                                  \tag{4}
\]

Every element of $E$ is positive and has the parity of $G$. Moreover,

\[
 (G+2z_i)+(G+2z_j)=(G+2z_k)+(G+2z_l)
\]

if and only if $z_i+z_j=z_k+z_l$. Thus $E$ is Sidon, diagonals included,
exactly when $Z$ is Sidon. Likewise,

\[
 G+2z_t=(G+2z_a)+(G+2z_b)+(G+2z_c)
\]

if and only if

\[
 z_t=G+z_a+z_b+z_c.                              \tag{5}
\]

Hence

\[
 E\cap3E=\varnothing
 \quad\Longleftrightarrow\quad
 Z\cap(G+3Z)=\varnothing.                        \tag{6}
\]

No distinctness condition occurs among $a,b,c$. In particular, (5) retains
$z_a=z_b=z_c$.

For an integer set $A$, write

\[
 D^+(A)=\{a'-a:a,a'\in A,\ a<a'\}.
\]

Sidonicity implies that every positive difference has one ordered endpoint
pair. Indeed, $a'-a=b'-b>0$ gives $a'+b=b'+a$, and Sidonicity recovers the
endpoint pairs.

## 2. Full tensors and separable carries

Let $U_0=\{u_i\}$ and $V_0=\{v_j\}$, each with at least two elements. A full
two-factor tensor has form

\[
 P=\{u_i+v_j:i,j\}.
\]

For $i_0\ne i_1$ and $j_0\ne j_1$,

\[
 (u_{i_0}+v_{j_0})+(u_{i_1}+v_{j_1})
 =
 (u_{i_0}+v_{j_1})+(u_{i_1}+v_{j_0}).            \tag{7}
\]

If all four encoded points are distinct, (7) is a pair-sum collision. If
the encoding identifies points, it already loses the product cardinality.

This includes $\{x_i+Qy_j\}$ for every radix $Q$. It also includes every
deterministic carry of separable form

\[
 \kappa(i,j)=\alpha(i)+\beta(j),
\]

because

\[
 x_i+Qy_j+R\kappa(i,j)
 =(x_i+R\alpha(i))+(Qy_j+R\beta(j)).
\]

Thus full Cartesian tensors, digitwise powers, and separable carry
corrections fail before (6) is checked. The audit tested 400 nontrivial
small products and all 243 three-valued separable carry assignments for a
$3$-by-$2$ template. Every injective encoding collided. The smallest stored
example is

\[
 \{0,1,5,6\},\qquad0+6=1+5.                     \tag{8}
\]

## 3. Costas and recursive block composition

One point per fiber avoids (7), but the standard Kronecker composition of
Costas permutations does not preserve distinct displacements. If $\pi$ has
order $m\ge2$, $\tau$ has order $n\ge2$, and

\[
 \rho(in+j)=n\pi(i)+\tau(j),
\]

then for fixed $j<k$, the displacement

\[
 (k-j,\tau(k)-\tau(j))                           \tag{9}
\]

occurs in every coarse block $i$. Any flattening
$a\longmapsto a+Q\rho(a)$ repeats a positive difference and is not Sidon.
The audit checked all 324 compositions of Costas permutations of orders
$2,3,4$. Its first flattened collision is diagonal-sensitive:

\[
 0+12=6+6.                                       \tag{10}
\]

Two translated copies of the same nontrivial block at the same absolute
scale similarly repeat every internal difference. P17 proves that a
fixed-seed affine recursion either repeats a leaf scale or pays a factorial
span cost. The obstruction below lets both child rulers vary with $p$.

## 4. Fully range-guarded heterogeneous unions

Let

\[
 X=\{0=x_0<\cdots<x_{m-1}=U\},\qquad
 Y=\{0=y_0<\cdots<y_{n-1}=V\}.                  \tag{11}
\]

Choose $G,T$ satisfying (1), and put

\[
 Z=X\cup(T+Y),\qquad E=G+2Z.                    \tag{12}
\]

The guards imply $T>U$, so the union is disjoint and $|E|=m+n$.

### Lemma 4.1 (exact validity gate)

Under (1), $E$ is Sidon if and only if

1. $X$ and $Y$ are Sidon, including diagonals; and
2. $D^+(X)\cap D^+(Y)=\varnothing$.

Whenever these conditions hold, $E\cap3E=\varnothing$ with repeated
summands allowed.

### Proof

The three pair-sum bands of $Z$ are

\[
 X+X\subseteq[0,2U],
\]

\[
 X+(T+Y)\subseteq[T,T+U+V],
\]

\[
 (T+Y)+(T+Y)\subseteq[2T,2T+2V].                \tag{13}
\]

Because $G>V$ and $T>G+3U$,

\[
 T>2U,\qquad T>U+V.                              \tag{14}
\]

Thus the bands are disjoint. The internal bands are simple exactly when
$X,Y$ are Sidon. Two cross sums agree exactly when

\[
 x_1+T+y_1=x_2+T+y_2,\qquad
 x_1-x_2=y_2-y_1.                                \tag{15}
\]

A nontrivial equality in (15) is precisely a common positive difference.
This proves the Sidon criterion, including internal diagonal sums.

It remains to check (6). A low target is at most $U<G$, so it cannot lie in
$G+3Z$. Consider a high target $T+y\le T+V$.

* A triple with no high summand is at most $G+3U<T$.
* A triple with exactly one high summand is at least $G+T>T+V$.
* A triple with at least two high summands is at least $G+2T>T+V$.

The inequalities do not require distinct summands. This proves the lemma.
QED.

The strict guards cannot be weakened silently. Equality gives these
repeated-summand failures:

\[
\begin{array}{c|c|c}
\text{failed guard}&E&\text{literal hit}\\ \hline
G=U&\{2,6,20,22\}&6=2+2+2\\
G=V&\{2,4,14,18\}&18=2+2+14\\
T=G+3U&\{3,5,15,19\}&15=5+5+5.
\end{array}                                           \tag{16}
\]
