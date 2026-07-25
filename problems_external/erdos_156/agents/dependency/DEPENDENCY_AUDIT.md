# Erdős 156 Route A: exact dependency audit of Ruzsa's random lift

## Verdict

The dependency-graph route does not remove Ruzsa's logarithm.

More precisely, for the random lift used by Ruzsa, the probability that a
fixed nonexceptional integer is not saturated is
\[
 \exp\!\left(-\Theta\!\left(\frac pM\right)\right),
\]
with absolute effective constants.  Every full bad event has the canonical
variable support \(\{d_0,\ldots,d_p\}\), so the ordinary, asymmetric, and
canonical variable-model lopsided dependency graphs are complete.  Their
criteria require
\[
 \frac pM \gg \log N.
\]
Since \(M=N/q+O(1)\), \(q=p^2+p+1\), this is precisely
\[
 p^3\gg N\log N.
\]

The independent-matching reduction in Ruzsa's proof does not admit a hidden
lopsided improvement: for a fixed residue, bad events for different quotient
targets are strictly negatively correlated, and hence must be adjacent in a
lopsided dependency graph.  They form a clique of order \(\Theta(M)\), again
forcing \(p/M\gg\log M\).

Thus symmetric LLL, asymmetric LLL, the support-based lopsided LLL, the
lopsided LLL applied to Ruzsa's independent matching, and standard
Moser--Tardos all retain a logarithm.  This is an obstruction to those
mechanisms, not a proof that no deterministic choice of the lifts exists.

## Source and convention

The source used here is:

- I. Z. Ruzsa, *A small maximal Sidon set*, Ramanujan Journal 2 (1998),
  55--58, DOI `10.1023/A:1009757824153`.
- Local scan: `problems_external/erdos_156/ruzsa_source.pdf`.
- SHA-256:
  `C9DB9E80EFE1CDEE2E54CAFB3174FD1C88BFDDEDE6915D7E9CC066E659CDD9B9`.

The notation below makes explicit the formulae on pp. 55--58.  Let
\[
 q=p^2+p+1,\qquad I=\{0,\ldots,p\},
\]
and let \(B=\{b_i:i\in I\}\subset\mathbb Z/q\mathbb Z\) be a Singer
difference set.  Thus every nonzero residue has exactly one ordered
representation \(b_v-b_w\), \(v\ne w\).  Choose independent variables
\[
 d_i\sim\operatorname{Unif}\{0,\ldots,M-1\}
\]
and lift \(b_i\) to
\[
 a_i=b_i+qd_i.
\]
The Singer property makes \(A_0=\{a_i:i\in I\}\) a Sidon set.

Fix \(m\in[1,N]\) whose residue \(r=m\bmod q\) is not in \(B\).  Define
\[
 T_r=\{(u,v,w)\in I^3:b_u+b_v-b_w\equiv r\pmod q\}.
\]
For each \(u\), \(r-b_u\ne0\), so the perfect-difference property gives
exactly one ordered pair \((v,w)\).  Consequently
\[
 |T_r|=p+1.
\]
Moreover \(w\notin\{u,v\}\), because \(w=u\) or \(w=v\) would imply
\(r\in B\).  The equality
\[
 m=a_u+a_v-a_w
\]
is equivalent to
\[
 d_u+d_v-d_w=t_{m,u,v,w},
 \qquad
 t_{m,u,v,w}:=\frac{m-(b_u+b_v-b_w)}q.
\]
With Ruzsa's choices of representatives and \(M\), all relevant targets
satisfy
\[
 -1\le t_{m,u,v,w}\le M+1.
\]

Let \(F_{m,\tau}\) denote this witness event for \(\tau=(u,v,w)\), and let
\[
 E_m=\bigcap_{\tau\in T_r}\overline{F_{m,\tau}}
\]
be the full bad event that \(m\) has no witness.

## Exact one-witness probabilities

For three distinct indices, put
\[
 S_M(t)=
 \#\{(x,y,z)\in\{0,\ldots,M-1\}^3:x+y-z=t\}.
\]
For the complete range used in Ruzsa's proof,
\[
\begin{aligned}
 S_M(-1)&=\frac{M(M-1)}2,\\
 S_M(t)&=\frac{M(M+1)}2+t(M-t-1)
       &&(0\le t\le M-1),\\
 S_M(M)&=\frac{M(M-1)}2,\\
 S_M(M+1)&=\frac{(M-1)(M-2)}2.
\end{aligned}
\]
Therefore
\[
 \min_{-1\le t\le M+1}\Pr(x+y-z=t)
 =\frac{(M-1)(M-2)}{2M^3}.
\]

If \(u=v\), put
\[
 S'_M(t)=
 \#\{(x,z)\in\{0,\ldots,M-1\}^2:2x-z=t\}.
\]
Exactly,
\[
 S'_M(t)=
 \max\left(
 0,\,
 \min\!\left(M-1,\left\lfloor\frac{t+M-1}{2}\right\rfloor\right)
 -
 \max\!\left(0,\left\lceil\frac t2\right\rceil\right)
 +1
 \right).
\]
On \([-1,M+1]\),
\[
 \min_t S'_M(t)=\left\lfloor\frac{M-1}{2}\right\rfloor.
\]
For \(M\ge4\), the three-variable minimum is the smaller of the two.
Thus every atomic witness event satisfies
\[
 \frac{(M-1)(M-2)}{2M^3}
 \le \Pr(F_{m,\tau})\le\frac1M.
\tag{1}
\]

