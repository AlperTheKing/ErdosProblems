# Erdős 156: alteration and repair audit

## Status

This note audits only the alteration, repeated-lift, and deterministic
covering variants of Ruzsa's Singer lift (source: `problems_external/erdos_156/ruzsa_source.pdf`, pp. 56-58).  It does **not** prove Erdős 156.
The audited first-moment mechanisms retain the logarithmic loss.  A
correlated one-block saturation lemma remains the single missing bridge.

## 1. Setup

Let
\[
q=p^2+p+1,\qquad B=\{b_0,\ldots,b_p\}\subseteq \mathbb Z/q\mathbb Z
\]
be a Singer Sidon set, represented in \(\{1,\ldots,q\}\).  Choose independent
uniform variables
\[
d_i\in\{0,\ldots,M-1\}
\]
and put
\[
a_i=b_i+qd_i,\qquad A_0=\{a_0,\ldots,a_p\}.
\]
Every choice of the \(d_i\) makes \(A_0\) Sidon.

For a nonexceptional integer \(m\), meaning
\[
m\not\equiv b_i\pmod q\quad\text{for every }i,
\]
Ruzsa's lemma supplies at least \(I_m\ge p/8\) pairwise variable-disjoint
index triples \((u_j,v_j,w_j)\) satisfying
\[
m\equiv b_{u_j}+b_{v_j}-b_{w_j}\pmod q.
\]
The corresponding exact lift equation is
\[
d_{u_j}+d_{v_j}-d_{w_j}=t_{m,j},\qquad
t_{m,j}:=\frac{m-b_{u_j}-b_{v_j}+b_{w_j}}q.
\]
In Ruzsa's range,
\[
-1\le t_{m,j}\le M+1.
\]
If this equation holds, then
\[
m+a_{w_j}=a_{u_j}+a_{v_j},
\]
and the nonexceptional residue assumption makes the two unordered pairs
different.  Thus adjoining \(m\) destroys the Sidon property.

## 2. Exact one-equation probabilities

For three distinct indices define
\[
S_M(t)=\#\{(x,y,z)\in[0,M-1]^3:x+y-z=t\}.
\]
Let
\[
T_M(s)=
\begin{cases}
s+1,&0\le s\le M-1,\\
2M-1-s,&M\le s\le2M-2,\\
0,&\text{otherwise}.
\end{cases}
\]
Then the exact identity is
\[
S_M(t)=\sum_{z=0}^{M-1}T_M(t+z).
\]
In the full range used by Ruzsa this gives
\[
S_M(-1)=\frac{M(M-1)}2,
\]
\[
S_M(t)=\frac{M(M+1)}2+tM-t(t+1)
\quad(0\le t\le M-1),
\]
\[
S_M(M)=\frac{M(M-1)}2,
\qquad
S_M(M+1)=\frac{(M-1)(M-2)}2.
\]
Consequently
\[
\Pr(d_u+d_v-d_w=t)=\frac{S_M(t)}{M^3}
\ge \frac{(M-1)(M-2)}{2M^3}.
\]

