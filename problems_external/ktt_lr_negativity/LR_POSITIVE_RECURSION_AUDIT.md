# LR-specific positive recursion audit for full KTT

## Verdict

No known tableau, Kostka, rigged-configuration, branching, or Horn recursion
preserves stretching in the form needed to prove ordinary monomial
coefficient positivity.  Each currently available positive formula fails at
one of three exact points:

1. it extracts a fixed content or a selected `q`-coefficient;
2. its positive summation set depends on the stretch parameter; or
3. recovering the desired irreducible multiplicity requires an alternating
   sum or finite difference.

Thus this route supplies no rank-uniform proof of KTT.

## Direct-Proof-Guard route

* **Deliverable:** prove that every nonzero polynomial
  `P(n)=c(n nu; n lambda,n mu)` has nonnegative ordinary monomial
  coefficients, uniformly in the rank.
* **Frontier lemma:** `LR-POSITIVE-RECURSION`: express every `P(n)` by a
  rank-reducing finite sum/product whose index set is independent of `n`,
  whose leaves are known-positive polynomials, and which has no coefficient
  extraction or subtraction.
* **Bridge:** nonnegative sums and products preserve ordinary monomial
  coefficient positivity, so induction would close at rank four.
* **Falsifiable action:** apply the proposed bridge to fixed-content tableaux,
  parabolic Kostka/fermionic formulas, and Horn or branching reduction.
* **Exit:** stop on an `n`-dependent index set, diagonal/`q`-coefficient
  extraction, or cancellation.  All three exits occur below.

## 1. Marked order maps count all SSYT, not an LR fiber

Jochemko--Menon prove that the counting polynomial of an integral marked
order polytope on a skew-shape poset has nonnegative coefficients in the
successive marking differences.  In particular, their Theorem 3.5 proves
Ehrhart positivity of the skew Gelfand--Tsetlin polytope.  Stretching the skew
shape is genuinely preserved:

```text
n GT_m^k(y,z) = GT_m^k(ny,nz).
```

This counts **all** semistandard tableaux of the stretched skew shape with a
bounded alphabet.  An LR coefficient instead fixes the content and imposes
the highest-weight/lattice-word condition.  If `x_{i,j}` is the number of
entries at most `j` in row `i`, fixed content imposes the global equations

```text
sum_i (x_{i,j} - x_{i,j-1}) = n mu_j.
```

These are row-sum fibers, not marked coordinates and not the flagged faces
covered by the marked-order theorem.  Equivalently, extracting content is a
diagonal coefficient operation, and coefficient extraction does not preserve
ordinary monomial positivity in the stretch variable.

There is also an exact geometric obstruction to identifying the fiber with an
integrally marked order polytope.  Such a polytope has a totally unimodular
order-constraint matrix and hence integral vertices.  The genuine rank-five
LR triple

```text
lambda = (2,2,1,0,0)
mu     = (4,3,2,1,0)
nu     = (5,4,3,2,1)
```

has a four-dimensional hive polytope with seven vertices, two half-integral.
The exact local certificate is recorded in `tier0/BUILD_TIER0.md`.  Therefore
the LR fiber is not itself an integral marked-order polytope (nor a face or
product of such polytopes) under an integral affine change of variables.

Primary source: Jochemko--Menon, *Ehrhart positivity for marked order
polytopes*, Proposition 2.1 and Theorems 1.3 and 3.5:
<https://arxiv.org/pdf/2604.08394>.

## 2. The fermionic formula has an `n`-dependent configuration set

For a dominant sequence of rectangles `R`, Kirillov's fermionic formula is

```text
K_{lambda,R}(q)
 = sum_{C(lambda;R)} q^charge
     product_{k,s} [P_s^(k)+m_s^(k) choose m_s^(k)]_q.
```

Every displayed summand is positive in `q`.  This does not give a positive
polynomial in the stretching parameter.  A configuration contains partitions
whose prescribed sizes are

```text
|rho^(k)| = sum_{j>k} lambda_j
            - sum_a width(R_a) max(height(R_a)-k,0),
```

and admissibility is imposed by vacancy inequalities depending on `rho`.
After `(lambda,R)` is replaced by `(n lambda,nR)`, the required sizes multiply
by `n`, but the partitions of those sizes are not just the `n`-fold dilates of
the old configurations.  Thus `C(n lambda;nR)` is an `n`-dependent lattice
index set.  Summing positive terms over it is another lattice-point problem,
not a fixed positive polynomial decomposition.

The LR specialization does not remove this defect.  Equation (5.46) realizes
`c^nu_{lambda,mu}` as the coefficient of the lowest `q`-power of a parabolic
Kostka polynomial.  Under stretching, this is a moving coefficient
`[q^{n a}] K_{n lambda~,nR~}(q)`, not evaluation at `q=1` of a fixed family.
Kirillov explicitly states the required stretch-coefficient positivity as
Conjecture 1.9 and warns immediately afterward that it does not follow from
the rational generating function and that its numerator can have negative
coefficients.  Invoking it would therefore assume a stronger open conjecture,
not prove KTT.

