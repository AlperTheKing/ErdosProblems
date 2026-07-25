# Hilbert / Hurwitz bridge audit for full KTT

## Verdict

The invariant-ring realization is exact, but its known algebraic properties do
**not** imply positivity in the ordinary monomial basis.  Normality,
Cohen--Macaulayness, rational singularities, negative `a`-invariant,
standardness, Koszulness, and even Gorensteinness are jointly insufficient.

There is one strictly stronger statement which would prove KTT:

> **LR-HURWITZ.** Every nonzero stretched Littlewood--Richardson polynomial has
> all of its zeros in the open left half-plane.

The current exact corpus is consistent with LR-HURWITZ, but neither the
semi-invariant-ring structure nor Speyer's skep `L`-log-concavity supplies a
logical bridge to it.  Thus this route does not give a rank-uniform proof of
KTT.

## 1. What the Hilbert realization really gives

For the triple-flag quiver and the weight determined by
`(lambda,mu,nu)`, set

```text
R(lambda,mu,nu) = direct_sum_{n >= 0} SI(Q,beta)_{n sigma}.
```

Then

```text
dim R(lambda,mu,nu)_n = c(n nu; n lambda,n mu).
```

This is not only an analogy.  Derksen--Weyman identify the ray algebra with
the invariant ring `K[Rep(Q,beta)]^H`, where `H=ker(sigma)` is reductive.  They
therefore obtain Cohen--Macaulayness from Hochster--Roberts and rational
singularities from Boutot.  They also prove

```text
Hilb_R(z) = G(z)/(1-z)^q,     deg G < q,
```

and hence polynomiality of `dim R_n`.  Equivalently, the `a`-invariant is
negative.  See Derksen--Weyman, *On the Littlewood--Richardson polynomials*,
especially Section 3 and Corollaries 1--3:

<https://sites.lsa.umich.edu/hderksen/wp-content/uploads/sites/614/2018/05/A.I.a.13.pdf>

These are the strongest directly relevant generic Hilbert facts in that
proof.  They give positivity of dimensions at integer degrees and a rational
Hilbert series; they do not give signs of the Taylor coefficients of the
polynomial interpolation at zero.

## 2. Exact obstruction to every generic CM/Koszul/RR implication

Let `Q_20` be the poset with one minimal element covered by 20 incomparable
elements, and let `O(Q_20)` be its order polytope.  Its Ehrhart/Hilbert
polynomial is

```text
H(n) = sum_{i=1}^{n+1} i^20.
```

The coefficient of `n` is exactly

```text
B_20 + 20 = -174611/330 + 20 = -168011/330 < 0.
```

This is Example 1.3 of Liu--Tsuchiya, *Stanley's non-Ehrhart-positive order
polytopes*:

<https://arxiv.org/pdf/1806.08403>

The corresponding Ehrhart ring is a Hibi ring.  It has all of the following
properties.

* It is standard graded: an integral order-preserving map into
  `{0,...,n}` decomposes by its level sets into `n` degree-one maps.
* It is a normal affine semigroup ring, hence Cohen--Macaulay; in
  characteristic zero its toric singularities are rational.
* Its defining Hibi relations have a quadratic Groebner basis, hence it is
  Koszul.
* `Q_20` is pure, so its Hibi ring is Gorenstein.  Its codegree is 3, so its
  `a`-invariant is `-3 < 0`.

Thus even the package

```text
standard + normal + CM + rational singularities + Koszul + Gorenstein + a<0
```

does not imply nonnegative ordinary monomial coefficients.  This also kills a
generic Riemann--Roch argument: the same polynomial is the Hilbert polynomial
of an ample toric line bundle, so one of the Todd-class pairings in

```text
chi(L^n) = sum_k n^k/k! * integral(c1(L)^k Td_{d-k})
```

is negative despite all of the structure above.  An LR-specific Todd
effectivity theorem would be needed; ordinary equivariant RR does not provide
one.

## 3. Real-rootedness is already false for genuine hives

For every `k >= 4`, the genuine rank-five family

```text
lambda = (2,2,1)
mu     = (k,3,2,1)
nu     = (k+1,4,3,2,1)
```

has

```text
P(n) = 1 + 2n + 17n^2/12 + n^3/2 + n^4/12
     = (n+1)(n+2)(n^2+3n+6)/12.
```

Its zeros are

```text
-1, -2, (-3+i sqrt(15))/2, (-3-i sqrt(15))/2.
```

So a real-rooted/Lorentzian-numerator proof cannot hold in this form.  The
exact held-out checks for this family are in `tier0/VALIDATION_TIER0.txt`.
Notice that the example is nevertheless strictly Hurwitz.

## 4. Why Hurwitz stability would be enough

Let `P` have real coefficients, positive leading coefficient, and `P(0)=1`.
If every zero has negative real part, its real factorization is a product of

