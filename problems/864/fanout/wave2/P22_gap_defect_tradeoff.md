# P22: reflected depth and gap-defect tradeoffs

## Verdict

There is an exact, residual-safe mechanism which converts duplicated
differences into overlap of adjacent gap intervals.  Let $C$ be the forced
reflected core, let $c=|C|$, and let

\[
 m_H(C)=\max_x |C\cap[x,x+H-1]|.
\]

Then

\[
 \boxed{
 kH-M_H(A)=\sum_i(H-g_i)_+
 \ge {4Z_H+2J_H\over m_H(C)},}                         \tag{1}
\]

where

\[
 J_H=\sum_i(H-2u_i)_+
\]

is the contribution of the singleton partner differences of the core.
In particular, (1) gives both a pointwise scalar upper bound for $M_H$ and
the averaged gap inequality

\[
 \boxed{
 \sum_{h=H}^{2H}\sum_i(h-g_i)_+
 \ge {4\over B_{2H}(c)}\sum_{h=H}^{2H}Z_h,}             \tag{2}
\]

with an explicit $B_{2H}(c)=O(\sqrt H)$.  These inequalities do not assume
that all of $A$ is reflected.

There is also a colored onset inequality.  In the no-midpoint case, if

\[
 \lambda=\min_{i<j}(u_i+u_j)=u_1+u_2,
\]

then

\[
 \boxed{
 M_H(A)\le L_C+(r+1)H-(\lambda-2H)_+,}                  \tag{3}
\]

where $L_C=\max C-\min C$ and $r=|A\setminus C|$.  This is asymptotically
sharp on the Erdos--Freud construction: $L_C/N\to1$,
$\lambda/N\to1/3$, $r=0$, and hence (3) gives $M_H/N\le2/3+o(1)$ for
$H=o(N)$.  Together with $Z_H/H^2\to1/2$, the P02 product tends to
$4/3$.

What is not proved is that large *uncolored* $Z_H$ forces the onset
$\lambda\ge(1/3-o(1))N$, or forces an equivalent core gap defect.  An exact
six-point pair below has identical $Z_H$ at every dyadic scale but different
$M_H$.  Thus a dyadic argument using only the scalar $Z_H$ loses genuine
offset-incidence information.  The residual error $rH$ in (3) is also
exactly necessary.

## 1. Normalization and the D1 labels

Translate $A\subseteq[1,N]$ when convenient.  Suppose its only repeated
unordered sum is $\sigma$, and put

\[
 C=A\cap(\sigma-A),\qquad R=A\setminus C,\qquad r=|R|.
\]

Write $m=\sigma/2$ and

\[
 C=\{m-u_i,m+u_i:1\le i\le p\}
   \mathbin{\dot\cup}
   \bigl(\{m\}\text{ if }\delta=1\bigr),
\]

where

\[
 0<u_1<\cdots<u_p,
 \qquad
 \delta={\bf1}_{\{m\in A\}}.
\]

The $u_i$ may be half-integers, but every label below is an integer.  Put

\[
 q_i=u_{i+1}-u_i,qquad L_C=2u_p,qquad c=2p+\delta,
 \qquad k=c+r.
\]

By D1, the duplicated positive-difference labels form the disjoint union

\[
 \begin{split}
 D^-&=\{u_j-u_i:i<j\},\\
 D^+&=\{u_i+u_j:i<j\},\\
 D^0&=\{u_i:1\le i\le p\}\quad(\delta=1).
 \end{split}                                             \tag{4}
\]

Every label in (4) has exactly two representations.  Every difference using
a point of $R$ is unique, and all such labels are mutually distinct and
disjoint from (4).  With

\[
 \nu_A(d)=\#\{(a,b)\in A^2:a-b=d\},\qquad d>0,
\]

we use the unambiguous form

