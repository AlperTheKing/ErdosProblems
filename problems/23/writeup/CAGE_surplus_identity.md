# CAGE Total-Surplus Identity

This note records an exact identity that every CAGE certificate satisfies.
It does not prove universal CAGE existence, but it is a useful constraint on
any tight CAGE/KKT obstruction.

Use the notation of `CAGE_certificate_note.md`.  For a gate

```text
g = (f,t,e)
```

write

```text
m_g := H_{f,t} pi_{f,t,e}.
```

By the CAGE marginal equation `(R2)`,

```text
sum_{i<=t<j} alpha_{f,i,j,t,e} = m_g.
```

Since every layer probability vector has mass one,

```text
sum_v A_g(v) = m_g,
sum_v B_g(v) = m_g.
```

Therefore the total CAGE budget used by a certificate `(alpha,r)` is

```text
sum_v sum_g (r_g A_g(v) + r_g^{-1} B_g(v))
  = sum_g (r_g + r_g^{-1}) m_g.
```

Now sum the minimum possible gate masses.  For one bad edge `f` of length
`L=ell(f)`,

```text
sum_t H_{f,t}
 = sum_t sum_{0<=i<=t<j<L} 1/(j-i)
 = sum_{0<=i<j<L} sum_{t=i}^{j-1} 1/(j-i)
 = binom(L,2).
```

Also `sum_e pi_{f,t,e}=1` for every gap `t`.  Hence

```text
sum_g 2 m_g = sum_f L_f(L_f-1).
```

Let

```text
Ltot := sum_f ell(f) = sum_v S(v),
Gamma := sum_f ell(f)^2.
```

Then

```text
sum_g 2m_g = Gamma - Ltot.
```

The total vertex capacity in CAGE is

```text
sum_v (N-S(v)) = N^2 - Ltot.
```

Combining these equalities gives the exact total-slack formula

```text
sum_v [
  N-S(v) - sum_g (r_g A_g(v) + r_g^{-1} B_g(v))
]
=
N^2 - Gamma
-
sum_g m_g (r_g + r_g^{-1} - 2).
```

Equivalently,

```text
total CAGE slack = extremal slack - ratio waste.
```

Consequences:

1. Every feasible CAGE certificate obeys

   ```text
   sum_g m_g (r_g + r_g^{-1} - 2) <= N^2 - Gamma.
   ```

2. In an equality case `Gamma=N^2`, every feasible CAGE certificate has
   `r_g=1` for every positive-mass gate, total vertex slack zero, and hence
   every vertex budget is tight.

3. In a strict case `Gamma<N^2`, a CAGE obstruction cannot be explained by
   total capacity.  The obstruction must be purely distributional: the ratio
   waste and routed load concentrate on the wrong vertices.

This identity is independent of the floating solver, exact repair, and any
particular choice of `alpha`.  It follows only from `(R2)` and the layer-mass
identity.
