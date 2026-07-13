# P125: exact octahedral falsifier to six-sign row independence

## Verdict

The six-sign candidate is false over `Q`, not merely modulo `1000003`.
The first failure archived in
`compute/p124/p86_translations_gate.json` contains an eight-triangle
`2 x 2 x 2` trade.  Its primitive coefficients are

\[
                         \lambda_{ijk}=(-1)^{i+j+k}.
\tag{1}
\]

Every `F_0`, `F_Z`, and `F_X` fold occurs twice in its own role with
opposite coefficients.  Consequently support, `L1`, and `L2` cancel role
by role.  All eight triangles are in the chamber

\[
             (X,Z,R,R+X,R+Z,Z-X)=(+,+,-,-,+,+).
\tag{2}
\]

This is the smallest exact combinatorial obstruction a repaired statement
must exclude: a monochromatic role-preserving octahedron.  For this first
failure, either one extra phase block `dL1` or `dL2` restores rank.  The
smallest local chamber repair is the one additional comparison `sign(r-z)`.
Ordering by only one of `a,c,u,s` does not isolate a row of the trade.

The JSON record is internally a `p=140` system, although the accompanying
description reported `p=138`: its displayed list `B` has 140 distinct
marks.  The file-backed parameters are

\[
 (p,h,C_S,T_F,\delta)=(140,20285,617,856,9046).
\tag{3}
\]

Its 9,730 positive differences and 9,870 unordered sums are respectively
all distinct, so the mark set is integer Sidon.  It is not a literal-hole
row: the phase-1 and phase-2 collision counts are 1,142 and 1,140.

## 1. The twelve supporting folds

Use

\[
\begin{array}{c|cc}
 &0&1\\ \hline
 a_i&1355&1685\\
 c_j&5014&6027\\
 u_k&13180&14205.
\end{array}
\tag{4}
\]

The following twelve folds all occur in the archived fold system.  Each
tuple is in canonical order and satisfies `low sum + h = high sum`.

\[
\begin{array}{c|c@{\qquad}c|c}
 A_{00}&(1355,5014,10110,16544)&A_{01}&(1355,6027,9862,17805)\\
 A_{10}&(1685,5014,9272,17712)&A_{11}&(1685,6027,11333,16664)\\ \hline
 B_{00}&(1355,9926,13180,18386)&B_{01}&(1355,10846,14205,18281)\\
 B_{10}&(1685,9942,13180,18732)&B_{11}&(1685,10270,14205,18035)\\ \hline
 C_{00}&(3725,5014,13180,15844)&C_{01}&(3501,5014,14205,14595)\\
 C_{10}&(3257,6027,13180,16389)&C_{11}&(4343,6027,14205,16450).
\end{array}
\tag{5}
\]

For every `i,j,k in {0,1}`, let

\[
                  T_{ijk}=(A_{ij},B_{ik},C_{jk}),
\tag{6}
\]

in the roles `(F_0,F_Z,F_X)`.  These are eight distinct loose triangles.
Their P83 data and primitive coefficients are:

\[
\begin{array}{c|r|rrrrrr}
T&\lambda&X&Z&R&R+X&R+Z&Z-X\\ \hline
000& 1&41376&119515&-3070& -700&172821&78139\\
001&-1&34267&108964&-4095&-1949&159268&74697\\
010&-1&40324&112633&-3318&-1416&171128&72309\\
011& 1&40369&102082&-4343&-1355&157575&61713\\
100&-1&39142&113156&-3908&-1868&167621&74014\\
101& 1&32033&112288&-4933&-3117&163751&80255\\
110& 1&38090&106274&-1847& -275&162057&68184\\
111&-1&38135&105406&-2872& -214&158187&67271.
\end{array}
\tag{7}
\]

Thus every P83 canonical inequality holds, and (7) verifies (2) without a
boundary case.  In the enumerator these are global triangle indices

\[
                 27,28,29,32,212,213,220,222,
\tag{8}
\]

with coefficients `+,-,-,+,-,+,+,-`.

## 2. Exact symbolic cancellation

For a fold `F`, retain the formal mark vector

\[
                  q(F)=e_{\rm low_1}+e_{\rm low_2}
                       -e_{\rm high_1}-e_{\rm high_2}.
\tag{9}
\]

The row of `T_ijk` is

\[
 \bigl(e_{A_{ij}}+e_{B_{ik}}+e_{C_{jk}},
       q(B_{ik})-q(C_{jk}),q(A_{ij})-q(B_{ik})\bigr).
\tag{10}
\]

For fixed `(i,j)`, the two coefficients in the `k`-fiber sum to zero;
the same statement holds in the `j`-fibers at fixed `(i,k)` and the
`i`-fibers at fixed `(j,k)`.  Hence