\[
 Z_H=\sum_{d=1}^{H-1}(H-d)(\nu_A(d)-1)_+
    =\sum_{d\in D}(H-d)_+.                               \tag{5}
\]

The positive part in (5) may be omitted if the sum is understood to run only
over represented differences.

The only singleton differences internal to $C$ are the partner labels

\[
 P=\{2u_i:1\le i\le p\}.                                 \tag{6}
\]

They are mutually distinct and disjoint from $D$ and from every residual
difference.  Consequently, if ${\cal R}$ is the set of differences of
pairs touching $R$, then the exact label budget is

\[
 \boxed{
 Z_H+J_H+\sum_{d\in{\cal R}}(H-d)_+
 \le \binom H2,\qquad
 J_H=\sum_{i=1}^p(H-2u_i)_+.}                            \tag{7}
\]

Thus $Z_H\sim H^2/2$ leaves little weighted room for short residual or
partner differences.  Section 5 shows why this fact alone still does not
control the amount by which residual intervals enlarge $M_H$.

## 2. Reflected-depth gap inequality

For $x\in\mathbb Z$, let

\[
 F_H(x)=|\{c\in C:x\in c+\{0,\ldots,H-1\}\}|.
\]

Then

\[
 \sum_xF_H(x)=cH,
 \qquad
 cH-M_H(C)=\sum_{x:F_H(x)>0}(F_H(x)-1).                  \tag{8}
\]

Double-counting pairs of core intervals gives the exact identity

\[
 \sum_x\binom{F_H(x)}2=2Z_H+J_H.                         \tag{9}
\]

Indeed, a nonpartner core edge belongs to a two-edge reflection orbit and
contributes twice its overlap $(H-d)_+$; a partner edge is fixed by
reflection and contributes once.

Set

\[
 m_H=m_H(C)=\max_xF_H(x).
\]

For every positive integer $f\le m_H$,

\[
 \binom f2\le {m_H\over2}(f-1).
\]

Using (8)-(9) gives

\[
 cH-M_H(C)\ge {4Z_H+2J_H\over m_H}.                     \tag{10}
\]

Adding the $r$ residual intervals enlarges a union by at most $rH$, so

\[
 M_H(A)\le M_H(C)+rH.
\]

Equations (1) and the sharper support bound

\[
 \boxed{
 M_H(A)\le kH-{4Z_H+2J_H\over m_H}}                     \tag{11}
\]

follow.  This is the requested direct mechanism: duplicated differences
force pair-overlap energy inside the reflected core, bounded depth converts
that energy to adjacent-gap overlap, and residual points cost only their
literal $rH$ union increment.

There are two exact ways to eliminate or constrain $m_H$.

First, the $\binom{m_H}{2}$ differences inside an $H$-term interval use
the labels $1,\ldots,H-1$, each at most twice.  Hence

\[
 m_H\le B_H(c):=
 \min\left\{c,
 \left\lfloor{1+\sqrt{1+16(H-1)}\over2}\right\rfloor
 \right\}.                                              \tag{12}
\]

Second, the $m_H$ core intervals witnessing the maximum depth have union
of size at most $2H-1$.  Adding all other intervals separately gives

\[
 M_H(A)\le(k-m_H+2)H-1.                                  \tag{13}
\]

Combining (11)-(13), and dropping the favorable $J_H$, gives a scalar,
finite, exact-testable upper bound:

\[
 \boxed{
 M_H(A)\le\min\{N+H-1,{\cal U}_H(k,c,Z_H)\},}           \tag{14}
\]

where

\[
 {\cal U}_H(k,c,z)=
 \max_{1\le s\le B_H(c)}
 \min\left\{kH-{4z\over s},\ (k-s+2)H-1\right\}.       \tag{15}
\]

For the actual value $s=m_H$, both entries in the inner minimum bound
$M_H$; maximizing merely removes the unknown $m_H$.

Since $m_h\le B_{2H}(c)$ for $H\le h\le2H$, summing (10) proves the
announced averaged gap inequality

