# P11: exact truncated-energy barrier

## Verdict

The P07 cutoff inequality, even with the **exact** value of

\[
 \Phi_{Z,G}(u)=\sum_{0\le i\le j<p}(u-G-z_i-z_j)_+,
\]

does not force

\[
 G+2W\ge (3-o(1))p^2.
\]

There is an exact integer rank-relaxation countermodel.  For every
\(p\ge2\), put

\[
 \widetilde z_i=pi\quad(0\le i<p),\qquad
 \widetilde G=1,\qquad
 \widetilde W=p(p-1).
 \tag{1}
\]

Keep P07's formal number of selected lag differences

\[
 M_r=rp-\frac{r(r+1)}2,
\]

and compute \(T_r\) and \(\Phi\) from (1).  Then for every integer
\(1\le r<p\) and every integer \(u\ge1\),

\[
 \boxed{
 uM_r-\binom u2+\widetilde\Phi_p(u)\le \widetilde T_r.}
 \tag{2}
\]

Nevertheless,

\[
 \widetilde G+2\widetilde W
 =2p^2-2p+1=(2+o(1))p^2.                 \tag{3}
\]

The profile (1) is deliberately not a Sidon ruler: it is a countermodel to
the **scalar cutoff/rank system**, not a counterexample to Problem 864.
It shows exactly what the system forgets.  Once the lag differences have
been replaced by their formal cardinality \(M_r\), all microscopic
difference multiplicities and the unit-lattice phase separating
\(D(Z)\) from \(G+S(Z)\) are gone.  No optimization of \(r,u\), and no
lower bound for \(\Phi\) that depends only on this rank profile, can recover
the missing coefficient.

This is the finite integer counterpart of P13's sharp continuum barrier.
A surviving argument must retain a microscopic integrality invariant; a
purely continuum or macroscopic truncated-energy lemma is dead.

## 1. Exact barrier theorem

For (1), define

\[
 \widetilde T_r
 =\sum_{h=1}^r\sum_{i=0}^{p-h-1}
   (\widetilde z_{i+h}-\widetilde z_i)
 =p\sum_{h=1}^r h(p-h),                              \tag{4}
\]

and

\[
 \widetilde\Phi_p(u)
 =\sum_{0\le i\le j<p}(u-1-p(i+j))_+.               \tag{5}
\]

**Theorem 1 (exact rank-relaxation barrier).**  Equations (2)--(5) hold
for all integers \(p\ge2\), \(1\le r<p\), and \(u\ge1\).

### Proof

For fixed \(u\), the part of the left side of (2) which depends on \(r\)
is \(uM_r-\widetilde T_r\).  Its successive difference is

\[
 \begin{aligned}
 &(uM_{r+1}-\widetilde T_{r+1})
  -(uM_r-\widetilde T_r)\\
 &\hspace{35mm}=(p-r-1)\bigl(u-p(r+1)\bigr).          \tag{6}
 \end{aligned}
\]

Thus the maximizing rank is determined exactly by the quotient of \(u-1\)
by \(p\).  Write

\[
 u-1=qp+s,\qquad 0\le s<p.                             \tag{7}
\]

If \(q=0\), the maximum is attained at \(r=1\).  If
\(1\le q\le p-1\), it is attained at \(r=q\) (with a harmless adjacent
tie when \(s=p-1\)).  If \(q\ge p\), it is attained at \(r=p-1\).

Let

\[
 c_t=\#\{(i,j):0\le i\le j<p,\ i+j=t\}.
\]

For \(0\le q\le2p-2\), (5) is exactly

\[
 \widetilde\Phi_p(u)
 =p\sum_{t<q}c_t(q-t)+s\sum_{t\le q}c_t.               \tag{8}
\]

For \(0\le t<p\),

\[
 c_t=\left\lfloor\frac t2\right\rfloor+1.             \tag{9}
\]

Consequently, if \(q=2a\),

\[
 \sum_{t\le q}c_t=(a+1)^2,qquad
 \sum_{t<q}c_t(q-t)=\frac{a(a+1)(4a+5)}6,              \tag{10}
\]

whereas if \(q=2a+1\),