## Local witness hypergraph

The following role counts are exact consequences of the Singer difference
property.

- A fixed vertex occurs as \(u\) in exactly one ordered triple of \(T_r\).
- It occurs as \(v\) in exactly one ordered triple.
- It occurs as \(w\) in at most two ordered triples (the two orders of
  \(u,v\)).

Hence the ordered-triple vertex degree is at most \(4\).  A fixed pair of
vertices can occur in at most the six ordered role placements, so the
ordered pair codegree is at most \(6\).

After identifying the duplicate events associated to
\((u,v,w)\) and \((v,u,w)\), there are at most \(p+1\) distinct atomic
witness events.  Their variable-overlap dependency graph has maximum degree
at most
\[
 3\cdot4-1=11.
\tag{2}
\]

Ruzsa's sharper greedy count gives a pairwise-variable-disjoint subfamily
\(J_r\subseteq T_r\) of size \(\ell\) with
\[
 8\ell>p.
\tag{3}
\]
Indeed a selected triple excludes itself, its \(u,v\) swap, at most two
triples with \(u\) in the third position, at most two with \(v\) in the
third position, one with \(w\) first, and one with \(w\) second.

## Two-sided probability theorem

**Theorem.** For every nonexceptional \(m\) and \(M\ge44\),
\[
 \exp\!\left(-\frac{4(p+1)}M\right)
 \le \Pr(E_m)
 \le
 \exp\!\left(-\frac{3p}{128M}\right).
\tag{4}
\]

**Upper bound.** Failure on all witnesses implies failure on the disjoint
subfamily \(J_r\).  Its events are independent.  From (1), for \(M\ge4\),
\[
 \Pr(F_{m,\tau})
 \ge \frac{(M-1)(M-2)}{2M^3}
 \ge \frac{3}{16M}.
\]
Using (3),
\[
 \Pr(E_m)
 \le\left(1-\frac{3}{16M}\right)^\ell
 <\exp\!\left(-\frac{3p}{128M}\right).
\]

**Lower bound.** Apply the asymmetric local lemma to the *atomic success
events* \(F_{m,\tau}\), whose simultaneous avoidance is \(E_m\).
By (1)--(2), their probabilities are at most \(1/M\) and their dependency
degree is at most \(11\).  Set \(x=2/M\).  Bernoulli's inequality gives,
for \(M\ge44\),
\[
 x(1-x)^{11}
 =\frac2M\left(1-\frac2M\right)^{11}
 \ge\frac2M\left(1-\frac{22}M\right)
 \ge\frac1M.
\]
The quantitative local lemma therefore yields
\[
 \Pr(E_m)\ge(1-2/M)^K,
\]
where \(K\le p+1\) is the number of distinct atomic events.  Since
\(\log(1-2/M)\ge-4/M\) for \(M\ge4\), the lower bound in (4) follows.

This lower bound is important: the union-bound loss is not caused by an
overestimate of the probability of one full bad event.  That probability
really stays bounded away from zero whenever \(p/M\) is bounded.

## Full bad-event supports and codegrees

For every nonexceptional \(m\),
\[
 \operatorname{vbl}(E_m)
 =\bigcup_{\tau\in T_{m\bmod q}}\operatorname{vbl}(F_{m,\tau})
 =I,
\tag{5}
\]
because every \(u\in I\) occurs as the first coordinate of one triple.

Let
\[
 H=\#\{m\in[1,N]:m\bmod q\notin B\}.
\]
Then
\[
 H\ge N-(p+1)(\lceil N/q\rceil),
\]
and in the intended regime \(H=N-O(N/p+p)=\Theta(N)\).

Thus:

- every full bad event has support size \(p+1\);
- every pair of full bad events has support intersection size \(p+1\);
- every lift variable is incident with all \(H\) bad events;
- the canonical variable dependency graph is the clique \(K_H\);
- its event degree is exactly \(H-1\).

## Symmetric and asymmetric LLL obstruction

The symmetric criterion on the clique is
\[
 e\,\Pr(E_m)\,H\le1.
\]
By (4), it cannot hold unless
\[
 \frac{4(p+1)}M\ge\log(eH).
\tag{6}
\]

The same conclusion is necessary for the usual asymmetric criterion, not
merely for the symmetric choice.  Suppose parameters \(x_m\in(0,1)\)
satisfied
\[
 \Pr(E_m)\le x_m\prod_{n\ne m}(1-x_n).
\]
If every probability is at least \(\delta\), put
\[
 Q=\prod_n(1-x_n)^{-1},\qquad
 y_m=\frac{x_m}{1-x_m},\qquad t=\delta Q.
\]
Then \(y_m\ge t\) for all \(m\), so
\[
 Q=\prod_m(1+y_m)\ge(1+t)^H,
\qquad
 t\ge\delta(1+t)^H.
\]
Consequently
\[
 \delta\le\max_{t\ge0}\frac{t}{(1+t)^H}
 =\frac{(H-1)^{H-1}}{H^H}<\frac1H.
\]
Taking \(\delta=\exp(-4(p+1)/M)\) reproduces (6), up to an
inessential additive constant.

