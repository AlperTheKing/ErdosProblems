# B07: nonlinear bootstrap

## Verdict

No linear lower bound is proved. There is an exact obstruction to the natural
bootstrap principle "a polynomial lower bound plus availability of every new
value as a multiplier forces positive lower density." The same restricted
operation, with seeds 9 and 10, gives a closure which

1. has a polynomial lower bound;
2. makes every generated value available in every later multiplication; and
3. nevertheless has upper density zero.

Thus cardinality growth and dynamic multiplier availability alone cannot
bootstrap a sublinear bound to `cX`. Any successful bootstrap for the target
set must use arithmetic special to the small seeds 2 and 3, beyond those two
facts. The distinct-input condition is retained throughout.

The supplied exact census \(A(10^8)=51{,}899{,}129\) and the declining
fixed-\(\{2,3,5\}\) affine density are not extrapolated here. The fixed
alphabet is used only to establish a starting lower bound; the main theorem
allows the full nonlinear closure and all newly generated multipliers.

For context, a direct equal-slope construction does prove the unconditional
target-set bound

\[
 |A\cap[1,X]|\ge {1\over6}(X/9)^{\log 6/\log 30}\qquad(X\ge9). \tag{1}
\]

The obstruction below shows why feeding only such a power-law count back into
the binary operation is not, by itself, a route to exponent 1.

## 1. A polynomial lower bound for the actual set

Put \(T_d(x)=dx-1\). The elements \(5=2\cdot3-1\) and
\(9=2\cdot5-1\) belong to \(A\). Starting from any \(x\ge9\), every use of
a multiplier in \(\{2,3,5\}\) has distinct inputs, and the new value is again
at least 9.

Apply each permutation of \((2,3,5)\) from left to right. The six resulting
three-step maps are

\[
 x\longmapsto30x-b,
 \qquad b\in D:=\{9,10,13,16,19,21\}. \tag{2}
\]

For example, the order \((2,3,5)\) gives \(30x-21\). The other five values
follow from

\[
 b=d_3d_2+d_3+1
\]

for a permutation \((d_1,d_2,d_3)\): in order they are
\(21,19,16,13,10,9\).

After \(n\) blocks, (2) gives

\[
 30^n9-\sum_{j=0}^{n-1}b_j30^j,\qquad b_j\in D. \tag{3}
\]

The \(6^n\) values in (3) are distinct, by uniqueness of a length-\(n\)
base-30 expansion with digits in the six-element subset \(D\subset[0,29]\).
All are less than \(9\cdot30^n\), and every intermediate operation had
unequal inputs. For

\[
 n=\lfloor\log_{30}(X/9)\rfloor
\]

this supplies \(6^n\ge6^{-1}(X/9)^{\log_{30}6}\) elements at most \(X\),
proving (1).

## 2. What "use every element as a multiplier" says exactly

For a set \(B\), write

\[
 B\widehat\times B=\{xy:x,y\in B,\ x<y\}.
\]

Because \(A\) is the *least* restricted closure, every non-seed element has
a finite derivation and hence was produced at its last node from two distinct
earlier values. Conversely, closure licenses every such product. Therefore

\[
 A=\{2,3\}\mathbin\sqcup\bigl(A\widehat\times A-1\bigr), \tag{4}
\]

and, for \(X\ge3\),

\[
 |A\cap[1,X]|
 =2+\left|\{xy\le X+1:x,y\in A,\ x<y\}\right|. \tag{5}
\]

The union is disjoint: an output equal to 2 would require \(xy=3\), and an
output equal to 3 would require the forbidden equal pair \(x=y=2\).

Thus the full nonlinear fanout is not an additional inequality omitted from
the definition; it is exactly the fixed-point identity (5). To turn (1) into
a linear estimate through (5), one needs a new lower bound for the number of
*distinct* restricted products. A count of available multipliers alone does
not provide that bound, as the following theorem proves.

## 3. Exact dynamic-multiplier counterexample

**Theorem (polynomial growth does not bootstrap).** Let \(C\) be the least
set containing 9 and 10 and closed under \(xy-1\) for distinct values
\(x\ne y\). Put

\[
 \rho={\log2\over\log90},\qquad
 \theta={\log8\over\log(80/9)}<1.
\]

Then, for every \(X\ge89\),

\[
 |C\cap[1,X]|\ge {1\over2}(X/89)^\rho, \tag{6}
\]

while

\[
 |C\cap[1,X]|=O(X^\theta)=o(X). \tag{7}
\]

