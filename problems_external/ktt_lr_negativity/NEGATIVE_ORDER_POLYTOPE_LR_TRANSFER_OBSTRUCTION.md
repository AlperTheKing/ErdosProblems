# Why the Negative Order Polytope Does Not Yet Transfer to KTT

## Verdict

The Liu--Tsuchiya polytope `O(P_{7,7})` is an exact negative Ehrhart
example, but it does **not** currently give a KTT counterexample.  The direct
transfer route is dead for three exact reasons:

1. an unweighted or flagged skew Gelfand--Tsetlin realization is impossible,
   because that entire class is Ehrhart positive;
2. the fixed-content section required by the homogeneous skew-Kostka-to-LR
   bridge is not supplied by the order-map model, and the standard
   parsimonious two-row contingency-to-Kostka reduction is excluded by an
   exact codegree/count obstruction; and
3. embedding the order polytope as a proper face or nontrivial product does
   not preserve its Ehrhart polynomial, while a projection gives the required
   count only after a separate lattice-point bijection (singleton-fibre)
   theorem.

This is a verdict about the proposed transfer, not a theorem that no unrelated
LR hive can have the same Ehrhart polynomial.  Producing such a hive would
itself be a counterexample to KTT and still requires an explicit partition
triple and the full two-engine certificate.

## 1. Exact order-polytope data

Let `P_{7,7}=A_7 \oplus A_7` be the ordinal sum of two seven-element
antichains.  In coordinates `x_1,...,x_7,y_1,...,y_7`,

```text
O(P_{7,7}) = {0 <= x_i <= y_j <= 1 for every i,j}.
```

It has dimension 14, `7+49+7=63` facets, and

```text
(2^7-1)+2^7 = 255
```

vertices.  Its `h*`-polynomial is `A_7(z)^2`.  Thus it has `h*`-degree 12,
codegree three, and

```text
[n] L_O(n) = -3041/1430,
L_O(1)=255,
L_O(-1)=L_O(-2)=0,
L_O(-3)=1.
```

The last three identities say that the first interior lattice point occurs in
`3O` and is unique there.  These statements are reconstructed over `Q` by

```text
python problems_external/ktt_lr_negativity/order_polytope_lr_transfer_obstruction.py
```

which returns `PASS`.  Checker SHA-256:

```text
4B79741BCFB710A2540E80F9927D24592F70310FA4A6A8055AA65FC5393B116F
```

The source formula is Liu--Tsuchiya, *Stanley's non-Ehrhart-positive order
polytopes*, Example 3.2 and Table 1:
<https://arxiv.org/pdf/1806.08403>.

## 2. Unweighted and flagged skew GT realizations are excluded

A skew Gelfand--Tsetlin polytope fixes the top and bottom shapes but does not
fix the tableau content.  Its lattice points enumerate all semistandard
tableaux of the dilated skew shape with a fixed alphabet.  Jochemko--Menon,
Theorem 3.5, proves that every such skew GT polytope is Ehrhart positive.  Their
more general Theorem 1.5 covers integral marked-order/flagged versions on a
skew-shape poset:
<https://arxiv.org/pdf/2604.08394>.

Integral affine equivalence preserves the Ehrhart polynomial.  Since
`O(P_{7,7})` has negative linear coefficient, it cannot be integrally affinely
equivalent to any polytope in either of those classes.

This also identifies the parameter mismatch in the tempting tableau model.
The points of `nO(P_{7,7})` are order-preserving maps from one fixed
fourteen-element poset to the growing chain `{0,...,n}`.  Skew-GT dilation
instead scales the boundary shape while keeping the alphabet fixed.  The
former is not a homogeneous fixed-content family.

## 3. Fixed content is an additional fibre, not a marking

The homogeneous bridge uses

```text
K_(n lambda / n beta, n w) = c^(nR)_(n lambda,nS).
```

Geometrically, the skew-Kostka polytope is a skew GT polytope intersected with
global row-sum equations fixing the content `nw`.  Those equations are not
marked coordinates of the skew-shape poset and are not covered by the
Jochemko--Menon positivity theorem.

