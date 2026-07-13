# P34: direct same-parity Sidon constructions

## Verdict

No infinite family with

\[
 E\cap3E=\varnothing,\qquad
 \max E\leq(3-\varepsilon)|E|^2
\]

was constructed in this lane. Here \(E\) is always Sidon with diagonal
pair sums included, and repetitions are allowed in \(3E\).

The direct modular route has an exact obstruction at coefficient three.

> **Modular parity obstruction.** Let \(E\) be a \(p\)-element subset of one
> parity class in \(\mathbb Z_{2h}\). If \(E\) is Sidon modulo \(2h\),
> including diagonals, and \(E\cap3E=\varnothing\) modulo \(2h\), then
> \[
>                   2h\geq3p^2-p+2.                    \tag{1}
> \]

The proof is a two-set covering argument. After dividing out parity, every
strong Sidon set \(B\) in a finite abelian group \(H\) satisfies

\[
 |B+B|={p(p+1)\over2},\qquad |B-B|=p(p-1)+1.
\]

If the sum of these cardinalities exceeds \(|H|\), then

\[
                    3B-B=H.                            \tag{2}
\]

Thus no finite-field, modular Costas, or modular product-free construction
can beat coefficient three by certifying the target relation entirely in its
ambient group. Any surviving integer construction must use the order of the
chosen representatives: its modular \(3B-B\) collisions must carry to the
wrong integer layer. This report does not analyze those carry layers.

Two sharper falsifiers were also obtained.

1. For every finite field of odd characteristic, the parabola
   \(S=\{(x,x^2):x\in\mathbb F_q\}\) is strong Sidon but
   \(3S-S=\mathbb F_q^2\). Hence every affine image and every translate
   meets its own threefold sumset.
2. If a fixed even modulus \(m\) and odd residue gate
   \(R\subseteq\mathbb Z_m\) enforce \(R\cap3R=\varnothing\), then
   \(|R|\leq m/4\). Arbitrarily varying modular fibers over \(R\) still
   have ambient coefficient at least \(4-o(1)\). Thus, within modular-fiber amplification, the coefficient four
   in P19 is not an artifact of using one residue class.

These are obstruction theorems, not a resolution of Problem 864. Literal
integer Sidonicity is weaker than modular Sidonicity because sums and
differences may collide only after reduction. That carry distinction is
exactly what remains outside P34.

## 1. Conventions

For a subset \(B\) of an additive abelian group, write

\[
 B+B=\{a+b:a,b\in B\},\qquad
 B-B=\{a-b:a,b\in B\},
\]

and similarly for \(3B-B\). All variables may repeat.

Call \(B\) **strong Sidon** when

\[
 a+b=c+d\quad\Longrightarrow\quad
 \{a,b\}=\{c,d\}
\]

as multisets. This includes diagonal sums \(2a\). It is the modular
condition needed to imply literal integer Sidonicity after representatives
are chosen.

A nonzero difference of a strong Sidon set has a unique ordered
representation. Indeed,

\[
 a-b=c-d\quad\Longrightarrow\quad a+d=c+b.
\]

Strong Sidonicity gives either \((a,b)=(c,d)\), or \(a=b\) and \(c=d\).
The latter case has zero difference. Consequently, if \(|B|=p\), then

\[
 \boxed{|B+B|={p(p+1)\over2},\qquad |B-B|=p(p-1)+1.}     \tag{3}
\]

The argument includes elements of order two: if \(a-b=b-a\ne0\), then
\(2a=2b\), which is already a forbidden diagonal collision.

## 2. Universal modular coverage

### Theorem 1 (strong Sidon coverage threshold)

Let \(B\) be a \(p\)-element strong Sidon subset of a finite abelian group
\(H\). If

\[
 |H|<{3p^2-p+2\over2},                                  \tag{4}
\]

then

\[
                         3B-B=H.                         \tag{5}
\]

### Proof

Fix \(g\in H\). The two sets

\[
 B+B,\qquad g-(B-B)
\]

have total cardinality, by (3),

\[
 {p(p+1)\over2}+p(p-1)+1
 ={3p^2-p+2\over2}>|H|.                                 \tag{6}
\]

They intersect. Thus for some \(a,b,c,x\in B\),

\[
 a+b=g-(c-x),
\]

or