In particular, this closure has a proved power-law lower bound and uses every
generated element as a future multiplier, but it has zero upper density.

**Proof of (6).** First \(89=9\cdot10-1\in C\). On values \(x\ge89\), both
two-step blocks below are admissible at both internal steps:

\[
 T_9(T_{10}(x))=90x-10,
 \qquad
 T_{10}(T_9(x))=90x-11. \tag{8}
\]

Indeed every current and intermediate value is greater than 10, so it is
different from the multiplier 9 or 10 being used. Composing \(n\) blocks
from (8), starting at 89, produces

\[
 90^n89-\sum_{j=0}^{n-1}\varepsilon_j90^j,
 \qquad \varepsilon_j\in\{10,11\}. \tag{9}
\]

Uniqueness of base-90 expansion makes these \(2^n\) values distinct. They
are all below \(89\cdot90^n\). Taking
\(n=\lfloor\log_{90}(X/89)\rfloor\) gives

\[
 2^n\ge {1\over2}(X/89)^{\log_{90}2},
\]

which is (6).

**Proof of (7).** Every element of \(C\) has a finite full binary derivation
tree with leaves labelled 9 or 10. A valid tree has distinct evaluated
children at each internal node. We upper-bound the number of valid trees by
counting all ordered labelled full binary trees, including invalid ones.

Set \(\lambda=80/9\). A tree with \(n\) leaves has value at least

\[
 9\lambda^{n-1}. \tag{10}
\]

This is clear for a leaf. If child values \(u,v\ge9\) have \(n_1,n_2\)
leaves, then

\[
 uv-1\ge {80\over81}uv
 \ge {80\over81}\,9^2
       \lambda^{n_1+n_2-2}
 =9\lambda^{n_1+n_2-1},
\]

proving (10) by induction. Hence a value at most \(X\) has

\[
 n-1\le {\log(X/9)\over\log\lambda}. \tag{11}
\]

There are \(\operatorname{Cat}_{n-1}\) ordered full binary tree shapes and
\(2^n\) leaf labellings. Since
\(\operatorname{Cat}_{n-1}\le4^{n-1}\), the number of candidate trees with
\(n=j+1\) leaves is at most \(2\cdot8^j\). Summing this geometric bound for
the values of \(j\) allowed by (11) gives

\[
 |C\cap[1,X]|
 \le {16\over7}(X/9)^{\log8/\log\lambda}
 =O(X^\theta).
\]

Because \(\lambda=80/9>8\), one has \(\theta<1\). Counting invalid trees
only enlarged the family, so the argument applies to the distinct-input
closure. This proves (7). \(\square\)

The theorem is an exact counterexample to any bootstrap whose hypotheses are
only a power-law lower bound, restricted closure, and dynamic availability of
all generated multipliers. It does not rule out a theorem which uses special
arithmetic forced by the target seeds 2 and 3.

## 4. Exact obstruction to the balanced-word extrapolation

One might try to strengthen (1) by taking longer balanced words in
\(2,3,5\), asserting that distinct words with the same slope have distinct
intercepts. This is false already at length 6. With a word denoting the order
in which multipliers are applied,

\[
 T_{322255}(x)=600x-381=T_{255232}(x). \tag{12}
\]

For the first word the intercept recursion \(b\leftarrow db+1\) is

\[
 0,1,3,7,15,76,381,
\]

and for the second it is

\[
 0,1,6,31,63,190,381.
\]

Both words have slope \(2^3\cdot3\cdot5^2=600\). For every input \(x>5\),
all twelve displayed operations are admissible, so (12) is a collision inside
the genuine distinct-input affine subsystem of \(A\), not an artefact of
allowing equal operands. Appending the same suffix preserves the collision.
Consequently, multinomial word counts cannot be used as value counts without
a separate theorem controlling the quotient by affine relations.

## 5. Novelty and boundary

The [official problem page](https://www.erdosproblems.com/424), checked
2026-07-13, marks #424 open, reports no claimed partial or complete solution,
and has no comments. [OEIS A005244](https://oeis.org/A005244) records finite
terms and representation counts but no density theorem. No source found in
the wave-1 audit supplies either (1) or the counterexample theorem in the
form above.

This report does **not** show that the target set has zero density, nor that
an arithmetic nonlinear bootstrap is impossible. It isolates the missing
input exactly: one must prove target-specific expansion for the distinct
product set in (5), or an equivalent collision bound. Raw power-law size and
the fact that outputs become multipliers are insufficient.
