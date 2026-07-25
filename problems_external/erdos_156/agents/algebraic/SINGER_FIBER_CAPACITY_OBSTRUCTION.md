# Route B: exact Singer-fiber capacity obstruction

## Verdict

No algebraic lift rule closing Erdős Problem 156 was obtained.  The proposed
Singer-lift route has, however, an exact invariant which rules out the
unqualified target \(M=\Theta(p)\) above the sharp constant \(1/2+o(1)\).
For at least \(p(p-1)/2\) nonexceptional Singer residues, every deterministic
lift has at most \((p+1)/2\) or \((p+2)/2\) different quotient values,
independently of how the lift values are chosen.

Consequently, a Route B construction must use
\[
 \frac{N}{p^2+p+1}\leq \frac{p+1}{2}+O(1),
\]
and hence \(p^3\geq (2-o(1))N\).  More importantly, near this boundary it
must make the quotient map essentially injective on every low-diagonal
Singer fiber.  No identity in the Singer difference-set axioms supplies this
simultaneous near-bijection.  This is the single missing bridge.

This result does not prove or disprove Erdős Problem 156.

## Setup

Let
\[
 q=p^2+p+1
\]
and let
\[
 B=\{b_0,\ldots,b_p\}\subseteq \mathbb Z/q\mathbb Z
\]
be a Singer perfect difference set, represented by integers
\(0\leq b_i<q\).  Thus every nonzero residue modulo \(q\) has exactly one
ordered representation \(b_v-b_w\) with \(v\ne w\).

Choose arbitrary lift values
\[
 d_i\in\{0,\ldots,M-1\},\qquad a_i=b_i+qd_i.
\]
For a residue \(r\notin B\), define the Singer fiber
\[
 T_r=\{(u,v,w): b_u+b_v-b_w\equiv r\pmod q\}.
\]
For \((u,v,w)\in T_r\), define its carry
\[
 \kappa_r(u,v,w)
 =\frac{b_u+b_v-b_w-r}{q}.
\]
Since
\[
 -(q-1)\leq b_u+b_v-b_w\leq 2(q-1)
\]
and \(0\leq r<q\), the carry is one of \(-1,0,1\).

The quotient-value set of the lifted fiber is
\[
 C_r(d)=
 \left\{
 \kappa_r(u,v,w)+d_u+d_v-d_w:
 (u,v,w)\in T_r
 \right\}.
\]

For an integer \(m=r+qt\), the saturation equation in Ruzsa's construction,
\[
 m+a_w=a_u+a_v,
\]
is equivalent, with no omitted boundary term, to
\[
 t=\kappa_r(u,v,w)+d_u+d_v-d_w.                 \tag{1}
\]
Thus the lift saturates every nonexceptional integer in \([1,N]\) exactly
when
\[
 I_r(N)\subseteq C_r(d)\quad\text{for every }r\notin B,       \tag{2}
\]
where
\[
 I_r(N)=\{t\in\mathbb Z:1\leq r+qt\leq N\}.
\]

## Lemma 1: every nonexceptional fiber has \(p+1\) ordered triples

For every \(r\notin B\),
\[
 |T_r|=p+1.
\]

### Proof

Fix \(u\).  Since \(r-b_u\ne0\pmod q\), the perfect-difference property
gives a unique ordered pair \((v,w)\), with \(v\ne w\), such that
\[
 b_v-b_w=r-b_u.
\]
This is equivalent to \((u,v,w)\in T_r\).  There is exactly one triple for
each of the \(p+1\) choices of \(u\). \(\square\)

## Lemma 2: the swap involution gives the exact orbit count

Let
\[
 F_r=\#\{(u,u,w)\in T_r\}.
\]
Then the involution
\[
 (u,v,w)\longmapsto(v,u,w)
\]
has exactly \(F_r\) fixed points, and therefore \(T_r\) has
\[
 O_r=\frac{p+1+F_r}{2}                              \tag{3}
\]
orbits.  Moreover, both members of a two-element orbit give the same value
in \(C_r(d)\).  Hence, for every deterministic lift \(d\),
\[
 |C_r(d)|\leq O_r=\frac{p+1+F_r}{2}.                \tag{4}
\]

### Proof

