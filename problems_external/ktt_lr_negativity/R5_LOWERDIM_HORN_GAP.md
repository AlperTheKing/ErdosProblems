# Rank-five lower-dimensional Horn-factorisation gap

Date: 2026-07-22

Horn-facet factorisation does not remove the lower-dimensional caveat in the
rank-five codimension-four BV theorem.  The exact example

```text
lambda = (4,3,3,1,0)
mu     = (4,2,1,1,0)
nu     = (6,5,4,2,2)
```

has four hive vertices, affine dimension three, and unstretched
Littlewood--Richardson coefficient four.  Nevertheless all 142 essential
size-five Horn inequalities are strict; the minimum integral slack is one.
The King--Tollu--Toumazet Horn factorisation theorem is therefore not
triggered.

The dimension drop instead occurs on the Weyl-chamber walls

```text
lambda_2=lambda_3,  mu_3=mu_4,  nu_4=nu_5.
```

Consequently it is not enough to factor saturated essential Horn facets into
ranks at most four.  Extending the full-dimensional rank-five theorem requires
an intrinsic-lattice theorem for such chamber-wall contractions (or a separate
classification of them).

Exact checker:

```text
python r5_lowerdim_horn_factorization_gap.py
```

It generates the essential Horn triples from the defining condition
`c_{tau(I),tau(J)}^{tau(K)}=1`, counts those small coefficients by the exact
hive model, and makes no floating-point decision.

Reference: King--Tollu--Toumazet, *Factorisation of Littlewood--Richardson
coefficients*, Journal of Combinatorial Theory A 116 (2009), 314--333:
<https://doi.org/10.1016/j.jcta.2008.06.005>.