```text
n+a                         (a>0),
n^2 + 2a n + (a^2+b^2)     (a>0).
```

Every factor has positive coefficients.  Hence strict Hurwitz stability
implies KTT coefficientwise positivity.  Closed left-half-plane stability
would imply nonnegativity, subject to the harmless zero-root case excluded by
`P(0)=1`.

This implication is proof-quality and rank-uniform.  The missing assertion is
that LR stretching polynomials are Hurwitz.

### Exact evidence, not a theorem

`hstar_spread/hstar_atlas2.tsv` contains 2,492 distinct `h*` profiles attached
to actual partition triples and retained only from records with a passed
held-out check (`heldout_ok=true` or `extra_match=yes`).  The exact rational
Routh test gives

```text
Reeve q=13 -> RHP(2)       [negative control]
LR atlas    -> STRICT 2492/2492
RHP failures -> 0
```

Reproduction:

```text
cd problems_external/ktt_lr_negativity/hstar_spread
python hurwitz.py
```

Hashes:

```text
hstar_atlas2.tsv  EFA01D8474572E5F38F1258E3FEF1C3F1FC48EA0D428C09D8FFB769A66C784CB
hurwitz.py        EE095A481E9FC198F257D4EB624F82E76ADE3D77C3D00593B962E252199E4F48
```

The independent two-engine rank-five validation corpus contributes 52 records
but only three distinct polynomials; all three are strictly Hurwitz.  This is
useful falsification evidence only.  A `NO_HIT` cannot establish
LR-HURWITZ.

One broad scan initially reported the polynomial

```text
1 + 221n/60 + 5n^2/8 + 43n^3/12 - n^4/8 + 7n^5/30.
```

That record explicitly had `heldout:false`; it was an under-degree fit and
failed its later samples.  It is excluded, not an LR counterexample.  The
canonical strict scanner is `hilbert_hurwitz_audit_v4.py` (SHA-256
`BC24E19A6B8CBC3D735AF84EA16C319AC6AF14EEB1EB089D00B578FADD163E91`).
Version 3 is superseded because its wrapper accidentally rebound its imported
validator recursively.

## 5. Speyer's 2026 theorem does not control the stretch ray

Speyer proves that skeps count LR coefficients (Theorem 3.16) and that
`SkepExt(g+,lambda)` is `L`-log-concave as a function of `lambda` for **fixed
`g+`** (Theorem 6.1).  Corollary 3.17 recovers the LR coefficient only after
summing over `g+` with fixed `nu` and fixed `lambda+mu`.  Immediately after
Theorem 6.1, the paper explicitly notes that a sum of `L`-log-concave functions
need not be `L`-log-concave, so the theorem does not imply the corresponding
statement for the LR coefficient.  Stretching also changes `nu`,
`lambda+mu`, and the set of `g+` being summed over.

Primary source: Speyer, *L-log-concavity and a proof of the conjecture of Lam,
Postnikov and Pylyavskyy*, Theorems 3.16 and 6.1 and the paragraph following
Theorem 6.1:

<https://arxiv.org/pdf/2601.05007>

There are two further exact obstructions.

1. Stretch-ray log-concavity itself is false.  Chindris--Derksen--Weyman give,
   for `p>=21`, partitions with

   ```text
   P(0)=1,
   P(1)=binom(p+2,2),
   P(2)=binom(p+5,5).
   ```

   At `p=21`, `P(1)^2=253^2=64009 < 65780=P(2)`, contradicting ordinary
   log-concavity on the stretching ray.  See Theorem 1.2 of
   <https://arxiv.org/pdf/math/0610819>.

2. Even strong FKG/log-supermodularity does not imply Hurwitz stability.  On
   the Boolean lattice of subsets of `[3]`, the weights

   ```text
   w(S)=4^(binom(|S|,2))
   ```

   are log-supermodular, but their size generating polynomial is

   ```text
   1 + 3t + 12t^2 + 64t^3.
   ```

   The cubic Hurwitz determinant is `12*3-64*1=-28<0`.  Thus no generic
   implication from Speyer's `L`-log-concavity/strong-FKG property to Hurwitz
   stability exists.

## 6. Direct-Proof-Guard conclusion

The proposed Hilbert route has reached its exit condition:

```text
DEAD: generic Hilbert structure has no monomial bridge.
```

LR-HURWITZ is a clean sufficient conjecture, and the exact data currently
supports it, but it is strictly stronger than KTT and no algebraic or skep
theorem above implies it.  Replacing KTT by an unbounded hierarchy of Hurwitz
determinants would be a reformulation maze, not a proof.  A future revival of
this route requires one new load-bearing, rank-uniform theorem--for example an
LR-specific positive factorization or a stability-preserving operator that
constructs every stretching polynomial--not another fixed-rank census.