\[
 \sum_{t\le q}c_t=(a+1)(a+2),qquad
 \sum_{t<q}c_t(q-t)=\frac{(a+1)(a+2)(4a+3)}6.          \tag{11}
\]

We now check the maximizing rank from (6).  Denote the right side of (2)
minus the left side by \(\mathcal S\).

When \(q=0\), write \(p=s+1+n\).  Direct substitution gives

\[
 2\mathcal S=2n^2+2ns+s(s-1)\ge0.                      \tag{12}
\]

Suppose \(1\le q\le p-1\), and write \(n=p-q-1\).
For even \(q=2a\) (so \(a\ge1\)), (8) and (10) give

\[
\begin{aligned}
6\mathcal S={}&6an^2+an(4a^2+15a-1)+6a(a-1)s+3s(s-1)\\
 &+a(8a^3+10a^2+a-1),                                  \tag{13}
\end{aligned}
\]

which is nonnegative.  For odd \(q=2a+1\), (8) and (11) give

\[
\begin{aligned}
6\mathcal S={}&8a^4+4a^3n+26a^3+21a^2n+6a^2s+28a^2\\
 &+6an^2+17an+10a+3n^2+3n+3s(s-1)+6,                  \tag{14}
\end{aligned}
\]

again nonnegative.  Notice that (14) includes \(q=1\), where \(a=0\).

It remains to check \(p\le q\le2p-2\).  Put

\[
 k=2p-2-q,qquad p=k+2+n.                               \tag{15}
\]

The involution

\[
 (i,j)\longmapsto(p-1-j,p-1-i)
\]

shows that \(c_t=c_{2p-2-t}\).  If \(k=2a\), substitution into (8) at
the maximizing rank \(r=p-1\) yields

\[
\begin{aligned}
6\mathcal S={}&8a^4+28a^3n+38a^3+36a^2n^2+87a^2n
 +6a^2s+52a^2\\
 &+20an^3+72an^2+12ans+81an+6as+28a\\
 &+4n^4+20n^3+6n^2s+35n^2+12ns+25n+3s^2+3s+6.
                                                               \tag{16}
\end{aligned}
\]

If \(k=2a+1\), the corresponding identity is

\[
\begin{aligned}
6\mathcal S={}&8a^4+28a^3n+54a^3+36a^2n^2+129a^2n
 +6a^2s+121a^2\\
 &+20an^3+108an^2+12ans+189an+12as+111a\\
 &+4n^4+30n^3+6n^2s+80n^2+18ns+90n+3s^2+9s+36.
                                                               \tag{17}
\end{aligned}
\]

Every term in (16)--(17) is nonnegative.

Finally, after every pair in (5) is active,

\[
 \widetilde\Phi_p(u+1)-\widetilde\Phi_p(u)
 =\frac{p(p+1)}2.
\]

At \(r=p-1\), the successive difference of the whole left side of (2) is

\[
 \frac{p(p-1)}2-u+\frac{p(p+1)}2=p^2-u.                \tag{18}
\]

The all-active tail starts strictly after \(u=p^2\), so it is decreasing;
its first values are already covered by (16)--(17).  Equations
(12)--(18), together with the rank maximization (6), prove (2).  QED.

## 2. The strongest generic prefix lower bound

There is a clean exact lower bound on \(\Phi\), but Theorem 1 explains why
it cannot close the coefficient.  For \(1\le t\le p\), put

\[
 S_t=\sum_{i=0}^{t-1}z_i,qquad n_t=\binom{t+1}{2}.
\]

**Lemma 2 (prefix Jensen).**  For every signed ruler and every \(u\),

\[
 \boxed{
 \Phi_{Z,G}(u)\ge
 n_t\left(u-G-\frac{2S_t}{t}\right)_+.}                \tag{19}
\]

**Proof.**  Restrict \(\Phi\) to pairs \(0\le i\le j<t\).  The convex
function \(x\mapsto(u-G-x)_+\) and Jensen's inequality apply because

\[
 \sum_{0\le i\le j<t}(z_i+z_j)=(t+1)S_t,
\]

whose average over the \(n_t\) pairs is \(2S_t/t\).  QED.

