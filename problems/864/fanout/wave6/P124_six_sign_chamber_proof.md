# P124: exact obstruction to six-sign chamber independence

## Verdict

The proposed chamber statement is false.  In the first failure from
`compute/p124/p86_translations_gate.json`, eight of the 74 rows in the
chamber

\[
 (\operatorname {sgn}X,\operatorname {sgn}Z,\operatorname {sgn}R,
   \operatorname {sgn}(R+X),\operatorname {sgn}(R+Z),
   \operatorname {sgn}(Z-X))=(+,+,-,-,+,+)              \tag{1}
\]

form an integral `2 x 2 x 2` trade.  With coefficients
`lambda_ijk=(-1)^(i+j+k)`, the incidences of the three fold roles vanish
separately.  Consequently both formal relation blocks vanish automatically:

\[
 \sum_{i,j,k}\lambda_{ijk}
 (e_{F_{0,ij}}+e_{F_{Z,ik}}+e_{F_{X,jk}},L_{1,ijk},L_{2,ijk})=0. \tag{2}
\]

This is an exact rational counterexample, not only a modular rank drop.

There is a metadata correction.  The current `first_failure.B` array has
`p=140`, not 138.  Its comma-separated SHA-256 is

```text
78c19f262267511d143c2df1dddcafb435368ad582c5a1549f4297f4cf9f48d4
```

It has `h=20285`, `min(B)=1355`, `max(B)=20284`, `C_S=617`, and
`T_F=856`.  Its 9,870 unordered sums and 9,730 positive differences are
all distinct.  The chamber (1) has 74 rows.

## 1. The eight-triangle trade

Put

\[
 (a_0,a_1)=(1355,1685),\quad
 (c_0,c_1)=(5014,6027),\quad
 (u_0,u_1)=(13180,14205).                              \tag{3}
\]

The following twelve folds occur in the endpoint system.  Every displayed
tuple is in canonical `(low,low,high,high)` order and satisfies
`low+low+h=high+high`.

\[
\begin{array}{c|c}
(i,j)&F_{0,ij}\\ \hline
(0,0)&(1355,5014,10110,16544)\\
(0,1)&(1355,6027, 9862,17805)\\
(1,0)&(1685,5014, 9272,17712)\\
(1,1)&(1685,6027,11333,16664)
\end{array}
\qquad
\begin{array}{c|c}
(i,k)&F_{Z,ik}\\ \hline
(0,0)&(1355, 9926,13180,18386)\\
(0,1)&(1355,10846,14205,18281)\\
(1,0)&(1685, 9942,13180,18732)\\
(1,1)&(1685,10270,14205,18035)
\end{array}                                             \tag{4}
\]

\[
\begin{array}{c|c}
(j,k)&F_{X,jk}\\ \hline
(0,0)&(3725,5014,13180,15844)\\
(0,1)&(3501,5014,14205,14595)\\
(1,0)&(3257,6027,13180,16389)\\
(1,1)&(4343,6027,14205,16450).
\end{array}                                             \tag{5}
\]

For every `(i,j,k) in {0,1}^3`, the triple

\[
             \tau_{ijk}=(F_{0,ij},F_{Z,ik},F_{X,jk})   \tag{6}
\]

is a loose fold triangle with shared marks `(a_i,c_j,u_k)`.  These are
global triangle indices

\[
\begin{array}{c|rrrrrrrr}
(i,j,k)&000&001&010&011&100&101&110&111\\ \hline
\text{index}&27&28&29&32&212&213&220&222\\
\lambda&1&-1&-1&1&-1&1&1&-1.
\end{array}                                             \tag{7}
\]

All eight triangles lie in (1).  Indeed, across (4)--(5),

\[
 x>a,\quad z>c,\quad r<u,\quad y<s,\quad w>s,
 \quad w>y,                                             \tag{8}
\]

which are respectively the six signs in (1).  Equivalently, the four P83
offsets have the fixed order

\[
                         0<X<-R<Z.                     \tag{9}
\]

## 2. Exact dependence

Let `Qe_F=q(F)`.  For the P103 relation convention,

\[
 L_1=Q(e_{F_Z}-e_{F_X}),\qquad
 L_2=Q(e_{F_0}-e_{F_Z}).                               \tag{10}
\]

The alternating coefficients in (7) cancel every role separately:

\[
\begin{split}
 \sum_{i,j,k}\lambda_{ijk}e_{F_{0,ij}}
 &=\sum_{i,j}(-1)^{i+j}e_{F_{0,ij}}
      \sum_k(-1)^k=0,\\
 \sum_{i,j,k}\lambda_{ijk}e_{F_{Z,ik}}
 &=\sum_{i,k}(-1)^{i+k}e_{F_{Z,ik}}
      \sum_j(-1)^j=0,\\
 \sum_{i,j,k}\lambda_{ijk}e_{F_{X,jk}}
 &=\sum_{j,k}(-1)^{j+k}e_{F_{X,jk}}
      \sum_i(-1)^i=0.                                 \tag{11}
\end{split}
\]

Equation (11) proves the support, `L1`, and `L2` cancellations in (2) over
the integers.  Thus no extreme-mark argument using only the six signs and
the unweighted blocks can prove the proposed statement.

The audit gives support rank 73 over `GF(2)` and full relation rank 73
modulo 1,000,003.  The latter gives an integer 73-minor which is nonzero,
so the rational rank is at least 73.  Equation (2) gives rank at most 73.
Therefore the exact rational rank of the 74 rows is 73, and their rational
nullspace is precisely the span of (7), extended by zero on the other 66
rows.

## 3. Smallest repairs on this obstruction

### One phase-weighted relation block works

Put `d_ijk=a_i+c_j+1`.  Adding either one of the two `p`-column blocks
`dL1` or `dL2` kills the unique nullvector.  Two exact nonzero coordinates
are

\[
 \left[\sum\lambda_{ijk}d_{ijk}L_{1,ijk}\right]_{3257}
      =7383-7713=-330,                                 \tag{12}
\]

and

\[
 \left[\sum\lambda_{ijk}d_{ijk}L_{2,ijk}\right]_{9926}
      =-6370+7383=1013.                                \tag{13}
\]

Since (7) spans the old kernel, either `(support,L1,L2,dL1)` or
`(support,L1,L2,dL2)` has exact rational rank 74 on this chamber.  A single
scalar phase column does not work:

\[
               \sum_{i,j,k}\lambda_{ijk}d_{ijk}=0,    \tag{14}
\]

because `d_ijk` is independent of `k`.  Thus the smallest natural phase
repair certified here is one weighted relation block, not one scalar
moment.  The same calculation is unaffected by changing the constant `b`
in `d=a+c+b`, because the unweighted relation sum is zero.

### One extra cross-order comparison also works here

The six signs already encode the complete order (9), so no finer chamber
of those four offsets exists.  The first unresolved useful comparison is
`z` versus `r`.  On all 74 rows, splitting by this comparison gives

\[
\begin{array}{c|ccc}
\text{subclass}&z<r&z=r&z>r\\ \hline
\text{rows}&57&3&14\\
\text{support rank over }\mathbf F_2&57&3&14\\
\text{relation rank mod }1000003&57&3&14.
\end{array}                                             \tag{15}
\]

For the eight rows in (7), three have `z<r` and five have `z>r`.  Hence
even the binary split `z<r` versus `z>=r` destroys the unique dependence.
This is a fixed-factor repair of this witness and would make 48 subclasses,
but (15) is only a finite certificate, not a universal independence proof.

### Ordering only `a,c,u,s` does not work

Every one of the 74 rows, including all eight rows in the trade, has

\[
                             a<c<u<s.                  \tag{16}
\]

Indeed the eight rows have the stronger common order

\[
 a<x<c<\{z,r\}<u<y<s<w,                               \tag{17}
\]

with only the order of `z,r` changing.  Therefore refinement by the
relative order type of `a,c,u,s`, or merely sorting the rows by those
coordinates, cannot remove (2).  Partitioning by the exact value of one
coordinate does split this finite cube, but introduces up to `p` classes
and loses the desired quadratic consequence.

## 4. Claim boundary

The universal six-sign unweighted candidate is exactly false by (2).  On
this first witness, either one phase-weighted relation block or one extra
comparison `z<r` removes the only rational dependency; relative ordering of
`a,c,u,s` does not.

This endpoint ruler has positive defect

\[
 {3p^2-p+2\over2}-h=9046,                              \tag{18}
\]

but it is not a literal hole: the intersections
`Delta^+(B) intersect (B+B+b)` have sizes 1,142 and 1,140 for `b=1,2`.
Thus it does not falsify a chamber statement with the literal-hole gate
added.  No universal claim is made here for either repaired candidate.
