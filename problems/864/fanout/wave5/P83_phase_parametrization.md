# P83: exact phase parametrization of loose fold triangles

## Verdict

Every loose fold triangle has a unique seven-parameter affine normal form.
The form retains all nine raw ruler marks, the shift `h`, and the endpoint
phase `b`.  It gives two exact injections:

\[
 \tau\longmapsto(a,c,u),\qquad
 \tau\longmapsto(d,d+Z,d+X),\quad d=a+c+b.              \tag{1}
\]

The second target is an ordered triple of distinct literal-hole difference
labels.  In particular,

\[
                    T_F(B,h)\leq {p+1\choose3}.          \tag{2}
\]

This is only an `O(p^3)` bound and does not close P82's required little-oh
estimate.  Two exact finite checks show why the most direct endpoint repairs
do not improve it: 22 of the 25 P75 triangles have `a+c+u+b>h-1`, and a
seven-point positive-defect literal-hole ruler has a loose triangle for which
the tempting fourth label `d-R` is a represented difference.

## 1. Unique normal form

Retain all variables in P82's three folds, writing them as

\[
\begin{array}{rcl}
 F_0:&a+c+h&=r+s,\\
 F_Z:&a+z+h&=u+w,\\
 F_X:&x+c+h&=u+y,
\end{array}                                             \tag{3}
\]

with the canonical fold orders

\[
 a\leq c<r\leq s,\qquad
 a\leq z<u\leq w,\qquad
 x\leq c<u\leq y.                                      \tag{4}
\]

The three shadow edges meet at the labelled vertices `a_A,c_C,u_U`.

### Lemma P83.1 (phase-retaining parametrization)

There is a bijection between loose fold triangles and integer tuples

\[
                       (a,c,u,s,X,Z,R)                   \tag{5}
\]

such that the following nine numbers belong to `B`:

\[
\begin{array}{c}
 a,\ c,\ u,\ s,\quad a+X,\ c+Z,\ u+R,\\
 s+R+X,\quad s+R+Z,                                    \tag{6}
\end{array}
\]

the endpoint equation is

\[
                       a+c+h=u+R+s,                      \tag{7}
\]

and

\[
\begin{array}{rcl}
 a&\leq&c<u+R\leq s,\\
 a&\leq&c+Z<u\leq s+R+Z,\\
 a+X&\leq&c<u\leq s+R+X.                              \tag{8}
\end{array}
\]

Here `X,Z,R` are nonzero.  The raw variables in (3) are recovered exactly by

\[
\boxed{
 x=a+X,\quad z=c+Z,\quad r=u+R,\quad
 y=s+R+X,\quad w=s+R+Z.}                               \tag{9}
\]

#### Proof

Given (3), define

\[
                       X=x-a,\quad Z=z-c,\quad R=r-u.
\]

The first fold gives (7).  Subtracting its equation from the other two,
without eliminating `h`, gives

\[
                       w-s=R+Z,\qquad y-s=R+X,
\]

which proves (9).  The three fold orders are exactly (8).  Pairwise
distinctness of the three supporting hyperedges, together with P82.1,
forces `X,Z,R` to be nonzero.

Conversely, (6)--(8) and (9) give all three equations and orders in
(3)--(4).  Their labelled hyperedges are

\[
 (a,c,u+R),\qquad(a,c+Z,u),\qquad(a+X,c,u).
\]

They are distinct and meet pairwise at `a_A,c_C,u_U`, so they form one loose
triangle.  Both constructions recover every variable, proving bijectivity.
QED.

## 2. Endpoint phase and the literal hole

Put `H=h-1` and

\[
                         d=a+c+b,\qquad \lambda=H-d.     \tag{10}
\]

The low pairs of the three folds in (3) give the ordered labels

\[
 (d_0,d_Z,d_X)=(d,d+Z,d+X)
 =(a+c+b,a+z+b,x+c+b).                                  \tag{11}
\]

The literal hole therefore gives

\[
             d_0,d_Z,d_X\notin\Delta^+(B).              \tag{12}
\]

These labels retain the endpoint phase through the exact complementary-pair
identities

\[
\begin{array}{rcl}
 \lambda&=&(H-r)+(H-s)+1-b,\\
 \lambda-Z&=&(H-u)+(H-w)+1-b,\\
 \lambda-X&=&(H-u)+(H-y)+1-b.                           \tag{13}
\end{array}
\]

Thus for `b=1` the three endpoint phases are literal pair sums from `H-B`.
For `b=2` they are those pair sums shifted down by one.  This is the
one-unit discrepancy noted in P82, now retained in every triangle variable.