\[
 g=a+b+c-x\in3B-B.
\]

Since \(g\) was arbitrary, (5) follows. Repetitions among
\(a,b,c,x\) were never excluded. QED.

The strict inequality in (4) is essential to this covering proof. Its
contrapositive is the exact hole bound

\[
 g\notin3B-B
 \quad\Longrightarrow\quad
 |H|\geq{3p^2-p+2\over2}.                                \tag{7}
\]

### Corollary 2 (same-parity modular obstruction)

Let \(E\subseteq\mathbb Z_{2h}\) have \(p\) elements, all congruent to
\(\epsilon\in\{0,1\}\) modulo \(2\). If \(E\) is strong Sidon and
\(E\cap3E=\varnothing\) in \(\mathbb Z_{2h}\), then (1) holds.

### Proof

There is a unique set \(B\subseteq\mathbb Z_h\) such that

\[
                 E=\epsilon+2B.                         \tag{8}
\]

An equality between pair sums in \(B\) modulo \(h\) is equivalent, after
multiplication by \(2\), to an equality between the corresponding pair sums
in \(E\) modulo \(2h\). Hence \(B\) is strong Sidon.

If \(-\epsilon\in3B-B\), choose \(a,b,c,x\in B\) with

\[
 a+b+c-x=-\epsilon.
\]

Then, modulo \(2h\),

\[
 (\epsilon+2a)+(\epsilon+2b)+(\epsilon+2c)
   =\epsilon+2x.                                        \tag{9}
\]

This is an element of \(E\cap3E\), including any repeated summands in the
chosen representation. Therefore \(-\epsilon\notin3B-B\), and (7) gives

\[
 h\geq{3p^2-p+2\over2}.
\]

Multiplying by two proves (1). QED.

### Consequence for constructions

Corollary 2 rules out a standard direct recipe:

1. build a same-parity strong Sidon set in a group of order
   \((3-\varepsilon)p^2\);
2. make it modularly disjoint from its threefold sumset;
3. take integer representatives.

Step 2 is impossible for every \(p\), not merely asymptotically. The
corollary does not rule out choosing a larger modulus and placing all
representatives in a shorter interval, nor does it rule out a set that is
Sidon over the integers but not modulo the chosen modulus. Both escapes are
integer carry problems.

## 3. Affine finite-field parabola is saturated

### Theorem 3 (parabola falsifier)

Let \(q\) be a prime power of odd characteristic and put

\[
 P(x)=(x,x^2),\qquad
 S=\{P(x):x\in\mathbb F_q\}\subseteq\mathbb F_q^2.
\]

Then \(S\) is strong Sidon and

\[
                         3S-S=\mathbb F_q^2.             \tag{10}
\]

Consequently every invertible affine image of \(S\) intersects its own
threefold sumset.

### Proof of Sidonicity

Suppose

\[
 P(a)+P(b)=P(c)+P(d).
\]

The first coordinate gives \(a+b=c+d\), and the second gives
\(a^2+b^2=c^2+d^2\). Since \(2\ne0\), comparison of

\[
 (a+b)^2=a^2+b^2+2ab
\]

gives \(ab=cd\). Thus \(\{a,b\}\) and \(\{c,d\}\) are the two root
multisets of the same polynomial

\[
 X^2-(a+b)X+ab.
\]

They are equal, including diagonal pairs.

### Proof of saturation

Take an arbitrary target \((u,v)\in\mathbb F_q^2\), and put

\[
 r={u^2-v\over2},\qquad
 a=u+1,\quad b=u+r,\quad c=0,\quad x=u+1+r.              \tag{11}
\]

The first coordinate of
\(P(a)+P(b)+P(c)-P(x)\) is \(u\). The second is

\[
 (u+1)^2+(u+r)^2-(u+1+r)^2=u^2-2r=v.                    \tag{12}
\]

This proves (10) with an explicit witness for every target. If
\(A=T(S)+t\), where \(T\) is an invertible additive map, then

\[
 3A-A=T(3S-S)+2t=\mathbb F_q^2.
\]

In particular \(0\in3A-A\), so \(A\cap3A\ne\varnothing\). QED.

In characteristic two, a set of more than one point cannot be strong Sidon
in the additive group \(\mathbb F_q^2\), because every diagonal sum is
zero. Thus the omitted characteristic does not provide a replacement under
the required diagonal convention.