Because \(M=N/q+O(1)\),
\[
 \frac pM=(1+o(1))\frac{pq}{N}
 =(1+o(1))\frac{p^3}{N}.
\]
Hence a fixed condition \(p^3\ge C_0N\) does not satisfy (6) for any fixed
\(C_0\); this dependency method needs \(p^3\gg N\log N\).

## Lopsided LLL obstruction for Ruzsa's matching

Equation (5) means that the canonical product-space lopsided graph is also
\(K_H\).  The only established attempt to shrink it is to use Ruzsa's
independent matching \(J_r\).  That attempt still has a forced clique.

Fix a nonexceptional residue \(r\), use one matching \(J_r\) for every
integer \(m\equiv r\pmod q\), and define the matching-only bad event
\[
 E_m^*=\bigcap_{\tau\in J_r}\overline{F_{m,\tau}}.
\]
For \(m\ne n\) with the same residue, each independent linear form has two
different target values.  Write
\[
 a_\tau=\Pr(F_{m,\tau}),\qquad
 b_\tau=\Pr(F_{n,\tau}).
\]
Both are positive in Ruzsa's target range.  Independence across the matching
gives
\[
 \Pr(E_m^*\cap E_n^*)
 =\prod_{\tau\in J_r}(1-a_\tau-b_\tau)
 <
 \prod_{\tau\in J_r}(1-a_\tau)(1-b_\tau)
 =\Pr(E_m^*)\Pr(E_n^*).
\tag{7}
\]

If two bad events are nonadjacent in a lopsided dependency graph, the
singleton conditioning requirement includes
\[
 \Pr(E_m^*\mid\overline{E_n^*})\le\Pr(E_m^*),
\]
which is equivalent to
\[
 \Pr(E_m^*\cap E_n^*)\ge
 \Pr(E_m^*)\Pr(E_n^*).
\]
Equation (7) violates this.  Therefore all matching-only bad events in one
residue class must be pairwise adjacent.

There are \(\lfloor N/q\rfloor\) or \(\lceil N/q\rceil\) such targets, hence
a clique of order \(\Theta(M)\).  Also, by independence and the upper bound
in (1),
\[
 \Pr(E_m^*)\ge(1-1/M)^\ell
 \ge\exp\!\left(-\frac{2(p+1)}M\right)
\]
for \(M\ge2\).  The asymmetric clique calculation above now forces
\[
 \frac{2(p+1)}M\ge \log(\Theta(M)).
\tag{8}
\]
Thus even the matching-specific lopsided formulation retains a logarithm.

Equation (7) is deliberately stated only for the exact independent-matching
mechanism.  It does not claim that an unknown correlation theorem could not
exploit all overlapping witnesses simultaneously.

## Moser--Tardos audit

For the full events \(E_m\), standard Moser--Tardos resamples
\(\operatorname{vbl}(E_m)=I\).  One resampling therefore redraws every lift
variable and invalidates every other bad event.  Its dependency graph and
criterion are exactly the complete-graph asymmetric LLL criterion above, so
(6) is necessary for that certificate.

Using the matching-only events does not help: all targets in a fixed residue
use the same matching support, and (7)--(8) force a clique of order
\(\Theta(M)\).

Encoding a chosen witness with an auxiliary selector also fails at the
local-probability level: the event that the selected equality fails has
probability \(1-O(1/M)\), not \(O(1/M)\).  Avoiding every atomic failure
would moreover require every selected triple to hit its target, which is
strictly stronger than, and incompatible with, the required disjunction of
witnesses across many targets.

## Alteration and exact scope

At \(p^3=\Theta(N)\), (4) gives a constant lower bound on the expected
fraction of uncovered nonexceptional integers.  Therefore the naive
alteration "add one repair element per uncovered integer" adds
\(\Theta(N)\), not \(O(p)\), in expectation.

This does **not** exclude a new deterministic or batched repair invariant in
which one added element repairs many uncovered integers.  No such invariant
is present in Ruzsa's proof or in the dependency calculation above.

The rigorous conclusion is therefore:

`DEAD: Ruzsa lift's dependency-graph, lopsided-matching, and standard
Moser--Tardos mechanisms retain p/M >= c log M (and the full-support forms
retain p/M >= c log N); a new deterministic covering invariant is required.`

## Independent finite check of the exact counts

A direct enumeration of every `(x,y,z)` and `(x,z)`, for every
`4 <= M <= 20` and every `-1 <= t <= M+1`, was compared with the two
closed formulae above.  The result was

`exact_count_formula_check=True`.

This check is not used as a proof; the displayed summations prove the
formulae for all `M`.