The same normal form also gives the represented signed-difference hexagon

\[
 \boxed{X,Z,R,R+X,R+Z,Z-X\in B-B,}                      \tag{14}
\]

with the coherent representations

\[
\begin{array}{lll}
 X=x-a,&Z=z-c,&R=r-u,\\
 R+X=y-s,&R+Z=w-s,&Z-X=w-y.                             \tag{15}
\end{array}
\]

Equations (11)--(15) are an exact phase-sensitive description: a represented
difference hexagon is accompanied by three specified nonedges of the
difference support, and (7) locates the configuration at the endpoint shift.

## 3. Two injections and the quantitative bound

The map to the shared vertices `(a,c,u)` is injective.  Indeed, P82.1 says
that `(a,c)`, `(c,u)`, and `(u,a)` each support at most one fold, so these
three coordinates recover all three edges.  Equation (8) gives
`a<=c<u`.  If `B={b_0<...<b_{p-1}}`, the number of possible triples is

\[
 \sum_{j=0}^{p-1}(j+1)(p-1-j)
 ={p(p-1)(p+1)\over6}={p+1\choose3},                    \tag{16}
\]

which proves (2).

There is also an injection into literal-hole slots.  From an ordered label
triple in (11), subtract `b`.  Integer Sidonicity recovers each of the three
low pairs from its sum, and adding the fixed `h` recovers each high pair.
The ordered roles then recover the loose triangle.  The labels are pairwise
distinct because coincident low sums would give the same fold.  Hence (1)
maps every triangle injectively to three distinct members of

\[
 \mathcal F_b={q+b:q\in B+B,\ q+h\in B+B\}
              \subseteq(B+B+b)\setminus\Delta^+(B).     \tag{17}
\]

This is the requested bounded-multiplicity connection to the literal hole,
but it does not itself save a power of `p`: under the bad alternative
`C_S=Omega(p^2)`, the set in (17) can also have quadratic size.

## 4. Exact barriers to pointwise completion

First, the shared-vertex injection does not usually land at an in-range
endpoint hole.  Its natural target would be

\[
                         a+c+u+b\notin B.                \tag{18}
\]

For the P75 ruler, exact enumeration gives `T_F=25`, but only three shared
triples satisfy `a+c+u+b<=H`; the other 22 lie above the endpoint.  Thus (18)
is a finite falsifier to using the shared triple as an in-range hole label
for every loose triangle.

Second, (12) cannot be enlarged by the most symmetric-looking fourth label.
Take

\[
 B=\{5,7,18,24,25,28,33\},\qquad h=34,\qquad b=2.       \tag{19}
\]

This set is integer Sidon, has

\[
 \delta={3\cdot7^2-7+2\over2}-34=37>0,
 \qquad \Delta^+(B)\cap(B+B+2)=\varnothing,             \tag{20}
\]

and has the loose triangle

\[
\begin{array}{rcl}
 5+7+34&=&18+28,\\
 5+18+34&=&24+33,\\
 7+7+34&=&24+24.                                       \tag{21}
\end{array}
\]

Its parameters are

\[
 (a,c,u,s;X,Z,R)=(5,7,24,28;2,11,-6),
 \qquad(d,d+Z,d+X)=(14,25,16).                          \tag{22}
\]

All three labels in (22) are absent positive differences, as required.
However,

\[
                         d-R=20=25-5\in\Delta^+(B).      \tag{23}
\]

Thus the literal hole plus the full loose-triangle equations do not force
the fourth Cayley nonedge `d-R`.  Any denser induced-configuration argument
using that extra nonedge is false.

## 5. Exact audit and claim boundary

The standalone integer checker is
`compute/p83/audit_phase_parametrization.py`.  It verifies every identity,
both injections, and (2) on P75; it obtains

```text
p=26, h=988, b=1, delta=14, C_S=51, T_F=25,
phase keys=25, shared keys=25, in-range shared targets=3.
```

It separately verifies (19)--(23), where `C_S=4` and `T_F=1`.  No floating
point arithmetic is used.

The proved outputs are the bijective parametrization P83.1, the two
injections (1), and the cubic bound (2).  They do not prove
`T_F=o(p^3)`, a phase-sensitive joint estimate, or an infinite
counterfamily.  The surviving quantitative task is to show that the
phase-decorated configurations (7), (11)--(15) occupy a vanishing fraction
of the `binom(p+1,3)` possible shared triples.

The parametrization and (2) require only endpoint normalization and integer
Sidonicity.  The literal hole enters precisely in (12) and (17); positive
defect is used only to place the two finite audits inside the live frontier.