Theorem 3 falsifies the natural proposal that a translation of the standard
finite-field parabola might remove all one-versus-three relations while
preserving its optimal Sidon density. Translation cannot remove even one
target class: all classes already occur.

## 4. Fixed modular residue gates retain coefficient four

A residue gate can enforce the repeated-summand condition before any fiber
is chosen. The next theorem shows why a fixed such gate cannot improve P19 by modular-fiber amplification.

### Theorem 4 (odd gate and arbitrary modular fibers)

Let \(m\) be even and let

\[
 R\subseteq\{1,3,\ldots,m-1\}\subseteq\mathbb Z_m
\]

be nonempty with \(R\cap3R=\varnothing\). Write \(r=|R|\). Then

\[
                            r\leq {m\over4}.              \tag{13}
\]

Now let \(A\subseteq\mathbb Z_{mh}\) be a \(p\)-element strong Sidon set
whose reduction modulo \(m\) lies in \(R\). Then

\[
 mh\geq {m\over r}p^2-mp+m
      \geq4p^2-mp+m.                                    \tag{14}
\]

In particular, for fixed \(m\), or more generally \(m=o(p)\),

\[
                         mh\geq(4-o(1))p^2.              \tag{15}
\]

No equality, affine-copy, or fixed-seed hypothesis is imposed on the
fibers.

### Proof

Fix any \(a,b\in R\). The translate \(R+a+b\) has \(r\) elements and lies
inside \(3R\). Both \(R\) and \(3R\) consist only of odd residues, and they
are disjoint. There are \(m/2\) odd residues in total, so

\[
 2r\leq {m\over2},
\]

which proves (13). This uses repeated summands: \(a\) and \(b\) are allowed
to coincide.

For each \(s\in R\), let \(n_s\) be the number of elements of \(A\)
reducing to \(s\). All ordered differences between two distinct elements in
the same fiber are nonzero multiples of \(m\). Strong Sidonicity makes all
these ordered differences distinct, even across different fibers. The
subgroup of multiples of \(m\) in \(\mathbb Z_{mh}\) has only \(h-1\)
nonzero elements. Hence

\[
 \sum_{s\in R}n_s(n_s-1)\leq h-1.                        \tag{16}
\]

Since \(\sum_s n_s=p\), Cauchy--Schwarz gives

\[
 h\geq\sum_s n_s^2-p+1
   \geq {p^2\over r}-p+1.                               \tag{17}
\]

Multiplying by \(m\) and using (13) proves (14). QED.

Thus allowing globally varying fibers does not repair a fixed modular
product-free gate. The obstruction is the shared zero-residue difference
fiber, not a repeated affine block. This is independent of P17's
fixed-seed product obstruction.

The theorem is deliberately modular. For a merely integer Sidon set,
different modular differences may differ by a carry and (16) need not hold
after reduction.

## 5. Costas compatibility and the Ruzsa boundary

For completeness, the general coverage theorem also applies to the modular
Welch Costas graph. Let \(q>3\) be a prime power, let
\(n=q-1\), choose a primitive element \(\alpha\in\mathbb F_q^*\), and put

\[
 W=\{(i,\alpha^i):i\in\mathbb Z_n\}
       \subseteq\mathbb Z_n\times\mathbb F_q.            \tag{18}
\]

If two pair sums in \(W\) agree, their first coordinates give equality of
the products \(\alpha^{i+j}\), while their second coordinates give equality
of the sums. The two field elements are therefore the same root multiset of
a quadratic. Hence \(W\) is strong Sidon, including diagonals.

Its size is \(n\), while its ambient group has order

\[
 n(n+1)< {3n^2-n+2\over2}\qquad(n>2),                   \tag{19}
\]

because the difference between the right and left sides is
\((n-1)(n-2)/2\). Theorem 1 gives

\[
 3W-W=\mathbb Z_n\times\mathbb F_q.                     \tag{20}
\]

This is only a direct modular obstruction. When (q) is prime, CRT identifies (18) with the standard
Ruzsa residue set; P30 proves a stronger representation-count statement for
that family and studies its integer carries. No Ruzsa carry claim is made
here. Likewise, P26 proves modular saturation for Singer perfect difference
sets by their exact difference support. The new point used in P34 is the
family-independent threshold in Theorem 1.

