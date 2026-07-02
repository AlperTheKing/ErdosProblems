# C5-RS Assessment

Status: strategic assessment after Claude's 2026-07-01 C5-RS gate.

## Statement

For an all-length-5 positive K-component and a shortest C5 row

```text
Q = (q0,q1,q2,q3,q4),
s_i = Tw_C(q_i),
m = |M| globally,
eta = N^2/25 - m,
tau = 5m/N,
```

the proposed row stability lemma is:

```text
sum_i max(0, s_i - tau) <= (1 + 25/N) * eta.
```

Claude exact-gated this on the L=5-multi battery and reports 0 failures,
tight only at balanced C5 blow-ups when `eta=0`.

## Reduction to GERSH

Use uniform width

```text
w_i = N/5.
```

Then

```text
sum_i w_i = N,
w_i w_{i+1} = N^2/25 >= m.
```

Also

```text
tau = 5m/N = N/5 - 5 eta/N,
5 tau = N - 25 eta/N.
```

Therefore

```text
sum_i max(s_i, tau)
  = 5 tau + sum_i max(0, s_i - tau)
  <= N - 25 eta/N + (1 + 25/N) eta
  = N + eta.
```

Since `sum_i s_i <= sum_i max(s_i,tau)`, this gives the rowwise GERSH
bound

```text
sum_i s_i <= N + eta.
```

Thus C5-RS is theorem-sufficient for the entire L=5-multi branch.  It does
not need the sharp PMS-5 coefficient `2/3`.

## Relation To Seven-Cut PMS-5

The seven-cut/PMS-5 route proves a sharper sum bound in the equality-atom
model:

```text
sum_i s_i <= N + (2/3) eta.
```

This does **not** imply C5-RS as a formal inequality, because C5-RS controls
the positive part above the moving threshold `tau`, not only the total sum.

For example, at the level of abstract vectors with `N=10`, `eta=1`, and
`tau=3/2`, the vector

```text
s = (32/3,0,0,0,0)
```

satisfies the PMS-5 sum ceiling

```text
sum s_i = 32/3 = N + (2/3) eta,
```

but violates C5-RS badly:

```text
sum_i max(0,s_i-tau) = 55/6 > 7/2 = (1+25/N)eta.
```

This vector is not claimed to be graph-realizable; it only shows that
PMS-5 sum control alone cannot prove C5-RS.  A bridge would need additional
distribution/row-regularity input.

Conversely, C5-RS implies the GERSH-level sum bound `N+eta`, but not the
sharper PMS-5 coefficient `2/3`.

So the two routes are related but logically independent at the level of
their main inequalities:

```text
C5-RS: distribution / positive-part stability around tau, GERSH-level.
PMS-5: sharp total-overlap stability for sparse equality atom.
```

## Likely Proof Shape

C5-RS should be attacked directly as a C5 stability lemma.

The layer-cake form is:

```text
sum_i max(0, s_i - tau)
  = integral_{tau}^{infty} |{i in {0..4}: s_i > t}| dt.
```

At `eta=0`, the lemma says:

```text
m = N^2/25  =>  s_i <= N/5 for every C5 row vertex.
```

This is exactly the balanced C5 rigidity regime.  Away from equality,
the excess over `tau` must be paid by the global product deficit
`eta = N^2/25 - m`.

This suggests proving a threshold version:

```text
For every t > tau, the set H_t={i:s_i>t} forces a max-cut/product deficit
large enough that integrating over t gives (1+25/N)eta.
```

That is a different target than the seven-cut face algebra and may bypass
the fingerprint enumeration entirely.