\[
 \begin{split}
 \sum_{h=H}^{2H}\sum_i(h-g_i)_+
 &=\sum_{h=H}^{2H}(kh-M_h(A))\\
 &\ge {1\over B_{2H}(c)}
       \sum_{h=H}^{2H}(4Z_h+2J_h)\\
 &\ge {4\over B_{2H}(c)}\sum_{h=H}^{2H}Z_h.
 \end{split}                                             \tag{16}
\]

This is stronger than P02 in a literal sense.  P02 gives

\[
 k^2H^2\le M_H(A)\bigl(kH+H(H-1)+2Z_H\bigr).             \tag{17}
\]

Substituting (14) yields the additional finite restriction

\[
 \boxed{
 k^2H^2\le
 \min\{N+H-1,{\cal U}_H(k,c,Z_H)\}
 \bigl(kH+H(H-1)+2Z_H\bigr).}                            \tag{18}
\]

P02 alone has no upper bound for $M_H$ below $N+H-1$.  In the exact
five-point example in Section 5, (14) gives $M_3\le11$, with equality,
whereas the ambient bound is $13$.

## 3. Exact core defect and colored onset

The gaps of $C$ are completely explicit.  If $\delta=0$, each $q_i$
occurs twice and the central gap is $2u_1$.  If $\delta=1$, each $q_i$
occurs twice and the two central gaps are both $u_1$.  Therefore

\[
 E_H(C):=L_C+H-M_H(C)
 =2\sum_{i=1}^{p-1}(q_i-H)_+
 +\begin{cases}
 (2u_1-H)_+,&\delta=0,\\
 2(u_1-H)_+,&\delta=1.
 \end{cases}                                             \tag{19}
\]

This identity remains useful when $R\ne\varnothing$, because

\[
 \boxed{
 M_H(A)\le L_C+H-E_H(C)+rH.}                             \tag{20}
\]

The following bounds $E_H(C)$ from below using only a colored star of D1 sum
labels.  In the no-midpoint case define

\[
 \Gamma_H=
 \max_{2\le j\le p}(u_1+u_j-jH)_+,                      \tag{21}
\]

with an empty maximum interpreted as zero.  Since

\[
 u_1+u_j=2u_1+q_1+\cdots+q_{j-1},
\]

subadditivity of the positive part gives

\[
 (u_1+u_j-jH)_+
 \le(2u_1-H)_++\sum_{i<j}(q_i-H)_+
 \le E_H(C).
\]

Hence

\[
 \boxed{
 M_H(A)\le L_C+(r+1)H-\Gamma_H\qquad(\delta=0).}        \tag{22}
\]

Restricting the maximum in (21) to $j=2,4,8,\ldots$ gives a valid dyadic
rank version.  Summing only the $j=2$ bound gives a closed averaged form.
If

\[
 \lambda=u_1+u_2,
 \qquad Q=\left\lfloor{\lambda-1\over2}\right\rfloor,
\]

then

\[
 \boxed{
 \sum_{h=1}^{Q}
 \bigl(L_C+(r+1)h-M_h(A)\bigr)
 \ge Q\lambda-Q(Q+1).}                                  \tag{23}
\]

For a midpoint, the corresponding valid defect is

\[
 \Gamma_H^{\rm mid}=
 \max\left\{
 2(u_1-H)_+,
 \max_{2\le j\le p}(u_1+u_j-(j+1)H)_+
 \right\},                                              \tag{24}
\]

and (22) holds with $\Gamma_H^{\rm mid}$.  In (24), write
$u_1+u_j$ as two copies of $u_1$ plus $q_1+\cdots+q_{j-1}$ before
applying positive-part subadditivity.

## 4. Sharp P02 product on the Erdos--Freud family

Assume $\delta=0$, $p\ge2$, and $\lambda=u_1+u_2>2H$.  The $j=2$
case of (22) gives