Primary source: Kirillov, *An Invitation to the Generalized Saturation
Conjecture*, Definition 5.1, Theorem 5.3, equation (5.46), and Conjecture 1.9:
<https://www.kurims.kyoto-u.ac.jp/preprint/file/RIMS1452.pdf>.

## 3. Reduction to ordinary Kostka numbers is signed and is not a stretch

The Weyl character formula gives the exact Racah--Speiser identity

```text
c^nu_{lambda,mu}
 = sum_{w in S_r} (-1)^length(w)
     mult_lambda(nu + rho - w(mu+rho)).
```

Consequently,

```text
c^{n nu}_{n lambda,n mu}
 = sum_w (-1)^length(w)
     mult_{n lambda}(n(nu-w mu) + rho-w rho).
```

The summands have alternating signs, and for `w != 1` their weights contain
the non-scaling shift `rho-w rho`.  They are not stretched Kostka polynomials
of the form `K_{n alpha,n beta}`.  Hence even a proof of the separate stretched
Kostka positivity conjecture would not pass through this formula.

Shrivastava's Corollary 1 gives the same obstruction explicitly: a general LR
coefficient is a signed sum of Kostka numbers, with the Weyl shift `rho` in
the indexing.  Kostka numbers are special LR coefficients in the forward
direction, but the reverse reduction is not positive.

Primary source: Shrivastava, *Littlewood--Richardson coefficients as a signed
sum of Kostka numbers*, Theorem 1 and Corollary 1:
<https://arxiv.org/pdf/2211.10669>.

## 4. Horn factorization preserves stretching only on the boundary

King--Tollu--Toumazet prove an exact product decomposition when an essential
Horn inequality is saturated.  Homogeneity preserves that equality under
stretching, so this is a valid positive rank reduction.  But it is defined
only on Horn facets.  A triple is called primitive precisely when every
essential Horn inequality is strict; the factorization gives no reduction on
the full-dimensional primitive region.

The obstruction already occurs in the first rank beyond the proved rank-four
case.  For

```text
lambda = (2,2,1,0,0)
mu     = (4,3,2,1,0)
nu     = (5,4,3,2,1),
```

all 142 essential rank-five Horn inequalities are strict (minimum integral
slack one).  Yet

```text
P(n) = (n+1)(n+2)(n^2+3n+6)/12
```

has degree four.  So Horn factorization cannot reduce even this genuine
rank-five stretching problem to rank four.  The exact Horn checker is
`r5_lowerdim_horn_factorization_gap.py`; applying its defining essential-Horn
test to this triple returns `142, minimum slack 1, equalities 0`.

Primary source: King--Tollu--Toumazet, *Factorisation of
Littlewood--Richardson coefficients*, JCTA 116 (2009), 314--333:
<https://doi.org/10.1016/j.jcta.2008.06.005>.

## 5. Branching and Pieri induction require inversion

Restriction from `GL_r` to `GL_{r-1}` is positive and multiplicity-free:

```text
s_lambda(x_1,...,x_{r-1},1)
 = sum_{alpha interlaces lambda} s_alpha(x_1,...,x_{r-1}).
```

Applied to a tensor product, it determines only the cumulative quantities

```text
sum_{gamma interlaces nu} c^nu_{lambda,mu}
 = sum_{alpha interlaces lambda, beta interlaces mu} c^gamma_{alpha,beta}.
```

Recovering an individual coefficient requires triangular/Mobius inversion,
hence subtraction.  Under stretching, the interlacing intervals themselves
grow from `[lambda_{i+1},lambda_i]` to
`[n lambda_{i+1},n lambda_i]`; the positive side is also an `n`-dependent
sum.  Thus branching does not supply `LR-POSITIVE-RECURSION`.

The same issue appears in Pieri induction.  Products of one-row Schur
functions expand positively, but isolating a specified irreducible uses the
inverse Kostka matrix or Jacobi--Trudi determinant.  Already

```text
s_(1,1) = s_(1)^2 - s_(2)
```

forces cancellation.  Positivity of the forward branching/Pieri rule is
therefore not positivity of the inverse recursion needed for LR
multiplicities.

## Direct-Proof-Guard conclusion

```text
DEAD: no stretching-preserving LR-positive recursion.
```

The only exact product bridge found is Horn factorization, and it stops on
primitive triples before rank induction begins.  Tableaux and rigged
configurations give positive formulas for each integer value but have moving
content/configuration sets; Kostka and branching reductions require
coefficient extraction or cancellation.  Continuing with more fixed-rank
recurrences would be a reformulation maze.

A future revival requires a genuinely new theorem: a disjoint,
`n`-independent decomposition of every primitive LR tableau/hive family into
pieces whose counting polynomials are already monomial-positive.  None of the
known formulas above provides such a decomposition.
