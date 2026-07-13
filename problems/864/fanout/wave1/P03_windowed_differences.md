# P03: windowed positive differences

**Outcome: obstruction, with a sharp partial bound and exact witnesses.**

Let

\[
A=\{a_1<\cdots<a_k\},\qquad L=a_k-a_1\leq N-1.
\]

If a repeated sum exists, denote it by \(\sigma\), put
\(R(x)=\sigma-x\), and let

\[
B=A\cap R(A),\qquad b=|B|.
\]

If there is no repeated sum, set \(B=\varnothing\) and \(b=0\).
No assumption that \(A=R(A)\) is made below.

## 1. Reflection lemma for positive differences

Suppose a positive difference has two distinct representations

\[
x-y=u-v>0.
\]

Then \(x+v=y+u\).  The unordered pairs \(\{x,v\}\) and
\(\{y,u\}\) are distinct, so their common sum must be \(\sigma\).
Consequently

\[
v=R(x),\qquad u=R(y).
\]

There cannot be a third representation: once \((x,y)\) is fixed, the
second one is forced to be \((R(y),R(x))\).  Thus every positive
difference has multiplicity at most two, and every doubled difference
uses two reflected edges whose four endpoints (three when a fixed point
is involved) lie in \(B\).

Conversely, two distinct unordered representations of the same sum can
be ordered as \(a<c\leq d<b\), giving
\(c-a=b-d>0\).  If these two difference edges are reflected mates, then
\(a+b=c+d=\sigma\).  Thus the assertion that every doubled difference
consists only of its reflected pair is also sufficient for admissibility.

## 2. Exact finite rank-window inequality

For \(1\leq r<k\), select all edges of index lag at most \(r\):

\[
E_r=\{(i,i+h):1\leq h\leq r,\ 1\leq i\leq k-h\}.
\]

Write

\[
M_r=|E_r|=rk-\frac{r(r+1)}2,
\qquad
S_r=\sum_{h=1}^r\sum_{i=1}^{k-h}(a_{i+h}-a_i).
\]

Let \(q_r\) be the number of difference values occurring twice in
\(E_r\).  There are \(M_r-q_r\) distinct values.  Rearrangement gives
the sharp lower bound based only on \((M_r,q_r)\):

\[
S_r\geq
 \binom{M_r-q_r+1}{2}+\binom{q_r+1}{2}.                 \tag{1}
\]

Indeed, the minimum is obtained by using the integers
\(1,\ldots,M_r-q_r\) and doubling the smallest \(q_r\) of them.

If \(g_j=a_{j+1}-a_j\), then a fixed gap \(g_j\) occurs at most \(h\)
times among the lag-\(h\) edges.  Hence

\[
S_r\leq \binom{r+1}{2}L.                               \tag{2}
\]

The reflection lemma bounds \(q_r\) without assuming global symmetry.
Every doubled value consumes two selected \(B\)-\(B\) edges.  If

\[
t=\min(r,b-1),\qquad
H_r(b)=tb-\frac{t(t+1)}2,
\]

then at most \(H_r(b)\) pairs of the \(b\) marked indices can have
index lag at most \(r\).  Therefore

\[
q_r\leq Q_r:=
\min\left(\left\lfloor\frac{M_r}{2}\right\rfloor,
          \left\lfloor\frac{H_r(b)}{2}\right\rfloor\right).
\]

The right side of (1) decreases for \(0\leq q\leq M_r/2\).  Combining
(1) and (2) proves the finite inequality

\[
\boxed{
 \binom{M_r-Q_r+1}{2}+\binom{Q_r+1}{2}
 \leq \binom{r+1}{2}L.}                                \tag{3}
\]

This is also usable with the actual \(q_r\), which can be computed from
the reflected pairs and is often smaller than \(Q_r\).

## 3. Continuous optimization

Take \(r\to\infty\), \(r=o(k)\), and suppose \(b/k\to\rho\).  From
(1)-(2) and \(q_r\leq rb/2\),