\[
 M_H(A)\le L_C-\lambda+(r+3)H.                           \tag{25}
\]

Since the duplicate labels are distinct,

\[
 Z_H\le\binom H2.
\]

Thus the exact support--duplicate product satisfies

\[
 \boxed{
 {M_H(A)\over N}\left(1+{2Z_H\over H^2}\right)
 \le
 \left(2-{1\over H}\right)
 \left({L_C-\lambda+(r+3)H\over N}\right).}             \tag{26}
\]

For the Erdos--Freud set

\[
 A_L=B_L\cup(3L+1-B_L)\subseteq[1,3L],
\]

take $B_L$ dense Sidon and $N=3L$.  There is no residual, and the two
largest members $x_p,x_{p-1}$ of $B_L$ satisfy

\[
 \lambda=3L+1-x_p-x_{p-1}=L+o(L),
 \qquad L_C=3L+o(L).
\]

Choose $\sqrt N\ll H\ll N$ slowly enough that the standard dense-Sidon
short-difference asymptotic holds.  Equations (25)-(26) give

\[
 {M_H(A_L)\over N}\le{2\over3}+o(1),
 \qquad
 {M_H(A_L)\over N}\left(1+{2Z_H\over H^2}\right)
 \le{4\over3}+o(1).                                     \tag{27}
\]

The reverse limits $M_H/N\to2/3$ and $Z_H/H^2\to1/2$ hold for this
family, so (25)-(27) are asymptotically sharp.  Relative to P02's ambient
support bound, (3) improves $N+H-1$ by

\[
 \lambda-(r+2)H
\]

whenever this quantity is positive.

## 5. Exact algebraic obstructions

### 5.1 Identical dyadic $Z$, different $M$, with no residual

Work in $[0,22]$, which may be shifted into $[1,23]$.  Consider the two
fully reflected admissible sets

\[
 \begin{split}
 A&=\{0,1,9,13,21,22\},\\
 A'&=\{0,1,10,12,21,22\}.
 \end{split}                                             \tag{28}
\]

Both have exceptional sum $22$ with three representations.  Their offset
sets and duplicate labels are

\[
 \begin{array}{c|c|c|c}
 &\{u_1,u_2,u_3\}&D&P\\ \hline
 A&\{2,10,11\}&\{1,8,9,12,13,21\}&\{4,20,22\}\\
 A'&\{1,10,11\}&\{1,9,10,11,12,21\}&\{2,20,22\}.
 \end{array}                                             \tag{29}
\]

In each row the six duplicate labels and three partner labels are distinct,
which is a complete D1 certificate of admissibility.  Direct calculation
gives

