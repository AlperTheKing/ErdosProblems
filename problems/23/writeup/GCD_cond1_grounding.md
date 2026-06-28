# GCD Cond1 Grounding Reduction

This note isolates the first Schur condition in the Green-capacity route.

Let

```text
H = L_omega + diag(N - T),
O = {v : T(v) > N},
Q = V \ O.
```

The Schur split of GCD uses

```text
H_QQ = H[Q,Q].
```

## Grounded-Laplacian Criterion

For a component `C` of the omega-support graph induced by `Q`, define

```text
ground(v) = (N - T(v)) + omega(v,O).
```

Then

```text
x^T H_QQ x =
  sum_{uv in E_omega[Q]} omega_uv (x_u - x_v)^2
  + sum_{v in Q} ground(v) x_v^2.
```

Therefore `H_QQ` is positive definite iff every omega-component `C` in
`Q` has positive total ground, equivalently iff no `Q`-component has

```text
T(v)=N for all v in C
and
omega(C,O)=0.
```

When `O` is empty this positive-definiteness condition is not part of the
Schur reduction; the full GCD matrix may have the expected constant null
mode on odd-cycle blow-up extremals.

## Reduction To SAT-ZMU-CONN

Assume `O` is nonempty and suppose, for contradiction, that a dangerous
component `C` exists:

```text
C is an omega-component in Q,
T(v)=N for every v in C,
omega(C,O)=0.
```

The omega-support graph has:

```text
positive omega on every bad edge;
positive omega on exactly the B-edges with positive shortest-cycle traffic mu.
```

Thus omega-components are the same positive-traffic/K components, with
zero-mu B-edges removed.

Since the cut graph `B` is connected and `O` is nonempty outside `C`, there
is a `B`-edge `uv` with `u in C`, `v notin C`. This edge cannot have
positive `mu`; otherwise it would be a positive omega edge and would either
join `v` to the same `Q` component or give omega-boundary from `C` to `O`.
Hence

```text
mu(uv)=0,     T(u)=N.
```

The saturation-qualified lemma `SAT-ZMU-CONN` says that if `O` is nonempty
and a zero-mu B-edge has a saturated endpoint, then that endpoint's
positive-traffic/K component meets `O`. This contradicts `omega(C,O)=0`.

Consequently, under `SAT-ZMU-CONN`, every omega-component of `Q` is grounded
and `H_QQ` is positive definite.

## Remaining Proof Obligation

This does not prove `SAT-ZMU-CONN`; it repackages the first Schur condition
of GCD into that already-verified saturation/maxcut statement. The remaining
work for cond1 is therefore the existing zero-moat / gamma-min forcing proof
of `SAT-ZMU-CONN`.