When \(u=v\), define
\[
S'_M(t)=\#\{(x,z)\in[0,M-1]^2:2x-z=t\}.
\]
The exact formula is
\[
S'_M(t)=
\max\!\left(
0,\,
\min\!\left(M-1,\left\lfloor\frac{t+M-1}{2}\right\rfloor\right)
-
\max\!\left(0,\left\lceil\frac t2\right\rceil\right)
+1
\right).
\]
For \(-1\le t\le M+1\),
\[
S'_M(t)\ge \left\lfloor\frac{M-2}{2}\right\rfloor,
\qquad
\Pr(2d_u-d_w=t)=\frac{S'_M(t)}{M^2}.
\]
In particular, for every \(M\ge4\), both types of equation have probability
at least
\[
\alpha_M:=\frac1{8M}.
\]

## 3. Exact residual identity and the certified bound

For each \(m\), let \(\pi_{m,j}\) be the appropriate exact probability from
Section 2.  The selected triples have disjoint variable supports, including
the two-variable support when \(u_j=v_j\).  Hence the exact probability that
all selected witnesses fail is
\[
\Pr(E_m^*)=\prod_{j=1}^{I_m}(1-\pi_{m,j}).
\]
If \(E_m\) is the event that **all** admissible Singer witnesses fail, then
\[
E_m\subseteq E_m^*.
\]
Let \(U(d)\) be the number of genuinely uncovered nonexceptional integers in
\([1,N]\), and let \(U^*(d)\) count misses for only the selected disjoint
witness families.  Linearity of expectation gives the exact identity
\[
\mathbb E U^*
=\sum_{\substack{1\le m\le N\\m\not\equiv B\pmod q}}
\prod_{j=1}^{I_m}(1-\pi_{m,j}),
\]
and
\[
\mathbb E U\le\mathbb E U^*.
\]
Using \(I_m\ge p/8\) and \(\pi_{m,j}\ge1/(8M)\),
\[
\boxed{\mathbb E U
\le N\left(1-\frac1{8M}\right)^{p/8}
\le N\exp\!\left(-\frac{p}{64M}\right).}
\]
This is the complete certified residual estimate from the disjoint-family
argument.  It is an upper bound; it is not a lower bound on the true number
of uncovered integers, because overlapping unselected witnesses may help.

For the selected-family surrogate, the retained constant-failure regime is
also explicit.  Each one-equation probability is \(O(1/M)\), and
\(I_m\le p+1\).  Therefore, when \(p/M=O(1)\), the product defining
\(\Pr(E_m^*)\) is bounded below by a positive constant depending only on that
ratio.  Thus the selected disjoint family by itself misses a positive
proportion in expectation at the scale \(M=\Theta(p)\).  This statement does
not exclude a new argument using all correlated witnesses.

## 4. Exact maximal-completion cost

Fix a lift assignment and extend \(A_0\) to any maximal Sidon set
\(A\subseteq[1,N]\).  Split the new elements into
\[
R=\{a\in A\setminus A_0:a\not\equiv B\pmod q\}
\]
and
\[
T=\{a\in A\setminus A_0:a\equiv b_i\pmod q
\text{ for some }i\}.
\]

Every element of \(R\) was genuinely uncovered by \(A_0\), so
\[
|R|\le U(d).
\]

For \(a\in T\), let \(i(a)\) be the unique index with
\(a\equiv b_{i(a)}\pmod q\), and define
\[
\Delta(a)=a-a_{i(a)}.
\]
Then \(\Delta(a)\) is a nonzero multiple of \(q\) in
\([-(N-1),N-1]\).  If \(\Delta(a)=\Delta(a')\), then
\[
a+a_{i(a')}=a'+a_{i(a)},
\]
contradicting the Sidon property unless \(a=a'\).  Hence the map
\(a\mapsto\Delta(a)\) is injective and
\[
|T|\le2\left\lfloor\frac{N-1}{q}\right\rfloor.
\]
Therefore the exact repair estimate is
\[
\boxed{|A|\le p+1+U(d)
+2\left\lfloor\frac{N-1}{q}\right\rfloor.}
\]
By averaging, there is a lift assignment for which
\[
|A|\le p+1
+N\exp\!\left(-\frac{p}{64M}\right)
+2\left\lfloor\frac{N-1}{q}\right\rfloor.
\]

## 5. Why first-moment alteration retains the logarithm

At the desired scale \(p^3=\Theta(N)\),
\[
q=\Theta(p^2),\qquad M=\Theta(N/q)=\Theta(p),
\]
so \(p/M=\Theta(1)\).  The certified residual term in Section 4 is then only
\(O(N)\), not \(O(p)\).

For the alteration bound to give an \(O(p)\) completion, it is necessary
within this proof that
\[
N\exp\!\left(-\frac{p}{64M}\right)=O(p),
\]
or equivalently
\[
\frac pM\ge64\log(N/p)-O(1).
\]
Since \(M=\Theta(N/p^2)\), this requires
\[
p^3\gg N\log(N/p),
\]
which is precisely the retained logarithmic loss (up to constants and the
equivalent \(\log p\) form).

This is an obstruction to the audited first-moment proof mechanism, not a
lower bound ruling out a better lift assignment.

## 6. Repeated rounds and deterministic covering

### Independent lift rounds

Suppose one uses \(T\) independent Singer lift blocks.  Even granting, without
proof, that their union can be made Sidon, repeating the same disjoint-family calculation certifies the upper bound
\[
\exp\!\left(-\Theta(Tp/M)\right).
\]
At \(M=\Theta(p)\), making this certified repair bound \(O(p)\) requires
\[
T=\Omega(\log(N/p)).
\]
The blocks themselves then contain
\[
T(p+1)=\Omega(p\log(N/p))
\]
elements.  Hence independent multiround covering merely moves the logarithm
from the residual term into the size of the set.  In addition, an untagged
union of lift blocks is not automatically Sidon because of cross-round sums.

### Resampling the same variables

Resampling the same \(p+1\) lift variables does not produce a monotone
covering process: a change that repairs one integer can destroy witnesses for
previously covered integers.  Accumulating the union of the assignments
reduces to the preceding oversized multiblock construction.  No monotone
potential or invariant proving simultaneous saturation is present in the
Ruzsa argument.

### Conditional expectation and deterministic choice

Applying conditional expectation to \(U^*\), or directly to the upper bound
for \(U\), produces one assignment with residual no larger than the
first-moment average.  It therefore reproduces
\[
U(d)\le N\exp(-p/(64M))
\]
and does not remove the logarithm.  The generic deterministic set-cover guarantee for several constant-coverage assignments likewise uses \(O(\log(N/p))\) blocks; beating it requires additional incidence structure not supplied by this calculation.

## 7. Verdict and the single missing bridge

No audited alteration, independent multiround, resampling, or conditional
expectation argument proves saturation at \(p^3=\Theta(N)\).

The exact missing theorem-closing lemma is:

> For \(q=p^2+p+1\), \(M=\Theta(p)\), and all sufficiently large \(p\), there
> is one vector \(d\in[0,M-1]^{p+1}\) such that every nonexceptional
> \(m\in[1,N]\) satisfies at least one admissible Singer lift equation.

This correlated one-block statement, combined with the exact completion
bound in Section 4, would give a maximal Sidon set of size \(O(p)=O(N^{1/3})\).
None of the mechanisms audited here proves it.

Route-A exit condition for this family:

`DEAD: alteration/independent-round/conditional-expectation mechanisms retain
the logarithm; only an unaudited correlated one-block saturation invariant
could reopen the route.`