Integer radix flattenings of Costas arrays are not excluded by (20), because
their modular collisions can land in different carry layers. P17's finite
Welch scan remains the relevant evidence for that nonmodular question.

## 6. Exact computational audit

All programs use exact integer arithmetic. The symbolic proofs above, not
the finite ranges, establish Theorems 1, 3, and 4.

### 6.1 Residue gates

'residue_fiber_audit.py' exhausts every nonempty subset of the odd residues
for every even modulus \(m\leq40\):

~~~text
python problems/864/compute/p34/residue_fiber_audit.py \
  --max-modulus 40 \
  --output problems/864/compute/p34/residue_fiber_m40.json
~~~

It checked 2,097,130 nonempty subset masks across the nested odd-residue spaces.
There are no nonempty gates at \(m=2\). The first primitive gate, meaning no
congruence collapse beyond parity, appears at \(m=14\). Among primitive
gates through \(m=40\), the best balanced pair-fiber capacity diagnostic is

\[
 {28\over9}>3,
\]

attained for example by \(R=\{1,9,15\}\pmod {28}\). This diagnostic is
finite evidence only; Theorem 4 is the rigorous fixed-gate obstruction.

### 6.2 Universal cyclic coverage

'modular_coverage_audit.py' enumerates every nonempty subset of
\(\mathbb Z_h\) for \(1\leq h\leq18\), filters literal strong Sidon sets,
checks both cardinalities in (3), and verifies Theorem 1 and both parity
lifts:

~~~text
python problems/864/compute/p34/modular_coverage_audit.py \
  --max-order 18 \
  --output problems/864/compute/p34/modular_coverage_h18.json
~~~

The exact totals are:

~~~text
nonempty subsets:          524268
strong Sidon subsets:        5107
forced-coverage subsets:     1830
parity lifts checked:       10214
~~~

Every asserted intersection with \(3E\) is generated with repetitions
allowed.

### 6.3 Finite-field families

The explicit parabola witness (11) and all translations were checked for
the 13 odd primes through \(43\):

~~~text
python problems/864/compute/p34/parabola_obstruction.py \
  --max-prime 43 \
  --output problems/864/compute/p34/parabola_q43.json
~~~

This checked 8,253 field targets and 8,253 translated collisions, together
with every diagonal-inclusive pair sum.

The modular Welch graph was checked for the 12 primes \(5\leq q\leq43\):

~~~text
python problems/864/compute/p34/costas_welch_obstruction.py \
  --max-prime 43 \
  --output problems/864/compute/p34/costas_welch_q43.json
~~~

All 7,968 ambient group elements occurred in \(3W-W\), and every pair sum
and ordered difference cardinality matched (3).

### 6.4 Lean certificate

The finite-group overlap engine in Theorem 1 is formalized as
\(P34.modular\_cover\_overlap\) in 'ModularCover.lean'. It uses the
cardinality pigeonhole principle for two translated finsets and no
'native_decide':

~~~text
cd apn-gpt55-workbench/formal-conjectures
lake env lean E:/Projects/ErdosProblems/problems/864/compute/p34/ModularCover.lean
~~~

## 7. Scope and surviving route

The exact conclusions are:

1. A same-parity construction that is both Sidon and three-free modulo an
   ambient group cannot have ambient coefficient below three.
2. Every affine finite-field parabola is saturated by one-versus-three
   relations.
3. Every fixed odd product-free residue gate has density at most \(1/4\),
   and arbitrary modular fibers over it retain coefficient at least four.
4. The modular Welch Costas graph is saturated; its integer radix carries
   are not analyzed here.

What remains possible is genuinely nonmodular: choose representatives so
that every relevant modular \(3B-B\) representation has a nonzero carry,
while preserving literal Sidonicity and keeping the endpoint below
\((3-\varepsilon)p^2\). That is not a residue-only, group-only, or affine
finite-field construction. It is also precisely why the Singer and Ruzsa
carry lanes require indexed phase information.

The local literature audits P14 and P32 found no direct coefficient-below-
three family. P26 and P30 contain stronger saturation statements for their
specific Singer and Ruzsa objects, respectively. No separate global
literature-first claim is made for Theorem 1; its role here is a
self-contained obstruction that closes the independent direct-modular
construction lane.