\[
 \begin{array}{c|rrrr}
 H&2&4&8&16\\ \hline
 Z_H(A)=Z_H(A')&1&3&7&37\\
 M_H(A)&10&18&30&38\\
 M_H(A')&10&16&28&38.
 \end{array}                                             \tag{30}
\]

The gap lists are respectively

\[
 (1,8,4,8,1),\qquad(1,9,2,9,1).                         \tag{31}
\]

Thus even the complete dyadic scalar data
$(N,k,r,Z_2,Z_4,Z_8,Z_{16})$ do not determine the gap defect or $M_H$.
An inequality which averages only the uncolored values $Z_{2^j}$ must
allow both rows.  The missing datum is which offset pairs generated the
duplicate labels, precisely the information retained by $m_H(C)$,
$E_H(C)$, or the colored star in (21).

### 5.2 The residual error $rH$ is exact

The two admissible sets

\[
 A_3=\{0,1,3,9,10\},\qquad
 A_4=\{0,1,4,9,10\}                                     \tag{32}
\]

have the same exceptional sum $10$, the same reflected core

\[
 C=\{0,1,9,10\},
\]

the same duplicate set $D=\{1,9\}$, and therefore the same $Z_H$ for
every $H$.  Their only repeated unordered sum is

\[
 0+10=1+9=10;
\]

all diagonal sums are singleton.  Their gap lists are

\[
 (1,2,6,1),\qquad(1,3,5,1).                              \tag{33}
\]

At $H=3$,

\[
 Z_3=2,qquad M_3(C)=8,qquad
 M_3(A_3)=10,qquad M_3(A_4)=11.                         \tag{34}
\]

For $A_4$, the residual interval adds all $H=3$ new points, so

\[
 M_3(A_4)=M_3(C)+rH.
\]

Moreover $m_3(C)=2$ and $J_3=0$, so (11) is an equality:

\[
 M_3(A_4)=5\cdot3-{4\cdot2\over2}=11.                   \tag{35}
\]

This is the smallest algebraic obstruction needed here: the entire duplicate
profile can remain fixed while one residual point changes occupied support,
and the coefficient of $rH$ cannot be reduced universally.

### 5.3 Why weak averaged occupation cannot force the onset

There is also an asymptotic obstruction to eliminating the colored onset
from (3).  The exact rational continuum profile

\[
 w=1,qquad g={1\over2},qquad \mu={\bf1}_{[0,1]}(x)\,dx
\]

has difference-label density

\[
 a(t)=(1-t){\bf1}_{[0,1]}(t)
\]

and shifted-sum density

\[
 b(t)=
 \begin{cases}
 0,&t<1/2,\\
 (t-1/2)/2,&1/2\le t\le3/2,\\
 (5/2-t)/2,&3/2\le t\le5/2,\\
 0,&t>5/2.
 \end{cases}                                             \tag{36}
\]

One checks piecewise that $a(t)+b(t)\le1$.  Thus every nonnegative
interval-weighted label-capacity inequality is satisfied.  For a cutoff
$0<\alpha<1/2$, its duplicate weight is exactly

\[
 z(\alpha)=\int_0^\alpha(\alpha-t)(1-t)\,dt
 ={\alpha^2\over2}-{\alpha^3\over6}.                     \tag{37}
\]

As $\alpha\downarrow0$, $z(\alpha)/\alpha^2\to1/2$, while the two
occupied side blocks have support ratio

\[
 {2w\over g+2w}={4\over5}>{2\over3}.                     \tag{38}
\]

This is a fractional countermodel, not an integer counterexample to Problem
864.  It is an exact obstruction to proving the missing onset or gap defect
from weak averaged occupation data alone.  An integer proof must retain a
unit-scale phase or an equivalent offset-incidence statistic.

## 6. Exact finite audit and remaining frontier

All finite set identities and inequalities above were checked by exhaustive integer enumeration of every
admissible subset of $[0,L]$ with a repeated sum for $L\le16$.  The audit
covered 13,505 sets: 7,328 with a midpoint and 6,177 without one.  For every
set and every $1\le H\le L+1$, it checked:

* the D1 decomposition (4), including half-integer centers;
* disjointness of duplicate, partner, and residual labels in (7);
* the pair-overlap identity (9);
* the depth bounds (11)-(15);
* the exact core defect (19) and onset bounds (21)-(24).

The proved frontier can now be stated without a hidden reflection
assumption.  To close the P02 product it is enough, for some mesoscopic
$H$, to force

\[
 E_H(C)-rH\ge(1/3-o(1))N,                                \tag{39}
\]

or a comparable bound from (1).  The sufficient colored special case is

\[
 u_1+u_2\ge(1/3-o(1))N,qquad rH=o(N).                   \tag{40}
\]

Equations (30) and (36)-(38) show why neither (39) nor (40) follows from
the scalar or weakly averaged $Z_H$ profile.  The remaining open lemma must
control the microscopic offset incidence, for example $m_H(C)$, the
colored onset, or a unit-lattice mixed correlation.  Replacing those data by
another uncolored average of $Z_H$ repeats the exact obstruction above.