The same argument works for any subset of ruler points, not only a prefix.
But Theorem 1 uses the **actual** \(\widetilde\Phi_p\), which is at least
every valid lower bound such as (19), and still satisfies all cutoffs with
span coefficient two.  Therefore (19), its optimization over \(t\), or any
other lower estimate depending only on the macroscopic rank profile cannot
prove coefficient three.

## 3. Exact finite audit

The following lower representatives \(X\) were checked.  For each row we
formed

\[
 W=\max X,qquad Z=W-X,qquad G=L-2W,
\]

verified that \(Z\) is Sidon and
\(D(Z)\cap(G+S(Z))=\varnothing\), and then checked P07's cutoff inequality
for every \(1\le r<p\) and every \(1\le u\le L+1\).  Beyond \(L+1\) the
left side is decreasing, since all shifted sums are active and the \(p^2\)
distinct labels already force \(L\ge p^2\).  Lemma 2 was checked for every
prefix and every cutoff.  All arithmetic was integer or `Fraction`.

\[
\begin{array}{c|l|r|r|r|r}
p&X&L&W&G&\min(T_r-\mathrm{LHS})\\ \hline
2&0,1&4&1&2&0\\
3&0,1,3&10&3&4&0\\
4&0,2,5,6&19&6&7&0\\
5&0,1,3,8,12&30&12&6&0\\
6&0,1,3,8,14,18&48&18&12&3\\
7&0,5,8,9,15,26,28&68&28&12&0\\
8&0,2,3,10,16,28,33,37&85&37&11&8\\
9&0,1,3,11,15,20,36,43,49&116&49&18&13\\
10&0,1,3,8,14,26,30,47,62,71&152&71&10&26\\
11&0,1,4,6,14,30,41,50,62,69,84&191&84&23&29\\
12&0,1,4,6,14,29,36,53,69,87,96,107&240&107&26&41
\end{array}                                               \tag{20}
\]

The rows through \(p=9\) are certified finite optima of the CP-SAT model;
the \(p=10,11,12\) rows are exact feasible witnesses only.  The P07
interlacing example is the \(p=5\) row, and its larger example is the
\(p=9\) row.  Thus both requested P07 guardrails are included in (20).

As an independent finite check of Theorem 1, the exact recurrence

```text
phi[1] = 0
phi[u+1] - phi[u]
  = #{(i,j): 0 <= i <= j < p and p(i+j) <= u-1}
```

was used to test every \(p=2,\ldots,64\), every \(1\le r<p\), and every
\(1\le u\le2p(p-1)+2\).  All 63 parameter families passed.  The symbolic
identities (12)--(17), rather than this finite audit, prove the theorem.

## 4. What a surviving lemma must retain

For an actual signed ruler, define unit-lattice colour indicators

\[
 d(n)={\bf1}_{D(Z)}(n),\qquad
 s(n)={\bf1}_{G+S(Z)}(n).
\]

The missing exact condition is the coefficientwise identity

\[
 d(n)s(n)=0\qquad(n\in\mathbb Z).                        \tag{21}
\]

P07's cutoff inequality keeps only cumulative capacities derived from
(21).  The barrier profile (1) passes every such cumulative inequality
after the lag cardinalities are declared, despite collapsing many labels
onto the same lattice phases.  P13 shows that even the complete weak
occupation law and all continuum lag windows retain this defect.

A viable next statement must therefore control a microscopic mixed
correlation.  With

\[
 D_+(z)=\sum_{i<j}z^{z_j-z_i},\qquad
 S_+(z)=\sum_{i\le j}z^{G+z_i+z_j},
\]

(21) is equivalently

\[
 [z^0]D_+(z)S_+(z^{-1})
 =\int_0^1D_+(e^{2\pi it})
       \overline{S_+(e^{2\pi it})}\,dt=0.              \tag{22}
\]

Unlike \(\Phi\), (22) retains unit-lattice phase.  The P11 conclusion is
therefore a barrier, not a proof of the signed-ruler theorem:

\[
\boxed{
\text{all scalar truncated-energy cutoffs are insufficient; the next
lemma must use microscopic phase/integrality.}}
\]