\[
\boxed{
 \frac{L}{k^2}\geq 1-\rho+\frac{\rho^2}{2}-o(1).}       \tag{4}
\]

The coefficient in (4) is optimal for the rank-window relaxation (3).
To see this also for macroscopic windows, put \(r=\alpha k\).  After
division by \(k^2\), set

\[
m=\alpha-\frac{\alpha^2}{2},\qquad
h=\begin{cases}
\alpha\rho-\alpha^2/2,&\alpha\leq\rho,\\
\rho^2/2,&\alpha\geq\rho,
\end{cases}
\qquad z=h/2.
\]

The resulting coefficient is

\[
C(\alpha,\rho)=\frac{(m-z)^2+z^2}{\alpha^2}.
\]

For \(\alpha\leq\rho\), direct expansion gives

\[
C(\alpha,\rho)
=1-\rho+\frac{\rho^2}{2}-\frac\alpha2+\frac{\alpha^2}{8},
\]

which is decreasing on \((0,1]\).  For \(\alpha\geq\rho\),

\[
C(\alpha,\rho)\leq (1-\alpha/2)^2
\leq (1-\rho/2)^2
\leq 1-\rho+\rho^2/2.
\]

Thus \(\alpha\downarrow0\) is the optimizer and yields (4).

The target coefficient \(3/4\) follows from (4) only when

\[
1-\rho+\rho^2/2\geq 3/4,
\quad\text{i.e.}\quad
\rho\leq 1-\frac1{\sqrt2}=0.292893\ldots .              \tag{5}
\]

So this lane proves the desired asymptotic bound whenever at most a
\((1-1/\sqrt2+o(1))\)-fraction of \(A\) has a \(\sigma\)-partner.  The
remaining high-reflection regime is the obstruction.

## 4. Sharpness inside the lag-window class

Consider a fully reflected set with \(k=2p\) and no central fixed point.
Reflection sends the edge \((i,i+h)\) to
\((2p+1-i-h,2p+1-i)\), preserving its lag.  For the initial window,

\[
q_r=\frac{M_r-\lceil r/2\rceil}{2}.                     \tag{6}
\]

The subtracted edges are exactly the self-reflected pairs.  Hence every
local window is asymptotically half doubled, and (1)-(2) yield only

\[
L\geq (2-o(1))p^2=(1/2-o(1))k^2.                        \tag{7}
\]

This is not an artifact of choosing consecutive lags.  If a lag-only
window uses a set \(J\) of \(s\) lags with \(\max J=o(k)\), then its gap
coefficient is at most \(\sum_{h\in J}h\), while all but \(O(s)\) of
its edges are paired.  The multiplicity/rearrangement calculation can
therefore certify at most the coefficient

\[
\frac{s^2}{4\sum_{h\in J}h}\leq\frac12+o(1),
\]

because \(\sum_{h\in J}h\geq s(s+1)/2\).  Consecutive initial lags
attain the limit.  Reflection pairing alone therefore cannot raise the
fully reflected constant from \(1/2\) to the required \(3/4\).

## 5. Exact reflected test and counterexample to range separation

Take

\[
X=\{0,1,3,8,12\},\qquad T=30,
\]

and form the shifted reflected set

\[
A_R=\{1,2,4,9,13,19,23,28,30,31\}\subset[31].
\]

Its exceptional sum is \(32\), with exactly the five representations

\[
(1,31),(2,30),(4,28),(9,23),(13,19).
\]

Here is an exact certificate that there is no other repeated sum.  The
positive-difference orbits are the following two disjoint sets:

\[
\begin{aligned}
D&=\{x_j-x_i:i<j\}\\
 &=\{1,2,3,4,5,7,8,9,11,12\},\\
C&=\{T-x_i-x_j:i\leq j\}\\
 &=\{6,10,14,15,17,18,19,21,22,24,26,27,28,29,30\}.
\end{aligned}
\]

All \(25\) labels are distinct.  Thus every repeated difference is
exactly its reflected mate, which by Section 1 is equivalent to the
claimed sum condition.