In the natural order-map encoding of `O(P_{7,7})`, the content records how
many poset elements take each value in `{0,...,n}`.  It varies with the order
map, and even its number of possible coordinates grows with `n`.  Fixing one
content selects only one fibre; summing over all contents uses an
`n`-dependent index set.  Therefore the order-map bijection does not produce
one fixed triple `(lambda,beta,w)` whose dilation is counted by the order
polynomial.

A projection or extended formulation repairs this only if it is
lattice-preserving, surjective on lattice points at every dilation, and has
singleton lattice fibres.  No such bijection is supplied by the order-map
model; without it, equality of the source and image counts does not follow.

## 4. Exact obstruction to the standard parsimonious Kostka reduction

Narayanan's standard parsimonious reduction sends a `2 x k` contingency-table
fibre with positive column margins `b_1,...,b_k` and first-row sum `A` to a
two-row Kostka number.  It is homogeneous when all margins are scaled, so it
is the published homogeneous reduction analyzed here that could have
transferred an entire Ehrhart polynomial rather than one isolated count.

It cannot transfer `O(P_{7,7})`.

After zero columns are deleted, a full-dimensional `2 x k` table fibre is

```text
T(A;b) = {z in R^k : 0 <= z_i <= b_i, sum_i z_i=A}
```

and has dimension `k-1`.  Equality with a degree-fourteen polynomial forces
`k=15`.

At dilation three, relative-interior lattice points are the positive bounded
compositions

```text
1 <= z_i <= 3b_i-1,    sum_i z_i=3A.
```

Put `u_i=z_i-1`.  Their generating polynomial is a product

```text
product_i (1+x+...+x^(3b_i-2)).
```

Every exponent bound is at least one.  For fifteen factors, an interior
coefficient is one only at one of the two endpoints: away from an endpoint,
moving one unit between two non-saturated coordinates gives at least two
compositions.  Hence uniqueness in `3T` forces

```text
3A=15   or   3(sum b_i-A)=15.
```

After complementing the two rows, assume `A=5`.  At dilation one every
zero-one vector of weight five is feasible because every surviving `b_i` is
at least one.  Consequently

```text
L_T(1) >= binomial(15,5) = 3003,
```

whereas `L_O(1)=255`.  This contradiction excludes the homogeneous two-row
contingency/Kostka route exactly.

Primary reduction: Narayanan, Lemma 1:
<https://arxiv.org/pdf/math/0501176>.

## 5. Proper faces and products cannot preserve the count

Two elementary lemmas close the face/product escape routes.

**Proper-face lemma.**  If `F` is a proper face of a rational polytope `Q`,
choose a rational point `q in Q\F` and clear its denominator.  For some
positive integer `m`, `mq` is a lattice point of `mQ` outside `mF`.  Therefore
`L_Q(m)>L_F(m)`.  A proper face never has the same Ehrhart function as its
ambient polytope at every dilation.

**Product lemma.**  If `L_(P x Q)(n)=L_P(n)` for all positive `n`, then
`L_Q(n)=1` for all positive `n`.  A positive-dimensional rational polytope has
two distinct rational points which become distinct lattice points after a
common denominator is cleared.  Thus `Q` must be a point.  A product with an
Ehrhart-neutral factor adds nothing.

An Ehrhart-equivalent subdivision or a union of faces is likewise not one LR
hive polytope and is not accepted by the homogeneous bridge.

## Direct-Proof-Guard conclusion

```text
DEAD: negative order-polytope transfer fails -- the only direct skew/flagged
GT class is Ehrhart positive; fixed content is a non-marked global fibre; the
homogeneous 2-row Kostka reduction contradicts codegree 3 and L(1)=255; proper
faces and nontrivial products change the count, while a projection requires an
unproved dilation-wise lattice-point bijection.
```

The exact negative order polytope remains a useful obstruction to generic
`h*`-shape and generic alcoved-positivity arguments.  It is not an LR
counterexample without a new singleton-fibre, dilation-compatible construction.
