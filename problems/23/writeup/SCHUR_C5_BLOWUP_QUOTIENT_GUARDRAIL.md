# Schur C5 Blowup Quotient Guardrail

This guardrail explains why the quantitative Schur minority-current target is
false, while bare Schur row-sum positivity may still survive.

Take a C5 blowup with sizes

```text
[k+1,k,k+1,k,k+1]
```

and a connected maximum cut leaving one minimum-product edge bad.  The
gamma-minimal tied maxcuts are the four choices leaving a minimum product edge
bad.  Put the bad edge between classes `0` and `1`.

Let

```text
b = BETA[5].
```

For a vertex `o` in overloaded class `1` (or symmetrically class `3`):

```text
N = 5k+3,
T(o) = 5k+5,
a_o = T(o)-N = 2,
A = 4k,
g_o = A - 2a_o = 4k-4.
```

The underloaded classes have harmonic defect values

```text
psi0 = psi4 = 3/(3 + b k),
psi2        = 3/(3 + 2 b k).
```

The normal Schur current is

```text
I_o = b(k+1)(psi0 + psi2),
rho_o = I_o - 2.
```

Thus

```text
rho_o = b(k+1) * ( 3/(3+bk) + 3/(3+2bk) ) - 2.
```

As `k -> infinity`,

```text
rho_o -> 5/2,
g_o -> infinity.
```

Consequently no fixed positive coefficient `c` can make

```text
rho_o >= c*(A-2a_o)
```

hold uniformly.

With the repository rational `BETA[5]`, the `1/25` pointwise margin

```text
25*rho_o - (A-2a_o)
```

first fails at `k=16`:

```text
k=13, N=68:   +8.4838246968
k=14, N=73:   +4.8568737145
k=15, N=78:   +1.1863529360
k=16, N=83:   -2.5205246417
k=20, N=103: -17.6129970708
k=100,N=503:-334.3912356816
```

The broader harvest split fails earlier:

```text
25*rho_o - 4(cU_o-a_o) < 0
```

already at `k=5`, i.e. sizes `[6,5,6,5,6]`.

This guardrail rules out:

```text
rho_o >= (A-2a_o)/25,
25*rho_o >= 4(cU_o-a_o),
```

and every fixed positive-coefficient strengthening of bare absorption.

Any surviving Schur proof must target a coefficient-free statement, such as
bare non-majority absorption or PSD/effective-shunt domination.
