# P76: P61 + P74 do not assemble the general sharp bound

## Verdict

The two P61 branches, the exact original difference packing, the uniform
P74 charge

\[
  2\beta\le h_S \qquad (|A|\ge1726),
\]

and a hypothetical reflected estimate

\[
 H_\delta(q)\ge {3\over4}(2q+\delta)^2-o(q^2)
\]

do **not** imply

\[
 L\ge {3\over4}k^2-o(k^2)
\]

for a general admissible set.  The complete normalized optimization of
these inequalities has minimum

\[
 \boxed{\inf {L\over k^2}={3\over8}},
\]

not \(3/4\).  The minimum occurs at

\[
 {u\over k}={b\over k}=1-{1\over\sqrt2}.
\]

An exact asymptotic integer parameter ray satisfying every inequality is
given in Section 4.  This is a logical obstruction to the proposed
assembly, not a construction of admissible sets with that density.

## 1. Exact data from P56, P61, and P74

Use the endpoint-normalized P56 notation

\[
 c=2p+\delta,\qquad k=c+u,\qquad b=\min(u,\beta),
 \qquad \delta\in\{0,1\}.
\]

The exact positive-difference count is

\[
 D:=|D^+(A)|=p(p+\delta)+cu+\binom u2,                 \tag{1}
\]

so every actual set also satisfies

\[
 L\ge D.                                                \tag{2}
\]

The exact number of missing sum labels is

\[
 h_S=2L-\left(2p(p+\delta)+cu+\binom{u+1}{2}\right).   \tag{3}
\]

P61 gives

\[
 2L\ge H_\delta(p)+
 \max\left\{
 H_\delta(p+u-b),
 D+\binom{u-b+1}{2}
 \right\}.                                             \tag{4}
\]

P74 gives \(2\beta\le h_S\) for \(k\ge1726\).  Since
\(b\le\beta\), it follows that

\[
 2b\le h_S.                                             \tag{5}
\]

The scale in (5) is important: \(b=O(k)\), whereas \(h_S\) may be
\(\Theta(k^2)\).  Consequently (5) need not impose any nonzero
quadratic-scale restriction.

## 2. Full normalized optimization

Consider a sequence with \(k\to\infty\), and put

\[
 x={u\over k},\qquad y={b\over k},\qquad
 \lambda={L\over k^2}.
\]

Then

\[
 0\le y\le x\le1,
 \qquad {2p+\delta\over k}=1-x.
\]

At any point with \(p\) and \(p+u-b\) proportional to \(k\), the
hypothetical reflected estimate and the first branch of (4) give

\[
 \lambda\ge G_1(x,y)-o(1),                              \tag{6}
\]

where

\[
 G_1(x,y)
 ={3\over8}\left((1-x)^2+(1+x-2y)^2\right).            \tag{7}
\]

The label branch of (4) gives

\[
 \lambda\ge G_2(x,y)-o(1),                              \tag{8}
\]

where

\[
 \begin{aligned}
 G_2(x,y)
 &={3\over8}(1-x)^2+{1\over8}(1+x-2y)^2
   +{y\over2}-{y^2\over4}\\
 &={1\over2}-{x\over2}+{x^2\over2}
   -{xy\over2}+{y^2\over4}.
 \end{aligned}                                          \tag{9}
\]

The independent exact packing (2) gives

\[
 \lambda\ge G_0(x)-o(1),
 \qquad
 G_0(x)={1+2x-x^2\over4}.                              \tag{10}
\]

Finally, the represented-sum expression in (3) has the notable
normalization

\[
 {1\over k^2}\left(2p(p+\delta)+cu+\binom{u+1}{2}\right)
 ={1\over2}+o(1),                                       \tag{11}
\]

uniformly in \(x\).  Thus

\[
 {h_S\over k^2}=2\lambda-{1\over2}+o(1).               \tag{12}
\]

After division by \(k^2\), (5) becomes

\[
 {2y\over k}\le 2\lambda-{1\over2}+o(1).              \tag{13}
\]

Whenever \(\lambda>1/4\), (13) is automatic for all fixed
\(0\le y\le x\).  Therefore P74 adds no limiting constraint at the
candidate minimum below.

It remains to minimize

\[
 G(x,y):=\max\{G_0(x),G_1(x,y),G_2(x,y)\}               \tag{14}
\]

over \(0\le y\le x\le1\).

### Proposition P76.1

\[
 \boxed{
 \min_{0\le y\le x\le1}G(x,y)={3\over8}.
 }
\]

### Proof

Put

\[
 x_0=1-{1\over\sqrt2}.
\]

The function \(G_0(x)=(1+2x-x^2)/4\) is increasing on \([0,1]\).
Hence, if \(x\ge x_0\),

\[
 G(x,y)\ge G_0(x)\ge G_0(x_0)={3\over8}.              \tag{15}
\]