The fiber equation and the value in (1) are symmetric in \(u,v\).  The fixed
points of the swap are precisely the triples with \(u=v\).  The standard
fixed-point formula for an involution gives (3), and constancy on orbits
gives (4). \(\square\)

## Lemma 3: diagonal solutions have a fixed total mass

The diagonal counts satisfy
\[
 \sum_{r\notin B}F_r=p(p+1).                        \tag{5}
\]

### Proof

Every ordered pair \((u,w)\) with \(u\ne w\) determines the residue
\[
 r=2b_u-b_w\pmod q
\]
and hence the fixed triple \((u,u,w)\in T_r\).

This residue cannot lie in \(B\).  Indeed, if
\[
 2b_u-b_w=b_j,
\]
then
\[
 b_u+b_u=b_w+b_j.
\]
The Sidon property of \(B\) forces equality of the unordered pairs
\(\{u,u\}=\{w,j\}\), so \(w=u\), contrary to the choice \(u\ne w\).

Conversely, every fixed triple counted by some \(F_r\) arises from exactly
one ordered pair \((u,w)\) with \(u\ne w\), because \(r\notin B\) rules out
\(w=u\).  There are \((p+1)p\) such ordered pairs. \(\square\)

## Corollary 4: at least half the residues have half-sized capacity

There are \(q-(p+1)=p^2\) nonexceptional residues.  From (5),
\[
 \#\{r\notin B:F_r\geq2\}
 \leq \frac{p(p+1)}2.
\]
Therefore
\[
 \#\{r\notin B:F_r\leq1\}
 \geq p^2-\frac{p(p+1)}2
 =\frac{p(p-1)}2.                                  \tag{6}
\]
For each of these residues, (4) yields
\[
 |C_r(d)|
 \leq \left\lfloor\frac{p+2}{2}\right\rfloor.       \tag{7}
\]
For every odd prime \(p\), this is \((p+1)/2\).

This bound is independent of the lift rule, algebraic or otherwise.

## Corollary 5: universal obstruction on the interval length

For every residue \(0\leq r<q\) and every \(N\geq q\),
\[
 |I_r(N)|\geq\left\lfloor\frac Nq\right\rfloor.
\]
Choose a residue supplied by (6).  If (2) holds, then (7) forces
\[
 \left\lfloor\frac Nq\right\rfloor
 \leq\left\lfloor\frac{p+2}{2}\right\rfloor.        \tag{8}
\]

In particular, for odd prime \(p\),
\[
 N<q\,\frac{p+3}{2}
 =\frac{(p^2+p+1)(p+3)}2.                           \tag{9}
\]
Equivalently, any successful Singer lift for an interval of length \(N\)
must satisfy
\[
 p^3\geq(2-o(1))N.                                  \tag{10}
\]

### Proof

For \(r=0\), \(I_r(N)=\{1,\ldots,\lfloor N/q\rfloor\}\).  For \(r>0\),
the admissible values start at \(t=0\), and their count is at least
\(\lfloor N/q\rfloor\).  Inclusion (2), followed by (7), gives (8).
For odd \(p\), the right side of (8) is \((p+1)/2\); hence
\(\lfloor N/q\rfloor\leq(p+1)/2\), which implies (9). \(\square\)

## The exact remaining bridge

After imposing the necessary safe range
\[
 M\leq\frac{p+1}{2}+O(1),
\]
Route B still requires one vector
\[
 d=(d_0,\ldots,d_p)
\]
such that simultaneously for all \(p^2\) residues \(r\notin B\),
\[
 I_r(N)\subseteq C_r(d).
\]
For the at least \(p(p-1)/2\) residues in (6), the number of available swap
orbits is at most the number of required quotient levels plus \(O(1)\).
Consequently a construction near the \(N\sim p^3/2\) boundary must make the
orbit-value map
\[
 T_r/(u,v,w)\sim(v,u,w)
 \longrightarrow \mathbb Z,\qquad
 [u,v,w]\longmapsto
 \kappa_r(u,v,w)+d_u+d_v-d_w
\]
essentially bijective onto a consecutive interval, for every such \(r\),
using the same \(p+1\) lift variables.

The perfect-difference property proves the fiber cardinalities, but it does
not control these integral quotient values or their collisions.  Establishing
this simultaneous consecutive-interval property by an explicit algebraic
choice of \(d_i\) is the single missing bridge.  Merely checking it for
finitely many primes would not close the route.