For the rank-2 window one has

\[
M_2=17,\quad q_2=8,\quad S_2=88.
\]

The doubled labels are
\(1,2,3,4,5,7,9,10\), and the only singleton is \(6\).  Consequently

\[
81=\binom{10}{2}+\binom{9}{2}
\leq S_2=88
\leq 3L=90.                                             \tag{8}
\]

Both sides of the window argument are already close to equality.

This set also kills the tempting geometric bridge for reflected sets.
The lower block has span \(W=12\), but its central reflected gap is

\[
G=T-2W=6<W,
\]

so neither \(G\geq W\) nor \(T\geq3W\) is universally true.  This is
an exact counterexample, not a continuous relaxation.

## 6. Exact unbalanced test

Delete three partners from the preceding set:

\[
A_U=\{1,2,4,9,13,30,31\}\subset[31].
\]

The only repeated sum is again \(32\), now represented by
\((1,31)\) and \((2,30)\).  Thus

\[
B=\{1,2,30,31\},\qquad b=4,
\]

while \(4,9,13\) are unpaired.  The only globally doubled positive
differences are

\[
1:(1,2),(30,31),qquad
29:(1,30),(2,31).
\]

In its rank-2 window the second doubled value is not selected, and

\[
M_2=11,\quad q_2=1,\quad S_2=88,
\]

so the exact check is

\[
56=\binom{11}{2}+\binom22
\leq88\leq90=3L.                                       \tag{9}
\]

This verifies that (1)-(4) do not rely on an ambient reflection
assumption; only the endpoints of actually doubled differences are
reflected.

## 7. Continuous marginal-count obstruction

There is a stronger obstruction to any argument that retains only the
marginal distribution of the two reflected label families.  In a fully
reflected continuous relaxation, distribute the lower marks uniformly
over a span

\[
W=p^2,\qquad G=0,\qquad L=2p^2.
\]

Normalize a label threshold as \(t=sW\).  The limiting numbers of
within-side difference labels and cross labels below \(t\), divided by
\(p^2\), are

\[
d(s)=\begin{cases}s-s^2/2,&0\leq s\leq1,\\1/2,&1\leq s\leq2,
\end{cases}
\]

and

\[
c(s)=\begin{cases}s^2/4,&0\leq s\leq1,\\
1/2-(2-s)^2/4,&1\leq s\leq2.
\end{cases}
\]

Distinct integer labels below \(t\) have capacity \(s p^2\).  This
relaxation passes every such threshold test, since

\[
d(s)+c(s)=s-s^2/4\leq s\quad(0\leq s\leq1),
\]

and

\[
d(s)+c(s)=1-(2-s)^2/4\leq s\quad(1\leq s\leq2).
\]

It has \(L/k^2=1/2\), exactly the ceiling in (7).  This is deliberately
a pseudo-construction, not an admissible integer set: it shows that
continuous threshold counts and their nonnegative weighted integrals
discard the arithmetic information needed to reach \(3/4\).

## 8. Precise obstruction / next lemma

For a fully reflected core, write its lower representatives as
\(x_1<\cdots<x_p<\sigma/2\).  Besides distinctness, the labels satisfy
the coupled identities

\[
d_{ij}=x_j-x_i,qquad
c_{ij}=\sigma-x_i-x_j,qquad
e_i=\sigma-2x_i,qquad
d_{ij}+c_{ij}=e_i.                                      \tag{10}
\]

The window proof uses only that each label has multiplicity one or two;
the continuous marginal relaxation also discards (10).  The missing
high-leverage statement must exploit these coupled triples.  In the
fully reflected case it would need to prove

\[
\max A-\min A\geq(3-o(1))p^2
\]

from the distinctness of all \(d_{ij},c_{ij},e_i\).  The exact set
\(A_R\) shows that this cannot be replaced by pointwise separation of
the \(d\)- and \(c\)-ranges.  Without such a coupled-label lemma, the
sharp optimized window method stops at (4), leaving precisely the
regime \(\rho>1-1/\sqrt2\).
