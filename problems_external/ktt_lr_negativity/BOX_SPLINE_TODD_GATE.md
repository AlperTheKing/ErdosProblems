# Box-spline/Todd route: exact identity and exact obstruction

## Outcome

The box-spline deconvolution formula gives an exact rank-uniform expression
for every coefficient of a generic stretched Littlewood--Richardson
polynomial.  It does **not** by itself prove coefficientwise positivity: the
resulting Todd operator is not positivity preserving, even on the type-A4
Dahmen--Micchelli polynomial space.  An exact nonnegative polynomial in that
space is sent to a polynomial with two negative monomial coefficients.

This is an obstruction to a proof using only

1. nonnegativity of the volume/chamber polynomial, and
2. membership in the Dahmen--Micchelli space.

It is not a KTT counterexample.  A successful proof through this route would
need a new differential inequality special to *actual hive volume chamber
polynomials*.

## Exact stretching operator

Let `j` be the one-sided homogeneous chamber polynomial of the volume function
`J` at a compatible type-A triple `x=(lambda,mu,nu)`, and let

`d=(r-1)(r-2)/2`.

McSwiggen's Corollary 3.5 gives, with the operator acting in the third
argument,

```
C^nu_{lambda,mu} = Ahat(Phi+) J(lambda+rho,mu+rho;nu+rho),
Ahat(Phi+) = product_{alpha>0}
  D_alpha/(exp(D_alpha/2)-exp(-D_alpha/2)).
```

For a shielded/generic ray, homogeneity therefore gives

```
C^{N nu}_{N lambda,N mu}
 = sum_{k=0}^d N^(d-k) [T_k j](x),
```

where the homogeneous operators `T_k` are defined by

```
sum_{k>=0} z^k T_k
 = exp(z(D_rho^(lambda)+D_rho^(mu)+D_rho^(nu)))
   product_{alpha>0}
     (z D_alpha^(nu))/(exp(z D_alpha^(nu)/2)-exp(-z D_alpha^(nu)/2)).
```

Using `rho=(1/2) sum_{alpha>0} alpha`, this becomes the Todd form

```
sum_{k>=0} z^k T_k
 = exp(z(D_rho^(lambda)+D_rho^(mu)))
   product_{alpha>0}
     (z D_alpha^(nu))/(1-exp(-z D_alpha^(nu))).
```

Consequently the full KTT conjecture on generic chambers is exactly the family
of differential inequalities

```
[T_k j](lambda,mu,nu) >= 0,  0 <= k <= d.
```

The box-spline formula supplies the identity, but not these inequalities.
Boundary rays additionally require the one-sided chamber limit in the
deconvolution theorem.

## Exact positivity obstruction in type A4

Identify the positive roots of `A4` with the oriented edges
`e_i-e_j` (`i<j`) of `K5`.  Let `L` be the covector with vertex potentials

```
(L(e_1),...,L(e_5)) = (1,0,1,1,0)
```

and put `p(x)=L(x)^4`.  Plainly `p>=0` everywhere.

The graphic cocircuits are the nontrivial cuts of `K5`.  They have sizes 4 or
6.  A size-6 cocircuit differential annihilates `p` by degree.  Every size-4
cut is a vertex star; because both level sets of `L` have at least two
vertices, each star contains an edge `alpha` with `L(alpha)=0`.  Hence its
cocircuit derivative also annihilates `p`.  By the standard
Dahmen--Micchelli cocircuit characterization,

```
p belongs to D(Phi+).
```

On the ten positive roots the values of `L` are

```
(1,0,0,1,-1,-1,0,0,1,1).
```

Writing `Todd(t)=t/(1-exp(-t))`, exact multiplication gives

```
product_{alpha>0} Todd(z L(alpha))
 = 1 + z + z^2/4 - z^3/12 - z^4/20 + O(z^5).
```

Therefore, at a point with `L(x)=N`,

```
[product_{alpha>0} Todd(D_alpha)] p(x)
 = N^4 + 4 N^3 + 3 N^2 - 2 N - 6/5.
```

The input is globally nonnegative and is in the exact polynomial space on
which box-spline deconvolution acts, but the output has negative `N` and
constant coefficients.  Thus no argument asserting that the Todd/deconvolution
operator preserves monomial coefficientwise positivity on nonnegative
Dahmen--Micchelli chamber polynomials can be valid.

The standard-library replay is

```
python box_spline_todd_gate.py
```

## Structural interpretation

The obstruction begins exactly where the universal low-rank argument stops.
The one-variable Todd factor is

```
t/(1-exp(-t)) = 1 + t/2 + t^2/12 - t^4/720 + ... .
```

The first intrinsically negative Bernoulli term is order four.  Hence the
box-spline identity is compatible with positivity of the top three local
coefficients and with the special low-dimensional results, while it offers no
automatic control of all lower coefficients starting in higher rank.

## Primary sources

- Colin McSwiggen, *Box splines, tensor product multiplicities and the volume
  function*, Algebraic Combinatorics 4 (2021), Corollary 3.5 and equations
  (26)--(30): <https://arxiv.org/abs/1909.12278>.
- Etienne Rassart, *A polynomiality property for Littlewood--Richardson
  coefficients*, JCTA 107 (2004):
  <https://arxiv.org/abs/math/0308101>.
- Robert Coquereaux and Jean-Bernard Zuber, *From orbital measures to
  Littlewood--Richardson coefficients and hive polytopes*, AIHPD 5 (2018):
  <https://arxiv.org/abs/1706.02793>.