\[
 \sum_{ijk}\lambda_{ijk}e_{A_{ij}}=
 \sum_{ijk}\lambda_{ijk}e_{B_{ik}}=
 \sum_{ijk}\lambda_{ijk}e_{C_{jk}}=0.
\tag{11}
\]

Equation (11) separately kills support and every `q(A)`, `q(B)`, `q(C)`
term in (10).  Therefore

\[
                  \sum_{ijk}\lambda_{ijk}(S,L_1,L_2)_{T_{ijk}}=0
\tag{12}
\]

over the integers.  Signs, magnitudes, and accidental mark relations play
no part in this cancellation.

The whole chamber has 74 rows.  Exact rational nullspace elimination gives
nullity one and (1) as its primitive generator.  Independently, the same
rows have rank 73 modulo `1000033`.  The explicit integer dependence gives
rank at most 73 over `Q`, while that nonzero modular minor gives rank at
least 73.  Thus

\[
                  \operatorname{rank}_{\mathbb Q}(S,L_1,L_2)=73.
\tag{13}
\]

## 3. Small repairs on the first failure

### 3.1 One phase-weighted block works

Put `d=a+c+1`, as in P103.  The unique null vector does not kill either
weighted relation block.  For example,

\[
\begin{split}
 \sum\lambda dL_2={}&1013(
 e_{9926}-e_{9942}+e_{10270}-e_{10846}\\
 &\hspace{35mm}-e_{18035}+e_{18281}-e_{18386}+e_{18732}),
\end{split}
\tag{14}
\]

where `1013=c_1-c_0`.  Also the coefficient of `e_3257` in
`sum lambda dL1` is `-330=-(a_1-a_0)`.  Thus either augmentation

\[
                    (S,L_1,L_2,dL_1)
       \quad\hbox{or}\quad (S,L_1,L_2,dL_2)
\tag{15}
\]

has exact rank 74 on this chamber.  Rank 74 modulo `1000033` independently
certifies both assertions.  The smaller-looking choice is `dL2`: one of
its coordinates already witnesses failure of (12).  This is a repair of
the first row only, not a claim about the other 51 archived failures.

### 3.2 One extra order sign works

Among the eight active rows, the complete order of the nine P83 marks is
fixed except for the order of `r` and `z`.  Three have `z<r` and five have
`r<z`.  Refining (2) by

\[
                             \operatorname{sign}(r-z)
\tag{16}
\]

therefore splits the support of the unique null vector.  On all 74 rows,
the three classes `r<z`, `r=z`, and `r>z` have sizes and ranks

\[
                         (14,14),\quad(3,3),\quad(57,57).
\tag{17}
\]

The full-order classes likewise have `(size,rank)` equal to
`(3,3),(17,17),(54,54)`.  Since (13) has a one-dimensional kernel whose
generator is nonzero at all eight corners, every proper subset of those
corners is independent inside the 74-row chamber.  Thus (16) is the
smallest one-bit local refinement exposed by this falsifier.  It is not a
universal theorem for the remaining failures.

### 3.3 Ordering only by `a,c,u,s` is not a bounded repair

In the active trade each value of `a`, `c`, and `u` occurs four times, and
each of the four values of `s` occurs twice.  Both signs occur at every such
extremal fiber.  Therefore choosing a least or greatest `a`, `c`, `u`, or
`s` does not expose a private coefficient; the opposite cube faces cancel.

Partitioning by the exact value of one coordinate does split this particular
kernel.  In the full 74-row chamber, however, it creates respectively
24, 41, 34, or 31 classes for `a,c,u,s`.  In general this is up to `p`
classes, so separate dimension counts lose the required quadratic bound.
Lexicographic ordering changes no row and cannot by itself remove (12).

## 4. Exact condition left by the red team

Let `M_0,M_Z,M_X` be the three role-incidence maps from triangles to folds.
Every vector in

\[
                         \ker M_0\cap\ker M_Z\cap\ker M_X
\tag{18}
\]

is automatically in the kernel of `(S,L1,L2)`, because `L1` and `L2` are
differences of the same rolewise fold vectors after applying `q`.  The cube
(1) is the basic nonzero element of (18): all of its two-coordinate
marginals vanish.

Consequently any unweighted chamber proof needs, at minimum, the exact
combinatorial condition

> no chamber contains a role-preserving signed trade; in particular, no
> chamber contains all eight corners `T_ijk=(A_ij,B_ik,C_jk)` of a
> monochromatic `2 x 2 x 2` octahedron.

The six signs in (2) do not imply this condition.  A viable repair must use
new information that splits such an octahedron, as `sign(r-z)` does here,
or weight a formal relation so that opposite faces no longer cancel, as
`dL2` does in (14).  No conclusion about all 52 failures or a universally
repaired independence statement is claimed.