If \(x\le x_0\), then \(y\le x\) implies

\[
 1+x-2y\ge1-x.
\]

Therefore

\[
 G(x,y)\ge G_1(x,y)
 \ge {3\over4}(1-x)^2
 \ge {3\over4}(1-x_0)^2={3\over8}.                    \tag{16}
\]

At \((x,y)=(x_0,x_0)\), all three bounds are equal:

\[
 G_0(x_0)={3\over8},
\]

\[
 G_1(x_0,x_0)={3\over4}(1-x_0)^2={3\over8},
\]

and

\[
 G_2(x_0,x_0)
 ={1+(1-x_0)^2\over4}={3\over8}.                       \tag{17}
\]

This proves both the lower bound and attainment.  QED.

The minimizer has \(y=x\), hence \(b=u\): the P56 repair deletes all
residual points, and both reflected applications in P61 collapse to the
same paired core.  The original difference packing is exactly the third
active constraint.

## 3. Why P74 is slack at the minimizer

At the minimizing point,

\[
 \lambda={3\over8},
 \qquad {h_S\over k^2}\longrightarrow {1\over4}.       \tag{18}
\]

Taking \(\beta=b=u=x_0k+o(k)\), one has

\[
 {2\beta\over h_S}=O(k^{-1})\longrightarrow0.          \tag{19}
\]

Thus even the exact P74 inequality has quadratic slack.  The charge
controls the number of colliding virtual labels, but the P56 repair cost
is capped at \(u\); once \(\beta\ge u\), increasing the sum-hole bank no
longer improves the repaired reflected size.

This is the precise scaling reason the P74 theorem cannot close the P61
assembly.

## 4. Exact asymptotic feasible parameter obstruction

The preceding minimizer can be realized by integer parameters satisfying
all the displayed inequalities, without any limiting handwave.

For each integer \(n\ge2\), let

\[
 t=2(\sqrt2-1),\qquad
 p=n,\quad \delta=0,\quad
 u=\lceil tn\rceil+1,quad c=2n,quad k=2n+u,
\]

and set

\[
 b=\beta=u.                                             \tag{20}
\]

Use the exact reflected model

\[
 \widehat H_0(r)=3r^2,                                  \tag{21}
\]

which satisfies the hypothetical reflected estimate with zero error.  Put

\[
 D=n^2+2nu+\binom u2,
 \qquad L=D.                                             \tag{22}
\]

Since \(u\ge tn+1\) and \(t^2/2+2t=2\),

\[
 \begin{aligned}
 D-3n^2
 &=2nu+{u(u-1)\over2}-2n^2\\
 &\ge 2n(tn+1)+{(tn+1)tn\over2}-2n^2\\
 &=2n+{tn\over2}>0.                                    \tag{23}
 \end{aligned}
\]

Here \(p+u-b=p=n\) and \(\binom{u-b+1}{2}=0\).  Therefore the exact P61
right side is

\[
 \widehat H_0(n)+\max\{\widehat H_0(n),D\}
 =3n^2+D\le2D=2L,                                      \tag{24}
\]

so both P61 branches hold.  Difference packing holds with equality.

The exact sum-hole count is

\[
 \begin{aligned}
 h_S
 &=2D-\left(2n^2+2nu+\binom{u+1}{2}\right)\\
 &={u(4n+u-3)\over2}.                                  \tag{25}
 \end{aligned}
\]

For \(n\ge2\), equation (25) gives \(h_S\ge2u=2\beta\), so the P74
charge also holds exactly.  All parameters are nonnegative integers and
\(b=\min(u,\beta)\).

Finally,

\[
 {u\over n}\longrightarrow t,qquad
 {k\over n}\longrightarrow2+t=2\sqrt2,
\]

while

\[
 {L\over n^2}
 \longrightarrow1+2t+{t^2\over2}=3.                   \tag{26}
\]

Consequently

\[
 \boxed{
 {L\over k^2}\longrightarrow {3\over8}< {3\over4}.
 }                                                       \tag{27}
\]

This exact parameter ray proves that the named lemmas and constraints do
not logically imply the desired general sharp bound.

## 5. Consequence for the proof program

P74 correctly closes the standalone completion-charge statement
\(2\beta\le h_S\), but that charge is at the wrong scale for P61 once
\(b=\min(u,\beta)=u\).  A successful assembly needs a new statement that
prevents the normalized corner

\[
 b/u\to1,qquad
 {u\over k}\to1-{1\over\sqrt2},qquad
 {h_S\over k^2}\to{1\over4},                           \tag{28}
\]

or extracts additional span from it.  Equivalently, it must relate the
*repair cover number* \(b\), not merely the collision count \(\beta\), to
the placement of the quadratic sum-hole bank.  Neither P61 nor P74 supplies
that relation.

