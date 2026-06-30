# Local Per-Cycle Circulant PSD Identity

Status: proof note for the local atom in the `SPEC` route.

Let `C_ell` be an odd cycle of length `ell >= 5`, with cyclic vertices
`v_0,...,v_{ell-1}`. Let `p` be the all-ones vector on the cycle support,
let `D = ell * I` on that support, and let `L = L(C_ell)` be the cycle
Laplacian.

Define the sharp coefficient

```text
a_ell = ell / (2 + 2*cos(pi/ell)).
```

Then

```text
D - p p^T - a_ell L  >=  0
```

in PSD order. Equivalently,

```text
p p^T + a_ell L  <=  ell I.
```

## Fourier proof

The Fourier basis diagonalizes both `J = p p^T` and `L`. The cycle Laplacian
eigenvalues are

```text
mu_k = 2 - 2*cos(2*pi*k/ell),       k=0,...,ell-1.
```

On the constant mode, `J` has eigenvalue `ell` and `L` has eigenvalue `0`, so
`ell I - J - a_ell L` has eigenvalue `0`.

On every nonconstant Fourier mode, `J` has eigenvalue `0`, and the eigenvalue is

```text
ell - a_ell * mu_k.
```

For odd `ell`, the largest Laplacian eigenvalue is

```text
mu_max = 2 + 2*cos(pi/ell),
```

attained at `k=(ell-1)/2,(ell+1)/2`. Hence `a_ell = ell/mu_max` makes
`ell - a_ell*mu_k >= 0` for all `k`. This proves the PSD inequality.

## Rational exact coefficient

For exact rational gates use

```text
abar_ell = ell^3 / (4*(ell^2 - 2)).
```

It is enough to check `abar_ell <= a_ell`, because lowering the coefficient of
`L` only increases `D - p p^T - a L`.

The inequality `abar_ell <= a_ell` is equivalent to

```text
cos(pi/ell) <= 1 - 4/ell^2.
```

Using `cos x <= 1 - x^2/2 + x^4/24` with `x=pi/ell`, it is enough that

```text
pi^2/2 - pi^4/(24*ell^2) >= 4.
```

For `ell >= 5` the left side is minimized at `ell=5`, where it is already
larger than `4`. Thus `abar_ell <= a_ell` for every odd `ell >= 5`, and

```text
D - p p^T - abar_ell L >= 0.
```

## Geodesic-averaged corollary

For a bad edge `f`, let `P_f` be the set of shortest `B`-geodesics between its
endpoints. Closing each geodesic with `f` gives an odd cycle of length `ell(f)`.
For a geodesic `Q`, let `q_Q` be the cycle vertex indicator and `L_Q` the cycle
Laplacian. The single-cycle inequality gives

```text
q_Q q_Q^T + abar_ell L_Q <= ell diag(q_Q).
```

Averaging over `Q in P_f` gives

```text
E[q_Q q_Q^T] + abar_ell L_{tau_f} <= ell diag(p_f),
```

where `p_f = E[q_Q]` and `tau_f` is the averaged cycle-edge incidence. Since

```text
p_f p_f^T <= E[q_Q q_Q^T]
```

by Jensen/Covariance PSD, we obtain the exact per-bad-edge local comparison

```text
p_f p_f^T + abar_{ell(f)} L_{tau_f} <= ell(f) diag(p_f).
```

Summing over bad edges gives the local half of the spectral sandwich:

```text
K + L_omega <= diag(T),
```

with `omega(e)=sum_f abar_{ell(f)} tau_f(e)`. The remaining global work is the
separate domination

```text
L_omega + diag(N-T) >= 0,
```

or its load-PSC/component-bank equivalent.
